"""
横切关注点 - 日志记录器

提供统一的日志记录服务，支持不同级别的日志记录和格式化输出。
遵循DDD架构中的横切关注点设计原则，为整个应用提供日志基础设施。
"""

import logging
import sys
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
from enum import Enum


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ILogger(ABC):
    """日志记录器接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def debug(self, message: str, **kwargs):
        """记录调试级别日志"""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs):
        """记录信息级别日志"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs):
        """记录警告级别日志"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs):
        """记录错误级别日志"""
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs):
        """记录严重错误级别日志"""
        pass
    
    @abstractmethod
    def log(self, level: LogLevel, message: str, **kwargs):
        """记录指定级别的日志"""
        pass


class ILogConfigProvider(ABC):
    """日志配置提供者接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def get_log_level(self) -> LogLevel:
        """获取日志级别"""
        pass
    
    @abstractmethod
    def get_log_dir(self) -> str:
        """获取日志目录"""
        pass
    
    @abstractmethod
    def get_log_format(self) -> str:
        """获取日志格式"""
        pass
    
    @abstractmethod
    def get_date_format(self) -> str:
        """获取日期格式"""
        pass
    
    @abstractmethod
    def should_log_to_console(self) -> bool:
        """是否输出到控制台"""
        pass
    
    @abstractmethod
    def should_log_to_file(self) -> bool:
        """是否输出到文件"""
        pass


class DefaultLogConfigProvider(ILogConfigProvider):
    """默认日志配置提供者 - 使用环境变量和默认值"""
    
    def get_log_level(self) -> LogLevel:
        """获取日志级别"""
        level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
        try:
            return LogLevel[level_name]
        except KeyError:
            return LogLevel.INFO
    
    def get_log_dir(self) -> str:
        """获取日志目录"""
        return os.environ.get('LOG_DIR', 'logs')
    
    def get_log_format(self) -> str:
        """获取日志格式"""
        return os.environ.get('LOG_FORMAT', 
                             '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    def get_date_format(self) -> str:
        """获取日期格式"""
        return os.environ.get('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
    
    def should_log_to_console(self) -> bool:
        """是否输出到控制台"""
        return os.environ.get('LOG_TO_CONSOLE', 'true').lower() == 'true'
    
    def should_log_to_file(self) -> bool:
        """是否输出到文件"""
        return os.environ.get('LOG_TO_FILE', 'true').lower() == 'true'


class LoggerFactory:
    """日志记录器工厂 - 统一创建和管理日志记录器"""
    
    _loggers: Dict[str, 'ApplicationLogger'] = {}
    _config_provider: Optional[ILogConfigProvider] = None
    
    @classmethod
    def set_config_provider(cls, config_provider: ILogConfigProvider):
        """设置配置提供者"""
        cls._config_provider = config_provider
    
    @classmethod
    def get_logger(cls, name: str, log_dir: Optional[str] = None) -> 'ApplicationLogger':
        """
        获取或创建日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志目录（可选，默认使用配置）
            
        Returns:
            ApplicationLogger: 日志记录器实例
        """
        if name not in cls._loggers:
            cls._loggers[name] = ApplicationLogger(name, log_dir, cls._config_provider)
        return cls._loggers[name]
    
    @classmethod
    def clear_loggers(cls):
        """清除所有日志记录器（用于测试）"""
        cls._loggers.clear()


class ApplicationLogger(ILogger):
    """应用程序日志记录器 - 实现统一的日志记录功能"""
    
    def __init__(self, name: str, log_dir: Optional[str] = None, 
                 config_provider: Optional[ILogConfigProvider] = None):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志目录（可选）
            config_provider: 配置提供者（可选）
        """
        self.name = name
        self.config_provider = config_provider or DefaultLogConfigProvider()
        self.logger = self._setup_logger(log_dir)
    
    def _setup_logger(self, log_dir: Optional[str] = None) -> logging.Logger:
        """
        设置日志记录器配置
        
        Args:
            log_dir: 日志目录
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        # 创建日志记录器
        logger = logging.getLogger(self.name)
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 设置日志级别
        logger.setLevel(self.config_provider.get_log_level().value)
        
        # 创建格式化器
        formatter = logging.Formatter(
            self.config_provider.get_log_format(),
            datefmt=self.config_provider.get_date_format()
        )
        
        # 添加控制台处理器
        if self.config_provider.should_log_to_console():
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logger.level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if self.config_provider.should_log_to_file():
            # 确定日志目录
            if log_dir is None:
                log_dir = self.config_provider.get_log_dir()
            
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 设置日志文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"{self.name}_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logger.level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def debug(self, message: str, *args, **kwargs):
        if args:
            message = message % args
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        if args:
            message = message % args
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        if args:
            message = message % args
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        if args:
            message = message % args
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        if args:
            message = message % args
        self.logger.critical(message, **kwargs)
    
    def log(self, level: LogLevel, message: str, *args, **kwargs):
        if args:
            message = message % args
        self.logger.log(level.value, message, **kwargs)


# 便捷函数
def get_logger(name: str) -> ApplicationLogger:
    """获取日志记录器"""
    return LoggerFactory.get_logger(name)


def get_logger_factory() -> LoggerFactory:
    """获取日志记录器工厂"""
    return LoggerFactory


def set_log_config_provider(config_provider: ILogConfigProvider):
    """设置日志配置提供者"""
    LoggerFactory.set_config_provider(config_provider) 