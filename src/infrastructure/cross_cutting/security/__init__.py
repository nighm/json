"""
横切关注点 - 安全模块

提供统一的安全服务，包括身份验证、授权、加密、解密等。
"""

from .security_provider import (
    ISecurityProvider,
    SecurityProvider,
    get_security_provider,
    hash_password,
    verify_password
)

__all__ = [
    'ISecurityProvider',
    'SecurityProvider', 
    'get_security_provider',
    'hash_password',
    'verify_password'
] 