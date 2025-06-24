#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试DeviceDataManager初始化过程
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_device_manager_init():
    """测试DeviceDataManager初始化"""
    try:
        print("=== 开始测试DeviceDataManager初始化 ===")
        
        # 测试1: 导入模块
        print("1. 导入DeviceDataManager模块...")
        from src.application.services.device_data_manager import DeviceDataManager
        print("   ✓ 导入成功")
        
        # 测试2: 创建实例
        print("2. 创建DeviceDataManager实例...")
        device_manager = DeviceDataManager()
        print("   ✓ 实例创建成功")
        
        # 测试3: 基本功能
        print("3. 测试基本功能...")
        stats = device_manager.get_device_statistics()
        print(f"   ✓ 获取统计信息成功: {stats}")
        
        print("=== 所有测试通过 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_device_manager_init()
    sys.exit(0 if success else 1) 