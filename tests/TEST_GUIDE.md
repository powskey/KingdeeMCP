# Kingdee MCP 工具测试文档

## 环境配置

```bash
# Windows
set KINGDEE_SERVER_URL=http://your-server/k3cloud/
set KINGDEE_ACCT_ID=your-acct-id
set KINGDEE_USERNAME=your-username
set KINGDEE_APP_ID=your-app-id
set KINGDEE_APP_SEC=your-app-secret
set KINGDEE_LCID=2052

# Linux/Mac
export KINGDEE_SERVER_URL="http://your-server/k3cloud/"
export KINGDEE_ACCT_ID="your-acct-id"
export KINGDEE_USERNAME="your-username"
export KINGDEE_APP_ID="your-app-id"
export KINGDEE_APP_SEC="your-app-secret"
export KINGDEE_LCID=2052
```

---

## 一、生产管理模块

### 1.1 生产订单 (PRD_MO)

#### 查询生产订单
```python
kingdee_query_production_orders({
    "filter_string": "FDocumentStatus='C'",
    "limit": 20
})
```

#### 查看生产订单详情
```python
kingdee_view_production_order({
    "bill_no": "MO000018"
})
```

#### 保存生产订单
```python
kingdee_save_production_order({
    "model": {
        "FMaterialId": {"FNumber": "MAT001"},
        "FBillNo": "AUTO",  // 新建留空
        "FUnitId": {"FNumber": "Pcs"},
        "FPlanStartDate": "2026-05-01",
        "FPlanFinishDate": "2026-05-10",
        "FWorkShopId": {"FNumber": "WS001"}
    },
    "is_delete_entry": false
})
```

#### 提交生产订单
```python
kingdee_submit_production_orders({
    "bill_ids": ["12345", "12346"]
})
```

#### 审核生产订单
```python
kingdee_audit_production_orders({
    "bill_ids": ["12345"]
})
```

#### 下推领料单
```python
kingdee_push_production_pick({
    "bill_nos": ["MO000018"],
    "rule_id": "STDJ000001"  // 转换规则ID
})
```

#### 下推入库单
```python
kingdee_push_production_stock_in({
    "bill_nos": ["MO000018"]
})
```

---

### 1.2 生产领料单 (PRD_PickMtrl)

#### 查询领料单
```python
kingdee_query_production_pick_materials({
    "filter_string": "",
    "limit": 20
})
```

---

### 1.3 生产入库单 (PRD_Instock)

#### 查询入库单
```python
kingdee_query_production_stock_in({
    "filter_string": "",
    "limit": 20
})
```

---

### 1.4 生产汇报单 (PRD_MOReport)

> ⚠️ Demo环境未启用，暂不可用

```python
kingdee_query_production_report({
    "filter_string": "",
    "top": 20
})
```

---

## 二、计划管理模块

### 2.1 MRP运算结果 (PLAN_MRPResult)

> ⚠️ Demo环境未启用，暂不可用

```python
kingdee_query_mrp_result({
    "filter_string": "",
    "top": 20
})
```

---

### 2.2 生产计划单 (PLAN_ProductionPlan)

> ⚠️ Demo环境未启用，暂不可用

```python
kingdee_query_production_plan({
    "filter_string": "",
    "top": 20
})
```

---

## 三、资产管理模块 (FA_*)

### 3.1 查询固定资产卡片
```python
kingdee_query_fixed_asset({
    "filter_string": "",
    "limit": 20
})
```

### 3.2 查询资产卡片详情
```python
kingdee_query_asset_card({
    "filter_string": "",
    "limit": 20
})
```

### 3.3 查询资产折旧记录
```python
kingdee_query_asset_depreciation({
    "filter_string": "",
    "limit": 20
})
```

### 3.4 新增/修改固定资产
```python
kingdee_save_asset({
    "model": {}
})
```

### 3.5 查询资产调拨单
```python
kingdee_query_asset_transfer({
    "filter_string": "",
    "limit": 20
})
```

