"""
横切关注点 - 验证器

提供统一的数据验证服务，包括输入验证、数据格式验证等。
遵循DDD架构中的横切关注点设计原则，为整个应用提供验证基础设施。
"""

import re
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime

from ..logging import get_logger
from ..exception_handler import ValidationException


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    field: Optional[str] = None
    value: Optional[Any] = None
    
    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append(error)
        self.is_valid = False


class ValidationRule:
    """验证规则"""
    
    def __init__(self, name: str, validator: Callable, message: str = None):
        """
        初始化验证规则
        
        Args:
            name: 规则名称
            validator: 验证函数
            message: 错误消息
        """
        self.name = name
        self.validator = validator
        self.message = message or f"验证失败: {name}"
    
    def validate(self, value: Any, field: str = None) -> ValidationResult:
        """
        执行验证
        
        Args:
            value: 要验证的值
            field: 字段名
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True, errors=[], field=field, value=value)
        
        try:
            if not self.validator(value):
                result.add_error(self.message)
        except Exception as e:
            result.add_error(f"验证异常: {str(e)}")
        
        return result


class IValidator(ABC):
    """验证器接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def validate(self, data: Any, rules: List[ValidationRule]) -> ValidationResult:
        """验证数据"""
        pass
    
    @abstractmethod
    def add_rule(self, rule: ValidationRule) -> bool:
        """添加验证规则"""
        pass
    
    @abstractmethod
    def validate_field(self, field: str, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """验证字段"""
        pass


class Validator(IValidator):
    """验证器实现 - 统一的数据验证"""
    
    def __init__(self):
        """初始化验证器"""
        self.logger = get_logger("validator")
        self._rules: Dict[str, ValidationRule] = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """设置默认验证规则"""
        # 必填验证
        self.add_rule(ValidationRule(
            "required",
            lambda x: x is not None and str(x).strip() != "",
            "字段不能为空"
        ))
        
        # 字符串长度验证
        self.add_rule(ValidationRule(
            "min_length",
            lambda x, min_len=1: len(str(x)) >= min_len,
            "字符串长度不能小于指定值"
        ))
        
        # 数字范围验证
        self.add_rule(ValidationRule(
            "number_range",
            lambda x, min_val=0, max_val=100: min_val <= float(x) <= max_val,
            "数值必须在指定范围内"
        ))
        
        # 邮箱验证
        self.add_rule(ValidationRule(
            "email",
            lambda x: re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(x)) is not None,
            "邮箱格式不正确"
        ))
        
        # 手机号验证
        self.add_rule(ValidationRule(
            "phone",
            lambda x: re.match(r'^1[3-9]\d{9}$', str(x)) is not None,
            "手机号格式不正确"
        ))
        
        # URL验证
        self.add_rule(ValidationRule(
            "url",
            lambda x: re.match(r'^https?://[^\s/$.?#].[^\s]*$', str(x)) is not None,
            "URL格式不正确"
        ))
    
    def validate(self, data: Any, rules: List[ValidationRule]) -> ValidationResult:
        """
        验证数据
        
        Args:
            data: 要验证的数据
            rules: 验证规则列表
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True, errors=[], value=data)
        
        try:
            for rule in rules:
                rule_result = rule.validate(data)
                if not rule_result.is_valid:
                    result.errors.extend(rule_result.errors)
                    result.is_valid = False
            
            if not result.is_valid:
                self.logger.warning(f"数据验证失败: {result.errors}")
            else:
                self.logger.debug("数据验证通过")
                
        except Exception as e:
            result.add_error(f"验证过程异常: {str(e)}")
            self.logger.error(f"验证异常: {str(e)}")
        
        return result
    
    def add_rule(self, rule: ValidationRule) -> bool:
        """
        添加验证规则
        
        Args:
            rule: 验证规则
            
        Returns:
            bool: 是否添加成功
        """
        try:
            self._rules[rule.name] = rule
            self.logger.info(f"添加验证规则: {rule.name}")
            return True
        except Exception as e:
            self.logger.error(f"添加验证规则失败: {str(e)}")
            return False
    
    def validate_field(self, field: str, value: Any, rules: List[ValidationRule]) -> ValidationResult:
        """
        验证字段
        
        Args:
            field: 字段名
            value: 字段值
            rules: 验证规则列表
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True, errors=[], field=field, value=value)
        
        try:
            for rule in rules:
                rule_result = rule.validate(value, field)
                if not rule_result.is_valid:
                    result.errors.extend(rule_result.errors)
                    result.is_valid = False
            
            if not result.is_valid:
                self.logger.warning(f"字段验证失败 {field}: {result.errors}")
            else:
                self.logger.debug(f"字段验证通过: {field}")
                
        except Exception as e:
            result.add_error(f"字段验证异常: {str(e)}")
            self.logger.error(f"字段验证异常 {field}: {str(e)}")
        
        return result
    
    def validate_dict(self, data: Dict[str, Any], field_rules: Dict[str, List[ValidationRule]]) -> Dict[str, ValidationResult]:
        """
        验证字典数据
        
        Args:
            data: 字典数据
            field_rules: 字段验证规则映射
            
        Returns:
            Dict[str, ValidationResult]: 字段验证结果映射
        """
        results = {}
        
        for field, rules in field_rules.items():
            value = data.get(field)
            results[field] = self.validate_field(field, value, rules)
        
        return results
    
    def create_rule(self, name: str, validator_func: Callable, message: str = None) -> ValidationRule:
        """
        创建验证规则
        
        Args:
            name: 规则名称
            validator_func: 验证函数
            message: 错误消息
            
        Returns:
            ValidationRule: 验证规则
        """
        return ValidationRule(name, validator_func, message)


