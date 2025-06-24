#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复Infrastructure层结构脚本
- 清理旧的目录结构
- 确保所有文件都在正确的新位置
- 删除重复文件
- 验证新结构完整性
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

class InfrastructureStructureFixer:
    """Infrastructure层结构修复器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.infrastructure_dir = self.project_root / "src" / "infrastructure"
        
        # 需要删除的旧目录
        self.old_directories = [
            "src/infrastructure/repositories",
            "src/infrastructure/jmeter", 
            "src/infrastructure/db_query",
            "src/infrastructure/monitor",
            "src/infrastructure/strategy",
            "src/infrastructure/report",
            "src/infrastructure/logging",
            "src/infrastructure/analysis"
        ]
        
        # 需要迁移的根目录服务文件
        self.root_service_files = [
            "src/infrastructure/api_test_service.py",
            "src/infrastructure/redis_service.py", 
            "src/infrastructure/uuid_service.py",
            "src/infrastructure/login_service.py"
        ]
        
        # 文件迁移映射
        self.file_migrations = {
            "src/infrastructure/api_test_service.py": "src/infrastructure/services/testing/api_test_service.py",
            "src/infrastructure/redis_service.py": "src/infrastructure/services/utilities/redis_service.py",
            "src/infrastructure/uuid_service.py": "src/infrastructure/services/utilities/uuid_service.py",
            "src/infrastructure/login_service.py": "src/infrastructure/services/authentication/login_service.py"
        }
    
    def check_new_structure(self):
        """检查新目录结构是否完整"""
        print("🔍 检查新目录结构...")
        
        expected_dirs = [
            "src/infrastructure/persistence/repositories",
            "src/infrastructure/persistence/database", 
            "src/infrastructure/external/testing_tools/jmeter",
            "src/infrastructure/external/monitoring",
            "src/infrastructure/external/file_system",
            "src/infrastructure/cross_cutting/logging",
            "src/infrastructure/cross_cutting/analysis",
            "src/infrastructure/cross_cutting/configuration",
            "src/infrastructure/services/authentication",
            "src/infrastructure/services/utilities",
            "src/infrastructure/services/testing"
        ]
        
        missing_dirs = []
        for dir_path in expected_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
                print(f"  ❌ 缺失目录: {dir_path}")
            else:
                print(f"  ✅ 目录存在: {dir_path}")
        
        return len(missing_dirs) == 0
    
    def migrate_root_service_files(self):
        """迁移根目录的服务文件"""
        print("\n📁 迁移根目录服务文件...")
        
        for old_path, new_path in self.file_migrations.items():
            old_file = self.project_root / old_path
            new_file = self.project_root / new_path
            
            if old_file.exists():
                # 确保目标目录存在
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 如果目标文件不存在，则迁移
                if not new_file.exists():
                    shutil.copy2(old_file, new_file)
                    print(f"  ✅ 迁移: {old_path} -> {new_path}")
                else:
                    print(f"  ⚠️  目标文件已存在: {new_path}")
            else:
                print(f"  ⚠️  源文件不存在: {old_path}")
    
    def remove_old_directories(self):
        """删除旧的目录结构"""
        print("\n🗑️  删除旧目录结构...")
        
        for dir_path in self.old_directories:
            full_path = self.project_root / dir_path
            if full_path.exists():
                try:
                    shutil.rmtree(full_path)
                    print(f"  ✅ 删除旧目录: {dir_path}")
                except Exception as e:
                    print(f"  ❌ 删除失败 {dir_path}: {e}")
            else:
                print(f"  ⚠️  目录不存在: {dir_path}")
    
    def remove_root_service_files(self):
        """删除根目录的服务文件（已迁移）"""
        print("\n🗑️  删除根目录服务文件...")
        
        for file_path in self.root_service_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    full_path.unlink()
                    print(f"  ✅ 删除文件: {file_path}")
                except Exception as e:
                    print(f"  ❌ 删除失败 {file_path}: {e}")
            else:
                print(f"  ⚠️  文件不存在: {file_path}")
    
    def verify_file_locations(self):
        """验证文件位置是否正确"""
        print("\n🔍 验证文件位置...")
        
        expected_files = {
            # 数据库相关
            "src/infrastructure/persistence/database/db_client.py": "数据库客户端",
            "src/infrastructure/persistence/repositories/device_repository.py": "设备仓储",
            "src/infrastructure/persistence/repositories/device_identifier_repository.py": "设备标识符仓储",
            "src/infrastructure/persistence/repositories/strategy_repository.py": "策略仓储",
            
            # JMeter相关
            "src/infrastructure/external/testing_tools/jmeter/jmeter_executor.py": "JMeter执行器",
            "src/infrastructure/external/testing_tools/jmeter/jmx_handler.py": "JMX处理器",
            "src/infrastructure/external/testing_tools/jmeter/parametrized_jmx_handler.py": "参数化JMX处理器",
            "src/infrastructure/external/testing_tools/jmeter/simple_parametrized_jmx_handler.py": "简化JMX处理器",
            
            # 监控相关
            "src/infrastructure/external/monitoring/remote_resource_collector.py": "远程资源收集器",
            "src/infrastructure/external/monitoring/excel_report_generator.py": "Excel报告生成器",
            "src/infrastructure/external/monitoring/report_generator.py": "监控报告生成器",
            
            # 文件系统相关
            "src/infrastructure/external/file_system/report_generator.py": "文件系统报告生成器",
            
            # 日志相关
            "src/infrastructure/cross_cutting/logging/test_logger.py": "测试日志",
            
            # 分析相关
            "src/infrastructure/cross_cutting/analysis/test_analyzer.py": "测试分析器",
            
            # 服务相关
            "src/infrastructure/services/authentication/login_service.py": "登录服务",
            "src/infrastructure/services/utilities/uuid_service.py": "UUID服务",
            "src/infrastructure/services/utilities/redis_service.py": "Redis服务",
            "src/infrastructure/services/testing/api_test_service.py": "API测试服务"
        }
        
        missing_files = []
        for file_path, description in expected_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {description}: {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  ❌ 缺失文件: {file_path} ({description})")
        
        return len(missing_files) == 0
    
    def test_imports(self):
        """测试关键模块的导入"""
        print("\n🧪 测试关键模块导入...")
        
        test_imports = [
            ("src.infrastructure.external.testing_tools.jmeter.jmeter_executor", "JMeterExecutor"),
            ("src.infrastructure.persistence.repositories.device_identifier_repository", "DeviceIdentifierRepository"),
            ("src.infrastructure.services.utilities.uuid_service", "UUIDService"),
            ("src.infrastructure.cross_cutting.logging.test_logger", "TestLogger")
        ]
        
        import sys
        import importlib
        
        failed_imports = []
        for module_path, class_name in test_imports:
            try:
                module = importlib.import_module(module_path)
                class_obj = getattr(module, class_name)
                print(f"  ✅ 导入成功: {module_path}.{class_name}")
            except Exception as e:
                failed_imports.append(f"{module_path}.{class_name}")
                print(f"  ❌ 导入失败: {module_path}.{class_name} - {e}")
        
        return len(failed_imports) == 0
    
    def create_structure_summary(self):
        """创建结构总结文档"""
        print("\n📋 创建结构总结文档...")
        
        summary_content = f"""# Infrastructure层结构修复总结

