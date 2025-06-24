"""
横切关注点 - 配置服务模块

提供统一的配置管理服务，包括配置加载、验证、缓存和动态更新。
遵循DDD架构的横切关注点设计原则，为整个应用提供配置基础设施。
"""

from .config_provider import (
    IConfigProvider,
    ConfigProvider,
    EnvironmentConfigProvider,
    get_config_provider,
    get_config,
    set_config
)

__all__ = [
    'IConfigProvider',
    'ConfigProvider',
    'EnvironmentConfigProvider',
    'get_config_provider',
    'get_config',
    'set_config'
] 