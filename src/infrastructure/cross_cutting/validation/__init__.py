"""
横切关注点 - 验证服务模块

提供统一的数据验证服务，包括输入验证、数据格式验证等。
遵循DDD架构的横切关注点设计原则，为整个应用提供验证基础设施。
"""

from .validator import (
    IValidator,
    Validator,
    ValidationRule,
    ValidationResult,
    get_validator,
    validate_data,
    validate_email,
    validate_phone,
    validate_url,
    create_required_rule
)

__all__ = [
    'IValidator',
    'Validator',
    'ValidationRule',
    'ValidationResult',
    'get_validator',
    'validate_data',
    'validate_email',
    'validate_phone',
    'validate_url',
    'create_required_rule'
] 