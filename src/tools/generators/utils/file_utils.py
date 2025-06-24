#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件操作工具模块
提供文件操作相关的通用功能
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("file_utils.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def ensure_directory(directory: Union[str, Path]) -> None:
    """
    确保目录存在，如果不存在则创建

    Args:
        directory: 目录路径
    """
    directory = Path(directory)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建目录: {directory}")


def copy_file(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> bool:
    """
    复制文件

    Args:
        src: 源文件路径
        dst: 目标文件路径
        overwrite: 是否覆盖已存在的文件

    Returns:
        bool: 是否复制成功
    """
    src = Path(src)
    dst = Path(dst)

    if not src.exists():
        logger.error(f"源文件不存在: {src}")
        return False

    if dst.exists() and not overwrite:
        logger.warning(f"目标文件已存在: {dst}")
        return False

    try:
        shutil.copy2(src, dst)
        logger.info(f"复制文件: {src} -> {dst}")
        return True
    except Exception as e:
        logger.error(f"复制文件失败: {e}")
        return False


def move_file(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> bool:
    """
    移动文件

    Args:
        src: 源文件路径
        dst: 目标文件路径
        overwrite: 是否覆盖已存在的文件

    Returns:
        bool: 是否移动成功
    """
    src = Path(src)
    dst = Path(dst)

    if not src.exists():
        logger.error(f"源文件不存在: {src}")
        return False

    if dst.exists() and not overwrite:
        logger.warning(f"目标文件已存在: {dst}")
        return False

    try:
        shutil.move(src, dst)
        logger.info(f"移动文件: {src} -> {dst}")
        return True
    except Exception as e:
        logger.error(f"移动文件失败: {e}")
        return False


def delete_file(file_path: Union[str, Path]) -> bool:
    """
    删除文件

    Args:
        file_path: 文件路径

    Returns:
        bool: 是否删除成功
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"文件不存在: {file_path}")
        return False

    try:
        file_path.unlink()
        logger.info(f"删除文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"删除文件失败: {e}")
        return False


def get_files(directory: Union[str, Path], pattern: str = "*.py") -> List[Path]:
    """
    获取目录中的所有文件

    Args:
        directory: 目录路径
        pattern: 文件匹配模式

    Returns:
        List[Path]: 文件路径列表
    """
    directory = Path(directory)
    if not directory.exists():
        logger.error(f"目录不存在: {directory}")
        return []

    try:
        files = list(directory.glob(pattern))
        logger.info(f"在 {directory} 中找到 {len(files)} 个文件")
        return files
    except Exception as e:
        logger.error(f"获取文件列表失败: {e}")
        return []


def read_file(file_path: Union[str, Path], encoding: str = "utf-8") -> Optional[str]:
    """
    读取文件内容

    Args:
        file_path: 文件路径
        encoding: 文件编码

    Returns:
        Optional[str]: 文件内容
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return None

    try:
        content = file_path.read_text(encoding=encoding)
        logger.info(f"读取文件: {file_path}")
        return content
    except Exception as e:
        logger.error(f"读取文件失败: {e}")
        return None


def write_file(file_path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
    """
    写入文件内容

    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码

    Returns:
        bool: 是否写入成功
    """
    file_path = Path(file_path)

    try:
        file_path.write_text(content, encoding=encoding)
        logger.info(f"写入文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"写入文件失败: {e}")
        return False


def create_backup(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Optional[Path]:
    """
    创建文件备份

    Args:
        file_path: 文件路径
        backup_dir: 备份目录路径

    Returns:
        Optional[Path]: 备份文件路径
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return None

    if backup_dir is None:
        backup_dir = file_path.parent / "backup"
    else:
        backup_dir = Path(backup_dir)

    ensure_directory(backup_dir)

    backup_path = backup_dir / f"{file_path.name}.bak"
    if copy_file(file_path, backup_path, overwrite=True):
        logger.info(f"创建备份: {backup_path}")
        return backup_path
    return None 