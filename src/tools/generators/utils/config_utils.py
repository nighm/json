from src.utils.parallel.decorators import parallel
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理工具模块
提供配置文件的读取、验证和更新功能
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("config_utils.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器类"""

    def __init__(self, config_path: Union[str, Path]):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> bool:
        """
        加载配置文件

        Returns:
            bool: 是否加载成功
        """
        if not self.config_path.exists():
            logger.error(f"配置文件不存在: {self.config_path}")
            return False

        try:
            if self.config_path.suffix == ".json":
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            elif self.config_path.suffix in (".yml", ".yaml"):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.error(f"不支持的配置文件格式: {self.config_path.suffix}")
                return False

            logger.info(f"加载配置文件: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return False

    def save_config(self) -> bool:
        """
        保存配置文件

        Returns:
            bool: 是否保存成功
        """
        try:
            if self.config_path.suffix == ".json":
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
            elif self.config_path.suffix in (".yml", ".yaml"):
                with open(self.config_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(self.config, f, allow_unicode=True)
            else:
                logger.error(f"不支持的配置文件格式: {self.config_path.suffix}")
                return False

            logger.info(f"保存配置文件: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            Any: 配置值
        """
        return self.config.get(key, default)

    def set_value(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
        logger.info(f"设置配置值: {key} = {value}")

    def delete_value(self, key: str) -> bool:
        """
        删除配置值

        Args:
            key: 配置键

        Returns:
            bool: 是否删除成功
        """
        if key in self.config:
            del self.config[key]
            logger.info(f"删除配置值: {key}")
            return True
        return False

    def validate_config(self, schema: Dict[str, Any]) -> bool:
        """
        验证配置是否符合模式

        Args:
            schema: 配置模式

        Returns:
            bool: 是否符合模式
        """
        try:
            for key, value_type in schema.items():
                if key not in self.config:
                    logger.error(f"缺少必需的配置项: {key}")
                    return False
                if not isinstance(self.config[key], value_type):
                    logger.error(f"配置项类型错误: {key}, 期望 {value_type}, 实际 {type(self.config[key])}")
                    return False
            return True
        except Exception as e:
            logger.error(f"验证配置失败: {e}")
            return False

    def merge_config(self, other_config: Dict[str, Any], overwrite: bool = False) -> None:
        """
        合并配置

        Args:
            other_config: 其他配置
            overwrite: 是否覆盖已存在的值
        """
        for key, value in other_config.items():
            if key not in self.config or overwrite:
                self.config[key] = value
                logger.info(f"合并配置: {key} = {value}")

    def get_all_config(self) -> Dict[str, Any]:
        """
        获取所有配置

        Returns:
            Dict[str, Any]: 所有配置
        """
        return self.config.copy()


def load_json_config(config_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    加载JSON配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        Optional[Dict[str, Any]]: 配置数据
    """
    config_path = Path(config_path)
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info(f"加载JSON配置文件: {config_path}")
        return config
    except Exception as e:
        logger.error(f"加载JSON配置文件失败: {e}")
        return None


def save_json_config(config_path: Union[str, Path], config: Dict[str, Any]) -> bool:
    """
    保存JSON配置文件

    Args:
        config_path: 配置文件路径
        config: 配置数据

    Returns:
        bool: 是否保存成功
    """
    config_path = Path(config_path)
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logger.info(f"保存JSON配置文件: {config_path}")
        return True
    except Exception as e:
        logger.error(f"保存JSON配置文件失败: {e}")
        return False


def load_yaml_config(config_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    加载YAML配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        Optional[Dict[str, Any]]: 配置数据
    """
    config_path = Path(config_path)
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logger.info(f"加载YAML配置文件: {config_path}")
        return config
    except Exception as e:
        logger.error(f"加载YAML配置文件失败: {e}")
        return None


def save_yaml_config(config_path: Union[str, Path], config: Dict[str, Any]) -> bool:
    """
    保存YAML配置文件

    Args:
        config_path: 配置文件路径
        config: 配置数据

    Returns:
        bool: 是否保存成功
    """
    config_path = Path(config_path)
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True)
        logger.info(f"保存YAML配置文件: {config_path}")
        return True
    except Exception as e:
        logger.error(f"保存YAML配置文件失败: {e}")
        return False 