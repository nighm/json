#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备标识符生成服务 - 领域层
负责设备标识符的生成和验证业务逻辑
"""

from src.domain.value_objects.device_identifier import DeviceIdentifierGenerator as BaseGenerator

class DeviceIdentifierGenerator(BaseGenerator):
    """设备标识符生成服务 - 领域层"""
    
    def __init__(self):
        super().__init__()
    
    # 继承基类的所有方法，可以根据需要添加领域特定的业务逻辑 