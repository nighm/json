# 横切关注点层 API 接口文档

## 概述

本文档详细描述了横切关注点层所有模块的API接口，包括参数说明、返回值、使用示例等。

## 日志模块 API

### get_logger(name: str) -> Logger
获取指定名称的日志器实例。

### get_logger_factory() -> LoggerFactory
获取日志器工厂实例。

## 配置模块 API

### get_config_provider() -> ConfigProvider
获取配置提供者实例。

### get_config(key: str, default: Any = None) -> Any
获取配置值。

## 安全模块 API

### get_security_provider() -> SecurityProvider
获取安全提供者实例。

### hash_password(password: str) -> str
哈希密码。

### verify_password(password: str, hashed: str) -> bool
验证密码。

## 缓存模块 API

### get_cache_provider() -> CacheProvider
获取缓存提供者实例。

### get_cache() -> Cache
获取缓存实例。

## 异常处理模块 API

### get_exception_handler() -> ExceptionHandler
获取异常处理器实例。

### handle_exception(exception: Exception, context: Dict[str, Any] = None) -> bool
处理异常。

## 验证模块 API

### get_validator() -> Validator
获取验证器实例。

### validate_data(data: Any, rules: List[ValidationRule]) -> ValidationResult
验证数据。

## 统计分析模块 API

### get_statistical_analyzer() -> StatisticalAnalyzer
获取统计分析器实例。

### calculate_statistics(data: List[float]) -> StatisticalResult
计算统计数据。

## 国际化模块 API

### get_i18n_provider() -> I18nProvider
获取国际化提供者实例。

### get_text(key: str, language: str = None, **kwargs) -> str
获取翻译文本。
