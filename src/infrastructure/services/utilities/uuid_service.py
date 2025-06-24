import requests
import urllib3
import json

# 警告：本模块为测试环境跳过SSL证书校验，生产环境请勿使用verify=False！
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_uuid(server_url: str, uuid_api: str) -> str:
    """
    请求UUID接口，获取uuid。严格模拟Postman请求头。
    :param server_url: 服务器地址（如192.168.24.45）
    :param uuid_api: uuid接口路径（如/prod-api/captchaImage）
    :return: uuid字符串
    """
    url = f"https://{server_url}{uuid_api}"
    headers = {
        "User-Agent": "PostmanRuntime/7.44.0",
        "Accept": "*/*",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    print(f"[UUID] 请求URL: {url}")
    print(f"[UUID] 请求头: {headers}")
    
    try:
        resp = requests.get(url, headers=headers, timeout=5, verify=False)
        print(f"[UUID] 响应状态码: {resp.status_code}")
        print(f"[UUID] 响应头: {dict(resp.headers)}")
        
        # 尝试解析响应内容
        try:
            data = resp.json()
            print(f"[UUID] 完整响应内容: {json.dumps(data, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"[UUID] 响应不是有效的JSON格式: {resp.text}")
            raise
            
        # 检查响应中是否包含uuid字段
        if 'uuid' not in data:
            print(f"[UUID] 响应中未找到uuid字段，可用字段: {list(data.keys())}")
            raise ValueError("响应中未找到uuid字段")
            
        uuid = data.get('uuid')
        if not uuid:
            print("[UUID] uuid字段值为空")
            raise ValueError("uuid字段值为空")
            
        print(f"[UUID] 获取到uuid: {uuid}")
        return uuid
        
    except requests.exceptions.RequestException as e:
        print(f"[UUID] 请求异常: {str(e)}")
        raise
    except Exception as e:
        print(f"[UUID] 其他异常: {str(e)}")
        raise 