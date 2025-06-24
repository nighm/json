import requests
import json
import urllib3

def login_and_get_token(server_url: str, login_api: str, username: str, password: str, code, uuid: str):
    """
    登录接口，先用字符串类型验证码请求，失败后自动用int类型重试。
    :param server_url: 服务器地址
    :param login_api: 登录接口路径
    :param username: 用户名
    :param password: 密码（加密后）
    :param code: 验证码
    :param uuid: uuid
    :return: token字符串或None
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f"https://{server_url}{login_api}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "PostmanRuntime/7.44.0"
    }
    # 先用字符串类型code
    payload = {
        "username": username,
        "password": password,
        "code": str(code),
        "uuid": uuid
    }
    print(f"[Login] 尝试字符串类型验证码: {json.dumps(payload, ensure_ascii=False)}")
    print(f"[Login] 请求头: {headers}")
    resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5, verify=False)
    resp.raise_for_status()
    data = resp.json()
    print(f"[Login] 登录接口完整响应: {json.dumps(data, ensure_ascii=False)}")
    token = data.get('token')
    if token:
        print(f"[Login] 登录成功，获取到token: {token}")
        return token
    # 如果失败，尝试int类型code
    try:
        int_code = int(code)
        payload["code"] = int_code
        print(f"[Login] 字符串类型失败，尝试int类型验证码: {json.dumps(payload, ensure_ascii=False)}")
        resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=5, verify=False)
        resp.raise_for_status()
        data = resp.json()
        print(f"[Login] int类型验证码登录接口完整响应: {json.dumps(data, ensure_ascii=False)}")
        token = data.get('token')
        if token:
            print(f"[Login] int类型验证码登录成功，获取到token: {token}")
            return token
    except Exception as e:
        print(f"[Login] int类型验证码请求异常: {e}")
    print(f"[Error] 登录响应未包含token字段，响应内容: {data}")
    return None 