## 修复时间
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 最终目录结构
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
│   │       ├── jmeter_executor.py
│   │       ├── jmx_handler.py
│   │       ├── parametrized_jmx_handler.py
│   │       └── simple_parametrized_jmx_handler.py
│   ├── monitoring/          # 监控系统
│   │   ├── remote_resource_collector.py
│   │   ├── excel_report_generator.py
│   │   └── report_generator.py
│   └── file_system/         # 文件系统
│       └── report_generator.py
├── cross_cutting/           # 横切关注点
│   ├── logging/             # 日志
│   │   └── test_logger.py
│   ├── analysis/            # 数据分析
│   │   └── test_analyzer.py
│   └── configuration/       # 配置管理（预留）
└── services/                # 基础设施服务
    ├── authentication/      # 认证服务
    │   └── login_service.py
    ├── utilities/           # 工具服务
    │   ├── uuid_service.py
    │   └── redis_service.py
    └── testing/             # 测试服务
        └── api_test_service.py
```

## 修复内容
1. ✅ 清理了旧的目录结构
2. ✅ 迁移了根目录服务文件
3. ✅ 验证了新目录结构完整性
4. ✅ 测试了关键模块导入

## 架构特点
- **清晰的职责分离**：按功能领域组织代码
- **统一的接口设计**：每个模块都有明确的对外接口
- **良好的依赖管理**：避免循环依赖，支持依赖注入
- **易于扩展维护**：新功能可以轻松集成到对应模块

## 使用建议
1. 新功能开发时，请按照新的目录结构组织代码
2. 导入时优先使用新的模块路径
3. 定期清理不再使用的向后兼容文件
"""
        
        summary_file = self.project_root / "docs" / "infrastructure_structure_fix_summary.md"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"  ✅ 创建结构总结: {summary_file}")
    
    def run_fix(self):
        """执行完整的修复流程"""
        print("🔧 开始修复Infrastructure层结构...")
        print("=" * 60)
        
        try:
            # 1. 检查新目录结构
            if not self.check_new_structure():
                print("❌ 新目录结构不完整，请先运行重构脚本")
                return False
            
            # 2. 迁移根目录服务文件
            self.migrate_root_service_files()
            
            # 3. 删除旧目录结构
            self.remove_old_directories()
            
            # 4. 删除根目录服务文件
            self.remove_root_service_files()
            
            # 5. 验证文件位置
            if not self.verify_file_locations():
                print("❌ 文件位置验证失败")
                return False
            
            # 6. 测试导入
            if not self.test_imports():
                print("❌ 导入测试失败")
                return False
            
            # 7. 创建结构总结
            self.create_structure_summary()
            
            print("\n" + "=" * 60)
            print("✅ Infrastructure层结构修复完成！")
            print("\n📝 重要提醒:")
            print("1. 旧目录结构已清理")
            print("2. 所有文件都在正确的新位置")
            print("3. 导入测试通过")
            print("4. 查看 docs/infrastructure_structure_fix_summary.md 了解详情")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 修复过程中出现错误: {e}")
            return False

def main():
    """主函数"""
    fixer = InfrastructureStructureFixer()
    success = fixer.run_fix()
    
    if success:
        print("\n🎉 修复成功！Infrastructure层结构现在完全合理。")
    else:
        print("\n💥 修复失败！请检查错误信息并手动处理。")

if __name__ == "__main__":
    main() 