#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试工具模块
提供通用的测试工具和辅助函数

作者：AI Assistant
创建时间：2025-01-27
"""

import pytest
from typing import Any, Dict, List
from pathlib import Path


class TestBase:
    """测试基类"""
    
    def setup_method(self):
        """测试前准备"""
        pass
    
    def teardown_method(self):
        """测试后清理"""
        pass


def create_test_data() -> Dict[str, Any]:
    """创建测试数据"""
    return {
        'test_string': 'test_value',
        'test_number': 42,
        'test_list': [1, 2, 3, 4, 5],
        'test_dict': {'key': 'value'}
    }


def assert_performance(target_time: float, actual_time: float, tolerance: float = 0.1):
    """性能断言"""
    assert actual_time <= target_time * (1 + tolerance),         f"性能不达标: 期望 {target_time}s, 实际 {actual_time}s"


def mock_external_service():
    """模拟外部服务"""
    # 这里可以添加外部服务的模拟逻辑
    pass
