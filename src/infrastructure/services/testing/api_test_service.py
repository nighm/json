import requests
import urllib3

def test_api(server_url: str, api_path: str, token: str):
    """
    带token请求目标接口，输出结果。
    :param server_url: 服务器地址
    :param api_path: 目标接口路径
    :param token: 登录token
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f"https://{server_url}{api_path}"
    headers = {"Authorization": token}
    resp = requests.get(url, headers=headers, timeout=5, verify=False)
    print(f"[Test] {api_path} 状态码: {resp.status_code}")
    try:
        print(f"[Test] 响应内容: {resp.json()}")
    except Exception:
        print(f"[Test] 响应内容: {resp.text}") 