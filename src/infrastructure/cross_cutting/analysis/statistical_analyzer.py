"""
横切关注点 - 统计分析器

提供统一的数据统计分析服务，包括统计计算、数据分析等。
遵循DDD架构中的横切关注点设计原则，为整个应用提供统计分析基础设施。
"""

import math
import statistics
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from collections import Counter

from ..logging import get_logger


@dataclass
class StatisticalResult:
    """统计分析结果"""
    count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    variance: float
    percentiles: Dict[str, float]
    distribution: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'count': self.count,
            'mean': self.mean,
            'median': self.median,
            'std_dev': self.std_dev,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'variance': self.variance,
            'percentiles': self.percentiles,
            'distribution': self.distribution
        }


class IStatisticalAnalyzer(ABC):
    """统计分析器接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def calculate_basic_stats(self, data: List[float]) -> StatisticalResult:
        """计算基础统计信息"""
        pass
    
    @abstractmethod
    def calculate_percentiles(self, data: List[float], percentiles: List[float]) -> Dict[str, float]:
        """计算百分位数"""
        pass
    
    @abstractmethod
    def analyze_distribution(self, data: List[float], bins: int = 10) -> Dict[str, int]:
        """分析数据分布"""
        pass
    
    @abstractmethod
    def detect_outliers(self, data: List[float], method: str = "iqr") -> List[float]:
        """检测异常值"""
        pass


class StatisticalAnalyzer(IStatisticalAnalyzer):
    """统计分析器实现 - 统一的数据分析"""
    
    def __init__(self):
        """初始化统计分析器"""
        self.logger = get_logger("statistical.analyzer")
    
    def calculate_basic_stats(self, data: List[float]) -> StatisticalResult:
        """
        计算基础统计信息
        
        Args:
            data: 数值数据列表
            
        Returns:
            StatisticalResult: 统计结果
        """
        try:
            if not data:
                raise ValueError("数据列表不能为空")
            
            # 过滤无效数据
            valid_data = [x for x in data if x is not None and not math.isnan(x)]
            
            if not valid_data:
                raise ValueError("没有有效的数值数据")
            
            # 计算基础统计量
            count = len(valid_data)
            mean = statistics.mean(valid_data)
            median = statistics.median(valid_data)
            variance = statistics.variance(valid_data)
            std_dev = math.sqrt(variance)
            min_value = min(valid_data)
            max_value = max(valid_data)
            
            # 计算百分位数
            percentiles = self.calculate_percentiles(valid_data, [25, 50, 75, 90, 95, 99])
            
            # 分析分布
            distribution = self.analyze_distribution(valid_data)
            
            result = StatisticalResult(
                count=count,
                mean=mean,
                median=median,
                std_dev=std_dev,
                min_value=min_value,
                max_value=max_value,
                variance=variance,
                percentiles=percentiles,
                distribution=distribution
            )
            
            self.logger.info(f"统计分析完成，数据量: {count}")
            return result
            
        except Exception as e:
            self.logger.error(f"统计分析失败: {str(e)}")
            raise
    
    def calculate_percentiles(self, data: List[float], percentiles: List[float]) -> Dict[str, float]:
        """
        计算百分位数
        
        Args:
            data: 数值数据列表
            percentiles: 百分位数列表
            
        Returns:
            Dict[str, float]: 百分位数结果
        """
        try:
            if not data:
                return {}
            
            sorted_data = sorted(data)
            result = {}
            
            for p in percentiles:
                if 0 <= p <= 100:
                    index = (p / 100) * (len(sorted_data) - 1)
                    if index.is_integer():
                        value = sorted_data[int(index)]
                    else:
                        lower = sorted_data[int(index)]
                        upper = sorted_data[int(index) + 1]
                        value = lower + (upper - lower) * (index - int(index))
                    
                    result[f"p{p}"] = value
            
            return result
            
        except Exception as e:
            self.logger.error(f"百分位数计算失败: {str(e)}")
            return {}
    
    def analyze_distribution(self, data: List[float], bins: int = 10) -> Dict[str, int]:
        """
        分析数据分布
        
        Args:
            data: 数值数据列表
            bins: 分箱数量
            
        Returns:
            Dict[str, int]: 分布统计
        """
        try:
            if not data:
                return {}
            
            min_val = min(data)
            max_val = max(data)
            
            if min_val == max_val:
                return {f"{min_val}": len(data)}
            
            # 计算分箱
            bin_width = (max_val - min_val) / bins
            distribution = {}
            
            for value in data:
                bin_index = min(int((value - min_val) / bin_width), bins - 1)
                bin_start = min_val + bin_index * bin_width
                bin_end = bin_start + bin_width
                bin_label = f"{bin_start:.2f}-{bin_end:.2f}"
                
                distribution[bin_label] = distribution.get(bin_label, 0) + 1
            
            return distribution
            
        except Exception as e:
            self.logger.error(f"分布分析失败: {str(e)}")
            return {}
    
    def detect_outliers(self, data: List[float], method: str = "iqr") -> List[float]:
        """
        检测异常值
        
        Args:
            data: 数值数据列表
            method: 检测方法 ("iqr" 或 "zscore")
            
        Returns:
            List[float]: 异常值列表
        """
        try:
            if not data or len(data) < 4:
                return []
            
            if method == "iqr":
                return self._detect_outliers_iqr(data)
            elif method == "zscore":
                return self._detect_outliers_zscore(data)
            else:
                raise ValueError(f"不支持的异常值检测方法: {method}")
                
        except Exception as e:
            self.logger.error(f"异常值检测失败: {str(e)}")
            return []
    
    def _detect_outliers_iqr(self, data: List[float]) -> List[float]:
        """使用IQR方法检测异常值"""
        sorted_data = sorted(data)
        q1 = statistics.quantiles(sorted_data, n=4)[0]
        q3 = statistics.quantiles(sorted_data, n=4)[2]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [x for x in data if x < lower_bound or x > upper_bound]
        return outliers
    
    def _detect_outliers_zscore(self, data: List[float], threshold: float = 3.0) -> List[float]:
        """使用Z-score方法检测异常值"""
        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)
        
        outliers = []
        for value in data:
            z_score = abs((value - mean) / std_dev)
            if z_score > threshold:
                outliers.append(value)
        
        return outliers
    
    def calculate_correlation(self, data1: List[float], data2: List[float]) -> float:
        """
        计算相关系数
        
        Args:
            data1: 第一组数据
            data2: 第二组数据
            
        Returns:
            float: 相关系数
        """
        try:
            if len(data1) != len(data2) or len(data1) < 2:
                return 0.0
            
            # 过滤无效数据
            valid_pairs = [(x, y) for x, y in zip(data1, data2) 
                          if x is not None and y is not None 
                          and not math.isnan(x) and not math.isnan(y)]
            
            if len(valid_pairs) < 2:
                return 0.0
            
            x_values, y_values = zip(*valid_pairs)
            
            # 计算相关系数
            correlation = statistics.correlation(x_values, y_values)
            return correlation
            
        except Exception as e:
            self.logger.error(f"相关系数计算失败: {str(e)}")
            return 0.0
    
    def calculate_trend(self, data: List[float]) -> Dict[str, Any]:
        """
        计算趋势分析
        
        Args:
            data: 时间序列数据
            
        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        try:
            if len(data) < 2:
                return {"trend": "insufficient_data", "slope": 0, "direction": "none"}
            
            # 计算线性趋势
            n = len(data)
            x_values = list(range(n))
            y_values = data
            
            # 计算斜率
            mean_x = statistics.mean(x_values)
            mean_y = statistics.mean(y_values)
            
            numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values))
            denominator = sum((x - mean_x) ** 2 for x in x_values)
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            # 判断趋势方向
            if abs(slope) < 0.01:
                direction = "stable"
            elif slope > 0:
                direction = "increasing"
            else:
                direction = "decreasing"
            
            return {
                "trend": direction,
                "slope": slope,
                "direction": direction,
                "data_points": n
            }
            
        except Exception as e:
            self.logger.error(f"趋势分析失败: {str(e)}")
            return {"trend": "error", "slope": 0, "direction": "error"}


# 全局统计分析器实例
_statistical_analyzer: Optional[StatisticalAnalyzer] = None


def get_statistical_analyzer() -> StatisticalAnalyzer:
    """获取全局统计分析器"""
    global _statistical_analyzer
    if _statistical_analyzer is None:
        _statistical_analyzer = StatisticalAnalyzer()
    return _statistical_analyzer


# 便捷函数
def calculate_statistics(data: List[float]) -> StatisticalResult:
    """便捷函数：计算统计信息"""
    return get_statistical_analyzer().calculate_basic_stats(data)


def analyze_distribution(data: List[float], bins: int = 10) -> Dict[str, int]:
    """便捷函数：分析数据分布"""
    return get_statistical_analyzer().analyze_distribution(data, bins)


def calculate_percentiles(data: List[float], percentiles: List[float]) -> Dict[str, float]:
    """便捷函数：计算百分位数"""
    return get_statistical_analyzer().calculate_percentiles(data, percentiles) 