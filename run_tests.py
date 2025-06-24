#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行脚本
提供便捷的测试执行方式
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("✅ 执行成功")
        if result.stdout:
            print("输出:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 执行失败")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False

def check_environment():
    """检查测试环境"""
    print("🔍 检查测试环境...")
    
    # 检查虚拟环境
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  警告: 未检测到虚拟环境，建议在虚拟环境中运行测试")
    
    # 检查pytest
    try:
        import pytest
        print(f"✅ pytest已安装: {pytest.__version__}")
    except ImportError:
        print("❌ pytest未安装，请运行: pip install pytest pytest-cov pytest-mock")
        return False
    
    # 检查测试目录
    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ tests目录不存在")
        return False
    
    print("✅ 测试环境检查完成")
    return True

def run_all_tests():
    """运行所有测试"""
    return run_command(
        ["python", "-m", "pytest"],
        "运行所有测试"
    )

def run_cli_tests():
    """运行CLI接口测试"""
    return run_command(
        ["python", "-m", "pytest", "tests/interfaces/", "-m", "cli", "-v"],
        "运行CLI接口测试"
    )

def run_service_tests():
    """运行服务层测试"""
    return run_command(
        ["python", "-m", "pytest", "tests/application/", "-m", "service", "-v"],
        "运行服务层测试"
    )

def run_infrastructure_tests():
    """运行基础设施层测试"""
    return run_command(
        ["python", "-m", "pytest", "tests/infrastructure/", "-m", "infrastructure", "-v"],
        "运行基础设施层测试"
    )

def run_domain_tests():
    """运行领域层测试"""
    return run_command(
        ["python", "-m", "pytest", "tests/domain/", "-m", "domain", "-v"],
        "运行领域层测试"
    )

def run_coverage():
    """运行覆盖率测试"""
    return run_command(
        ["python", "-m", "pytest", "--cov=src", "--cov-report=html", "--cov-report=term-missing"],
        "运行覆盖率测试"
    )

def run_specific_test(test_path):
    """运行特定测试"""
    return run_command(
        ["python", "-m", "pytest", test_path, "-v"],
        f"运行特定测试: {test_path}"
    )

def run_performance_test_cli_tests():
    """运行performance_test_cli专门测试"""
    return run_command(
        ["python", "-m", "pytest", "tests/interfaces/cli/test_performance_test_cli.py", "-v"],
        "运行performance_test_cli专门测试"
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="性能测试项目测试运行器")
    parser.add_argument(
        "--type", 
        choices=["all", "cli", "service", "infrastructure", "domain", "coverage", "performance-cli"],
        default="all",
        help="测试类型"
    )
    parser.add_argument(
        "--test-path",
        help="特定测试文件路径"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="仅检查测试环境"
    )
    
    args = parser.parse_args()
    
    print("🚀 性能测试项目测试运行器")
    print("="*60)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，请修复问题后重试")
        sys.exit(1)
    
    if args.check_env:
        print("✅ 环境检查完成")
        return
    
    # 根据参数运行测试
    success = True
    
    if args.test_path:
        success = run_specific_test(args.test_path)
    elif args.type == "all":
        success = run_all_tests()
    elif args.type == "cli":
        success = run_cli_tests()
    elif args.type == "service":
        success = run_service_tests()
    elif args.type == "infrastructure":
        success = run_infrastructure_tests()
    elif args.type == "domain":
        success = run_domain_tests()
    elif args.type == "coverage":
        success = run_coverage()
    elif args.type == "performance-cli":
        success = run_performance_test_cli_tests()
    
    # 输出结果
    print("\n" + "="*60)
    if success:
        print("🎉 所有测试执行完成")
    else:
        print("💥 测试执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 