import pytest
from src.infrastructure.cross_cutting.security import get_security_provider

# 安全模块单元测试

def test_password_hash_and_verify():
    """
    测试密码哈希与验证功能。
    """
    provider = get_security_provider()
    password = "abc123"
    hashed = provider.hash_password(password)
    assert provider.verify_password(password, hashed)
    assert not provider.verify_password("wrong", hashed)


def test_encrypt_and_decrypt():
    """
    测试加密与解密功能。
    """
    provider = get_security_provider()
    data = "hello world"
    encrypted = provider.encrypt_data(data)
    decrypted = provider.decrypt_data(encrypted)
    assert decrypted == data 