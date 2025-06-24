"""
横切关注点 - 统计分析模块

提供统一的数据统计分析服务，包括统计计算、数据分析等。
遵循DDD架构的横切关注点设计原则，为整个应用提供统计分析基础设施。
"""

from .statistical_analyzer import (
    IStatisticalAnalyzer,
    StatisticalAnalyzer,
    StatisticalResult,
    get_statistical_analyzer,
    calculate_statistics,
    analyze_distribution,
    calculate_percentiles
)

__all__ = [
    'IStatisticalAnalyzer',
    'StatisticalAnalyzer',
    'StatisticalResult',
    'get_statistical_analyzer',
    'calculate_statistics',
    'analyze_distribution',
    'calculate_percentiles'
] 