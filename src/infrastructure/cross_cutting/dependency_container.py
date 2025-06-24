#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入容器
统一管理项目依赖关系，实现依赖倒置原则

作者：AI Assistant
创建时间：2025-01-27
"""

from typing import Dict, Any, Type, Optional
import logging

logger = logging.getLogger(__name__)


class DependencyContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register(self, service_type: str, implementation: Any, singleton: bool = False) -> None:
        """
        注册服务
        
        Args:
            service_type: 服务类型标识
            implementation: 服务实现
            singleton: 是否为单例
        """
        if singleton:
            self._singletons[service_type] = implementation
        else:
            self._services[service_type] = implementation
        
        logger.info(f"已注册服务: {service_type}")
    
    def resolve(self, service_type: str) -> Any:
        """
        解析服务
        
        Args:
            service_type: 服务类型标识
            
        Returns:
            服务实例
        """
        # 优先返回单例
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # 返回普通服务
        if service_type in self._services:
            return self._services[service_type]
        
        raise KeyError(f"未找到服务: {service_type}")
    
    def get_singleton(self, service_type: str) -> Any:
        """
        获取单例服务
        
        Args:
            service_type: 服务类型标识
            
        Returns:
            单例服务实例
        """
        if service_type not in self._singletons:
            raise KeyError(f"未找到单例服务: {service_type}")
        
        return self._singletons[service_type]


# 全局依赖容器实例
container = DependencyContainer()


def register_services() -> None:
    """注册所有服务"""
    # 这里注册项目的所有服务
    # 示例：
    # container.register('logger', logging.getLogger(__name__), singleton=True)
    # container.register('config_service', ConfigService(), singleton=True)
    pass


def get_service(service_type: str) -> Any:
    """
    获取服务实例
    
    Args:
        service_type: 服务类型标识
        
    Returns:
        服务实例
    """
    return container.resolve(service_type)
