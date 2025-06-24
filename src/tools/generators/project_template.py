from src.utils.parallel.decorators import parallel
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目模板生成器
Project Template Generator

用于快速创建新的 Python 项目，自动配置开发环境和工具链
Used to quickly create new Python projects and automatically configure development environment and toolchain
"""

import os
import sys
import json
import shutil
import logging
import argparse
from pathlib import Path
from datetime import datetime

# 配置日志
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("project_creation.log"), logging.StreamHandler()],
)

class ProjectTemplate:
    def __init__(self, project_name: str, template_type: str = "standard"):
        self.project_name = project_name
        self.template_type = template_type
        self.root_dir = Path.cwd() / project_name
        self.template_dir = Path(__file__).parent / "templates"
        
    def create_project_structure(self):
        """创建项目目录结构
        Create project directory structure
        """
        logging.info("创建项目目录结构...")
        logging.info("Creating project directory structure...")
        
        # 标准项目结构
        # Standard project structure
        standard_structure = [
            "src",
            "tests",
            "docs",
            "scripts",
            "tools",
            "config",
            "logs",
            "data"
        ]
        
        # DDD 架构项目结构
        # DDD architecture project structure
        ddd_structure = [
            "src/application",
            "src/application/services",
            "src/application/interfaces",
            "src/domain",
            "src/domain/entities",
            "src/domain/value_objects",
            "src/domain/aggregates",
            "src/domain/repositories",
            "src/infrastructure",
            "src/infrastructure/persistence",
            "src/infrastructure/external",
            "src/infrastructure/messaging",
            "src/interfaces",
            "src/interfaces/api",
            "src/interfaces/web",
            "src/interfaces/cli",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tools/generators",
            "tools/scripts"
        ]
        
        # 创建基础目录
        # Create base directories
        for dir_path in standard_structure:
            (self.root_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
        # 如果是 DDD 架构，创建额外的目录
        # If DDD architecture, create additional directories
        if self.template_type == "ddd":
            for dir_path in ddd_structure:
                (self.root_dir / dir_path).mkdir(parents=True, exist_ok=True)
                
    def copy_template_files(self):
        """复制模板文件
        Copy template files
        """
        logging.info("复制模板文件...")
        logging.info("Copying template files...")
        
        # 复制 README 模板
        # Copy README template
        readme_template = self.template_dir / "README.md.template"
        if readme_template.exists():
            with open(readme_template, "r", encoding="utf-8") as f:
                content = f.read().format(project_name=self.project_name)
            with open(self.root_dir / "README.md", "w", encoding="utf-8") as f:
                f.write(content)
                
        # 复制主程序模板
        # Copy main program template
        main_template = self.template_dir / "main.py.template"
        if main_template.exists():
            with open(main_template, "r", encoding="utf-8") as f:
                content = f.read().format(project_name=self.project_name)
            with open(self.root_dir / "src" / "main.py", "w", encoding="utf-8") as f:
                f.write(content)
                
        # 复制工具目录模板
        # Copy tools directory templates
        tools_template = self.template_dir / "tools"
        if tools_template.exists():
            shutil.copytree(tools_template, self.root_dir / "tools", dirs_exist_ok=True)
                
    def create_gitignore(self):
        """创建 .gitignore 文件
        Create .gitignore file
        """
        logging.info("创建 .gitignore 文件...")
        logging.info("Creating .gitignore file...")
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# 项目特定
logs/
data/
*.log
.env
.env.*
!.env.example

# 测试
.coverage
htmlcov/
.pytest_cache/
.tox/
coverage.xml
*.cover
"""
        
        with open(self.root_dir / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
            
    def create_virtual_env(self):
        """创建虚拟环境
        Create virtual environment
        """
        logging.info("创建虚拟环境...")
        logging.info("Creating virtual environment...")
        
        try:
            import venv
            venv.create(self.root_dir / ".venv", with_pip=True)
        except Exception as e:
            logging.error(f"创建虚拟环境失败: {str(e)}")
            logging.error(f"Failed to create virtual environment: {str(e)}")
            raise
            
    def init_git_repo(self):
        """初始化 Git 仓库
        Initialize Git repository
        """
        logging.info("初始化 Git 仓库...")
        logging.info("Initializing Git repository...")
        
        try:
            import subprocess
            subprocess.run(["git", "init"], cwd=self.root_dir, check=True)
            subprocess.run(["git", "add", "."], cwd=self.root_dir, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.root_dir, check=True)
        except Exception as e:
            logging.error(f"初始化 Git 仓库失败: {str(e)}")
            logging.error(f"Failed to initialize Git repository: {str(e)}")
            raise
            
    def create(self):
        """创建项目
        Create project
        """
        try:
            # 创建项目目录
            # Create project directory
            self.root_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建项目结构
            # Create project structure
            self.create_project_structure()
            
            # 复制模板文件
            # Copy template files
            self.copy_template_files()
            
            # 创建 .gitignore
            # Create .gitignore
            self.create_gitignore()
            
            # 创建虚拟环境
            # Create virtual environment
            self.create_virtual_env()
            
            # 初始化 Git 仓库
            # Initialize Git repository
            self.init_git_repo()
            
            logging.info(f"项目 {self.project_name} 创建成功！")
            logging.info(f"Project {self.project_name} created successfully!")
            logging.info(f"项目路径: {self.root_dir}")
            logging.info(f"Project path: {self.root_dir}")
            
        except Exception as e:
            logging.error(f"创建项目失败: {str(e)}")
            logging.error(f"Failed to create project: {str(e)}")
            if self.root_dir.exists():
                shutil.rmtree(self.root_dir)
            raise

def main():
    parser = argparse.ArgumentParser(description="创建新的 Python 项目 / Create new Python project")
    parser.add_argument("project_name", help="项目名称 / Project name")
    parser.add_argument("--template", choices=["standard", "ddd"], default="standard",
                      help="项目模板类型 (standard 或 ddd) / Project template type (standard or ddd)")
    
    args = parser.parse_args()
    
    template = ProjectTemplate(args.project_name, args.template)
    template.create()

if __name__ == "__main__":
    main() 