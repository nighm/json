import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.application.auto_login_and_test_service import run_auto_login_and_test

if __name__ == '__main__':
    print('[DEBUG] main_auto_login_and_test.py 启动')
    try:
        with open(os.path.join(os.path.dirname(__file__), '../config/project_config.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f'[ERROR] 配置文件读取失败: {e}')
        sys.exit(1)

    # 调用应用层服务执行自动化登录和测试流程
    run_auto_login_and_test(config) 