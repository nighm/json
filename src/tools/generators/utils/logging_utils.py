#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志工具模块
提供统一的日志记录功能
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Union

# 默认日志格式
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 默认日志级别
DEFAULT_LOG_LEVEL = logging.INFO

# 默认日志文件大小（10MB）
DEFAULT_MAX_BYTES = 10 * 1024 * 1024

# 默认备份文件数量
DEFAULT_BACKUP_COUNT = 5


class Logger:
    """日志管理器类"""

    def __init__(
        self,
        name: str,
        log_dir: Optional[Union[str, Path]] = None,
        level: int = DEFAULT_LOG_LEVEL,
        format_str: str = DEFAULT_LOG_FORMAT,
        date_format: str = DEFAULT_DATE_FORMAT,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
    ):
        """
        初始化日志管理器

        Args:
            name: 日志器名称
            log_dir: 日志目录路径
            level: 日志级别
            format_str: 日志格式
            date_format: 日期格式
            max_bytes: 单个日志文件最大大小
            backup_count: 备份文件数量
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 创建格式化器
        formatter = logging.Formatter(format_str, date_format)

        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 如果指定了日志目录，添加文件处理器
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{name}.log"

            # 创建轮转文件处理器
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, msg: str, *args, **kwargs) -> None:
        """
        记录调试级别日志

        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """
        记录信息级别日志

        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """
        记录警告级别日志

        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """
        记录错误级别日志

        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        """
        记录严重错误级别日志

        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """
        记录异常信息

        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.logger.exception(msg, *args, **kwargs)


def setup_logger(
    name: str,
    log_dir: Optional[Union[str, Path]] = None,
    level: int = DEFAULT_LOG_LEVEL,
    format_str: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
) -> Logger:
    """
    设置日志器

    Args:
        name: 日志器名称
        log_dir: 日志目录路径
        level: 日志级别
        format_str: 日志格式
        date_format: 日期格式
        max_bytes: 单个日志文件最大大小
        backup_count: 备份文件数量

    Returns:
        Logger: 日志管理器实例
    """
    return Logger(
        name=name,
        log_dir=log_dir,
        level=level,
        format_str=format_str,
        date_format=date_format,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )


def get_logger(name: str) -> Logger:
    """
    获取日志器

    Args:
        name: 日志器名称

    Returns:
        Logger: 日志管理器实例
    """
    return Logger(name)


def set_log_level(level: int) -> None:
    """
    设置日志级别

    Args:
        level: 日志级别
    """
    logging.getLogger().setLevel(level)


def disable_logging() -> None:
    """禁用日志记录"""
    logging.disable(logging.CRITICAL)


def enable_logging() -> None:
    """启用日志记录"""
    logging.disable(logging.NOTSET) 