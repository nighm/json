import pytest
from src.infrastructure.cross_cutting.analysis import get_statistical_analyzer

# 统计分析模块单元测试

def test_statistical_analyzer_basic():
    """
    测试统计分析的基础功能。
    """
    analyzer = get_statistical_analyzer()
    data = [1, 2, 3, 4, 5]
    result = analyzer.calculate_basic_stats(data)
    assert result.mean == 3.0
    assert result.count == 5 