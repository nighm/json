"""
横切关注点 - 配置提供者

提供统一的配置管理服务，包括配置加载、验证、缓存和动态更新。
遵循DDD架构中的横切关注点设计原则，为整个应用提供配置基础设施。
"""

import os
import json
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from ..logging import get_logger

class IConfigProvider(ABC):
    """配置提供者接口 - 遵循依赖倒置原则"""
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        pass
    @abstractmethod
    def set_config(self, key: str, value: Any) -> bool:
        pass
    @abstractmethod
    def reload_config(self) -> bool:
        pass
    @abstractmethod
    def validate_config(self) -> bool:
        pass

class ConfigProvider(IConfigProvider):
    """配置提供者实现 - 统一的配置管理"""
    def __init__(self, config_dir: str = None):
        self.logger = get_logger("config.provider")
        self.config_dir = Path(config_dir) if config_dir else Path("src/config")
        self._config_cache: Dict[str, Any] = {}
        self._load_all_configs()
    def _load_all_configs(self):
        try:
            if self.config_dir.exists():
                for config_file in self.config_dir.glob("*.yaml"):
                    self._load_yaml_config(config_file)
                for config_file in self.config_dir.glob("*.json"):
                    self._load_json_config(config_file)
            self.logger.info("所有配置文件加载完成")
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
    def _load_yaml_config(self, config_file: Path):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                if config_data:
                    namespace = config_file.stem
                    self._config_cache[namespace] = config_data
                    self.logger.info(f"加载YAML配置文件: {config_file}")
        except Exception as e:
            self.logger.error(f"加载YAML配置文件失败 {config_file}: {str(e)}")
    def _load_json_config(self, config_file: Path):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                if config_data:
                    namespace = config_file.stem
                    self._config_cache[namespace] = config_data
                    self.logger.info(f"加载JSON配置文件: {config_file}")
        except Exception as e:
            self.logger.error(f"加载JSON配置文件失败 {config_file}: {str(e)}")
    def get_config(self, key: str, default: Any = None) -> Any:
        try:
            keys = key.split('.')
            current = self._config_cache
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
            return current
        except Exception as e:
            self.logger.warning(f"获取配置失败 {key}: {str(e)}")
            return default
    def set_config(self, key: str, value: Any) -> bool:
        try:
            keys = key.split('.')
            current = self._config_cache
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
            self.logger.info(f"设置配置: {key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"设置配置失败 {key}: {str(e)}")
            return False
    def reload_config(self) -> bool:
        try:
            self._config_cache.clear()
            self._load_all_configs()
            self.logger.info("配置重新加载完成")
            return True
        except Exception as e:
            self.logger.error(f"重新加载配置失败: {str(e)}")
            return False
    def validate_config(self) -> bool:
        try:
            required_configs = ["project.name", "project.version", "logging.level"]
            for config_key in required_configs:
                if self.get_config(config_key) is None:
                    self.logger.error(f"缺少必需配置: {config_key}")
                    return False
            self.logger.info("配置验证通过")
            return True
        except Exception as e:
            self.logger.error(f"配置验证失败: {str(e)}")
            return False

class EnvironmentConfigProvider(ConfigProvider):
    """环境配置提供者 - 支持环境变量覆盖"""
    def __init__(self, config_dir: str = None, env_prefix: str = "APP_"):
        super().__init__(config_dir)
        self.env_prefix = env_prefix
        self._load_environment_configs()
    def _load_environment_configs(self):
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                config_key = key[len(self.env_prefix):].lower().replace('_', '.')
                self.set_config(config_key, value)
        self.logger.info("环境变量配置加载完成")
    def get_config(self, key: str, default: Any = None) -> Any:
        env_key = self.env_prefix + key.upper().replace('.', '_')
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
        return super().get_config(key, default)

_config_provider: Optional[ConfigProvider] = None

def get_config_provider() -> ConfigProvider:
    global _config_provider
    if _config_provider is None:
        _config_provider = EnvironmentConfigProvider()
    return _config_provider

def get_config(key: str, default: Any = None) -> Any:
    return get_config_provider().get_config(key, default)

def set_config(key: str, value: Any) -> bool:
    return get_config_provider().set_config(key, value) 