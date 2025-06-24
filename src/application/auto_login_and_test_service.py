from src.infrastructure.uuid_service import get_uuid
from src.infrastructure.redis_service import get_captcha_code_from_redis
from src.infrastructure.login_service import login_and_get_token
from src.infrastructure.api_test_service import test_api


def run_auto_login_and_test(config: dict):
    """
    自动化登录与接口测试主流程，用于application层。
    :param config: 配置字典，包含所有必要参数
    """
    print("=== 自动化登录与接口测试流程开始 ===")
    uuid = get_uuid(config['server_url'], config['uuid_api'])
    code = get_captcha_code_from_redis(
        config['redis_host'],
        config['redis_port'],
        config['redis_password'],
        config['redis_captcha_prefix'],
        uuid
    )
    if code is None or str(code) == '0':
        print("[Error] 未能从Redis查到有效验证码，流程终止！")
        return
    token = login_and_get_token(
        config['server_url'],
        config['login_api'],
        config['login_username'],
        config['login_password'],
        code,
        uuid
    )
    if not token:
        print("[Error] 登录失败，未获取到token，流程终止！")
        return
    for api in config['test_apis']:
        test_api(config['server_url'], api, token)
    print("=== 流程结束 ===") 