import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.infrastructure.uuid_service import get_uuid
import json

def test_uuid():
    # 读取配置文件
    with open(os.path.join(os.path.dirname(__file__), '../src/config/project_config.json'), 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 测试获取UUID
    print("=== 开始测试UUID获取 ===")
    try:
        uuid = get_uuid(config['server_url'], config['uuid_api'])
        print(f"获取到的UUID: {uuid}")
        print(f"UUID长度: {len(uuid)}")
        print(f"UUID格式是否正确: {bool(uuid and '-' in uuid)}")
    except Exception as e:
        print(f"获取UUID时发生错误: {str(e)}")
    print("=== 测试结束 ===")

if __name__ == '__main__':
    test_uuid() 