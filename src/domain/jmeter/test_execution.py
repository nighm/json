#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter测试执行领域模型
- 管理测试执行状态和结果
- 处理测试报告生成
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class TestResult:
    """测试结果数据类"""
    concurrent_level: int
    timestamp: datetime
    total_samples: int
    success_rate: float
    average_response_time: float
    error_count: int
    throughput: float
    
    @classmethod
    def from_stats(cls, concurrent_level: int, stats: Dict[str, Any]) -> 'TestResult':
        """
        从统计数据创建测试结果
        
        Args:
            concurrent_level: 并发数
            stats: 统计数据
            
        Returns:
            TestResult: 测试结果对象
        """
        return cls(
            concurrent_level=concurrent_level,
            timestamp=datetime.now(),
            total_samples=stats.get('total_samples', 0),
            success_rate=stats.get('success_rate', 0.0),
            average_response_time=stats.get('average_response_time', 0.0),
            error_count=stats.get('error_count', 0),
            throughput=stats.get('throughput', 0.0)
        )

class TestExecution:
    """测试执行领域模型"""
    
    def __init__(self):
        """初始化测试执行"""
        self.results: List[TestResult] = []
    
    def add_result(self, result: TestResult) -> None:
        """
        添加测试结果
        
        Args:
            result: 测试结果
        """
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取测试执行摘要
        
        Returns:
            Dict[str, Any]: 测试执行摘要
        """
        if not self.results:
            return {}
            
        return {
            'total_tests': len(self.results),
            'concurrent_levels': [r.concurrent_level for r in self.results],
            'success_rates': [r.success_rate for r in self.results],
            'average_response_times': [r.average_response_time for r in self.results],
            'throughputs': [r.throughput for r in self.results],
            'error_counts': [r.error_count for r in self.results]
        }
    
    def get_best_performance(self) -> TestResult:
        """
        获取最佳性能的测试结果
        
        Returns:
            TestResult: 最佳性能的测试结果
            
        Raises:
            ValueError: 没有测试结果
        """
        if not self.results:
            raise ValueError('没有测试结果')
            
        return max(self.results, key=lambda x: x.throughput) 