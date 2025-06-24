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
"""

from .logging import get_logger, get_logger_factory
from .configuration import get_config_provider, get_config
from .security import get_security_provider
from .cache import get_cache_provider
from .exception_handler import get_exception_handler
from .validation import get_validator
from .analysis import get_statistical_analyzer
from .i18n import get_i18n_provider, get_text

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
    'get_text'
] 