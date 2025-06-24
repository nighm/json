import pytest
from src.infrastructure.cross_cutting.logging import get_logger

# 日志模块单元测试

def test_logger_basic_output(caplog):
    """
    测试日志输出功能，验证日志内容和级别。
    """
    logger = get_logger("test")
    with caplog.at_level("INFO"):
        logger.info("测试信息日志")
    assert any("测试信息日志" in record.message for record in caplog.records)


def test_logger_level_filter(caplog):
    """
    测试日志级别过滤功能。
    """
    logger = get_logger("test")
    with caplog.at_level("WARNING"):
        logger.info("这条不会被记录")
        logger.warning("警告日志")
    assert any("警告日志" in record.message for record in caplog.records)
    assert not any("这条不会被记录" in record.message for record in caplog.records) 