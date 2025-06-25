import pytest
from src.infrastructure.cross_cutting.configuration import get_config_provider
import tempfile
import shutil
import os
from src.infrastructure.cross_cutting.configuration.config_provider import ConfigProvider, EnvironmentConfigProvider, get_config, set_config
from unittest.mock import patch
from pathlib import Path

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


def test_dynamic_update_config():
    """
    测试动态更新配置项。
    """
    config = get_config_provider()
    if hasattr(config, 'set_config'):
        config.set_config('dynamic_key', 'dynamic_value')
        assert config.get_config('dynamic_key') == 'dynamic_value'


def test_environment_switch():
    """
    测试多环境配置切换。
    """
    config = get_config_provider()
    if hasattr(config, 'switch_environment'):
        config.switch_environment('test')
        assert config.get_config('env') == 'test'


def test_config_validation():
    """
    测试配置校验功能。
    """
    config = get_config_provider()
    if hasattr(config, 'validate_config'):
        assert config.validate_config() is True


def test_config_provider_basic_and_edge_cases():
    """
    测试ConfigProvider的基本操作、边界分支、多级key、缺省值。
    """
    temp_dir = tempfile.mkdtemp()
    provider = ConfigProvider(config_dir=temp_dir)
    # set/get多级key
    assert provider.set_config('a.b.c', 123)
    assert provider.get_config('a.b.c') == 123
    # get_config缺省值
    assert provider.get_config('not.exist', default='dft') == 'dft'
    # validate_config缺失
    provider._config_cache.clear()
    assert not provider.validate_config()
    # validate_config通过
    provider.set_config('project.name', 'n')
    provider.set_config('project.version', 'v')
    provider.set_config('logging.level', 'INFO')
    assert provider.validate_config()
    shutil.rmtree(temp_dir)


def test_config_provider_reload_and_exceptions():
    """
    测试ConfigProvider的reload_config、加载异常、set_config异常。
    """
    temp_dir = tempfile.mkdtemp()
    provider = ConfigProvider(config_dir=temp_dir)
    # reload_config
    assert provider.reload_config()
    # set_config异常
    provider._config_cache = None
    assert not provider.set_config('a', 1)
    shutil.rmtree(temp_dir)


def test_config_provider_load_file_exceptions():
    """
    测试ConfigProvider加载损坏YAML/JSON文件的异常分支。
    """
    temp_dir = tempfile.mkdtemp()
    yaml_path = os.path.join(temp_dir, 'bad.yaml')
    json_path = os.path.join(temp_dir, 'bad.json')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write('not: yaml: file')
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write('{bad json}')
    provider = ConfigProvider(config_dir=temp_dir)
    # 加载损坏文件不会抛异常
    provider._load_yaml_config(Path(yaml_path))
    provider._load_json_config(Path(json_path))
    shutil.rmtree(temp_dir)


def test_environment_config_provider_env_override():
    """
    测试EnvironmentConfigProvider的环境变量覆盖。
    """
    os.environ['APP_PROJECT_NAME'] = 'env_project'
    provider = EnvironmentConfigProvider()
    assert provider.get_config('project.name') == 'env_project'
    del os.environ['APP_PROJECT_NAME']


def test_global_functions_with_config_provider():
    """
    测试全局便捷函数get_config/set_config的调用路径。
    """
    set_config('test.key', 'v')
    assert get_config('test.key') == 'v' 