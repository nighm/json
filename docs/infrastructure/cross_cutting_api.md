# 横切关注点层 API 接口文档

## 概述

本文档详细描述了横切关注点层所有模块的API接口，包括参数说明、返回值、使用示例等。

## 日志模块 API

### get_logger(name: str) -> Logger

获取指定名称的日志器实例。

**参数**：
- `name` (str): 日志器名称，通常使用模块名

**返回值**：
- `Logger`: 日志器实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_logger

logger = get_logger("my_module")
logger.info("这是一条信息日志")
logger.error("这是一条错误日志")
```

### get_logger_factory() -> LoggerFactory

获取日志器工厂实例。

**返回值**：
- `LoggerFactory`: 日志器工厂实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_logger_factory

factory = get_logger_factory()
logger = factory.create_logger("custom_logger")
```

## 配置模块 API

### get_config_provider() -> ConfigProvider

获取配置提供者实例。

**返回值**：
- `ConfigProvider`: 配置提供者实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_config_provider

config = get_config_provider()
db_url = config.get_config("database.url", "sqlite:///app.db")
```

### get_config(key: str, default: Any = None) -> Any

获取配置值。

**参数**：
- `key` (str): 配置键，支持点号分隔的嵌套键
- `default` (Any): 默认值，当配置不存在时返回

**返回值**：
- `Any`: 配置值

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_config

# 获取简单配置
debug_mode = get_config("app.debug", False)

# 获取嵌套配置
db_host = get_config("database.host", "localhost")
```

### set_config(key: str, value: Any) -> bool

设置配置值。

**参数**：
- `key` (str): 配置键
- `value` (Any): 配置值

**返回值**：
- `bool`: 是否设置成功

**使用示例**：
```python
from src.infrastructure.cross_cutting import set_config

success = set_config("app.debug", True)
if success:
    print("配置设置成功")
```

## 安全模块 API

### get_security_provider() -> SecurityProvider

获取安全提供者实例。

**返回值**：
- `SecurityProvider`: 安全提供者实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_security_provider

security = get_security_provider()
```

### hash_password(password: str) -> str

哈希密码。

**参数**：
- `password` (str): 原始密码

**返回值**：
- `str`: 哈希后的密码

**使用示例**：
```python
from src.infrastructure.cross_cutting import hash_password

hashed = hash_password("user123")
print(f"哈希密码: {hashed}")
```

### verify_password(password: str, hashed: str) -> bool

验证密码。

**参数**：
- `password` (str): 原始密码
- `hashed` (str): 哈希后的密码

**返回值**：
- `bool`: 验证结果

**使用示例**：
```python
from src.infrastructure.cross_cutting import verify_password

is_valid = verify_password("user123", hashed_password)
if is_valid:
    print("密码验证成功")
```

## 缓存模块 API

### get_cache_provider() -> CacheProvider

获取缓存提供者实例。

**返回值**：
- `CacheProvider`: 缓存提供者实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_cache_provider

cache_provider = get_cache_provider()
```

### get_cache() -> Cache

获取缓存实例。

**返回值**：
- `Cache`: 缓存实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_cache

cache = get_cache()
cache.set("user:123", user_data, ttl=3600)
user = cache.get("user:123")
```

## 异常处理模块 API

### get_exception_handler() -> ExceptionHandler

获取异常处理器实例。

**返回值**：
- `ExceptionHandler`: 异常处理器实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_exception_handler

handler = get_exception_handler()
```

### handle_exception(exception: Exception, context: Dict[str, Any] = None) -> bool

处理异常。

**参数**：
- `exception` (Exception): 异常对象
- `context` (Dict[str, Any]): 上下文信息

**返回值**：
- `bool`: 是否处理成功

**使用示例**：
```python
from src.infrastructure.cross_cutting import handle_exception

try:
    # 可能出错的代码
    result = risky_operation()
except Exception as e:
    context = {"operation": "risky_operation", "user_id": 123}
    success = handle_exception(e, context)
```

## 验证模块 API

### get_validator() -> Validator

获取验证器实例。

**返回值**：
- `Validator`: 验证器实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_validator

validator = get_validator()
```

### validate_data(data: Any, rules: List[ValidationRule]) -> ValidationResult

验证数据。

**参数**：
- `data` (Any): 要验证的数据
- `rules` (List[ValidationRule]): 验证规则列表

**返回值**：
- `ValidationResult`: 验证结果

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_validator, create_required_rule

validator = get_validator()
required_rule = create_required_rule("用户名不能为空")
result = validator.validate(username, [required_rule])

if result.is_valid:
    print("验证通过")
else:
    print(f"验证失败: {result.errors}")
```

### create_required_rule(message: str = "字段不能为空") -> ValidationRule

创建必填验证规则。

**参数**：
- `message` (str): 错误消息

**返回值**：
- `ValidationRule`: 验证规则

**使用示例**：
```python
from src.infrastructure.cross_cutting import create_required_rule

required_rule = create_required_rule("用户名不能为空")
```

## 统计分析模块 API

### get_statistical_analyzer() -> StatisticalAnalyzer

获取统计分析器实例。

**返回值**：
- `StatisticalAnalyzer`: 统计分析器实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_statistical_analyzer

