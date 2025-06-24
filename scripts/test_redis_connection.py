import redis
import json
from pathlib import Path

def load_config():
    config_path = Path("src/config/project_config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_redis_connection():
    try:
        # 加载配置
        config = load_config()
        
        # 创建Redis连接
        r = redis.Redis(
            host=config['redis_host'],
            port=config['redis_port'],
            password=config['redis_password'],
            decode_responses=True
        )
        
        # 测试连接
        print("正在测试Redis连接...")
        print(f"Redis服务器: {config['redis_host']}:{config['redis_port']}")
        
        # 执行PING命令测试连接
        response = r.ping()
        print(f"Redis连接测试结果: {'成功' if response else '失败'}")
        
        # 测试写入和读取
        test_key = "test_connection_key"
        test_value = "test_connection_value"
        
        print("\n测试数据写入和读取...")
        r.set(test_key, test_value)
        retrieved_value = r.get(test_key)
        print(f"写入测试: {'成功' if retrieved_value == test_value else '失败'}")
        
        # 清理测试数据
        r.delete(test_key)
        print("测试数据已清理")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"Redis连接错误: {str(e)}")
        return False
    except Exception as e:
        print(f"发生其他错误: {str(e)}")
        return False

if __name__ == "__main__":
    test_redis_connection() 