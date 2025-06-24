import pytest
from src.infrastructure.cross_cutting.exception_handler import get_exception_handler

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