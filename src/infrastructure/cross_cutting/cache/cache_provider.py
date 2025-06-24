"""
横切关注点 - 缓存提供者

提供统一的缓存服务，包括内存缓存、文件缓存等。
遵循DDD架构中的横切关注点设计原则，为整个应用提供缓存基础设施。
"""

import json
import pickle
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta

from ..logging import get_logger


class ICacheProvider(ABC):
    """缓存提供者接口 - 遵循依赖倒置原则"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存值"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """清空所有缓存"""
        pass
    
    @abstractmethod
    def has_key(self, key: str) -> bool:
        """检查键是否存在"""
        pass
    
    @abstractmethod
    def get_ttl(self, key: str) -> Optional[int]:
        """获取键的剩余生存时间"""
        pass


class MemoryCacheProvider(ICacheProvider):
    """内存缓存提供者 - 基于内存的缓存实现"""
    
    def __init__(self):
        """初始化内存缓存提供者"""
        self.logger = get_logger("cache.memory")
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值或None
        """
        try:
            if key not in self._cache:
                return None
            
            cache_item = self._cache[key]
            
            # 检查是否过期
            if 'expires_at' in cache_item:
                if time.time() > cache_item['expires_at']:
                    # 过期，删除缓存项
                    del self._cache[key]
                    return None
            
            self.logger.debug(f"从内存缓存获取: {key}")
            return cache_item['value']
            
        except Exception as e:
            self.logger.error(f"从内存缓存获取失败 {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        try:
            expires_at = time.time() + ttl if ttl > 0 else None
            
            self._cache[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': expires_at,
                'ttl': ttl
            }
            
            self.logger.debug(f"设置内存缓存: {key}, TTL: {ttl}秒")
            return True
            
        except Exception as e:
            self.logger.error(f"设置内存缓存失败 {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            if key in self._cache:
                del self._cache[key]
                self.logger.debug(f"删除内存缓存: {key}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"删除内存缓存失败 {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            bool: 是否清空成功
        """
        try:
            self._cache.clear()
            self.logger.info("清空所有内存缓存")
            return True
            
        except Exception as e:
            self.logger.error(f"清空内存缓存失败: {str(e)}")
            return False
    
    def has_key(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 键是否存在
        """
        if key not in self._cache:
            return False
        
        # 检查是否过期
        cache_item = self._cache[key]
        if 'expires_at' in cache_item and time.time() > cache_item['expires_at']:
            del self._cache[key]
            return False
        
        return True
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        获取键的剩余生存时间
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[int]: 剩余生存时间（秒）或None
        """
        if not self.has_key(key):
            return None
        
        cache_item = self._cache[key]
        if 'expires_at' in cache_item:
            remaining = cache_item['expires_at'] - time.time()
            return max(0, int(remaining))
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_items = len(self._cache)
        expired_items = 0
        
        for key, item in self._cache.items():
            if 'expires_at' in item and time.time() > item['expires_at']:
                expired_items += 1
        
        return {
            'total_items': total_items,
            'expired_items': expired_items,
            'valid_items': total_items - expired_items
        }


class FileCacheProvider(ICacheProvider):
    """文件缓存提供者 - 基于文件的缓存实现"""
    
    def __init__(self, cache_dir: str = "cache"):
        """
        初始化文件缓存提供者
        
        Args:
            cache_dir: 缓存目录
        """
        self.logger = get_logger("cache.file")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用键的哈希值作为文件名，避免特殊字符问题
        import hashlib
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值或None
        """
        try:
            cache_file = self._get_cache_file(key)
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查是否过期
            if 'expires_at' in cache_data:
                if time.time() > cache_data['expires_at']:
                    # 过期，删除缓存文件
                    cache_file.unlink()
                    return None
            
            self.logger.debug(f"从文件缓存获取: {key}")
            return cache_data['value']
            
        except Exception as e:
            self.logger.error(f"从文件缓存获取失败 {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        try:
            expires_at = time.time() + ttl if ttl > 0 else None
            
            cache_data = {
                'key': key,
                'value': value,
                'created_at': time.time(),
                'expires_at': expires_at,
                'ttl': ttl
            }
            
            cache_file = self._get_cache_file(key)
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.logger.debug(f"设置文件缓存: {key}, TTL: {ttl}秒")
            return True
            
        except Exception as e:
            self.logger.error(f"设置文件缓存失败 {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            cache_file = self._get_cache_file(key)
            
            if cache_file.exists():
                cache_file.unlink()
                self.logger.debug(f"删除文件缓存: {key}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"删除文件缓存失败 {key}: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            bool: 是否清空成功
        """
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            self.logger.info("清空所有文件缓存")
            return True
            
        except Exception as e:
            self.logger.error(f"清空文件缓存失败: {str(e)}")
            return False
    
    def has_key(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 键是否存在
        """
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return False
        
        # 检查是否过期
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            if 'expires_at' in cache_data and time.time() > cache_data['expires_at']:
                cache_file.unlink()
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        获取键的剩余生存时间
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[int]: 剩余生存时间（秒）或None
        """
        if not self.has_key(key):
            return None
        
        try:
            cache_file = self._get_cache_file(key)
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            if 'expires_at' in cache_data:
                remaining = cache_data['expires_at'] - time.time()
                return max(0, int(remaining))
            
            return None
            
        except Exception:
            return None


# 全局缓存提供者实例
_cache_provider: Optional[ICacheProvider] = None


def get_cache_provider() -> ICacheProvider:
    """获取全局缓存提供者"""
    global _cache_provider
    if _cache_provider is None:
        _cache_provider = MemoryCacheProvider()
    return _cache_provider


# 便捷函数
def cache_get(key: str) -> Optional[Any]:
    """便捷函数：获取缓存值"""
    return get_cache_provider().get(key)


def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """便捷函数：设置缓存值"""
    return get_cache_provider().set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """便捷函数：删除缓存值"""
    return get_cache_provider().delete(key)


def cache_clear() -> bool:
    """便捷函数：清空所有缓存"""
    return get_cache_provider().clear() 