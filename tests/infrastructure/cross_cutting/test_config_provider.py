import pytest
from src.infrastructure.cross_cutting.configuration import get_config_provider

# 配置模块单元测试

def test_get_config_basic():
    """
    测试基础配置获取功能。
    """
    config = get_config_provider()
    # 使用正确的方法名
    assert hasattr(config, 'get_config')


def test_get_config_not_exist():
    """
    测试获取不存在的配置项时的异常处理。
    """
    config = get_config_provider()
    # 不存在的配置应该返回None或默认值，而不是抛出异常
    result = config.get_config('not_exist_key', default='default_value')
    assert result == 'default_value' 