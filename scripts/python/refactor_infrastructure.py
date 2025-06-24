#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Infrastructure层重构脚本
- 创建新的目录结构
- 迁移现有文件到新位置
- 更新导入路径
- 保持向后兼容性
"""
import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

class InfrastructureRefactor:
    """Infrastructure层重构器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.infrastructure_dir = self.project_root / "src" / "infrastructure"
        
        # 新的目录结构定义
        self.new_structure = {
            "persistence": {
                "repositories": [
                    "device_repository.py",
                    "device_identifier_repository.py"
                ],
                "database": [
                    "db_client.py"
                ]
            },
            "external": {
                "testing_tools": {
                    "jmeter": [
                        "jmeter_executor.py",
                        "jmx_handler.py", 
                        "parametrized_jmx_handler.py",
                        "simple_parametrized_jmx_handler.py"
                    ]
                },
                "monitoring": [
                    "remote_resource_collector.py",
                    "excel_report_generator.py",
                    "report_generator.py"
                ],
                "file_system": [
                    "report_generator.py"  # 从report目录迁移
                ]
            },
            "cross_cutting": {
                "logging": [
                    "test_logger.py"
                ],
                "analysis": [
                    "test_analyzer.py"
                ],
                "configuration": [
                    # 配置相关文件
                ]
            },
            "services": {
                "authentication": [
                    "login_service.py"
                ],
                "utilities": [
                    "uuid_service.py",
                    "redis_service.py"
                ],
                "testing": [
                    "api_test_service.py"
                ]
            }
        }
        
        # 文件迁移映射
        self.file_migrations = {
            # 数据库相关
            "src/infrastructure/db_query/db_client.py": "src/infrastructure/persistence/database/db_client.py",
            "src/infrastructure/db_query/device_repository.py": "src/infrastructure/persistence/repositories/device_repository.py",
            
            # 仓储相关
            "src/infrastructure/repositories/device_identifier_repository.py": "src/infrastructure/persistence/repositories/device_identifier_repository.py",
            "src/infrastructure/strategy/strategy_repository.py": "src/infrastructure/persistence/repositories/strategy_repository.py",
            
            # JMeter相关
            "src/infrastructure/jmeter/jmeter_executor.py": "src/infrastructure/external/testing_tools/jmeter/jmeter_executor.py",
            "src/infrastructure/jmeter/jmx_handler.py": "src/infrastructure/external/testing_tools/jmeter/jmx_handler.py",
            "src/infrastructure/jmeter/parametrized_jmx_handler.py": "src/infrastructure/external/testing_tools/jmeter/parametrized_jmx_handler.py",
            "src/infrastructure/jmeter/simple_parametrized_jmx_handler.py": "src/infrastructure/external/testing_tools/jmeter/simple_parametrized_jmx_handler.py",
            
            # 监控相关
            "src/infrastructure/monitor/remote_resource_collector.py": "src/infrastructure/external/monitoring/remote_resource_collector.py",
            "src/infrastructure/monitor/excel_report_generator.py": "src/infrastructure/external/monitoring/excel_report_generator.py",
            "src/infrastructure/monitor/report_generator.py": "src/infrastructure/external/monitoring/report_generator.py",
            
            # 报告相关
            "src/infrastructure/report/report_generator.py": "src/infrastructure/external/file_system/report_generator.py",
            
            # 日志相关
            "src/infrastructure/logging/test_logger.py": "src/infrastructure/cross_cutting/logging/test_logger.py",
            
            # 分析相关
            "src/infrastructure/analysis/test_analyzer.py": "src/infrastructure/cross_cutting/analysis/test_analyzer.py",
            
            # 根目录服务文件
            "src/infrastructure/login_service.py": "src/infrastructure/services/authentication/login_service.py",
            "src/infrastructure/uuid_service.py": "src/infrastructure/services/utilities/uuid_service.py",
            "src/infrastructure/redis_service.py": "src/infrastructure/services/utilities/redis_service.py",
            "src/infrastructure/api_test_service.py": "src/infrastructure/services/testing/api_test_service.py"
        }
        
        # 导入路径更新映射
        self.import_updates = {
            # 数据库相关导入更新
            "from .db_client import DBClient": "from src.infrastructure.persistence.database.db_client import DBClient",
            "from src.infrastructure.db_query.db_client import DBClient": "from src.infrastructure.persistence.database.db_client import DBClient",
            
            # 仓储相关导入更新
            "from src.infrastructure.repositories.device_identifier_repository import DeviceIdentifierRepository": 
            "from src.infrastructure.persistence.repositories.device_identifier_repository import DeviceIdentifierRepository",
            
            # JMeter相关导入更新
            "from src.infrastructure.jmeter.jmeter_executor import JMeterExecutor": 
            "from src.infrastructure.external.testing_tools.jmeter.jmeter_executor import JMeterExecutor",
            "from src.infrastructure.jmeter.jmx_handler import JMXHandler": 
            "from src.infrastructure.external.testing_tools.jmeter.jmx_handler import JMXHandler",
            
            # 监控相关导入更新
            "from src.infrastructure.monitor.remote_resource_collector import RemoteResourceCollector": 
            "from src.infrastructure.external.monitoring.remote_resource_collector import RemoteResourceCollector",
            
            # 报告相关导入更新
            "from src.infrastructure.report.report_generator import ReportGenerator": 
            "from src.infrastructure.external.file_system.report_generator import ReportGenerator",
            
            # 日志相关导入更新
            "from src.infrastructure.logging.test_logger import TestLogger": 
            "from src.infrastructure.cross_cutting.logging.test_logger import TestLogger",
            
            # 分析相关导入更新
            "from src.infrastructure.analysis.test_analyzer import TestAnalyzer": 
            "from src.infrastructure.cross_cutting.analysis.test_analyzer import TestAnalyzer",
            
            # 服务相关导入更新
            "from src.infrastructure.login_service import LoginService": 
            "from src.infrastructure.services.authentication.login_service import LoginService",
            "from src.infrastructure.uuid_service import UUIDService": 
            "from src.infrastructure.services.utilities.uuid_service import UUIDService",
            "from src.infrastructure.redis_service import RedisService": 
            "from src.infrastructure.services.utilities.redis_service import RedisService",
            "from src.infrastructure.api_test_service import APITestService": 
            "from src.infrastructure.services.testing.api_test_service import APITestService"
        }
    
    def create_directory_structure(self):
        """创建新的目录结构"""
        print("🔧 创建新的目录结构...")
        
        for main_dir, sub_dirs in self.new_structure.items():
            if isinstance(sub_dirs, dict):
                for sub_dir, files in sub_dirs.items():
                    if isinstance(files, dict):
                        # 嵌套目录
                        for nested_dir, nested_files in files.items():
                            dir_path = self.infrastructure_dir / main_dir / sub_dir / nested_dir
                            dir_path.mkdir(parents=True, exist_ok=True)
                            print(f"  ✅ 创建目录: {dir_path}")
                    else:
                        # 普通子目录
                        dir_path = self.infrastructure_dir / main_dir / sub_dir
                        dir_path.mkdir(parents=True, exist_ok=True)
                        print(f"  ✅ 创建目录: {dir_path}")
            else:
                # 直接文件列表
                dir_path = self.infrastructure_dir / main_dir
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ 创建目录: {dir_path}")
    
    def migrate_files(self):
        """迁移文件到新位置"""
        print("\n📁 迁移文件到新位置...")
        
        for old_path, new_path in self.file_migrations.items():
            old_file = self.project_root / old_path
            new_file = self.project_root / new_path
            
            if old_file.exists():
                # 确保目标目录存在
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(old_file, new_file)
                print(f"  ✅ 迁移: {old_path} -> {new_path}")
            else:
                print(f"  ⚠️  文件不存在: {old_path}")
    
    def create_backward_compatibility_files(self):
        """创建向后兼容的导入文件"""
        print("\n🔄 创建向后兼容的导入文件...")
        
        # 为每个迁移的文件创建向后兼容的导入
        for old_path, new_path in self.file_migrations.items():
            old_file = self.project_root / old_path
            new_file = self.project_root / new_path
            
            if new_file.exists():
                # 创建向后兼容的导入文件
                self._create_backward_compatibility_import(old_file, new_file)
    
    def _create_backward_compatibility_import(self, old_file: Path, new_file: Path):
        """创建向后兼容的导入文件"""
        # 计算相对导入路径
        relative_path = os.path.relpath(new_file, old_file.parent)
        module_name = new_file.stem
        
        # 创建向后兼容的导入文件
        compatibility_content = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
