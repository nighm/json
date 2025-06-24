import pytest
from src.infrastructure.cross_cutting.cache import get_cache_provider

# 缓存模块单元测试

def test_cache_set_and_get():
    """
    测试缓存的存取功能。
    """
    cache = get_cache_provider()
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'


def test_cache_clear():
    """
    测试缓存清理功能。
    """
    cache = get_cache_provider()
    cache.set('key2', 'value2')
    cache.clear()
    assert cache.get('key2') is None 