### 3.6 查询资产报废单
```python
kingdee_query_asset_scrape({
    "filter_string": "",
    "limit": 20
})
```

---

## 四、成本管理模块 (CB_* / STK_*)

### 4.1 查询物料成本库
```python
kingdee_query_material_cost({
    "filter_string": "",
    "limit": 20
})
```

### 4.2 查询物料目标成本
```python
kingdee_query_material_target_cost({
    "filter_string": "",
    "limit": 20
})
```

### 4.3 查询成本计算单
```python
kingdee_query_cost_calculation({
    "filter_string": "",
    "limit": 20
})
```

### 4.4 查询成本中心
```python
kingdee_query_cost_centers({
    "filter_string": "",
    "limit": 20
})
```

### 4.5 查询成本项目
```python
kingdee_query_cost_items({
    "filter_string": "",
    "limit": 20
})
```

### 4.6 查询产品标准成本
```python
kingdee_query_product_standard_cost({
    "filter_string": "",
    "limit": 20
})
```

### 4.7 查询成本调整单
```python
kingdee_query_cost_adjustments({
    "filter_string": "",
    "limit": 20
})
```

### 4.8 保存成本调整单
```python
kingdee_save_cost_adjustment({
    "model": {}
})
```

### 4.9 查询即时成本对比
```python
kingdee_query_instant_cost_compare({
    "filter_string": "",
    "limit": 20
})
```

### 4.10 查询成本趋势
```python
kingdee_query_cost_trend({
    "filter_string": "",
    "limit": 20
})
```

### 4.11 查询完工入库成本
```python
kingdee_query_finished_product_cost({
    "filter_string": "",
    "limit": 20
})
```

### 4.12 查询材料耗用成本
```python
kingdee_query_material_cost_usage({
    "filter_string": "",
    "limit": 20
})
```

---

## 五、调拨管理模块 (STK_*)

### 5.1 查询杂项出入库明细
```python
kingdee_query_misc_movement_detail({
    "filter_string": "",
    "limit": 20
})
```

### 5.2 查询分步式调出未调入明细
```python
kingdee_query_transfer_pending_detail({
    "filter_string": "",
    "limit": 20
})
```

### 5.3 查询调拨申请单
```python
kingdee_query_transfer_apply({
    "filter_string": "",
    "limit": 20
})
```

### 5.4 查询直接调拨单
```python
kingdee_query_transfer_direct({
    "filter_string": "",
    "limit": 20
})
```

### 5.5 下推调拨单
```python
kingdee_push_stock_transfer({
    "bill_nos": ["TJ001"]
})
```

---

## 六、质量管理模块 (QIS_*)

### 6.1 查询来料检验单 (IQC)
```python
kingdee_query_iqc_inspect({
    "filter_string": "",
    "limit": 20
})
```

### 6.2 查询过程检验单 (PQC)
```python
kingdee_query_pqc_inspect({
    "filter_string": "",
    "limit": 20
})
```

### 6.3 查询成品检验单 (OQC)
```python
kingdee_query_oqc_inspect({
    "filter_string": "",
    "limit": 20
})
```

---

## 七、审计合规模块 (BOS_* / SEC_*)

### 7.1 查询审计日志
```python
kingdee_query_audit_log({
    "filter_string": "",
    "limit": 20
})
```

### 7.2 查询操作日志
```python
kingdee_query_operation_logs({
    "filter_string": "",
    "limit": 20
})
```

### 7.3 查询变更记录
```python
kingdee_query_change_log({
    "filter_string": "",
    "limit": 20
})
```

### 7.4 查询审批流程
```python
kingdee_query_approval_flow({
    "filter_string": "",
    "limit": 20
})
```

### 7.5 查询权限变更
```python
kingdee_query_permission({
    "filter_string": "",
    "limit": 20
})
```

### 7.6 查询数据备份记录
```python
kingdee_query_data_backup({
    "filter_string": "",
    "limit": 20
})
```

---

## 八、通用操作

