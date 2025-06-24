"""
横切关注点 - 国际化模块

提供统一的国际化服务，包括多语言支持、本地化等。
遵循DDD架构的横切关注点设计原则，为整个应用提供国际化基础设施。
"""

from .i18n_provider import (
    II18nProvider,
    I18nProvider,
    get_i18n_provider,
    get_text,
    set_language,
    get_current_language,
    get_supported_languages
)

__all__ = [
    'II18nProvider',
    'I18nProvider',
    'get_i18n_provider',
    'get_text',
    'set_language',
    'get_current_language',
    'get_supported_languages'
] 