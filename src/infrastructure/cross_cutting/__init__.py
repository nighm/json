"""
横切关注点层 (Cross-cutting Concerns Layer)

提供应用程序的横切关注点服务，包括日志、配置、安全、缓存、异常处理等。
这些服务被整个应用程序的所有层使用，遵循DDD架构的横切关注点设计原则。

横切关注点层的特点：
1. 提供通用的基础设施服务
2. 不依赖具体的业务逻辑
3. 通过接口抽象和依赖注入提供服务
4. 遵循依赖倒置原则
5. 支持可扩展和可测试的设计

依赖注入容器说明：
------------------
依赖注入容器（Dependency Injection Container）用于统一注册和获取横切层及其他基础设施服务，
实现解耦和灵活扩展。通过register_services注册所有服务，通过get_service按需获取服务实例，
便于Mock测试和后续维护。

【依赖注入容器用法示例】
----------------------
1. 注册服务（通常在应用启动时统一注册）：
    from src.infrastructure.cross_cutting import register_services
    register_services()

2. 获取服务实例（推荐在业务代码或自动化脚本中使用）：
    from src.infrastructure.cross_cutting import get_service
    # 例如获取日志服务
    logger = get_service('logger')
    logger.info('依赖注入容器获取的日志服务')

3. 结合横切层实际服务举例：
    # 获取配置服务
    config = get_service('config_service')
    # 获取缓存服务
    cache = get_service('cache_service')
    # 获取安全服务
    security = get_service('security_service')

【注意】
- 推荐所有横切层服务都通过依赖注入容器注册和获取，便于Mock测试和灵活扩展。
- 服务类型标识（如'logger'、'config_service'等）需与register_services中注册时保持一致。
"""

from .logging import get_logger, get_logger_factory
from .configuration import get_config_provider, get_config
from .security import get_security_provider
from .cache import get_cache_provider
from .exception_handler import get_exception_handler
from .validation import get_validator
from .analysis import get_statistical_analyzer
from .i18n import get_i18n_provider, get_text
from .doc_generation import *
from .doc_generation import RstBeautifier
# 集成依赖注入容器相关方法
from .dependency_container import register_services, get_service

__all__ = [
    # 日志服务
    'get_logger',
    'get_logger_factory',
    
    # 配置服务
    'get_config_provider',
    'get_config',
    
    # 安全服务
    'get_security_provider',
    
    # 缓存服务
    'get_cache_provider',
    
    # 异常处理
    'get_exception_handler',
    
    # 验证服务
    'get_validator',
    
    # 统计分析
    'get_statistical_analyzer',
    
    # 国际化服务
    'get_i18n_provider',
    'get_text',
    # 依赖注入容器
    'register_services',
    'get_service',
    'RstBeautifier',
] 