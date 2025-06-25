import os
import tempfile
import shutil
import pytest
from src.infrastructure.cross_cutting.logging.logger import LoggerFactory, ApplicationLogger, DefaultLogConfigProvider, get_logger, set_log_config_provider

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


def test_logger_error_output(caplog):
    """
    测试异常日志输出功能。
    """
    logger = get_logger("test")
    with caplog.at_level("ERROR"):
        logger.error("异常日志内容")
    assert any("异常日志内容" in record.message for record in caplog.records)


def test_logger_format(caplog):
    """
    测试日志格式化输出。
    """
    logger = get_logger("test")
    with caplog.at_level("INFO"):
        logger.info("格式化日志：%s", "参数1")
    assert any("格式化日志：参数1" in record.message for record in caplog.records)


def test_logger_name_isolation(caplog):
    """
    测试不同Logger名称的隔离性。
    """
    logger1 = get_logger("logger1")
    logger2 = get_logger("logger2")
    with caplog.at_level("INFO"):
        logger1.info("logger1日志")
        logger2.info("logger2日志")
    assert any("logger1日志" in record.message for record in caplog.records)
    assert any("logger2日志" in record.message for record in caplog.records)


def test_application_logger_basic_and_edge():
    """
    测试ApplicationLogger的基本功能、异常分支。
    """
    logger = ApplicationLogger('test_logger')
    logger.debug('debug')
    logger.info('info')
    logger.warning('warn')
    logger.error('err')
    logger.critical('crit')
    logger.log(logger.config_provider.get_log_level(), 'log')
    # 异常分支（无效日志级别）
    with pytest.raises(Exception):
        logger.log(None, 'bad')


def test_logger_factory_and_clear():
    """
    测试LoggerFactory的get_logger、clear_loggers等分支。
    """
    LoggerFactory.clear_loggers()
    logger1 = LoggerFactory.get_logger('l1')
    logger2 = LoggerFactory.get_logger('l1')
    assert logger1 is logger2
    LoggerFactory.clear_loggers()
    logger3 = LoggerFactory.get_logger('l2')
    assert logger3.name == 'l2'


def test_default_log_config_provider_env(monkeypatch):
    """
    测试DefaultLogConfigProvider的环境变量分支。
    """
    monkeypatch.setenv('LOG_LEVEL', 'ERROR')
    monkeypatch.setenv('LOG_DIR', 'test_logs')
    monkeypatch.setenv('LOG_FORMAT', '%(message)s')
    monkeypatch.setenv('LOG_DATE_FORMAT', '%Y')
    monkeypatch.setenv('LOG_TO_CONSOLE', 'false')
    monkeypatch.setenv('LOG_TO_FILE', 'false')
    provider = DefaultLogConfigProvider()
    assert provider.get_log_level().name == 'ERROR'
    assert provider.get_log_dir() == 'test_logs'
    assert provider.get_log_format() == '%(message)s'
    assert provider.get_date_format() == '%Y'
    assert not provider.should_log_to_console()
    assert not provider.should_log_to_file()


def test_set_log_config_provider():
    """
    测试set_log_config_provider便捷函数。
    """
    provider = DefaultLogConfigProvider()
    set_log_config_provider(provider)
    logger = get_logger('set_config')
    assert isinstance(logger, ApplicationLogger) 