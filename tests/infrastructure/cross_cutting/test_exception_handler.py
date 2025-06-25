import pytest
from src.infrastructure.cross_cutting.exception_handler import get_exception_handler, BusinessException, ValidationException

# 异常处理模块单元测试

def test_handle_exception_basic():
    """
    测试异常捕获与处理。
    """
    handler = get_exception_handler()
    try:
        raise ValueError("测试异常")
    except Exception as e:
        result = handler.handle_exception(e)
        assert result is True  # 应该返回True表示处理成功


def test_handle_custom_business_exception():
    """
    测试自定义业务异常的处理。
    """
    handler = get_exception_handler()
    try:
        raise BusinessException("业务异常")
    except Exception as e:
        result = handler.handle_exception(e)
        assert result is True


def test_handle_validation_exception():
    """
    测试校验异常的处理。
    """
    handler = get_exception_handler()
    try:
        raise ValidationException("校验异常")
    except Exception as e:
        result = handler.handle_exception(e)
        assert result is True


def test_handle_nested_exception():
    """
    测试嵌套异常的处理。
    """
    handler = get_exception_handler()
    try:
        try:
            raise ValueError("内层异常")
        except Exception as inner:
            raise BusinessException("外层业务异常") from inner
    except Exception as e:
        result = handler.handle_exception(e)
        assert result is True 