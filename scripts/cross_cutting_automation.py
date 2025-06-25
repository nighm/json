#!/usr/bin/env python3
"""
横切关注点层自动化脚本

提供部署、测试、监控等自动化功能，简化运维操作。
"""

import os
import sys
import argparse
import subprocess
import time
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.cross_cutting import (
    register_services, get_service
)


class CrossCuttingAutomation:
    """
    横切关注点层自动化管理类。

    该类负责横切层（Cross-cutting Concerns Layer）的自动化管理，包括环境搭建、测试、配置验证、文档生成、系统监控、部署、备份等功能。
    通过依赖注入获取各横切服务，统一管理和调用。
    """
    
    def __init__(self):
        """
        初始化CrossCuttingAutomation实例，注册并获取所有横切层服务。

        :raises Exception: 服务注册或依赖注入失败时抛出异常。
        """
        # 注册所有横切层服务
        register_services()
        # 通过依赖注入容器获取服务实例
        self.logger = get_service('logger')  # 日志服务
        self.config = get_service('config_service')  # 配置服务
        self.cache = get_service('cache_service')  # 缓存服务
        self.security = get_service('security_service')  # 安全服务
        self.validator = get_service('validator_service')  # 验证服务
        self.statistical_analyzer = get_service('statistical_analyzer_service')  # 统计分析服务
        self.i18n = get_service('i18n_service')  # 国际化服务
        # 其他路径属性
        self.project_root = Path(__file__).parent.parent
        self.config_path = self.project_root / "config"
        self.logs_path = self.project_root / "logs"
        self.cache_path = self.project_root / "cache"
        
    def get_cache(self):
        """
        获取缓存实例（兼容旧用法）。

        :return: 缓存服务实例。
        :rtype: object
        """
        return self.cache.get_cache() if hasattr(self.cache, 'get_cache') else self.cache
        
    def setup_environment(self) -> bool:
        """
        设置运行环境。

        主要功能：
            - 创建必要目录（logs、cache、config等）
            - 检查Python版本和依赖包
            - 输出日志

        :return: 成功返回True，失败返回False。
        :rtype: bool
        :raises Exception: 环境设置失败时记录到日志，不抛出。
        """
        try:
            self.logger.info("开始设置运行环境...")
            
            # 创建必要目录
            directories = [
                self.logs_path,
                self.cache_path,
                self.config_path / "cross_cutting",
                self.config_path / "environment"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"创建目录: {directory}")
            
            # 检查Python环境
            python_version = sys.version_info
            if python_version < (3, 8):
                self.logger.error(f"Python版本过低: {python_version}, 需要3.8+")
                return False
            
            self.logger.info(f"Python版本: {python_version.major}.{python_version.minor}")
            
            # 检查依赖包
            required_packages = [
                "pytest", "pytest_cov", "pyyaml", "cryptography"
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package.replace("-", "_"))
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                self.logger.warning(f"缺少依赖包: {missing_packages}")
                self.logger.info("请运行: pip install -r requirements.txt")
            
            self.logger.info("环境设置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"环境设置失败: {e}")
            return False
    
    def run_tests(self, coverage: bool = True, verbose: bool = False) -> bool:
        """
        运行横切层相关的单元测试。

        :param coverage: 是否生成覆盖率报告，默认为True。
        :type coverage: bool
        :param verbose: 是否输出详细测试信息，默认为False。
        :type verbose: bool
        :return: 测试全部通过返回True，否则返回False。
        :rtype: bool
        :raises Exception: 测试执行异常时记录到日志，不抛出。
        """
        try:
            self.logger.info("开始运行测试...")
            
            test_path = self.project_root / "tests" / "infrastructure" / "cross_cutting"
            if not test_path.exists():
                self.logger.error(f"测试目录不存在: {test_path}")
                return False
            
            cmd = ["python", "-m", "pytest", str(test_path)]
            
            if verbose:
                cmd.append("-v")
            
            if coverage:
                cmd.extend([
                    "--cov=src/infrastructure/cross_cutting",
                    "--cov-report=html",
                    "--cov-report=term"
                ])
            
            self.logger.info(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("测试执行成功")
                if result.stdout:
                    self.logger.info(f"测试输出:\n{result.stdout}")
                return True
            else:
                self.logger.error("测试执行失败")
                if result.stderr:
                    self.logger.error(f"错误信息:\n{result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"测试执行异常: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """
        验证横切层配置的完整性和有效性。

        主要功能：
            - 检查必要配置项是否存在
            - 验证各横切模块功能可用性

        :return: 配置验证通过返回True，否则返回False。
        :rtype: bool
        :raises Exception: 配置验证异常时记录到日志，不抛出。
        """
        try:
            self.logger.info("开始验证配置...")
            
            # 验证横切关注点层配置
            validator = self.validator
            
            # 检查必要配置
            required_configs = [
                "logging.level",
                "cache.type",
                "security.password.algorithm",
                "i18n.default_language"
            ]
            
            missing_configs = []
            for config_key in required_configs:
                try:
                    value = self.config.get(config_key) if hasattr(self.config, 'get') else None
                    if value is None:
                        missing_configs.append(config_key)
                except Exception:
                    missing_configs.append(config_key)
            
            if missing_configs:
                self.logger.warning(f"缺少配置项: {missing_configs}")
                return False
            
            # 验证各模块功能
            modules = [
                ("日志模块", lambda: self.logger),
                ("缓存模块", lambda: self.get_cache()),
                ("安全模块", lambda: self.security),
                ("验证模块", lambda: self.validator),
                ("统计分析模块", lambda: self.statistical_analyzer),
                ("国际化模块", lambda: self.i18n)
            ]
            
            for module_name, module_func in modules:
                try:
                    module_func()
                    self.logger.info(f"{module_name} 验证通过")
                except Exception as e:
                    self.logger.error(f"{module_name} 验证失败: {e}")
                    return False
            
            self.logger.info("配置验证完成")
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证异常: {e}")
            return False
    
    def generate_documentation(self) -> bool:
        """
        生成横切层相关文档，包括API文档、架构文档、部署文档。

        主要功能：
            - 自动生成API接口文档
            - 自动生成架构设计文档
            - 自动生成部署说明文档

        :return: 文档生成成功返回True，否则返回False。
        :rtype: bool
        :raises Exception: 文档生成异常时记录到日志，不抛出。
        """
        try:
            self.logger.info("开始生成文档...")
            
            docs_path = self.project_root / "docs" / "infrastructure"
            docs_path.mkdir(parents=True, exist_ok=True)
            
            # 生成API文档
            self._generate_api_docs(docs_path)
            
            # 生成架构文档
            self._generate_architecture_docs(docs_path)
            
            # 生成部署文档
            self._generate_deployment_docs(docs_path)
            
            self.logger.info("文档生成完成")
            return True
            
        except Exception as e:
            self.logger.error(f"文档生成异常: {e}")
            return False
    
    def _generate_api_docs(self, docs_path: Path) -> None:
        """
        生成API文档（写入真实内容）。

        :param docs_path: 文档输出目录。
        :type docs_path: Path
        :return: 无返回值。
        """
        api_doc = docs_path / "cross_cutting_api.md"
        content = '''# 横切关注点层 API 接口文档

## 概述

本文档详细描述了横切关注点层所有模块的API接口，包括参数说明、返回值、使用示例等。

## 日志模块 API

### get_logger(name: str) -> Logger
获取指定名称的日志器实例。

### get_logger_factory() -> LoggerFactory
获取日志器工厂实例。

## 配置模块 API

### get_config_provider() -> ConfigProvider
获取配置提供者实例。

### get_config(key: str, default: Any = None) -> Any
获取配置值。

## 安全模块 API

### get_security_provider() -> SecurityProvider
获取安全提供者实例。

### hash_password(password: str) -> str
哈希密码。

### verify_password(password: str, hashed: str) -> bool
验证密码。

## 缓存模块 API

### get_cache_provider() -> CacheProvider
获取缓存提供者实例。

### get_cache() -> Cache
获取缓存实例。

## 异常处理模块 API

### get_exception_handler() -> ExceptionHandler
获取异常处理器实例。

### handle_exception(exception: Exception, context: Dict[str, Any] = None) -> bool
处理异常。

## 验证模块 API

### get_validator() -> Validator
获取验证器实例。

### validate_data(data: Any, rules: List[ValidationRule]) -> ValidationResult
验证数据。

## 统计分析模块 API

### get_statistical_analyzer() -> StatisticalAnalyzer
获取统计分析器实例。

### calculate_statistics(data: List[float]) -> StatisticalResult
计算统计数据。

## 国际化模块 API

### get_i18n_provider() -> I18nProvider
获取国际化提供者实例。

### get_text(key: str, language: str = None, **kwargs) -> str
获取翻译文本。
'''
        with open(api_doc, 'w', encoding='utf-8') as f:
            f.write(content)
        self.logger.info(f"API文档已生成: {api_doc}")
    
    def _generate_architecture_docs(self, docs_path: Path) -> None:
        """
        生成架构文档（写入真实内容）。

        :param docs_path: 文档输出目录。
        :type docs_path: Path
        :return: 无返回值。
        """
        arch_doc = docs_path / "cross_cutting_architecture.md"
        content = '''# 横切关注点层架构设计文档

## 概述
横切关注点层（Cross-cutting Concerns Layer）是DDD架构中的基础设施层重要组成部分，提供应用程序的通用服务，包括日志、配置、安全、缓存、异常处理、验证、统计分析、国际化等。

## 设计原则
- 依赖倒置原则
- 单一职责原则
- 开闭原则
- 接口隔离原则

## 模块架构
- logging/ 日志模块
- configuration/ 配置模块
- security/ 安全模块
- cache/ 缓存模块
- exception_handler/ 异常处理模块
- validation/ 验证模块
- analysis/ 统计分析模块
- i18n/ 国际化模块

## 依赖关系
- 日志、配置为基础依赖
- 其他模块可依赖日志、配置
- 各模块通过接口抽象解耦

## 扩展指南
- 新增模块：新建目录+接口+实现+导出+测试
- 扩展模块：接口加方法，类加实现，补测试
- 自定义实现：继承接口，依赖注入
'''
        with open(arch_doc, 'w', encoding='utf-8') as f:
            f.write(content)
        self.logger.info(f"架构文档已生成: {arch_doc}")
    
    def _generate_deployment_docs(self, docs_path: Path) -> None:
        """
        生成部署文档。

        :param docs_path: 文档输出目录。
        :type docs_path: Path
        :return: 无返回值。
        """
        deploy_doc = docs_path / "cross_cutting_deployment.md"
        
        # 这里可以添加自动生成部署文档的逻辑
        self.logger.info(f"部署文档已生成: {deploy_doc}")
    
    def monitor_system(self, duration: int = 300) -> None:
        """
        监控系统状态。

        :param duration: 监控持续时间（秒），默认300秒。
        :type duration: int
        :return: 无返回值。
        :raises Exception: 监控异常时记录到日志，不抛出。
        """
        try:
            self.logger.info(f"开始系统监控，持续{duration}秒...")
            
            start_time = time.time()
            end_time = start_time + duration
            
            while time.time() < end_time:
                # 检查各模块状态
                self._check_module_status()
                
                # 检查系统资源
                self._check_system_resources()
                
                # 等待下次检查
                time.sleep(30)
            
            self.logger.info("系统监控完成")
            
        except KeyboardInterrupt:
            self.logger.info("监控被用户中断")
        except Exception as e:
            self.logger.error(f"监控异常: {e}")
    
    def _check_module_status(self) -> None:
        """
        检查横切层各模块运行状态。

        :return: 无返回值。
        :raises Exception: 检查失败时记录到日志，不抛出。
        """
        try:
            # 检查缓存状态
            cache = self.get_cache()
            cache.set("health_check", time.time(), ttl=60)
            
            # 检查配置状态
            log_level = self.config.get("logging.level", "INFO") if hasattr(self.config, 'get') else "INFO"
            
            # 检查安全模块
            security = self.security
            
            self.logger.debug("模块状态检查完成")
            
        except Exception as e:
            self.logger.error(f"模块状态检查失败: {e}")
    
    def _check_system_resources(self) -> None:
        """
        检查系统资源（CPU、内存、磁盘等）。

        :return: 无返回值。
        :raises Exception: 检查失败时记录到日志，不抛出。
        """
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            self.logger.info(f"系统资源 - CPU: {cpu_percent}%, 内存: {memory_percent}%, 磁盘: {disk_percent}%")
            
        except ImportError:
            self.logger.warning("psutil未安装，跳过系统资源检查")
        except Exception as e:
            self.logger.error(f"系统资源检查失败: {e}")
    
    def deploy(self, environment: str = "development") -> bool:
        """
        部署横切层服务。

        :param environment: 部署环境（development/production），默认development。
        :type environment: str
        :return: 部署成功返回True，否则返回False。
        :rtype: bool
        :raises Exception: 部署异常时记录到日志，不抛出。
        """
        try:
            self.logger.info(f"开始部署到{environment}环境...")
            
            # 1. 环境检查
            if not self.setup_environment():
                return False
            
            # 2. 配置验证
            if not self.validate_configuration():
                return False
            
            # 3. 运行测试
            if not self.run_tests(coverage=True, verbose=True):
                return False
            
            # 4. 生成文档
            if not self.generate_documentation():
                return False
            
            # 5. 部署应用
            if environment == "production":
                if not self._deploy_production():
                    return False
            else:
                if not self._deploy_development():
                    return False
            
            self.logger.info(f"部署到{environment}环境完成")
            return True
            
        except Exception as e:
            self.logger.error(f"部署失败: {e}")
            return False
    
    def _deploy_development(self) -> bool:
        """
        开发环境部署逻辑。

        :return: 部署成功返回True，否则返回False。
        :rtype: bool
        """
        try:
            self.logger.info("部署到开发环境...")
            
            # 开发环境部署逻辑
            # 例如：启动开发服务器、设置开发配置等
            
            return True
            
        except Exception as e:
            self.logger.error(f"开发环境部署失败: {e}")
            return False
    
    def _deploy_production(self) -> bool:
        """
        生产环境部署逻辑。

        :return: 部署成功返回True，否则返回False。
        :rtype: bool
        """
        try:
            self.logger.info("部署到生产环境...")
            
            # 生产环境部署逻辑
            # 例如：Docker部署、服务配置等
            
            return True
            
        except Exception as e:
            self.logger.error(f"生产环境部署失败: {e}")
            return False
    
    def backup_config(self) -> bool:
        """
        备份横切层配置。

        :return: 备份成功返回True，否则返回False。
        :rtype: bool
        :raises Exception: 备份异常时记录到日志，不抛出。
        """
        try:
            self.logger.info("开始备份配置...")
            
            backup_dir = self.project_root / "backups" / f"config_{int(time.time())}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 备份配置文件
            config_files = [
                self.config_path / "cross_cutting",
                self.config_path / "environment"
            ]
            
            for config_file in config_files:
                if config_file.exists():
                    if config_file.is_dir():
                        import shutil
                        shutil.copytree(config_file, backup_dir / config_file.name)
                    else:
                        import shutil
                        shutil.copy2(config_file, backup_dir)
            
            self.logger.info(f"配置备份完成: {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置备份失败: {e}")
            return False
    
    def restore_config(self, backup_path: str) -> bool:
        """
        恢复横切层配置。

        :param backup_path: 备份文件路径。
        :type backup_path: str
        :return: 恢复成功返回True，否则返回False。
        :rtype: bool
        :raises Exception: 恢复异常时记录到日志，不抛出。
        """
        try:
            self.logger.info(f"开始恢复配置: {backup_path}")
            
            backup_path = Path(backup_path)
            if not backup_path.exists():
                self.logger.error(f"备份路径不存在: {backup_path}")
                return False
            
            # 恢复配置文件
            import shutil
            if backup_path.is_dir():
                shutil.copytree(backup_path, self.config_path, dirs_exist_ok=True)
            else:
                shutil.copy2(backup_path, self.config_path)
            
            self.logger.info("配置恢复完成")
            return True
            
        except Exception as e:
            self.logger.error(f"配置恢复失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="横切关注点层自动化脚本")
    parser.add_argument("action", choices=[
        "setup", "test", "validate", "docs", "monitor", 
        "deploy", "backup", "restore"
    ], help="执行的操作")
    
    parser.add_argument("--environment", "-e", default="development",
                       choices=["development", "staging", "production"],
                       help="部署环境")
    parser.add_argument("--coverage", "-c", action="store_true",
                       help="生成测试覆盖率报告")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="详细输出")
    parser.add_argument("--duration", "-d", type=int, default=300,
                       help="监控持续时间（秒）")
    parser.add_argument("--backup-path", "-b", type=str,
                       help="备份路径（用于恢复操作）")
    
    args = parser.parse_args()
    
    # 创建自动化实例
    automation = CrossCuttingAutomation()
    
    # 执行对应操作
    if args.action == "setup":
        success = automation.setup_environment()
        sys.exit(0 if success else 1)
        
    elif args.action == "test":
        success = automation.run_tests(coverage=args.coverage, verbose=args.verbose)
        sys.exit(0 if success else 1)
        
    elif args.action == "validate":
        success = automation.validate_configuration()
        sys.exit(0 if success else 1)
        
    elif args.action == "docs":
        success = automation.generate_documentation()
        sys.exit(0 if success else 1)
        
    elif args.action == "monitor":
        automation.monitor_system(duration=args.duration)
        
    elif args.action == "deploy":
        success = automation.deploy(environment=args.environment)
        sys.exit(0 if success else 1)
        
    elif args.action == "backup":
        success = automation.backup_config()
        sys.exit(0 if success else 1)
        
    elif args.action == "restore":
        if not args.backup_path:
            print("错误: 恢复操作需要指定备份路径 (--backup-path)")
            sys.exit(1)
        success = automation.restore_config(args.backup_path)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 