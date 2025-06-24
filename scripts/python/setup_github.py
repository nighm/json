#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub仓库初始化和上传脚本
用于将项目上传到GitHub，自动处理.gitignore和必要的文件
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional


class GitHubSetup:
    """GitHub仓库设置类"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.git_dir = self.project_root / ".git"
        
    def check_git_installed(self) -> bool:
        """检查Git是否已安装"""
        try:
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            print(f"✓ Git已安装: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ Git未安装，请先安装Git")
            return False
    
    def check_git_initialized(self) -> bool:
        """检查是否已初始化Git仓库"""
        if self.git_dir.exists():
            print("✓ Git仓库已初始化")
            return True
        else:
            print("ℹ Git仓库未初始化")
            return False
    
    def initialize_git(self) -> bool:
        """初始化Git仓库"""
        try:
            subprocess.run(
                ["git", "init"], 
                cwd=self.project_root, 
                check=True
            )
            print("✓ Git仓库初始化成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Git仓库初始化失败: {e}")
            return False
    
    def add_remote(self, remote_url: str) -> bool:
        """添加远程仓库"""
        try:
            # 检查是否已有远程仓库
            result = subprocess.run(
                ["git", "remote", "-v"], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            
            if remote_url in result.stdout:
                print("✓ 远程仓库已存在")
                return True
            
            # 添加远程仓库
            subprocess.run(
                ["git", "remote", "add", "origin", remote_url], 
                cwd=self.project_root, 
                check=True
            )
            print(f"✓ 远程仓库添加成功: {remote_url}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 远程仓库添加失败: {e}")
            return False
    
    def add_files(self) -> bool:
        """添加文件到Git"""
        try:
            subprocess.run(
                ["git", "add", "."], 
                cwd=self.project_root, 
                check=True
            )
            print("✓ 文件添加成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 文件添加失败: {e}")
            return False
    
    def commit_files(self, message: str = "Initial commit") -> bool:
        """提交文件"""
        try:
            subprocess.run(
                ["git", "commit", "-m", message], 
                cwd=self.project_root, 
                check=True
            )
            print(f"✓ 文件提交成功: {message}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 文件提交失败: {e}")
            return False
    
    def push_to_github(self, branch: str = "main") -> bool:
        """推送到GitHub"""
        try:
            # 设置默认分支
            subprocess.run(
                ["git", "branch", "-M", branch], 
                cwd=self.project_root, 
                check=True
            )
            
            # 推送到远程仓库
            subprocess.run(
                ["git", "push", "-u", "origin", branch], 
                cwd=self.project_root, 
                check=True
            )
            print(f"✓ 代码推送成功到分支: {branch}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 代码推送失败: {e}")
            return False
    
    def check_essential_files(self) -> List[str]:
        """检查必要文件是否存在"""
        essential_files = [
            "README.md",
            "requirements.txt",
            "LICENSE",
            ".gitignore"
        ]
        
        missing_files = []
        for file in essential_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"⚠ 缺少必要文件: {', '.join(missing_files)}")
        else:
            print("✓ 所有必要文件都存在")
        
        return missing_files
    
    def show_status(self) -> None:
        """显示Git状态"""
        try:
            result = subprocess.run(
                ["git", "status"], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            print("\n当前Git状态:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"✗ 无法获取Git状态: {e}")
    
    def setup_repository(self, remote_url: str, commit_message: str = "Initial commit") -> bool:
        """完整的仓库设置流程"""
        print("🚀 开始设置GitHub仓库...")
        print(f"项目根目录: {self.project_root}")
        
        # 检查Git安装
        if not self.check_git_installed():
            return False
        
        # 检查必要文件
        missing_files = self.check_essential_files()
        if missing_files:
            print("请先创建缺少的必要文件")
            return False
        
        # 初始化Git仓库
        if not self.check_git_initialized():
            if not self.initialize_git():
                return False
        
        # 添加远程仓库
        if not self.add_remote(remote_url):
            return False
        
        # 添加文件
        if not self.add_files():
            return False
        
        # 提交文件
        if not self.commit_files(commit_message):
            return False
        
        # 显示状态
        self.show_status()
        
        print("\n✅ GitHub仓库设置完成！")
        print(f"远程仓库: {remote_url}")
        print("下一步: 运行 'python scripts/python/setup_github.py --push' 推送到GitHub")
        
        return True
    
    def push_repository(self) -> bool:
        """推送仓库到GitHub"""
        print("📤 推送代码到GitHub...")
        
        if not self.check_git_initialized():
            print("✗ Git仓库未初始化")
            return False
        
        if not self.push_to_github():
            return False
        
        print("✅ 代码推送完成！")
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GitHub仓库设置和上传工具")
    parser.add_argument(
        "--remote-url", 
        type=str, 
        help="GitHub远程仓库URL (例如: https://github.com/username/repo.git)"
    )
    parser.add_argument(
        "--commit-message", 
        type=str, 
        default="Initial commit: 昆仑卫士性能测试与设备管理平台",
        help="提交消息"
    )
    parser.add_argument(
        "--push", 
        action="store_true", 
        help="推送代码到GitHub"
    )
    parser.add_argument(
        "--status", 
        action="store_true", 
        help="显示Git状态"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # scripts/python/../..
    
    setup = GitHubSetup(project_root)
    
    if args.status:
        setup.show_status()
        return
    
    if args.push:
        setup.push_repository()
        return
    
    if not args.remote_url:
        print("请提供GitHub远程仓库URL")
        print("示例: python scripts/python/setup_github.py --remote-url https://github.com/username/repo.git")
        return
    
    # 设置仓库
    setup.setup_repository(args.remote_url, args.commit_message)


if __name__ == "__main__":
    main() 