# 全局验证器实例
_validator: Optional[Validator] = None


def get_validator() -> Validator:
    """获取全局验证器"""
    global _validator
    if _validator is None:
        _validator = Validator()
    return _validator


# 便捷函数
def validate_data(data: Any, rules: List[ValidationRule]) -> ValidationResult:
    """便捷函数：验证数据"""
    return get_validator().validate(data, rules)


def validate_email(email: str) -> ValidationResult:
    """便捷函数：验证邮箱"""
    email_rule = ValidationRule(
        "email",
        lambda x: re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(x)) is not None,
        "邮箱格式不正确"
    )
    return get_validator().validate(email, [email_rule])


def validate_phone(phone: str) -> ValidationResult:
    """便捷函数：验证手机号"""
    phone_rule = ValidationRule(
        "phone",
        lambda x: re.match(r'^1[3-9]\d{9}$', str(x)) is not None,
        "手机号格式不正确"
    )
    return get_validator().validate(phone, [phone_rule])


def validate_url(url: str) -> ValidationResult:
    """便捷函数：验证URL"""
    url_rule = ValidationRule(
        "url",
        lambda x: re.match(r'^https?://[^\s/$.?#].[^\s]*$', str(x)) is not None,
        "URL格式不正确"
    )
    return get_validator().validate(url, [url_rule])


# 常用验证规则工厂函数
def create_required_rule(message: str = "字段不能为空") -> ValidationRule:
    """创建必填验证规则"""
    return ValidationRule("required", lambda x: x is not None and str(x).strip() != "", message)


def create_min_length_rule(min_length: int, message: str = None) -> ValidationRule:
    """创建最小长度验证规则"""
    if message is None:
        message = f"字符串长度不能小于{min_length}"
    return ValidationRule("min_length", lambda x: len(str(x)) >= min_length, message)


def create_max_length_rule(max_length: int, message: str = None) -> ValidationRule:
    """创建最大长度验证规则"""
    if message is None:
        message = f"字符串长度不能大于{max_length}"
    return ValidationRule("max_length", lambda x: len(str(x)) <= max_length, message)


def create_number_range_rule(min_val: float, max_val: float, message: str = None) -> ValidationRule:
    """创建数值范围验证规则"""
    if message is None:
        message = f"数值必须在{min_val}到{max_val}之间"
    return ValidationRule("number_range", lambda x: min_val <= float(x) <= max_val, message) 