### 8.1 创建并审核单据（复合工作流）
```python
kingdee_create_and_audit({
    "form_id": "SAL_SaleOrder",
    "model": {
        "FMaterialId": {"FNumber": "MAT001"},
        "FDate": "2026-05-01",
        "FOrgId": {"FNumber": "100"},
        "FCustomerId": {"FNumber": "C001"}
    }
})
```

### 8.2 下推并审核（复合工作流）
```python
kingdee_push_and_audit({
    "form_id": "SAL_SaleOrder",
    "target_form_id": "SAL_OUTSTOCK",
    "source_bill_nos": ["SO001"],
    "enable_default_rule": true,
    "auto_submit_audit": true
})
```

### 8.3 查询单据列表
```python
kingdee_query_bills({
    "form_id": "SAL_SaleOrder",
    "filter_string": "FDocumentStatus='C'",
    "limit": 20
})
```

### 8.4 查看单据详情
```python
kingdee_view_bill({
    "form_id": "SAL_SaleOrder",
    "bill_id": "12345"
})
```

### 8.5 保存单据
```python
kingdee_save_bill({
    "form_id": "SAL_SaleOrder",
    "model": {}
})
```

---

## 九、测试执行

### 运行所有测试
```bash
python -m pytest tests/ -v
```

### 仅运行单元测试
```bash
python -m pytest tests/test_server.py tests/test_tools_mock.py -v
```

### 运行E2E测试（需要真实环境）
```bash
python -m pytest tests/e2e -v -m e2e
```

### 运行生产模块E2E测试
```bash
python -m pytest tests/e2e/test_production_workflow.py -v
```

---

## 十、已知问题

| 问题 | 说明 | 状态 |
|------|------|------|
| PLAN_MRPResult 不可用 | Demo环境未启用MRP模块 | 待用户确认 |
| PLAN_ProductionPlan 不可用 | Demo环境未启用生产计划 | 待用户确认 |
| PRD_MOReport 不可用 | Demo环境未启用生产汇报 | 待用户确认 |
| FA_* (资产) 不可用 | Demo环境未启用资产管理 | 待用户确认 |
| CB_* (成本) 不可用 | Demo环境未启用成本管理 | 待用户确认 |
| QIS_* (质量) 不可用 | Demo环境未启用质量管理 | 待用户确认 |
| BOS_AuditLog/MODIFYLOG 不可用 | Demo环境未启用审计日志 | 待用户确认 |
| FA_Transfer 字段问题 | formId存在但字段FDate不存在 | 待修复 |
| BOS_OperateLog 字段问题 | formId存在但字段FOperateTime不存在 | 待修复 |

---

## 十一、测试结果汇总 (2026-04-30)

### 可用工具 (验证通过)
- PRD_MO: 查询/查看/保存/提交/审核/下推领料/下推入库
- PRD_PickMtrl: 查询/下推
- PRD_Instock: 查询/下推
- SAL_SaleOrder: 基础CRUD
- PUR_PurchaseOrder: 基础CRUD
- STK_InStock: 基础CRUD
- BD_Material/BD_Customer/BD_Supplier: 基础查询

### 不可用工具 (需修复或用户确认)
- kingdee_query_mrp_result (PLAN_MRPResult): 业务对象不存在
- kingdee_query_production_plan (PLAN_ProductionPlan): 业务对象不存在
- kingdee_query_production_report (PRD_MOReport): 业务对象不存在
- kingdee_query_fixed_asset (FA_FAGet): 业务对象不存在
- kingdee_query_asset_depreciation (FA_DepreciationBill): 业务对象不存在
- kingdee_save_asset (FA_FAGet): 业务对象不存在
- kingdee_query_asset_scrape (FA_Scrape): 业务对象不存在
- kingdee_query_asset_transfer (FA_Transfer): formId存在，字段名错误，需修复
- kingdee_query_material_cost (BD_MaterialCost): 业务对象不存在
- kingdee_query_cost_calculation (CB_CostCalBill): 字段标识符错误
- kingdee_query_cost_centers (CB_CostCenter): 字段标识符错误
- 其他成本/质量/审计工具: 业务对象不存在

---

更新日期：2026-04-30