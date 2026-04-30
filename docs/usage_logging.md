# 使用日志系统

本 MCP Server 内置了完整的使用日志系统，用于记录和分析 Agent 与金蝶 API 的交互情况。

## 功能特性

1. **自动记录** - 所有 API 调用自动记录，无需手动干预
2. **统计分析** - 实时聚合工具使用频率、成功率、耗时分布
3. **报告生成** - 支持 text/markdown/json 多种报告格式
4. **错误分类** - 自动归类常见错误类型，便于问题诊断

## 使用方法

### 1. 查看实时统计

在 MCP 客户端中调用：

```
kingdee_usage_stats
```

返回示例：
```json
{
  "tool_stats": {
    "api:query": {"total": 150, "success": 145, "failed": 5, "total_ms": 3200},
    "api:save": {"total": 20, "success": 18, "failed": 2, "total_ms": 4500}
  },
  "error_stats": {
    "ValidationError": 3,
    "HTTPError": 2
  },
  "log_file": "./usage_log.jsonl"
}
```

### 2. 查看详细报告

```
kingdee_usage_report(format="text")
```

报告包含：
- 概览（总调用次数、成功率）
- 工具使用排行（Top 20）
- 错误类型分布
- 使用时段分布
- 改进建议（低成功率工具、高耗时工具）

### 3. 命令行生成报告

```bash
# 查看文本报告
python scripts/usage_report.py

# 查看 Markdown 报告
python scripts/usage_report.py --format markdown -o report.md

# 分析特定日志文件
python scripts/usage_report.py --file /path/to/log.jsonl

# 合并分析多个日志文件
python scripts/usage_report.py --dir /path/to/logs/
```

## 日志文件格式

日志存储为 JSONL 格式（每行一个 JSON 对象）：

```json
{"timestamp": "2026-04-30T10:30:00.123456", "tool": "api:query", "params_keys": ["FormId", "FilterString"], "duration_ms": 150.5, "success": true, "error_type": "", "result_preview": ""}
{"timestamp": "2026-04-30T10:30:01.234567", "tool": "api:save", "params_keys": ["form_id", "model"], "duration_ms": 3200.0, "success": false, "error_type": "HTTPError", "result_preview": "502 Bad Gateway"}
```

字段说明：
| 字段 | 类型 | 说明 |
|------|------|------|
| timestamp | string | ISO 格式时间戳 |
| tool | string | 工具名称（如 `api:query`、`api:save`） |
| params_keys | list | 参数键名列表（已脱敏） |
| duration_ms | float | 执行耗时（毫秒） |
| success | bool | 是否成功 |
| error_type | string | 错误类型（失败时） |
| result_preview | string | 结果预览或错误信息（前200字符） |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MCP_USAGE_LOG` | `usage_log.jsonl` | 日志文件名 |
| `MCP_USAGE_LOG_DIR` | `.` | 日志目录 |

示例：
```bash
export MCP_USAGE_LOG_DIR=/var/log/mcp
export MCP_USAGE_LOG=kingdee_usage.jsonl
```

## 改进分析

### 分析什么？

1. **高频工具** - 优先优化核心查询/写入流程
2. **高频错误** - 归类到 `KNOWN_ERROR_PATTERNS` 自动匹配建议
3. **耗时分布** - 定位慢查询，优化查询条件或分页
4. **未覆盖场景** - 发现新 API 需求

### 如何基于日志改进？

1. **错误率分析**
   - 某工具持续失败 → 检查参数或权限
   - 某类错误集中 → 更新 `KNOWN_ERROR_PATTERNS`

2. **性能分析**
   - 慢查询识别 → 优化 FilterString 或添加分页
   - 时段峰值 → 考虑缓存策略

3. **覆盖率分析**
   - 缺少的工具 → 评估是否需要新增
   - 常用但低效的操作 → 设计高层复合工具

## 示例：完整改进流程

```bash
# 1. 运行一段时间后，导出日志
python scripts/usage_report.py --format markdown -o weekly_report.md

# 2. 分析报告，关注失败率 > 30% 的工具
# 3. 查看具体失败案例
grep "failed" usage_log.jsonl | jq '.tool, .result_preview'

# 4. 根据发现更新 server.py 中的 KNOWN_ERROR_PATTERNS
# 5. 重新部署并继续监控
```
