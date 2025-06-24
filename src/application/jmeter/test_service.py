#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter测试服务
- 协调测试计划和执行
- 管理测试流程
"""
import os
import time
from typing import List, Dict, Any

from src.domain.jmeter.test_plan import TestPlan
from src.domain.jmeter.test_execution import TestExecution, TestResult
from src.infrastructure.external.testing_tools.jmeter.jmeter_executor import JMeterExecutor

class JMeterTestService:
    """JMeter测试服务"""
    
    def __init__(self, jmx_dir: str, jmeter_home: str):
        """
        初始化测试服务
        
        Args:
            jmx_dir: JMX文件目录
            jmeter_home: JMeter安装目录
        """
        self.test_plan = TestPlan(jmx_dir)
        self.test_execution = TestExecution()
        self.jmeter_executor = JMeterExecutor(jmeter_home)
        self.jmx_dir = jmx_dir
    
    def run_concurrent_tests(self, concurrent_levels: List[int], wait_time: int = 30) -> Dict[str, Any]:
        """
        运行多级并发测试
        
        Args:
            concurrent_levels: 并发级别列表
            wait_time: 测试间隔时间（秒）
            
        Returns:
            Dict[str, Any]: 测试执行摘要
        """
        # 1. 获取基础JMX文件
        base_jmx_path = self.test_plan.get_latest_filtered_jmx()
        print(f'使用基础JMX文件：{base_jmx_path}')
        
        # 2. 为每个并发级别执行测试
        for concurrent_level in concurrent_levels:
            print(f'\n开始测试并发级别：{concurrent_level}')
            
            # 2.1 生成对应并发数的JMX文件
            jmx_file = self.test_plan.generate_jmx_filename(concurrent_level)
            jmx_path = os.path.join(self.jmx_dir, jmx_file)
            self.test_plan.modify_concurrent_level(base_jmx_path, concurrent_level, jmx_path)
            
            # 2.2 执行JMeter测试
            result_file = f'result_{concurrent_level}.jtl'
            success, error = self.jmeter_executor.execute_test(jmx_path, result_file)
            
            if not success:
                print(f'警告：并发级别 {concurrent_level} 的测试失败：{error}')
                continue
            
            # 2.3 解析测试结果
            stats = self._parse_result_file(result_file)
            result = TestResult.from_stats(concurrent_level, stats)
            self.test_execution.add_result(result)
            
            # 2.4 等待一段时间，避免系统负载过高
            if concurrent_level != concurrent_levels[-1]:
                print(f'等待{wait_time}秒后继续下一个测试...')
                time.sleep(wait_time)
        
        # 3. 返回测试执行摘要
        return self.test_execution.get_summary()
    
    def _parse_result_file(self, result_file: str) -> Dict[str, Any]:
        """
        解析结果文件
        
        Args:
            result_file: 结果文件路径
            
        Returns:
            Dict[str, Any]: 解析后的统计数据
        """
        # TODO: 实现结果文件解析逻辑
        # 这里需要实现从JTL文件解析统计数据的具体逻辑
        return {
            'total_samples': 0,
            'success_rate': 0.0,
            'average_response_time': 0.0,
            'error_count': 0,
            'throughput': 0.0
        } 