"""
横切关注点 - 异常处理器

提供统一的异常处理服务，包括异常捕获、记录、分类和恢复。
遵循DDD架构中的横切关注点设计原则，为整个应用提供异常处理基础设施。
"""

import traceback
import sys
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime

from ..logging import get_logger


class BusinessException(Exception):
    """业务异常 - 表示业务逻辑错误"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        """
        初始化业务异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "BUSINESS_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()


class ValidationException(Exception):
    """验证异常 - 表示数据验证错误"""
    
    def __init__(self, message: str, field: str = None, value: Any = None, details: Dict[str, Any] = None):
        """
        初始化验证异常
        
        Args:
            message: 错误消息
            field: 验证失败的字段
            value: 验证失败的值
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value
        self.details = details or {}
        self.timestamp = datetime.now()


class InfrastructureException(Exception):
    """基础设施异常 - 表示基础设施层错误"""
    
    def __init__(self, message: str, component: str = None, details: Dict[str, Any] = None):
        """
        初始化基础设施异常
        
        Args:
            message: 错误消息
            component: 出错的组件
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.component = component
        self.details = details or {}
        self.timestamp = datetime.now()


class IExceptionHandler(ABC):
    """异常处理器接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def handle_exception(self, exception: Exception, context: Dict[str, Any] = None) -> bool:
        """处理异常"""
        pass
    
    @abstractmethod
    def register_handler(self, exception_type: type, handler: Callable) -> bool:
        """注册异常处理器"""
        pass
    
    @abstractmethod
    def get_exception_info(self, exception: Exception) -> Dict[str, Any]:
        """获取异常信息"""
        pass
    
    @abstractmethod
    def should_rethrow(self, exception: Exception) -> bool:
        """判断是否应该重新抛出异常"""
        pass


class ExceptionHandler(IExceptionHandler):
    """异常处理器实现 - 统一的异常处理"""
    
    def __init__(self):
        """初始化异常处理器"""
        self.logger = get_logger("exception.handler")
        self._handlers: Dict[type, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """设置默认异常处理器"""
        # 业务异常处理器
        self.register_handler(BusinessException, self._handle_business_exception)
        
        # 验证异常处理器
        self.register_handler(ValidationException, self._handle_validation_exception)
        
        # 基础设施异常处理器
        self.register_handler(InfrastructureException, self._handle_infrastructure_exception)
        
        # 通用异常处理器
        self.register_handler(Exception, self._handle_generic_exception)
    
    def handle_exception(self, exception: Exception, context: Dict[str, Any] = None) -> bool:
        """
        处理异常
        
        Args:
            exception: 异常对象
            context: 上下文信息
            
        Returns:
            bool: 是否处理成功
        """
        try:
            # 获取异常信息
            exception_info = self.get_exception_info(exception)
            
            # 记录异常
            self._log_exception(exception, exception_info, context)
            
            # 查找并执行处理器
            handler = self._find_handler(exception)
            if handler:
                handler(exception, context)
                return True
            
            # 使用默认处理器
            self._handle_generic_exception(exception, context)
            return True
            
        except Exception as e:
            self.logger.error(f"异常处理失败: {str(e)}")
            return False
    
    def register_handler(self, exception_type: type, handler: Callable) -> bool:
        """
        注册异常处理器
        
        Args:
            exception_type: 异常类型
            handler: 处理器函数
            
        Returns:
            bool: 是否注册成功
        """
        try:
            self._handlers[exception_type] = handler
            self.logger.info(f"注册异常处理器: {exception_type.__name__}")
            return True
        except Exception as e:
            self.logger.error(f"注册异常处理器失败: {str(e)}")
            return False
    
    def get_exception_info(self, exception: Exception) -> Dict[str, Any]:
        """
        获取异常信息
        
        Args:
            exception: 异常对象
            
        Returns:
            Dict[str, Any]: 异常信息
        """
        return {
            'type': type(exception).__name__,
            'message': str(exception),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat(),
            'module': exception.__class__.__module__,
            'line_number': self._get_exception_line_number(exception)
        }
    
    def should_rethrow(self, exception: Exception) -> bool:
        """
        判断是否应该重新抛出异常
        
        Args:
            exception: 异常对象
            
        Returns:
            bool: 是否应该重新抛出
        """
        # 业务异常和验证异常通常不需要重新抛出
        if isinstance(exception, (BusinessException, ValidationException)):
            return False
        
        # 基础设施异常可能需要重新抛出
        if isinstance(exception, InfrastructureException):
            return True
        
        # 其他异常根据严重程度决定
        return True
    
    def _find_handler(self, exception: Exception) -> Optional[Callable]:
        """查找异常处理器"""
        # 按异常类型层次结构查找处理器
        exception_type = type(exception)
        
        # 直接匹配
        if exception_type in self._handlers:
            return self._handlers[exception_type]
        
        # 查找父类处理器
        for base_type in exception_type.__mro__[1:]:
            if base_type in self._handlers:
                return self._handlers[base_type]
        
        return None
    
    def _log_exception(self, exception: Exception, exception_info: Dict[str, Any], context: Dict[str, Any] = None):
        """记录异常"""
        log_message = f"异常: {exception_info['type']} - {exception_info['message']}"
        
        if context:
            log_message += f", 上下文: {context}"
        
        if isinstance(exception, BusinessException):
            self.logger.warning(log_message)
        elif isinstance(exception, ValidationException):
            self.logger.warning(log_message)
        elif isinstance(exception, InfrastructureException):
            self.logger.error(log_message)
        else:
            self.logger.error(log_message)
            self.logger.debug(f"异常堆栈: {exception_info['traceback']}")
    
    def _get_exception_line_number(self, exception: Exception) -> Optional[int]:
        """获取异常发生的行号"""
        try:
            tb = traceback.extract_tb(exception.__traceback__)
            if tb:
                return tb[-1].lineno
        except:
            pass
        return None
    
    def _handle_business_exception(self, exception: BusinessException, context: Dict[str, Any] = None):
        """处理业务异常"""
        self.logger.warning(f"业务异常: {exception.error_code} - {exception.message}")
        if exception.details:
            self.logger.debug(f"业务异常详情: {exception.details}")
    
    def _handle_validation_exception(self, exception: ValidationException, context: Dict[str, Any] = None):
        """处理验证异常"""
        field_info = f"字段: {exception.field}" if exception.field else ""
        value_info = f"值: {exception.value}" if exception.value else ""
        
        self.logger.warning(f"验证异常: {exception.message} {field_info} {value_info}")
        if exception.details:
            self.logger.debug(f"验证异常详情: {exception.details}")
    
    def _handle_infrastructure_exception(self, exception: InfrastructureException, context: Dict[str, Any] = None):
        """处理基础设施异常"""
        component_info = f"组件: {exception.component}" if exception.component else ""
        
        self.logger.error(f"基础设施异常: {exception.message} {component_info}")
        if exception.details:
            self.logger.debug(f"基础设施异常详情: {exception.details}")
    
    def _handle_generic_exception(self, exception: Exception, context: Dict[str, Any] = None):
        """处理通用异常"""
        self.logger.error(f"未处理的异常: {type(exception).__name__} - {str(exception)}")
        self.logger.debug(f"异常堆栈: {traceback.format_exc()}")


# 全局异常处理器实例
_exception_handler: Optional[ExceptionHandler] = None


def get_exception_handler() -> ExceptionHandler:
    """获取全局异常处理器"""
    global _exception_handler
    if _exception_handler is None:
        _exception_handler = ExceptionHandler()
    return _exception_handler


# 便捷函数
def handle_exception(exception: Exception, context: Dict[str, Any] = None) -> bool:
    """便捷函数：处理异常"""
    return get_exception_handler().handle_exception(exception, context)


def raise_business_exception(message: str, error_code: str = None, details: Dict[str, Any] = None):
    """便捷函数：抛出业务异常"""
    raise BusinessException(message, error_code, details)


def raise_validation_exception(message: str, field: str = None, value: Any = None, details: Dict[str, Any] = None):
    """便捷函数：抛出验证异常"""
    raise ValidationException(message, field, value, details)


def raise_infrastructure_exception(message: str, component: str = None, details: Dict[str, Any] = None):
    """便捷函数：抛出基础设施异常"""
    raise InfrastructureException(message, component, details) 