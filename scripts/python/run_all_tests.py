#!/usr/bin/env python3
"""
run_all_tests.py
一键运行 tests 目录下所有自动化测试（pytest），并统计 src 目录下的测试覆盖率。
用法：python scripts/python/run_all_tests.py
"""
import sys
import subprocess
import os

def main():
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    # 调用pytest运行所有测试，并统计src目录覆盖率，生成HTML报告
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--cov=src", "--cov-report=term", "--cov-report=html", "tests", "--maxfail=5", "--disable-warnings", "-v"],
        capture_output=False
    )
    print("\n覆盖率HTML报告已生成：htmlcov/index.html")
    sys.exit(result.returncode)

if __name__ == "__main__":
    main() 