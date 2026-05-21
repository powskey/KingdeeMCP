"""
测试元数据自动纠错功能
"""
import asyncio
import sys
sys.path.insert(0, "src")

from kingdee_mcp.server import MetadataValidator, FieldDef


# 模拟金蝶 QueryBusinessInfo 返回的元数据
MOCK_METADATA = {
    "Result": {
        "FormId": "SAL_SaleOrder",
        "FormName": "销售订单",
        "MetadataEntity": {
            "Name": "基础信息",
            "TableName": "SAL_SaleOrder",
            "Fields": [
                # 表头字段
                {"Name": "FDate", "Caption": "日期", "IsSystem": False, 
                 "FieldType": {"Name": "Datetime", "Key": "185"}, "MustInput": True},
                {"Name": "FSaleOrgId", "Caption": "销售组织", "IsSystem": False,
                 "FieldType": {"Name": "BaseData", "Key": "127"}, "MustInput": True},
                {"Name": "FCustId", "Caption": "客户", "IsSystem": False,
                 "FieldType": {"Name": "BaseData", "Key": "127"}, "MustInput": True},
                # 分录
                {
                    "Name": "FSaleOrderEntry", "Caption": "订单明细", "IsSystem": False,
                    "FieldType": {"Name": "Entry", "Key": "256"},
                    "Fields": [
                        {"Name": "FMaterialId", "Caption": "物料编码", "MustInput": True,
                         "FieldType": {"Name": "BaseData", "Key": "127"}},
                        {"Name": "FPriceUnitId", "Caption": "计价单位", "MustInput": True,
                         "FieldType": {"Name": "BaseData", "Key": "127"}},
                        {"Name": "FQuantity", "Caption": "数量",
                         "FieldType": {"Name": "Dec", "Key": "106"}},
                    ]
                }
            ]
        }
    }
}


def test_metadata_validator():
    """测试 MetadataValidator"""
    print("=" * 60)
    print("测试 MetadataValidator 自动纠错功能")
    print("=" * 60)

    validator = MetadataValidator(MOCK_METADATA)

    # 测试1: 字段名拼写错误
    print("\n[测试1] 字段名拼写错误")
    payload = {
        "FDate": "2026-05-11",
        "FSalesOrgId": {"FNumber": "001"},  # 错误：应该是 FSaleOrgId
        "FCustId": {"FNumber": "C001"},
        "FSalesOrderEntry": [  # 错误：应该是 FSaleOrderEntry
            {"FMaterialId": {"FNumber": "M001"}, "FPriceUnitId": {"FNumber": "P001"}}
        ]
    }

    fixed, fixes = validator.validate_and_fix(payload)
    print(f"  原始字段: {list(payload.keys())}")
    print(f"  修正后: {list(fixed.keys())}")
    print(f"  修正列表: {fixes}")

    # 验证
    assert "FSaleOrgId" in fixed, "FSalesOrgId 应该被修正为 FSaleOrgId"
    assert "FSaleOrderEntry" in fixed, "FSalesOrderEntry 应该被修正为 FSaleOrderEntry"
    assert "FSalesOrgId" not in fixed.get("FDate", ""), "FSalesOrgId 不应该还在原位"
    print("  [PASS]")

    # 测试2: 正确字段不应被修改
    print("\n[测试2] 正确字段不应被修改")
    payload2 = {
        "FDate": "2026-05-11",
        "FSaleOrgId": {"FNumber": "001"},  # 正确
        "FSaleOrderEntry": [  # 正确
            {"FMaterialId": {"FNumber": "M001"}}
        ]
    }

    fixed2, fixes2 = validator.validate_and_fix(payload2)
    print(f"  修正列表: {fixes2 if fixes2 else '无修正'}")
    assert len(fixes2) == 0, "正确的字段不应被修改"
    print("  [PASS]")

    # 测试3: 获取有效字段列表
    print("\n[测试3] 获取有效字段列表")
    valid_fields = validator.get_valid_field_names()
    print(f"  有效字段: {valid_fields}")
    assert "FSaleOrgId" in valid_fields
    assert "FSaleOrderEntry" in valid_fields
    assert "FSaleOrderEntry.FMaterialId" in valid_fields
    print("  [PASS]")

    # 测试4: 获取必填字段
    print("\n[测试4] 获取必填字段")
    required = validator.get_required_fields()
    print(f"  必填字段: {required}")
    assert "FSaleOrgId" in required
    assert "FDate" in required
    print("  [PASS]")

    print("\n" + "=" * 60)
    print("所有测试通过！元数据自动纠错功能正常")
    print("=" * 60)


if __name__ == "__main__":
    test_metadata_validator()