analyzer = get_statistical_analyzer()
```

### calculate_statistics(data: List[float]) -> StatisticalResult

计算统计数据。

**参数**：
- `data` (List[float]): 数值数据列表

**返回值**：
- `StatisticalResult`: 统计结果

**使用示例**：
```python
from src.infrastructure.cross_cutting import calculate_statistics

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
stats = calculate_statistics(data)
print(f"平均值: {stats.mean}")
print(f"标准差: {stats.std_dev}")
print(f"最小值: {stats.min_value}")
print(f"最大值: {stats.max_value}")
```

### analyze_distribution(data: List[float], bins: int = 10) -> Dict[str, int]

分析数据分布。

**参数**：
- `data` (List[float]): 数值数据列表
- `bins` (int): 分箱数量

**返回值**：
- `Dict[str, int]`: 分布统计

**使用示例**：
```python
from src.infrastructure.cross_cutting import analyze_distribution

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
distribution = analyze_distribution(data, bins=5)
print(f"数据分布: {distribution}")
```

## 国际化模块 API

### get_i18n_provider() -> I18nProvider

获取国际化提供者实例。

**返回值**：
- `I18nProvider`: 国际化提供者实例

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_i18n_provider

i18n = get_i18n_provider()
```

### get_text(key: str, language: str = None, **kwargs) -> str

获取翻译文本。

**参数**：
- `key` (str): 翻译键
- `language` (str): 语言代码（可选）
- `**kwargs`: 格式化参数

**返回值**：
- `str`: 翻译后的文本

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_text

# 获取默认语言文本
ok_text = get_text("common.ok")

# 获取指定语言文本
ok_text_en = get_text("common.ok", "en_US")

# 带参数的文本
welcome_text = get_text("user.welcome", username="张三")
```

### set_language(language: str) -> bool

设置当前语言。

**参数**：
- `language` (str): 语言代码

**返回值**：
- `bool`: 是否设置成功

**使用示例**：
```python
from src.infrastructure.cross_cutting import set_language

success = set_language("en_US")
if success:
    print("语言设置成功")
```

### get_current_language() -> str

获取当前语言。

**返回值**：
- `str`: 当前语言代码

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_current_language

current_lang = get_current_language()
print(f"当前语言: {current_lang}")
```

### get_supported_languages() -> List[str]

获取支持的语言列表。

**返回值**：
- `List[str]`: 支持的语言代码列表

**使用示例**：
```python
from src.infrastructure.cross_cutting import get_supported_languages

languages = get_supported_languages()
print(f"支持的语言: {languages}")
```

## 错误处理

### 常见错误码

| 错误类型 | 错误码 | 描述 |
|---------|--------|------|
| 配置不存在 | CONFIG_NOT_FOUND | 请求的配置项不存在 |
| 验证失败 | VALIDATION_FAILED | 数据验证失败 |
| 缓存错误 | CACHE_ERROR | 缓存操作失败 |
| 安全错误 | SECURITY_ERROR | 安全操作失败 |
| 国际化错误 | I18N_ERROR | 国际化操作失败 |

### 异常处理示例

```python
from src.infrastructure.cross_cutting import get_config, get_logger

logger = get_logger("api")

try:
    # 获取配置
    db_url = get_config("database.url")
    if not db_url:
        raise ValueError("数据库配置不存在")
        
    # 使用配置
    connect_database(db_url)
    
except Exception as e:
    logger.error(f"配置获取失败: {str(e)}")
    # 使用默认配置
    connect_database("sqlite:///default.db")
```

## 性能优化建议

### 1. 缓存使用
- 对于频繁访问的配置，使用缓存
- 合理设置缓存过期时间
- 避免缓存雪崩

### 2. 日志优化
- 使用合适的日志级别
- 避免在循环中频繁记录日志
- 使用结构化日志

### 3. 验证优化
- 预编译验证规则
- 批量验证数据
- 缓存验证结果

### 4. 统计分析优化
- 使用增量计算
- 缓存统计结果
- 异步处理大数据集

## 最佳实践

### 1. 配置管理
```python
# 推荐：使用环境变量覆盖默认配置
from src.infrastructure.cross_cutting import get_config

db_url = get_config("database.url", "sqlite:///app.db")
debug_mode = get_config("app.debug", False)
```

### 2. 日志记录
```python
# 推荐：使用结构化日志
from src.infrastructure.cross_cutting import get_logger

logger = get_logger(__name__)
logger.info("用户登录", extra={"user_id": 123, "ip": "192.168.1.1"})
```

### 3. 数据验证
```python
# 推荐：使用验证规则链
from src.infrastructure.cross_cutting import get_validator, create_required_rule

validator = get_validator()
rules = [
    create_required_rule("用户名不能为空"),
    create_min_length_rule(3, "用户名至少3个字符"),
    create_max_length_rule(20, "用户名最多20个字符")
]
result = validator.validate(username, rules)
```

### 4. 异常处理
```python
# 推荐：统一异常处理
from src.infrastructure.cross_cutting import handle_exception

try:
    process_data()
except Exception as e:
    context = {"operation": "process_data", "data_id": data_id}
    handle_exception(e, context)
    # 返回用户友好的错误信息
    return {"error": "数据处理失败，请稍后重试"}
```

## 总结

横切关注点层提供了丰富的API接口，支持各种常见的横切关注点需求。通过合理使用这些API，可以大大提高代码的可维护性、可测试性和可扩展性。建议在实际使用中遵循最佳实践，确保系统的稳定性和性能。 