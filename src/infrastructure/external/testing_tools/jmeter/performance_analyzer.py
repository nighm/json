"""
横切关注点 - 性能分析模块

提供统一的性能数据分析服务，包括响应时间统计、百分位计算、成功率分析等。
遵循DDD架构中的横切关注点设计原则，为整个应用提供性能分析基础设施。
"""

import csv
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.infrastructure.cross_cutting.logging.logger import get_logger


class IPerformanceAnalyzer(ABC):
    """性能分析器接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def analyze_response_times(self, data: List[float]) -> Dict[str, float]:
        """分析响应时间数据"""
        pass
    
    @abstractmethod
    def calculate_percentiles(self, data: List[float], percentiles: List[float]) -> Dict[str, float]:
        """计算百分位数"""
        pass
    
    @abstractmethod
    def calculate_success_rate(self, total: int, success: int) -> float:
        """计算成功率"""
        pass


class PerformanceMetrics:
    """性能指标数据类 - 封装性能分析结果"""
    
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
        
        # 计算派生指标
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
        
        # 基础统计
        self.min_response_time = min(self.response_times)
        self.max_response_time = max(self.response_times)
        self.avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # 百分位数
        sorted_times = sorted(self.response_times)
        self.tp90 = self._calculate_percentile(sorted_times, 0.9)
        self.tp99 = self._calculate_percentile(sorted_times, 0.99)
        
        # 成功率
        if self.total_requests > 0:
            self.success_rate = (self.success_count / self.total_requests) * 100
        else:
            self.success_rate = 0
    
    def _calculate_percentile(self, data: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not data:
            return 0
        k = int(len(data) * percentile)
        k = min(k, len(data) - 1)
        return data[k]
    
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


class PerformanceAnalyzer(IPerformanceAnalyzer):
    """性能分析器实现"""
    
    def __init__(self):
        self.logger = get_logger("performance.analyzer")
    
    def analyze_response_times(self, data: List[float]) -> Dict[str, float]:
        """分析响应时间数据"""
        if not data:
            return {'min': 0, 'max': 0, 'avg': 0, 'tp50': 0, 'tp90': 0, 'tp95': 0, 'tp99': 0}
        
        sorted_data = sorted(data)
        return {
            'min': min(data),
            'max': max(data),
            'avg': sum(data) / len(data),
            'tp50': self._calculate_percentile(sorted_data, 0.5),
            'tp90': self._calculate_percentile(sorted_data, 0.9),
            'tp95': self._calculate_percentile(sorted_data, 0.95),
            'tp99': self._calculate_percentile(sorted_data, 0.99)
        }
    
    def calculate_percentiles(self, data: List[float], percentiles: List[float]) -> Dict[str, float]:
        """计算百分位数"""
        if not data:
            return {f'tp{int(p*100)}': 0 for p in percentiles}
        
        sorted_data = sorted(data)
        result = {}
        for p in percentiles:
            result[f'tp{int(p*100)}'] = self._calculate_percentile(sorted_data, p)
        return result
    
    def calculate_success_rate(self, total: int, success: int) -> float:
        """计算成功率"""
        if total == 0:
            return 0
        return (success / total) * 100
    
    def _calculate_percentile(self, data: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not data:
            return 0
        k = int(len(data) * percentile)
        k = min(k, len(data) - 1)
        return data[k]


class JTLFileAnalyzer:
    """JTL文件分析器"""
    
    def __init__(self, result_dir: str):
        """
        初始化JTL文件分析器
        
        Args:
            result_dir: 测试结果目录
        """
        self.result_dir = Path(result_dir)
        self.analyzer = PerformanceAnalyzer()
        self.logger = get_logger("jtl.analyzer")
    
    def analyze_jtl_file(self, jtl_path: str, thread_count: int = None) -> PerformanceMetrics:
        """分析JTL文件"""
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
        """查找对应的JTL文件"""
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
        """分析指定测试结果"""
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


class PerformanceReportGenerator:
    """性能报告生成器"""
    
    def __init__(self):
        self.logger = get_logger("performance.report")
    
    def generate_csv_report(self, metrics_list: List[PerformanceMetrics], output_path: str):
        """生成CSV格式的性能报告"""
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
def get_performance_analyzer() -> PerformanceAnalyzer:
    """获取性能分析器"""
    return PerformanceAnalyzer()


def get_jtl_analyzer(result_dir: str) -> JTLFileAnalyzer:
    """获取JTL文件分析器"""
    return JTLFileAnalyzer(result_dir)


def get_report_generator() -> PerformanceReportGenerator:
    """获取报告生成器"""
    return PerformanceReportGenerator() 