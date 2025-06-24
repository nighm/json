"""
横切关注点 - 日志服务模块

提供统一的日志记录服务，支持不同级别的日志记录、格式化输出和日志管理。
遵循DDD架构的横切关注点设计原则，为整个应用提供日志基础设施。
"""

from .logger import (
    ILogger,
    ILogConfigProvider,
    LoggerFactory,
    ApplicationLogger,
    DefaultLogConfigProvider,
    get_logger,
    get_logger_factory,
    set_log_config_provider
)

__all__ = [
    'ILogger',
    'ILogConfigProvider', 
    'LoggerFactory',
    'ApplicationLogger',
    'DefaultLogConfigProvider',
    'get_logger',
    'get_logger_factory',
    'set_log_config_provider'
] 