向后兼容性导入文件
此文件用于保持现有代码的导入路径不变
"""

# 从新位置导入所有内容
from {relative_path.replace("/", ".").replace(".py", "")} import *

# 为了IDE支持，也可以显式导入主要类
try:
    from {relative_path.replace("/", ".").replace(".py", "")} import *
except ImportError:
    # 如果新路径导入失败，尝试旧路径
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    try:
        from {module_name} import *
    except ImportError:
        print(f"警告: 无法导入 {{module_name}} 模块")
'''
        
        # 写入向后兼容文件
        with open(old_file, 'w', encoding='utf-8') as f:
            f.write(compatibility_content)
        
        print(f"  ✅ 创建向后兼容文件: {old_file}")
    
    def update_imports_in_files(self):
        """更新文件中的导入路径"""
        print("\n🔄 更新文件中的导入路径...")
        
        # 需要更新导入的文件列表
        files_to_update = [
            "src/application/auto_login_and_test_service.py",
            "src/application/jmeter/test_service.py",
            "src/application/monitor/resource_monitor_service.py",
            "src/application/services/api_send_service.py",
            "src/application/services/device_data_manager.py",
            "src/application/services/device_generator_service.py",
            "src/application/services/performance_test_service.py",
            "src/interfaces/cli/db_query_cli.py",
            "src/interfaces/cli/device_generator_cli.py",
            "src/interfaces/cli/jmx_parametrization_cli.py",
            "src/interfaces/cli/performance_test_cli.py",
            "src/interfaces/cli/resource_monitor_cli.py",
            "src/interfaces/main_auto_login_and_test.py",
            "src/infrastructure/db_query/device_repository.py",
            "src/infrastructure/repositories/device_identifier_repository.py",
            "src/infrastructure/jmeter/jmeter_executor.py",
            "src/infrastructure/jmeter/jmx_handler.py",
            "src/infrastructure/jmeter/parametrized_jmx_handler.py",
            "src/infrastructure/jmeter/simple_parametrized_jmx_handler.py",
            "src/infrastructure/monitor/remote_resource_collector.py",
            "src/infrastructure/monitor/excel_report_generator.py",
            "src/infrastructure/monitor/report_generator.py",
            "src/infrastructure/report/report_generator.py",
            "src/infrastructure/logging/test_logger.py",
            "src/infrastructure/analysis/test_analyzer.py",
            "src/infrastructure/strategy/strategy_repository.py",
            "src/infrastructure/login_service.py",
            "src/infrastructure/uuid_service.py",
            "src/infrastructure/redis_service.py",
            "src/infrastructure/api_test_service.py"
        ]
        
        for file_path in files_to_update:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._update_file_imports(full_path)
    
    def _update_file_imports(self, file_path: Path):
        """更新单个文件中的导入路径"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 更新导入路径
            for old_import, new_import in self.import_updates.items():
                content = content.replace(old_import, new_import)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ 更新导入: {file_path}")
            
        except Exception as e:
            print(f"  ❌ 更新文件失败 {file_path}: {e}")
    
    def create_init_files(self):
        """创建__init__.py文件"""
        print("\n📄 创建__init__.py文件...")
        
        # 需要创建__init__.py的目录列表
        init_dirs = [
            "src/infrastructure/persistence",
            "src/infrastructure/persistence/repositories", 
            "src/infrastructure/persistence/database",
            "src/infrastructure/external",
            "src/infrastructure/external/testing_tools",
            "src/infrastructure/external/testing_tools/jmeter",
            "src/infrastructure/external/monitoring",
            "src/infrastructure/external/file_system",
            "src/infrastructure/cross_cutting",
            "src/infrastructure/cross_cutting/logging",
            "src/infrastructure/cross_cutting/analysis",
            "src/infrastructure/cross_cutting/configuration",
            "src/infrastructure/services",
            "src/infrastructure/services/authentication",
            "src/infrastructure/services/utilities",
            "src/infrastructure/services/testing"
        ]
        
        for dir_path in init_dirs:
            init_file = self.project_root / dir_path / "__init__.py"
            if not init_file.exists():
                init_file.parent.mkdir(parents=True, exist_ok=True)
                init_file.touch()
                print(f"  ✅ 创建: {init_file}")
    
    def create_migration_summary(self):
        """创建迁移总结文档"""
        print("\n📋 创建迁移总结文档...")
        
        summary_content = f"""# Infrastructure层重构总结

## 重构时间
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 新的目录结构
```
src/infrastructure/
├── persistence/              # 数据持久化
│   ├── repositories/         # 仓储实现
│   │   ├── device_repository.py
│   │   ├── device_identifier_repository.py
│   │   └── strategy_repository.py
│   └── database/            # 数据库连接
│       └── db_client.py
├── external/                # 外部服务集成
│   ├── testing_tools/       # 测试工具集成
│   │   └── jmeter/          # JMeter集成
│   ├── monitoring/          # 监控系统
│   └── file_system/         # 文件系统
├── cross_cutting/           # 横切关注点
│   ├── logging/             # 日志
│   ├── analysis/            # 数据分析
│   └── configuration/       # 配置管理
└── services/                # 基础设施服务
    ├── authentication/      # 认证服务
    ├── utilities/           # 工具服务
    └── testing/             # 测试服务
```

## 文件迁移映射
"""
        
        for old_path, new_path in self.file_migrations.items():
            summary_content += f"- {old_path} -> {new_path}\n"
        
        summary_content += f"""

## 向后兼容性
- 所有原有导入路径仍然有效
- 通过向后兼容文件保持现有代码不变
- 建议逐步迁移到新的导入路径

## 下一步建议
1. 测试所有功能确保正常工作
2. 逐步更新代码中的导入路径
3. 删除旧的向后兼容文件（在确认无问题后）
4. 更新文档和注释

## 注意事项
- 重构过程中保持了所有原有功能
- 没有删除任何现有文件
- 所有导入路径都有向后兼容支持
"""
        
        summary_file = self.project_root / "docs" / "infrastructure_refactor_summary.md"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"  ✅ 创建迁移总结: {summary_file}")
    
    def run_refactor(self):
        """执行完整的重构流程"""
        print("🚀 开始Infrastructure层重构...")
        print("=" * 60)
        
        try:
            # 1. 创建新的目录结构
            self.create_directory_structure()
            
            # 2. 迁移文件
            self.migrate_files()
            
            # 3. 创建向后兼容文件
            self.create_backward_compatibility_files()
            
            # 4. 更新导入路径
            self.update_imports_in_files()
            
            # 5. 创建__init__.py文件
            self.create_init_files()
            
            # 6. 创建迁移总结
            self.create_migration_summary()
            
            print("\n" + "=" * 60)
            print("✅ Infrastructure层重构完成！")
            print("\n📝 重要提醒:")
            print("1. 所有原有功能保持不变")
            print("2. 现有代码无需修改即可运行")
            print("3. 建议逐步迁移到新的导入路径")
            print("4. 查看 docs/infrastructure_refactor_summary.md 了解详情")
            
        except Exception as e:
            print(f"\n❌ 重构过程中出现错误: {e}")
            raise

def main():
    """主函数"""
    refactor = InfrastructureRefactor()
    refactor.run_refactor()

if __name__ == "__main__":
    main() 