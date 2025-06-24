import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.infrastructure.uuid_service import get_uuid

if __name__ == '__main__':
    print('[DEBUG] main_auto_login_and_test.py 启动')
    try:
        with open(os.path.join(os.path.dirname(__file__), '../config/project_config.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f'[ERROR] 配置文件读取失败: {e}')
        sys.exit(1)
    # 只获取uuid，不做后续操作
    uuid = get_uuid(config['server_url'], config['uuid_api'])
    print(f'[RESULT] 本次获取到的uuid: {uuid}')
    # 后续功能全部注释
    # code = get_captcha_code_from_redis(...)
    # token = login_and_get_token(...)
    # ... 