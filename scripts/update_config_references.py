#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置引用统一替换脚本
将项目中所有对src/config的直接引用统一替换为通过config_manager访问
"""
import os
import re
import glob
from pathlib import Path
from typing import List, Tuple, Dict

class ConfigReferenceUpdater:
    """配置引用更新器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.changes_made = []
        self.errors = []
        
        # 需要排除的目录
        self.exclude_dirs = {
            'venv', '__pycache__', '.git', 'node_modules', 
            'src/config', 'scripts'  # 排除config目录本身和scripts目录
        }
        
        # 替换规则
        self.replacement_rules = [
            # 旧的直接导入
            {
                'pattern': r'from src\.config\.jmeter_config import JMETER_CONFIG',
                'replacement': 'from src.config.config_manager import config_manager',
                'description': '替换jmeter_config直接导入'
            },
            {
                'pattern': r'from src\.config\.project_config import (.+)',
                'replacement': 'from src.config.config_manager import config_manager',
                'description': '替换project_config直接导入'
            },
            {
                'pattern': r'from src\.config import JMETER_CONFIG',
                'replacement': 'from src.config.config_manager import config_manager',
                'description': '替换统一导入JMETER_CONFIG'
            },
            # 直接访问src.config的
            {
                'pattern': r'src\.config\.jmeter_config\.JMETER_CONFIG',
                'replacement': 'config_manager.get_jmeter_config()',
                'description': '替换直接访问jmeter_config'
            },
            {
                'pattern': r'src\.config\.project_config\.(.+)',
                'replacement': 'config_manager.get_project_config()',
                'description': '替换直接访问project_config'
            }
        ]
        
        # JMETER_CONFIG使用替换规则
        self.jmeter_config_usage_rules = [
            {
                'pattern': r'JMETER_CONFIG\[(\'|\")test_config(\'|\")\]\[(\'|\")thread_counts(\'|\")\]',
                'replacement': 'config_manager.get_jmeter_config()[\'test\'][\'thread_counts\']',
                'description': '替换线程数配置访问'
            },
            {
                'pattern': r'JMETER_CONFIG\[(\'|\")test_config(\'|\")\]\[(\'|\")loop_counts(\'|\")\]',
                'replacement': 'config_manager.get_jmeter_config()[\'test\'][\'loop_counts\']',
                'description': '替换循环次数配置访问'
            },
            {
                'pattern': r'JMETER_CONFIG\[(\'|\")default_jmx(\'|\")\]',
                'replacement': 'config_manager.get_jmeter_config()[\'jmeter\'][\'default_jmx\']',
                'description': '替换默认JMX配置访问'
            },
            {
                'pattern': r'JMETER_CONFIG\[(\'|\")jmeter_bin(\'|\")\]',
                'replacement': 'config_manager.get_jmeter_config()[\'jmeter\'][\'jmeter_bin\']',
                'description': '替换JMeter路径配置访问'
            },
            {
                'pattern': r'JMETER_CONFIG\[(\'|\")default_test_name(\'|\")\]',
                'replacement': 'config_manager.get_jmeter_config()[\'jmeter\'][\'default_test_name\']',
                'description': '替换默认测试名称配置访问'
            },
            {
                'pattern': r'JMETER_CONFIG\[(\'|\")output_config(\'|\")\]\[(\'|\")base_dir(\'|\")\]',
                'replacement': 'config_manager.get_jmeter_config()[\'output\'][\'base_dir\']',
                'description': '替换输出目录配置访问'
            },
            {
                'pattern': r'JMETER_CONFIG\[(\'|\")language(\'|\")\]',
                'replacement': 'config_manager.get_jmeter_config()[\'jmeter\'][\'language\']',
                'description': '替换语言配置访问'
            },
            {
                'pattern': r'JMETER_CONFIG\[(\'|\")report_config(\'|\")\]',
                'replacement': 'config_manager.get_jmeter_config()[\'report\']',
                'description': '替换报告配置访问'
            }
        ]
    
    def find_python_files(self) -> List[Path]:
        """查找所有Python文件"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # 排除不需要的目录
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        return python_files
    
    def should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过某个文件"""
        # 跳过config目录本身
        if 'src/config' in str(file_path):
            return True
        
        # 跳过scripts目录
        if 'scripts' in str(file_path):
            return True
        
        # 跳过虚拟环境
        if 'venv' in str(file_path):
            return True
        
        return False
    
    def update_file(self, file_path: Path) -> bool:
        """更新单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_changed = False
            
            # 应用替换规则
            for rule in self.replacement_rules:
                if re.search(rule['pattern'], content):
                    content = re.sub(rule['pattern'], rule['replacement'], content)
                    file_changed = True
                    self.changes_made.append({
                        'file': str(file_path),
                        'rule': rule['description'],
                        'pattern': rule['pattern']
                    })
            
            # 如果文件有JMETER_CONFIG的使用，需要进一步替换
            if 'JMETER_CONFIG' in content and 'config_manager' in content:
                for rule in self.jmeter_config_usage_rules:
                    if re.search(rule['pattern'], content):
                        content = re.sub(rule['pattern'], rule['replacement'], content)
                        file_changed = True
                        self.changes_made.append({
                            'file': str(file_path),
                            'rule': rule['description'],
                            'pattern': rule['pattern']
                        })
            
            # 如果内容有变化，写回文件
            if file_changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已更新: {file_path}")
                return True
            
        except Exception as e:
            error_msg = f"处理文件 {file_path} 时出错: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
        
        return False
    
    def run(self) -> Dict:
        """执行更新"""
        print("🔍 开始查找Python文件...")
        python_files = self.find_python_files()
        
        print(f"📁 找到 {len(python_files)} 个Python文件")
        
        updated_files = 0
        skipped_files = 0
        
        for file_path in python_files:
            if self.should_skip_file(file_path):
                skipped_files += 1
                continue
            
            if self.update_file(file_path):
                updated_files += 1
        
        print(f"\n📊 更新完成:")
        print(f"   - 总文件数: {len(python_files)}")
        print(f"   - 跳过文件: {skipped_files}")
        print(f"   - 更新文件: {updated_files}")
        print(f"   - 变更次数: {len(self.changes_made)}")
        print(f"   - 错误数量: {len(self.errors)}")
        
        if self.changes_made:
            print(f"\n📝 详细变更:")
            for change in self.changes_made:
                print(f"   - {change['file']}: {change['rule']}")
        
        if self.errors:
            print(f"\n❌ 错误列表:")
            for error in self.errors:
                print(f"   - {error}")
        
        return {
            'total_files': len(python_files),
            'skipped_files': skipped_files,
            'updated_files': updated_files,
            'changes_made': len(self.changes_made),
            'errors': len(self.errors),
            'details': self.changes_made,
            'error_details': self.errors
        }

def main():
    """主函数"""
    print("🚀 配置引用统一替换脚本")
    print("=" * 50)
    
    # 创建更新器
    updater = ConfigReferenceUpdater()
    
    # 执行更新
    result = updater.run()
    
    print("\n" + "=" * 50)
    if result['errors'] == 0:
        print("🎉 所有文件更新成功！")
    else:
        print("⚠️  更新完成，但有一些错误，请检查上面的错误列表。")
    
    return result

if __name__ == '__main__':
    main() 