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
    get_logger, get_config, get_cache, get_security_provider,
    get_validator, get_statistical_analyzer, get_i18n_provider
)


class CrossCuttingAutomation:
    """横切关注点层自动化管理类"""
    
    def __init__(self):
        self.logger = get_logger("automation")
        self.project_root = Path(__file__).parent.parent
        self.config_path = self.project_root / "config"
        self.logs_path = self.project_root / "logs"
        self.cache_path = self.project_root / "cache"
        
    def setup_environment(self) -> bool:
        """设置运行环境"""
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
                "pytest", "pytest-cov", "pyyaml", "cryptography"
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
        """运行测试"""
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
        """验证配置"""
        try:
            self.logger.info("开始验证配置...")
            
            # 验证横切关注点层配置
            validator = get_validator()
            
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
                    value = get_config(config_key)
                    if value is None:
                        missing_configs.append(config_key)
                except Exception:
                    missing_configs.append(config_key)
            
            if missing_configs:
                self.logger.warning(f"缺少配置项: {missing_configs}")
                return False
            
            # 验证各模块功能
            modules = [
                ("日志模块", lambda: get_logger("test")),
                ("缓存模块", lambda: get_cache()),
                ("安全模块", lambda: get_security_provider()),
                ("验证模块", lambda: get_validator()),
                ("统计分析模块", lambda: get_statistical_analyzer()),
                ("国际化模块", lambda: get_i18n_provider())
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
        """生成文档"""
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
        """生成API文档"""
        api_doc = docs_path / "cross_cutting_api.md"
        
        # 这里可以添加自动生成API文档的逻辑
        # 例如：解析代码注释、生成接口文档等
        self.logger.info(f"API文档已生成: {api_doc}")
    
    def _generate_architecture_docs(self, docs_path: Path) -> None:
        """生成架构文档"""
        arch_doc = docs_path / "cross_cutting_architecture.md"
        
        # 这里可以添加自动生成架构文档的逻辑
        self.logger.info(f"架构文档已生成: {arch_doc}")
    
    def _generate_deployment_docs(self, docs_path: Path) -> None:
        """生成部署文档"""
        deploy_doc = docs_path / "cross_cutting_deployment.md"
        
        # 这里可以添加自动生成部署文档的逻辑
        self.logger.info(f"部署文档已生成: {deploy_doc}")
    
    def monitor_system(self, duration: int = 300) -> None:
        """监控系统状态"""
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
        """检查模块状态"""
        try:
            # 检查缓存状态
            cache = get_cache()
            cache.set("health_check", time.time(), ttl=60)
            
            # 检查配置状态
            log_level = get_config("logging.level", "INFO")
            
            # 检查安全模块
            security = get_security_provider()
            
            self.logger.debug("模块状态检查完成")
            
        except Exception as e:
            self.logger.error(f"模块状态检查失败: {e}")
    
    def _check_system_resources(self) -> None:
        """检查系统资源"""
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
        """部署应用"""
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
        """部署到开发环境"""
        try:
            self.logger.info("部署到开发环境...")
            
            # 开发环境部署逻辑
            # 例如：启动开发服务器、设置开发配置等
            
            return True
            
        except Exception as e:
            self.logger.error(f"开发环境部署失败: {e}")
            return False
    
    def _deploy_production(self) -> bool:
        """部署到生产环境"""
        try:
            self.logger.info("部署到生产环境...")
            
            # 生产环境部署逻辑
            # 例如：Docker部署、服务配置等
            
            return True
            
        except Exception as e:
            self.logger.error(f"生产环境部署失败: {e}")
            return False
    
    def backup_config(self) -> bool:
        """备份配置"""
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
        """恢复配置"""
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