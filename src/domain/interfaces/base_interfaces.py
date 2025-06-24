#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础接口定义
定义领域服务的抽象接口

作者：AI Assistant
创建时间：2025-01-27
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IRepository(ABC):
    """仓储接口"""
    
    @abstractmethod
    def save(self, entity: Any) -> bool:
        """保存实体"""
        pass
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[Any]:
        """根据ID查找实体"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Any]:
        """查找所有实体"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """删除实体"""
        pass


class IService(ABC):
    """服务接口"""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """执行服务"""
        pass


class IConfigService(ABC):
    """配置服务接口"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> bool:
        """设置配置"""
        pass
    
    @abstractmethod
    def load_config(self, config_path: str) -> bool:
        """加载配置"""
        pass


class ILogger(ABC):
    """日志接口"""
    
    @abstractmethod
    def info(self, message: str) -> None:
        """信息日志"""
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        """错误日志"""
        pass
    
    @abstractmethod
    def warning(self, message: str) -> None:
        """警告日志"""
        pass
    
    @abstractmethod
    def debug(self, message: str) -> None:
        """调试日志"""
        pass
