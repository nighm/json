"""
横切关注点 - 异常处理模块

提供统一的异常处理服务，包括异常捕获、记录、分类和恢复。
遵循DDD架构的横切关注点设计原则，为整个应用提供异常处理基础设施。
"""

from .exception_handler import (
    IExceptionHandler,
    ExceptionHandler,
    BusinessException,
    ValidationException,
    InfrastructureException,
    get_exception_handler,
    handle_exception,
    raise_business_exception,
    raise_validation_exception,
    raise_infrastructure_exception
)

__all__ = [
    'IExceptionHandler',
    'ExceptionHandler',
    'BusinessException',
    'ValidationException',
    'InfrastructureException',
    'get_exception_handler',
    'handle_exception',
    'raise_business_exception',
    'raise_validation_exception',
    'raise_infrastructure_exception'
] 