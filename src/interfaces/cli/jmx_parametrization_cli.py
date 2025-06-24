#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JMX参数化CLI工具
【已禁用自动生成JMX文件功能，仅允许列出和清理历史参数化文件】
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.application.services.jmx_parametrization_service import JMXParametrizationService

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="JMX参数化CLI工具（已禁用自动生成JMX文件，仅允许列出和清理历史文件）")
    parser.add_argument("--list", action="store_true", help="列出所有参数化JMX文件")
    parser.add_argument("--cleanup", action="store_true", help="清理所有参数化文件")
    # 已禁用的参数
    # parser.add_argument("--csv-file", help="设备信息CSV文件路径")
    # parser.add_argument("--interface", ...)
    # ... 其他参数 ...
    args = parser.parse_args()

    try:
        service = JMXParametrizationService()
        if args.list:
            files = service.list_parametrized_jmx_files()
            if files:
                print("=== 参数化JMX文件列表 ===")
                for file in files:
                    print(f"  {file}")
            else:
                print("暂无参数化JMX文件")
            return
        if args.cleanup:
            service.cleanup_parametrized_files()
            print("已清理所有参数化JMX文件")
            return
        print("【警告】自动生成参数化JMX文件的功能已禁用。请直接使用api_cases目录下的基础JMX模板进行测试。")
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 