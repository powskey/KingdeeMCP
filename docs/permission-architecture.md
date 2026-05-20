# 权限架构设计

> 目标：AI 调用金蝶 ERP 时，严格遵循企业现有的组织 / 岗位 / 角色 / 权限规则。员工没有权限的数据，AI 也不能绕过；高风险操作走二次确认或审批。

---

## 设计原则

1. **权限模型不在 MCP 重复造** —— 金蝶 RBAC 已有完整的角色 / 数据权限 / 字段权限体系，MCP 只做转发
2. **身份不能由 AI 自报** —— 谁在调用必须由可信源（OS 用户 / SSO / 配置）注入，不能放在工具参数里
3. **风险分级 + 拦截** —— 高风险写操作在 MCP 之上再加一层网关，触发审批流
4. **审计可追溯** —— 金蝶日志记录真实员工操作人，不是集成账号

---

## 四层架构

```
┌─────────────────────────────────────────────┐
│  L0  AI 客户端（Claude Desktop / Cursor）    │
└─────────────────────────────────────────────┘
                  ↓ stdio / HTTP
┌─────────────────────────────────────────────┐
│  L1  身份注入层                               │
│  - 从 SSO / OS 用户 / 配置读取员工 username  │
│  - AI 不可见、不可改                         │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  L2  风险网关层（新增）                       │
│  - 工具风险分级：low / medium / high         │
│  - high 走审批：返回 pending_id              │
│  - 审批通过后才真正执行                       │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  L3  MCP Server（当前 server.py）            │
│  - _do_post 注入 X-KDApi-RequestUser         │
│  - per-user session 池                       │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  L4  金蝶 ERP（权限源头）                     │
│  - 角色 / 数据权限 / 字段权限全部生效        │
│  - 操作日志记录真实员工                      │
└─────────────────────────────────────────────┘
```

---

## L1 身份注入层

### 起步方案：本机 env

每位员工在自己的 Claude Desktop / Cursor MCP 配置里加：

```json
{
  "mcpServers": {
    "kingdee": {
      "command": "uvx",
      "args": ["kingdee-mcp"],
      "env": {
        "KINGDEE_REQUEST_USER": "zhangsan"
      }
    }
  }
}
```

- 集成账号 `APP_ID/APP_SEC` 仍由公司统一管理
- 员工本人只看到自己的 username，改不了别人的

### 企业级方案：SSO 网关

MCP 部署为 HTTP 模式，前置一个网关：
- 网关验证员工 SSO token
- 解析出 username 注入到下游请求 header
- AI 客户端只持有自己的 token，无法伪造他人身份

---

## L2 风险网关层

### 工具风险分级

| 等级 | 处理 | 示例工具 |
|------|------|---------|
| **low** | 直接放行 | 所有 query / view 类只读工具 |
| **medium** | 记录日志 | save_bill、submit_bills |
| **high** | 拦截 → 审批 | audit_bills、delete_bills、unaudit_bills、create_and_audit、push_and_audit |

参数敏感型规则（待定）：
- save_bill 涉及金额 > 阈值 → 升级为 high
- 涉及特定客户/物料 → 升级

### 审批流程

high-risk 工具调用时：

1. 不立即执行，写入"待审批"队列
2. 返回结构化响应：
   ```json
   {
     "status": "pending_approval",
     "approval_id": "APV20260520001",
     "operator": "zhangsan",
     "operation": "audit_bills",
     "params": {"form_id": "PUR_PurchaseOrder", "bill_ids": "..."},
     "tip": "已提交审批，审批通过后自动执行"
   }
   ```
3. 审批载体可选：
   - **文件队列**（最简，1 天工时）：写到 `approval_queue.jsonl`，人工 CLI 审批
   - **钉钉/飞书审批单**（1 周）：调用对方 OpenAPI 发起审批
   - **自建 Web 审批页**（1 月+）：完整审批中心
4. 审批通过的回调里真正调用 MCP 工具执行

### 审批治理

- **超时**：pending 单 24h 未审批自动作废
- **审批人**：默认员工直属上级；金额超阈值升级到部门负责人
- **应急绕过**：仅 admin 角色可手动标记 emergency_override，全量审计留痕

---

## L3 MCP Server 改动

### Session 池

```python
# server.py
_session_pool: dict[str, str] = {}  # username -> session_id

async def _login(username: str) -> str:
    # 集成账号不变，session 与员工绑定
    payload = {"parameters": [ACCT_ID, USERNAME, APP_ID, APP_SEC, LCID]}
    ...
    _session_pool[username] = data["KDSVCSessionId"]
```

### Header 注入

`_do_post()`（`server.py:1567`、`server.py:1670`）改为：

```python
async def _do_post(username: str, session: str) -> httpx.Response:
    headers = {"Cookie": f"kdservice-sessionid={session}"}
    headers["X-KDApi-RequestUser"] = username  # 关键
    return await client.post(_url(ep_key), data={...}, headers=headers)
```

### Username 来源

```python
def _current_user() -> str:
    user = os.getenv("KINGDEE_REQUEST_USER")
    if not user:
        raise RuntimeError("KINGDEE_REQUEST_USER 未配置")
    return user
```

---

## L4 金蝶配置（零代码）

由金蝶管理员在 ERP 后台完成：

1. **用户管理** → 员工建账号（一次性）
2. **角色管理** → 配置数据权限（按部门 / 组织范围）、功能权限（哪些单据可读/写/审）
3. **集成用户** → 给集成账号开放"代理调用"权限，允许通过 `X-KDApi-RequestUser` 模拟其他员工

> ⚠️ 待验证：私有云金蝶版本是否支持 `X-KDApi-RequestUser`，不同版本字段名可能为 `X-KDApi-AcctID` 或 `AccessToken` 模式。需在部署前与金蝶顾问确认。

---

## 实施路线图

| 阶段 | 工时 | 交付 |
|------|------|------|
| **P0 身份注入** | 0.5 天 | L1 env + L3 header 注入 + per-user session 池 |
| **P1 风险分级** | 1 天 | RISK_LEVEL 表 + 装饰器 + low/medium 放行 |
| **P2 文件审批** | 1 天 | high-risk → approval_queue.jsonl + CLI 审批工具 |
| **P3 企业审批集成** | 1-4 周 | 钉钉/飞书/自建审批中心 |
| **P4 SSO 网关** | 2-8 周 | 取决于现有 SSO 基建 |

P0 + P1 + P2 一共 2.5 天即可上线最小可用版本，满足"按员工权限调用 + 高危拦截"两个核心诉求。

---

## 决策清单（需业务方确认）

1. L1 身份来源：本机 env 起步 / 直接上 SSO？
2. L2 审批载体：文件队列 / 钉钉飞书 / 自建？
3. 风险分级：是否需要参数敏感规则（金额阈值等）？
4. 审批超时与升级策略：直属上级 vs 固定审批组？
5. 金蝶版本是否支持 `X-KDApi-RequestUser`？
