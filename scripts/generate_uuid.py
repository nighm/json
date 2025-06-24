import json
import os
import subprocess
from pathlib import Path

def load_config():
    """加载项目配置文件"""
    config_path = Path(__file__).parent.parent / 'src' / 'config' / 'project_config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_curl_path():
    """获取curl可执行文件路径"""
    curl_dir = Path(__file__).parent.parent / 'tools' / 'curl' / 'curl-8.8.0_2-win64-mingw' / 'bin'
    return str(curl_dir / 'curl.exe')

def generate_uuid():
    """使用curl生成UUID"""
    config = load_config()
    curl_path = get_curl_path()
    
    # 构建完整的URL
    url = f"http://{config['server_url']}{config['uuid_api']}"
    print(f"正在请求URL: {url}")
    print(f"使用curl路径: {curl_path}")
    
    try:
        # 使用curl发送请求，添加-v参数查看详细信息
        result = subprocess.run(
            [curl_path, '-v', '-X', 'GET', url],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("\n=== curl 输出 ===")
        print(result.stdout)
        print("\n=== curl 错误输出 ===")
        print(result.stderr)
        
        # 解析响应
        response = json.loads(result.stdout)
        if 'uuid' in response:
            return response['uuid']
        else:
            raise ValueError("响应中没有找到UUID字段")
            
    except subprocess.CalledProcessError as e:
        print(f"curl命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"原始响应内容: {result.stdout if 'result' in locals() else 'No response'}")
        raise
    except Exception as e:
        print(f"发生未知错误: {e}")
        raise

if __name__ == '__main__':
    try:
        uuid = generate_uuid()
        print(f"生成的UUID: {uuid}")
    except Exception as e:
        print(f"生成UUID失败: {e}") 