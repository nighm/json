"""
横切关注点 - 安全提供者

提供统一的安全服务，包括身份验证、授权、加密、解密等。
遵循DDD架构中的横切关注点设计原则，为整个应用提供安全基础设施。
"""

import hashlib
import hmac
import secrets
import base64
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from ..logging import get_logger


class ISecurityProvider(ABC):
    """安全提供者接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        pass
    
    @abstractmethod
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        pass
    
    @abstractmethod
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        pass
    
    @abstractmethod
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        pass


class SecurityProvider(ISecurityProvider):
    """安全提供者实现 - 统一的安全服务"""
    
    def __init__(self, secret_key: str = None):
        """
        初始化安全提供者
        
        Args:
            secret_key: 密钥（可选，默认使用环境变量）
        """
        self.logger = get_logger("security.provider")
        self.secret_key = secret_key or self._get_default_secret_key()
    
    def _get_default_secret_key(self) -> str:
        """获取默认密钥"""
        import os
        return os.environ.get('SECRET_KEY', 'default-secret-key-change-in-production')
    
    def hash_password(self, password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 原始密码
            
        Returns:
            str: 哈希后的密码
        """
        try:
            # 使用SHA-256哈希
            salt = secrets.token_hex(16)
            hash_obj = hashlib.sha256()
            hash_obj.update((password + salt).encode('utf-8'))
            hashed = hash_obj.hexdigest()
            
            # 返回 salt:hash 格式
            return f"{salt}:{hashed}"
        except Exception as e:
            self.logger.error(f"密码哈希失败: {str(e)}")
            raise
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        验证密码
        
        Args:
            password: 原始密码
            hashed: 哈希后的密码
            
        Returns:
            bool: 验证结果
        """
        try:
            if ':' not in hashed:
                return False
            
            salt, stored_hash = hashed.split(':', 1)
            hash_obj = hashlib.sha256()
            hash_obj.update((password + salt).encode('utf-8'))
            computed_hash = hash_obj.hexdigest()
            
            return hmac.compare_digest(stored_hash, computed_hash)
        except Exception as e:
            self.logger.error(f"密码验证失败: {str(e)}")
            return False
    
    def encrypt_data(self, data: str) -> str:
        """
        加密数据（简单实现，生产环境应使用更安全的算法）
        
        Args:
            data: 原始数据
            
        Returns:
            str: 加密后的数据
        """
        try:
            # 简单的Base64编码（生产环境应使用AES等加密算法）
            encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
            self.logger.info("数据加密成功")
            return encoded
        except Exception as e:
            self.logger.error(f"数据加密失败: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        解密数据
        
        Args:
            encrypted_data: 加密后的数据
            
        Returns:
            str: 解密后的数据
        """
        try:
            # 简单的Base64解码
            decoded = base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
            self.logger.info("数据解密成功")
            return decoded
        except Exception as e:
            self.logger.error(f"数据解密失败: {str(e)}")
            raise
    
    def generate_random_string(self, length: int = 32) -> str:
        """
        生成随机字符串
        
        Args:
            length: 字符串长度
            
        Returns:
            str: 随机字符串
        """
        return secrets.token_hex(length // 2)
    
    def generate_uuid(self) -> str:
        """
        生成UUID
        
        Returns:
            str: UUID字符串
        """
        import uuid
        return str(uuid.uuid4())


# 全局安全提供者实例
_security_provider: Optional[SecurityProvider] = None


def get_security_provider() -> SecurityProvider:
    """获取全局安全提供者"""
    global _security_provider
    if _security_provider is None:
        _security_provider = SecurityProvider()
    return _security_provider


# 便捷函数
def hash_password(password: str) -> str:
    """便捷函数：哈希密码"""
    return get_security_provider().hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    """便捷函数：验证密码"""
    return get_security_provider().verify_password(password, hashed) 