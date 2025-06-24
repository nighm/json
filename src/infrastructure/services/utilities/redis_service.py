import redis

def get_captcha_code_from_redis(redis_host: str, redis_port: int, redis_password: str, redis_captcha_prefix: str, uuid: str):
    """
    连接Redis，查找验证码，并去除多余引号。
    :param redis_host: Redis主机地址
    :param redis_port: Redis端口
    :param redis_password: Redis密码
    :param redis_captcha_prefix: 验证码key前缀
    :param uuid: uuid字符串
    :return: 验证码（去除引号，可能为int或str）
    """
    r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
    key = f"{redis_captcha_prefix}{uuid}"
    code = r.get(key)
    if code is not None:
        code = code.strip('"')
        try:
            code = int(code)
        except Exception:
            pass
    print(f"[Redis] 查到验证码: {code} (key={key})")
    return code 