import pytest
from src.infrastructure.cross_cutting.validation import get_validator, create_required_rule

# 验证模块单元测试

def test_validator_basic():
    """
    测试基础校验功能。
    """
    validator = get_validator()
    required_rule = create_required_rule()
    
    # 测试非空验证
    result1 = validator.validate("abc", [required_rule])
    assert result1.is_valid is True
    
    result2 = validator.validate("", [required_rule])
    assert result2.is_valid is False 