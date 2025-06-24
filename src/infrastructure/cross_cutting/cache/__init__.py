"""
横切关注点 - 缓存服务模块

提供统一的缓存服务，包括内存缓存、文件缓存等。
遵循DDD架构的横切关注点设计原则，为整个应用提供缓存基础设施。
"""

from .cache_provider import (
    ICacheProvider,
    MemoryCacheProvider,
    FileCacheProvider,
    get_cache_provider,
    cache_get,
    cache_set,
    cache_delete,
    cache_clear
)

__all__ = [
    'ICacheProvider',
    'MemoryCacheProvider',
    'FileCacheProvider',
    'get_cache_provider',
    'cache_get',
    'cache_set',
    'cache_delete',
    'cache_clear'
] 