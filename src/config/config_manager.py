"""
配置管理器
统一管理项目所有配置的加载、验证和访问
"""
from pathlib import Path
import yaml
from typing import Dict, Any, Optional
import logging
from . import config

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器，提供统一的配置访问接口"""
    
    def __init__(self):
        self._config_cache: Dict[str, Any] = {}
    
    def get_project_config(self) -> dict:
        """获取项目核心配置"""
        return config.load_config_from_subdir("core", "project", "yaml")
    
    def get_jmeter_config(self) -> dict:
        """获取JMeter测试配置"""
        return config.load_config_from_subdir("test", "jmeter", "yaml")
    
    def get_api_config(self) -> dict:
        """获取API配置"""
        return config.load_config_from_subdir("api", "endpoints", "yaml")
    
    def get_logging_config(self) -> dict:
        """获取日志配置"""
        return config.load_config_from_subdir("core", "logging", "yaml")
    
    def get_database_config(self) -> dict:
        """获取数据库配置"""
        return config.load_config_from_subdir("core", "database", "yaml")
    
    def get_test_cases_config(self) -> dict:
        """获取测试用例配置"""
        return config.load_config_from_subdir("test", "cases", "yaml")
    
    def get_email_config(self) -> dict:
        """获取邮件配置（示例：新增配置）"""
        return config.load_config_from_subdir("core", "email", "yaml")
    
    def get_monitor_config(self) -> dict:
        """获取监控配置（示例：新增配置）"""
        return config.load_config_from_subdir("core", "monitor", "yaml")
    
    def get_all_configs(self) -> dict:
        """获取所有配置"""
        return {
            "project": self.get_project_config(),
            "jmeter": self.get_jmeter_config(),
            "api": self.get_api_config(),
            "logging": self.get_logging_config(),
            "database": self.get_database_config(),
            "test_cases": self.get_test_cases_config(),
            "email": self.get_email_config(),
            "monitor": self.get_monitor_config()
        }
    
    def validate_configs(self) -> bool:
        """验证所有配置的有效性"""
        try:
            configs = self.get_all_configs()
            # 这里可以添加具体的验证逻辑
            logger.info("所有配置验证通过")
            return True
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False
    
    def reload_configs(self):
        """重新加载所有配置"""
        config.clear_cache()
        self._config_cache.clear()
        logger.info("配置已重新加载")
    
    def get_jmeter_language(self) -> str:
        """获取JMeter语言设置"""
        return self.get_jmeter_config().get('jmeter', {}).get('language', 'zh_CN')
    
    def get_jmeter_bin_path(self) -> str:
        """获取JMeter可执行文件路径"""
        return self.get_jmeter_config().get('jmeter', {}).get('jmeter_bin', '')
    
    def get_server_url(self) -> str:
        """获取服务器URL"""
        return self.get_project_config().get('server', {}).get('url', '')
    
    def get_redis_config(self) -> dict:
        """获取Redis配置"""
        return self.get_database_config().get('redis', {})


# 创建全局配置管理器实例
config_manager = ConfigManager()

# 向后兼容的配置访问
def get_jmeter_config_dict() -> dict:
    """获取JMeter配置字典（向后兼容）"""
    jmeter_config = config_manager.get_jmeter_config()
    
    # 转换为旧格式以保持兼容性
    return {
        'language': jmeter_config.get('jmeter', {}).get('language', 'zh_CN'),
        'jmeter_bin': jmeter_config.get('jmeter', {}).get('jmeter_bin', 'D:/data/work/json/src/tools/jmeter/bin/jmeter.bat'),
        'default_jmx': jmeter_config.get('jmeter', {}).get('default_jmx', 'src/tools/jmeter/api_cases/heartbeat_test.jmx'),
        'default_test_name': jmeter_config.get('jmeter', {}).get('default_test_name', '接口性能测试'),
        'report_config': {
            'title': jmeter_config.get('report', {}).get('title', '性能测试报告'),
            'date_format': jmeter_config.get('report', {}).get('date_format', '%Y-%m-%d %H:%M:%S'),
            'csv_encoding': jmeter_config.get('report', {}).get('csv_encoding', 'utf-8'),
        },
        'test_config': {
            'thread_counts': jmeter_config.get('test', {}).get('thread_counts', [100, 500, 1000, 1500]),
            'loop_counts': jmeter_config.get('test', {}).get('loop_counts', [10, 100, 300, 500]),
            'ramp_up_time': jmeter_config.get('test', {}).get('ramp_up_time', 1),
        },
        'output_config': {
            'base_dir': jmeter_config.get('output', {}).get('base_dir', 'src/tools/jmeter/results'),
            'report_dir': jmeter_config.get('output', {}).get('report_dir', 'reports'),
            'log_dir': jmeter_config.get('output', {}).get('log_dir', 'logs'),
        }
    }


# 导出向后兼容的配置
JMETER_CONFIG = get_jmeter_config_dict()

def get_jmeter_language() -> str:
    """获取JMeter语言设置"""
    return config_manager.get_jmeter_language()

def get_jmeter_bin_path() -> str:
    """获取JMeter可执行文件路径"""
    return config_manager.get_jmeter_bin_path()

def get_server_url() -> str:
    """获取服务器URL"""
    return config_manager.get_server_url()

def get_redis_config() -> dict:
    """获取Redis配置"""
    return config_manager.get_redis_config() 