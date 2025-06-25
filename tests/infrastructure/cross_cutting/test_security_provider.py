import os
import pytest
from src.infrastructure.cross_cutting.security.security_provider import SecurityProvider, get_security_provider, hash_password, verify_password

# 安全模块单元测试

def test_hash_and_verify_password_normal_and_edge():
    """
    测试hash_password和verify_password的正常、边界、异常分支。
    """
    provider = SecurityProvider()
    pwd = 'abc123'
    hashed = provider.hash_password(pwd)
    assert ':' in hashed
    assert provider.verify_password(pwd, hashed)
    # 错误密码
    assert not provider.verify_password('wrong', hashed)
    # 错误格式
    assert not provider.verify_password(pwd, 'badformat')
    # 异常分支
    with pytest.raises(Exception):
        provider.hash_password(None)

def test_encrypt_decrypt_data_normal_and_edge():
    """
    测试encrypt_data和decrypt_data的正常、异常分支。
    """
    provider = SecurityProvider()
    data = 'hello'
    encrypted = provider.encrypt_data(data)
    assert encrypted != data
    decrypted = provider.decrypt_data(encrypted)
    assert decrypted == data
    # 解密异常
    with pytest.raises(Exception):
        provider.decrypt_data('notbase64')

def test_generate_random_string_and_uuid():
    """
    测试generate_random_string和generate_uuid的边界分支。
    """
    provider = SecurityProvider()
    s = provider.generate_random_string(8)
    assert isinstance(s, str) and len(s) == 8
    uuid = provider.generate_uuid()
    assert isinstance(uuid, str) and len(uuid) >= 32

def test_get_security_provider_and_convenience():
    """
    测试get_security_provider、hash_password、verify_password便捷函数。
    """
    pwd = 'test'
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed)
    assert not verify_password('bad', hashed)

def test_secret_key_env(monkeypatch):
    """
    测试SECRET_KEY环境变量分支。
    """
    monkeypatch.setenv('SECRET_KEY', 'envkey')
    provider = SecurityProvider()
    assert provider.secret_key == 'envkey'

def test_password_empty():
    """
    测试空密码哈希与验证。
    """
    provider = get_security_provider()
    hashed = provider.hash_password("")
    assert provider.verify_password("", hashed)

def test_algorithm_switch():
    """
    测试加密算法切换（如有多算法实现）。
    """
    provider = get_security_provider()
    if hasattr(provider, 'set_algorithm'):
        provider.set_algorithm('sha256')
        hashed = provider.hash_password('abc')
        assert provider.verify_password('abc', hashed)

def test_permission_check():
    """
    测试权限校验功能（如有权限相关实现）。
    """
    provider = get_security_provider()
    if hasattr(provider, 'check_permission'):
        assert provider.check_permission('admin', 'read') is True 