"""
配置管理模块
统一管理项目所有配置文件的加载和访问
"""
from pathlib import Path
import yaml
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器，统一管理所有配置文件"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self._config_cache: Dict[str, Any] = {}
    
    def load_yaml(self, name: str) -> dict:
        """加载YAML配置文件"""
        cache_key = f"yaml_{name}"
        if cache_key not in self._config_cache:
            config_path = self.config_dir / f"{name}.yaml"
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config_cache[cache_key] = yaml.safe_load(f)
                logger.info(f"成功加载YAML配置文件: {config_path}")
            except FileNotFoundError:
                logger.warning(f"配置文件不存在: {config_path}")
                self._config_cache[cache_key] = {}
            except Exception as e:
                logger.error(f"加载配置文件失败 {config_path}: {e}")
                self._config_cache[cache_key] = {}
        return self._config_cache[cache_key]
    
    def load_json(self, name: str) -> dict:
        """加载JSON配置文件"""
        cache_key = f"json_{name}"
        if cache_key not in self._config_cache:
            config_path = self.config_dir / f"{name}.json"
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._config_cache[cache_key] = json.load(f)
                logger.info(f"成功加载JSON配置文件: {config_path}")
            except FileNotFoundError:
                logger.warning(f"配置文件不存在: {config_path}")
                self._config_cache[cache_key] = {}
            except Exception as e:
                logger.error(f"加载配置文件失败 {config_path}: {e}")
                self._config_cache[cache_key] = {}
        return self._config_cache[cache_key]
    
    def load_config_from_subdir(self, subdir: str, name: str, file_type: str = "yaml") -> dict:
        """从子目录加载配置文件"""
        cache_key = f"{subdir}_{file_type}_{name}"
        if cache_key not in self._config_cache:
            config_path = self.config_dir / subdir / f"{name}.{file_type}"
            try:
                if file_type == "yaml":
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self._config_cache[cache_key] = yaml.safe_load(f)
                elif file_type == "json":
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self._config_cache[cache_key] = json.load(f)
                logger.info(f"成功加载配置文件: {config_path}")
            except FileNotFoundError:
                logger.warning(f"配置文件不存在: {config_path}")
                self._config_cache[cache_key] = {}
            except Exception as e:
                logger.error(f"加载配置文件失败 {config_path}: {e}")
                self._config_cache[cache_key] = {}
        return self._config_cache[cache_key]
    
    def clear_cache(self):
        """清除配置缓存"""
        self._config_cache.clear()
        logger.info("配置缓存已清除")


# 创建全局配置加载器实例
config = ConfigLoader()

# 便捷访问方法
def get_project_config() -> dict:
    """获取项目配置"""
    return config.load_config_from_subdir("core", "project", "yaml")

def get_jmeter_config() -> dict:
    """获取JMeter测试配置"""
    return config.load_config_from_subdir("test", "jmeter", "yaml")

def get_api_config() -> dict:
    """获取API配置"""
    return config.load_config_from_subdir("api", "endpoints", "yaml")

def get_logging_config() -> dict:
    """获取日志配置"""
    return config.load_config_from_subdir("core", "logging", "yaml")

def get_database_config() -> dict:
    """获取数据库配置"""
    return config.load_config_from_subdir("core", "database", "yaml")

def get_test_cases_config() -> dict:
    """获取测试用例配置"""
    return config.load_config_from_subdir("test", "cases", "yaml")

# 向后兼容的导入 - 使用配置管理器
try:
    from .config_manager import JMETER_CONFIG
except ImportError:
    # 如果config_manager.py不存在，使用默认配置
    JMETER_CONFIG = {
        'language': 'zh_CN',
        'jmeter_bin': 'D:/data/work/json/src/tools/jmeter/bin/jmeter.bat',
        'default_jmx': 'src/tools/jmeter/api_cases/heartbeat_test.jmx',
        'default_test_name': '接口性能测试',
        'report_config': {
            'title': '性能测试报告',
            'date_format': '%Y-%m-%d %H:%M:%S',
            'csv_encoding': 'utf-8',
        },
        'test_config': {
            'thread_counts': [100, 500, 1000, 1500],
            'loop_counts': [10, 100, 300, 500],
            'ramp_up_time': 1,
        },
        'output_config': {
            'base_dir': 'src/tools/jmeter/results',
            'report_dir': 'reports',
            'log_dir': 'logs',
        }
    }
    logger.warning("使用默认JMETER_CONFIG配置") 