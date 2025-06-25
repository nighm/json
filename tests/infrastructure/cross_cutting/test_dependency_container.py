import pytest
from src.infrastructure.cross_cutting import register_services, get_service

# 依赖注入容器集成测试

def test_register_and_get_service():
    """
    测试register_services后，get_service能正确获取各横切层服务实例。
    """
    register_services()
    logger = get_service('logger')
    config = get_service('config_service')
    cache = get_service('cache_service')
    security = get_service('security_service')
    validator = get_service('validator_service')
    analyzer = get_service('statistical_analyzer_service')
    i18n = get_service('i18n_service')
    assert logger is not None
    assert config is not None
    assert cache is not None
    assert security is not None
    assert validator is not None
    assert analyzer is not None
    assert i18n is not None


def test_singleton_service():
    """
    测试容器注册的服务为单例，获取多次为同一对象。
    """
    register_services()
    logger1 = get_service('logger')
    logger2 = get_service('logger')
    assert logger1 is logger2


def test_get_service_not_found():
    """
    测试获取未注册服务时抛出KeyError。
    """
    register_services()
    with pytest.raises(KeyError):
        get_service('not_exist_service') 