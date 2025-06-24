#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目结构脑图生成器 - XMind版本
自动化扫描项目目录结构，生成XMind格式的思维导图文件

功能特性：
1. 递归扫描项目目录，自动生成结构化的思维导图
2. 智能排除依赖、缓存、虚拟环境等无关目录
3. 支持生成简化版和详细版两种脑图
4. 输出XMind格式文件，可直接在XMind中打开美化和导出

作者：AI Assistant
创建时间：2025-01-27
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import List, Dict, Set, Optional
from datetime import datetime
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import xmind
except ImportError:
    print("正在安装xmind-sdk-python...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "xmind-sdk-python"])
    import xmind

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mindmap_generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class XMindMindmapGenerator:
    """XMind思维导图生成器"""
    
    def __init__(self, project_root: Path):
        """
        初始化思维导图生成器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.output_dir = project_root / "docs" / "development"
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 定义排除的目录和文件模式
        self.exclude_dirs = {
            '__pycache__', '.git', '.vscode', '.idea', 'node_modules',
            'venv', 'env', '.venv', '.env', 'dist', 'build', 'target',
            'bin', 'obj', '.vs', '.pytest_cache', '.coverage', 'htmlcov',
            'site-packages', 'Include', 'Lib', 'Scripts', 'share',
            'tools', 'temp', 'test_output', 'results', 'backups',
            'generated_devices', 'device_samples'
        }
        
        self.exclude_files = {
            '.gitignore', '.gitattributes', '.env', '.env.local',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe',
            '*.log', '*.tmp', '*.temp', '*.cache', '*.bak',
            '*.zip', '*.tar.gz', '*.rar', '*.7z',
            'package-lock.json', 'yarn.lock', 'requirements.txt',
            'Pipfile', 'Pipfile.lock', 'poetry.lock'
        }
        
        # 定义重要文件类型（用于详细版脑图）
        self.important_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h',
            '.html', '.css', '.scss', '.less', '.vue', '.jsx', '.tsx',
            '.json', '.yaml', '.yml', '.xml', '.md', '.txt',
            '.sql', '.sh', '.bat', '.ps1', '.dockerfile',
            '.gitignore', '.gitattributes', 'README', 'LICENSE'
        }

    def create_blank_template(self) -> Path:
        """
        创建一个空白的XMind模板文件
        
        Returns:
            Path: 模板文件路径
        """
        template_file = self.output_dir / "blank_template.xmind"
        
        try:
            # 创建一个简单的XMind文件作为模板
            workbook = xmind.load(str(template_file))
            sheet = workbook.getPrimarySheet()
            sheet.setTitle("空白模板")
            
            root_topic = sheet.getRootTopic()
            root_topic.setTitle("根主题")
            
            # 保存模板
            xmind.save(workbook)
            logger.info(f"空白模板已创建: {template_file}")
            
        except Exception as e:
            logger.warning(f"创建模板失败，将使用备用方案: {e}")
            # 如果创建失败，创建一个最小的XMind文件结构
            self._create_minimal_xmind(template_file)
            
        return template_file

    def _create_minimal_xmind(self, file_path: Path) -> None:
        """
        创建一个最小的XMind文件结构
        
        Args:
            file_path: 文件路径
        """
        try:
            # 创建一个包含基本结构的XMind文件
            workbook = xmind.load(str(file_path))
            sheet = workbook.getPrimarySheet()
            sheet.setTitle("项目结构")
            
            root_topic = sheet.getRootTopic()
            root_topic.setTitle("项目根目录")
            
            # 添加一个示例子主题
            sub_topic = root_topic.addSubTopic()
            sub_topic.setTitle("示例目录")
            
            xmind.save(workbook)
            logger.info(f"最小XMind文件已创建: {file_path}")
            
        except Exception as e:
            logger.error(f"创建最小XMind文件失败: {e}")
            raise

    def should_exclude(self, path: Path) -> bool:
        """
        判断是否应该排除该路径
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 是否应该排除
        """
        # 检查目录名
        if path.name in self.exclude_dirs:
            return True
            
        # 检查文件名模式
        for pattern in self.exclude_files:
            if pattern.startswith('*'):
                if path.name.endswith(pattern[1:]):
                    return True
            elif path.name == pattern:
                return True
                
        # 检查是否在排除的目录中
        for parent in path.parents:
            if parent.name in self.exclude_dirs:
                return True
                
        return False

    def is_important_file(self, path: Path) -> bool:
        """
        判断是否为重要文件（用于详细版脑图）
        
        Args:
            path: 文件路径
            
        Returns:
            bool: 是否为重要文件
        """
        if not path.is_file():
            return False
            
        # 检查文件扩展名
        if path.suffix.lower() in self.important_extensions:
            return True
            
        # 检查特殊文件名
        special_names = {'README', 'LICENSE', '.gitignore', '.gitattributes'}
        if path.name in special_names:
            return True
            
        return False

    def scan_directory(self, directory: Path, max_depth: int = 3, current_depth: int = 0) -> Dict:
        """
        递归扫描目录结构
        
        Args:
            directory: 要扫描的目录
            max_depth: 最大扫描深度
            current_depth: 当前扫描深度
            
        Returns:
            Dict: 目录结构字典
        """
        if current_depth > max_depth:
            return {}
            
        structure = {
            'name': directory.name,
            'type': 'directory',
            'children': []
        }
        
        try:
            for item in sorted(directory.iterdir()):
                if self.should_exclude(item):
                    continue
                    
                if item.is_dir():
                    # 递归扫描子目录
                    child_structure = self.scan_directory(item, max_depth, current_depth + 1)
                    if child_structure:  # 只添加非空的目录
                        structure['children'].append(child_structure)
                elif item.is_file():
                    # 添加文件（仅在详细版中）
                    if max_depth > 2 or self.is_important_file(item):
                        structure['children'].append({
                            'name': item.name,
                            'type': 'file',
                            'extension': item.suffix.lower()
                        })
                        
        except PermissionError:
            logger.warning(f"无法访问目录: {directory}")
        except Exception as e:
            logger.error(f"扫描目录时出错 {directory}: {e}")
            
        return structure

    def create_xmind_structure(self, structure: Dict, parent_topic=None) -> None:
        """
        递归创建XMind结构
        
        Args:
            structure: 目录结构字典
            parent_topic: 父主题
        """
        if not structure:
            return
            
        # 创建当前主题
        if parent_topic is None:
            # 根主题
            topic = self.sheet.getRootTopic()
            topic.setTitle(structure['name'])
        else:
            # 子主题
            topic = parent_topic.addSubTopic()
            topic.setTitle(structure['name'])
            
        # 递归处理子项
        for child in structure.get('children', []):
            self.create_xmind_structure(child, topic)

    def generate_simple_mindmap(self) -> str:
        """
        生成简化版思维导图（主目录 + 2级子目录）
        
        Returns:
            str: 输出文件路径
        """
        logger.info("开始生成简化版思维导图...")
        
        # 复制模板文件
        template_file = self.create_blank_template()
        output_file = self.output_dir / "project_mindmap_simple.xmind"
        shutil.copy2(template_file, output_file)
        
        # 加载并修改文件
        self.workbook = xmind.load(str(output_file))
        self.sheet = self.workbook.getPrimarySheet()
        self.sheet.setTitle("项目结构简化版")
        
        # 设置根主题
        root_topic = self.sheet.getRootTopic()
        root_topic.setTitle(self.project_root.name)
        
        # 扫描项目结构（最大深度2）
        structure = self.scan_directory(self.project_root, max_depth=2)
        
        # 创建XMind结构
        for child in structure.get('children', []):
            self.create_xmind_structure(child, root_topic)
            
        # 保存文件
        xmind.save(self.workbook)
        
        logger.info(f"简化版思维导图已生成: {output_file}")
        return str(output_file)

    def generate_detailed_mindmap(self) -> str:
        """
        生成详细版思维导图（递归所有代码相关目录和文件）
        
        Returns:
            str: 输出文件路径
        """
        logger.info("开始生成详细版思维导图...")
        
        # 复制模板文件
        template_file = self.output_dir / "blank_template.xmind"
        output_file = self.output_dir / "project_mindmap_full.xmind"
        shutil.copy2(template_file, output_file)
        
        # 加载并修改文件
        self.workbook = xmind.load(str(output_file))
        self.sheet = self.workbook.getPrimarySheet()
        self.sheet.setTitle("项目结构详细版")
        
        # 设置根主题
        root_topic = self.sheet.getRootTopic()
        root_topic.setTitle(self.project_root.name)
        
        # 扫描项目结构（最大深度5）
        structure = self.scan_directory(self.project_root, max_depth=5)
        
        # 创建XMind结构
        for child in structure.get('children', []):
            self.create_xmind_structure(child, root_topic)
            
        # 保存文件
        xmind.save(self.workbook)
        
        logger.info(f"详细版思维导图已生成: {output_file}")
        return str(output_file)

    def generate_mindmaps(self) -> Dict[str, str]:
        """
        生成所有版本的思维导图
        
        Returns:
            Dict[str, str]: 生成的文件路径字典
        """
        logger.info("开始生成项目结构思维导图...")
        
        results = {}
        
        try:
            # 生成简化版
            simple_file = self.generate_simple_mindmap()
            results['simple'] = simple_file
            
            # 生成详细版
            detailed_file = self.generate_detailed_mindmap()
            results['detailed'] = detailed_file
            
            # 清理模板文件
            template_file = self.output_dir / "blank_template.xmind"
            if template_file.exists():
                template_file.unlink()
                logger.info("模板文件已清理")
            
            logger.info("所有思维导图生成完成！")
            
        except Exception as e:
            logger.error(f"生成思维导图时出错: {e}")
            raise
            
        return results

    def print_usage_instructions(self, files: Dict[str, str]) -> None:
        """
        打印使用说明
        
        Args:
            files: 生成的文件路径字典
        """
        print("\n" + "="*60)
        print("🎯 项目结构思维导图生成完成！")
        print("="*60)
        
        print("\n📁 生成的文件:")
        for version, file_path in files.items():
            print(f"  • {version.title()}版: {file_path}")
            
        print("\n🔧 使用说明:")
        print("  1. 下载并安装 XMind (https://xmind.cn/)")
        print("  2. 用 XMind 打开生成的 .xmind 文件")
        print("  3. 在 XMind 中进行美化和样式调整")
        print("  4. 导出为 PNG/JPG/SVG 等格式的图片")
        
        print("\n💡 美化建议:")
        print("  • 调整主题颜色和字体")
        print("  • 添加图标和标签")
        print("  • 调整布局和分支样式")
        print("  • 添加备注和链接")
        
        print("\n📊 文件说明:")
        print("  • simple.xmind: 简化版，适合概览和演示")
        print("  • full.xmind: 详细版，包含所有代码文件")
        
        print("\n" + "="*60)


def main():
    """主函数"""
    try:
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent
        
        # 创建生成器实例
        generator = XMindMindmapGenerator(project_root)
        
        # 生成思维导图
        files = generator.generate_mindmaps()
        
        # 打印使用说明
        generator.print_usage_instructions(files)
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 