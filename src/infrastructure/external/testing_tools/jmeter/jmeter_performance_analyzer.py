"""
外部工具 - JMeter性能分析器

提供JMeter测试结果分析功能，包括JTL文件处理、性能指标计算等。
使用横切关注点的统计分析能力，遵循DDD架构设计原则。
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.infrastructure.cross_cutting.logging.logger import get_logger
from src.infrastructure.cross_cutting.analysis.statistical_analyzer import (
    StatisticalAnalyzer, StatisticalMetrics
)


class PerformanceMetrics:
    """性能指标数据类 - 封装JMeter测试结果"""
    
    def __init__(self, 
                 total_requests: int = 0,
                 success_count: int = 0,
                 error_count: int = 0,
                 response_times: List[float] = None,
                 thread_count: int = None,
                 loop_count: int = None,
                 test_name: str = None):
        """
        初始化性能指标
        
        Args:
            total_requests: 总请求数
            success_count: 成功请求数
            error_count: 错误请求数
            response_times: 响应时间列表
            thread_count: 线程数
            loop_count: 循环次数
            test_name: 测试名称
        """
        self.total_requests = total_requests
        self.success_count = success_count
        self.error_count = error_count
        self.response_times = response_times or []
        self.thread_count = thread_count
        self.loop_count = loop_count
        self.test_name = test_name
        
        # 使用横切关注点的统计分析器
        self.statistical_analyzer = StatisticalAnalyzer()
        self._calculate_derived_metrics()
    
    def _calculate_derived_metrics(self):
        """计算派生指标"""
        if not self.response_times:
            self.min_response_time = 0
            self.max_response_time = 0
            self.avg_response_time = 0
            self.tp90 = 0
            self.tp99 = 0
            self.success_rate = 0
            return
        
        # 使用统计分析器计算基础统计
        stats = self.statistical_analyzer.calculate_basic_stats(self.response_times)
        
        self.min_response_time = stats.min_value
        self.max_response_time = stats.max_value
        self.avg_response_time = stats.mean
        self.tp90 = stats.percentiles.get('tp90', 0)
        self.tp99 = stats.percentiles.get('tp99', 0)
        
        # 计算成功率
        self.success_rate = self.statistical_analyzer.calculate_success_rate(
            self.total_requests, self.success_count
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'test_name': self.test_name,
            'thread_count': self.thread_count,
            'loop_count': self.loop_count,
            'total_requests': self.total_requests,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': round(self.success_rate, 2),
            'min_response_time': round(self.min_response_time, 2),
            'max_response_time': round(self.max_response_time, 2),
            'avg_response_time': round(self.avg_response_time, 2),
            'tp90': round(self.tp90, 2),
            'tp99': round(self.tp99, 2)
        }


class JTLFileAnalyzer:
    """JTL文件分析器 - 专门处理JMeter测试结果文件"""
    
    def __init__(self, result_dir: str):
        """
        初始化JTL文件分析器
        
        Args:
            result_dir: 测试结果目录
        """
        self.result_dir = Path(result_dir)
        self.statistical_analyzer = StatisticalAnalyzer()
        self.logger = get_logger("jtl.analyzer")
    
    def analyze_jtl_file(self, jtl_path: str, thread_count: int = None) -> PerformanceMetrics:
        """
        分析JTL文件
        
        Args:
            jtl_path: JTL文件路径
            thread_count: 线程数
            
        Returns:
            PerformanceMetrics: 性能指标对象
        """
        self.logger.info(f"开始分析JTL文件: {jtl_path}")
        
        metrics = PerformanceMetrics(thread_count=thread_count)
        
        try:
            with open(jtl_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    metrics.total_requests += 1
                    
                    # 统计成功/失败数
                    if row.get('success', '').lower() == 'true':
                        metrics.success_count += 1
                    else:
                        metrics.error_count += 1
                    
                    # 统计响应时间
                    try:
                        response_time = float(row.get('elapsed', 0))
                        metrics.response_times.append(response_time)
                    except (ValueError, TypeError):
                        continue
            
            # 计算派生指标
            metrics._calculate_derived_metrics()
            
            self.logger.info(f"JTL文件分析完成: 总请求数={metrics.total_requests}, "
                           f"成功率={metrics.success_rate:.2f}%")
            
        except Exception as e:
            self.logger.error(f"分析JTL文件失败: {str(e)}")
            raise
        
        return metrics
    
    def find_jtl_file(self, test_name: str, thread_count: int, loop_count: int) -> Optional[Path]:
        """
        查找对应的JTL文件
        
        Args:
            test_name: 测试名称
            thread_count: 线程数
            loop_count: 循环次数
            
        Returns:
            Optional[Path]: JTL文件路径
        """
        # 尝试多种文件命名模式
        patterns = [
            f"**/{test_name}_{thread_count}_{loop_count}_*/result.jtl",
            f"**/{test_name}_{loop_count}_{thread_count}_*/result.jtl",
            f"**/{test_name}_*_{thread_count}_{loop_count}_*/result.jtl",
            f"**/{test_name}_*_{loop_count}_{thread_count}_*/result.jtl"
        ]
        
        for pattern in patterns:
            jtl_files = list(self.result_dir.glob(pattern))
            if jtl_files:
                # 返回最新的文件
                return max(jtl_files, key=lambda x: x.stat().st_mtime)
        
        return None
    
    def analyze_test_results(self, test_name: str, thread_count: int, loop_count: int) -> PerformanceMetrics:
        """
        分析指定测试结果
        
        Args:
            test_name: 测试名称
            thread_count: 线程数
            loop_count: 循环次数
            
        Returns:
            PerformanceMetrics: 性能指标对象
        """
        jtl_file = self.find_jtl_file(test_name, thread_count, loop_count)
        
        if not jtl_file:
            # 列出所有可能的JTL文件用于调试
            all_jtl_files = list(self.result_dir.glob("**/*.jtl"))
            debug_info = (f"未找到测试结果文件: {test_name}, "
                         f"线程数: {thread_count}, 循环次数: {loop_count}\n"
                         f"当前目录下所有JTL文件: {[str(f) for f in all_jtl_files]}")
            self.logger.error(debug_info)
            raise FileNotFoundError(debug_info)
        
        metrics = self.analyze_jtl_file(str(jtl_file), thread_count)
        metrics.test_name = test_name
        metrics.loop_count = loop_count
        
        return metrics


class JMeterReportGenerator:
    """JMeter报告生成器 - 专门生成JMeter测试报告"""
    
    def __init__(self):
        self.logger = get_logger("jmeter.report")
    
    def generate_csv_report(self, metrics_list: List[PerformanceMetrics], output_path: str):
        """
        生成CSV格式的性能报告
        
        Args:
            metrics_list: 性能指标列表
            output_path: 输出文件路径
        """
        self.logger.info(f"开始生成CSV报告: {output_path}")
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入表头
                writer.writerow([
                    '测试名称', '线程数', '循环次数', '总请求数', '成功数', '失败数',
                    '成功率(%)', '最小响应时间(ms)', '最大响应时间(ms)', 
                    '平均响应时间(ms)', 'TP90响应时间(ms)', 'TP99响应时间(ms)'
                ])
                
                # 写入数据
                for metrics in metrics_list:
                    data = metrics.to_dict()
                    writer.writerow([
                        data['test_name'], data['thread_count'], data['loop_count'],
                        data['total_requests'], data['success_count'], data['error_count'],
                        f"{data['success_rate']:.2f}", f"{data['min_response_time']:.2f}",
                        f"{data['max_response_time']:.2f}", f"{data['avg_response_time']:.2f}",
                        f"{data['tp90']:.2f}", f"{data['tp99']:.2f}"
                    ])
            
            self.logger.info(f"CSV报告生成完成: {output_path}")
            
        except Exception as e:
            self.logger.error(f"生成CSV报告失败: {str(e)}")
            raise


# 便捷函数
def get_jtl_analyzer(result_dir: str) -> JTLFileAnalyzer:
    """获取JTL文件分析器"""
    return JTLFileAnalyzer(result_dir)


def get_jmeter_report_generator() -> JMeterReportGenerator:
    """获取JMeter报告生成器"""
    return JMeterReportGenerator() 