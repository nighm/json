import pytest
from src.infrastructure.cross_cutting.validation import get_validator, create_required_rule, validate_email, validate_phone, validate_url

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

@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("user@domain.co", True),
    ("bad-email", False),
    ("", False),
    ("user@.com", False),
    ("user@domain", False),
    ("user@domain.c", False),
    ("user@domain.com.cn", True),
])
def test_email_validation_param(email, expected):
    """
    参数化测试邮箱格式校验，覆盖多种边界和异常场景。
    """
    assert validate_email(email) is expected

@pytest.mark.parametrize("phone,expected", [
    ("13800138000", True),
    ("19912345678", True),
    ("12345", False),
    ("", False),
    ("10000000000", False),
    ("1581234567a", False),
    ("158123456789", False),
])
def test_phone_validation_param(phone, expected):
    """
    参数化测试手机号格式校验，覆盖多种边界和异常场景。
    """
    assert validate_phone(phone) is expected

@pytest.mark.parametrize("url,expected", [
    ("https://www.example.com", True),
    ("http://domain.com", True),
    ("ftp://domain.com", False),
    ("not_a_url", False),
    ("", False),
    ("http://", False),
    ("https://sub.domain.com/path?query=1", True),
])
def test_url_validation_param(url, expected):
    """
    参数化测试URL格式校验，覆盖多种边界和异常场景。
    """
    result = validate_url(url)
    assert result.is_valid == expected, f"URL: {url} 校验结果: {result.is_valid}, 期望: {expected}, 错误信息: {result.errors}" 