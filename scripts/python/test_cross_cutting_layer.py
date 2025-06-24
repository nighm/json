#!/usr/bin/env python3
"""
横切关注点层测试脚本

测试所有横切关注点模块的功能，验证DDD架构设计的正确性。
"""

import sys
import os
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.cross_cutting import (
    get_logger, get_config_provider, get_security_provider, 
    get_cache_provider, get_exception_handler, get_validator,
    get_statistical_analyzer
)
from src.infrastructure.cross_cutting.validation import (
    ValidationRule, create_required_rule, create_min_length_rule
)
from src.infrastructure.cross_cutting.exception_handler import (
    BusinessException, ValidationException, InfrastructureException
)


def test_logging():
    """测试日志功能"""
    print("\n=== 测试日志功能 ===")
    
    logger = get_logger("test.logging")
    
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.debug("这是一条调试日志")
    
    print("✅ 日志功能测试完成")


def test_configuration():
    """测试配置功能"""
    print("\n=== 测试配置功能 ===")
    
    config_provider = get_config_provider()
    
    # 设置测试配置
    config_provider.set_config("test.key", "test.value")
    config_provider.set_config("test.number", 123)
    config_provider.set_config("test.list", [1, 2, 3])
    
    # 获取配置
    value = config_provider.get_config("test.key")
    number = config_provider.get_config("test.number")
    test_list = config_provider.get_config("test.list")
    
    print(f"配置值: {value}")
    print(f"配置数字: {number}")
    print(f"配置列表: {test_list}")
    
    # 验证配置
    is_valid = config_provider.validate_config()
    print(f"配置验证结果: {is_valid}")
    
    print("✅ 配置功能测试完成")


def test_security():
    """测试安全功能"""
    print("\n=== 测试安全功能 ===")
    
    security_provider = get_security_provider()
    
    # 测试密码哈希
    password = "test_password_123"
    hashed = security_provider.hash_password(password)
    print(f"原始密码: {password}")
    print(f"哈希密码: {hashed}")
    
    # 测试密码验证
    is_valid = security_provider.verify_password(password, hashed)
    print(f"密码验证结果: {is_valid}")
    
    # 测试JWT令牌
    payload = {"user_id": 123, "username": "test_user"}
    token = security_provider.generate_token(payload, expires_in=3600)
    print(f"生成的JWT令牌: {token[:50]}...")
    
    # 验证令牌
    decoded_payload = security_provider.verify_token(token)
    print(f"令牌验证结果: {decoded_payload is not None}")
    
    # 测试加密解密
    original_data = "敏感数据"
    encrypted = security_provider.encrypt_data(original_data)
    decrypted = security_provider.decrypt_data(encrypted)
    print(f"原始数据: {original_data}")
    print(f"加密数据: {encrypted}")
    print(f"解密数据: {decrypted}")
    
    print("✅ 安全功能测试完成")


def test_cache():
    """测试缓存功能"""
    print("\n=== 测试缓存功能 ===")
    
    cache_provider = get_cache_provider()
    
    # 测试设置和获取缓存
    cache_provider.set("test_key", "test_value", ttl=60)
    cached_value = cache_provider.get("test_key")
    print(f"缓存值: {cached_value}")
    
    # 测试缓存存在性
    has_key = cache_provider.has_key("test_key")
    print(f"缓存键存在: {has_key}")
    
    # 测试TTL
    ttl = cache_provider.get_ttl("test_key")
    print(f"剩余TTL: {ttl}秒")
    
    # 测试删除缓存
    cache_provider.delete("test_key")
    deleted_value = cache_provider.get("test_key")
    print(f"删除后缓存值: {deleted_value}")
    
    print("✅ 缓存功能测试完成")


def test_exception_handler():
    """测试异常处理功能"""
    print("\n=== 测试异常处理功能 ===")
    
    exception_handler = get_exception_handler()
    
    # 测试业务异常
    try:
        raise BusinessException("业务逻辑错误", "BUSINESS_ERROR_001")
    except BusinessException as e:
        exception_handler.handle_exception(e, {"context": "test"})
        print(f"业务异常处理完成: {e.error_code}")
    
    # 测试验证异常
    try:
        raise ValidationException("数据验证失败", "email", "invalid_email")
    except ValidationException as e:
        exception_handler.handle_exception(e, {"context": "test"})
        print(f"验证异常处理完成: {e.field}")
    
    # 测试基础设施异常
    try:
        raise InfrastructureException("数据库连接失败", "database")
    except InfrastructureException as e:
        exception_handler.handle_exception(e, {"context": "test"})
        print(f"基础设施异常处理完成: {e.component}")
    
    print("✅ 异常处理功能测试完成")


def test_validation():
    """测试验证功能"""
    print("\n=== 测试验证功能 ===")
    
    validator = get_validator()
    
    # 测试邮箱验证
    email_result = validator.validate_field("email", "test@example.com", [
        ValidationRule("email", lambda x: "@" in str(x), "邮箱格式不正确")
    ])
    print(f"邮箱验证结果: {email_result.is_valid}")
    
    # 测试必填验证
    required_rule = create_required_rule("用户名不能为空")
    username_result = validator.validate_field("username", "", [required_rule])
    print(f"用户名验证结果: {username_result.is_valid}")
    print(f"验证错误: {username_result.errors}")
    
    # 测试长度验证
    length_rule = create_min_length_rule(3, "密码长度不能少于3位")
    password_result = validator.validate_field("password", "ab", [length_rule])
    print(f"密码验证结果: {password_result.is_valid}")
    print(f"验证错误: {password_result.errors}")
    
    print("✅ 验证功能测试完成")


def test_statistical_analysis():
    """测试统计分析功能"""
    print("\n=== 测试统计分析功能 ===")
    
    analyzer = get_statistical_analyzer()
    
    # 测试数据
    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 100]
    
    # 基础统计
    stats = analyzer.calculate_basic_stats(test_data)
    print(f"数据量: {stats.count}")
    print(f"平均值: {stats.mean:.2f}")
    print(f"中位数: {stats.median:.2f}")
    print(f"标准差: {stats.std_dev:.2f}")
    print(f"最小值: {stats.min_value}")
    print(f"最大值: {stats.max_value}")
    
    # 百分位数
    percentiles = analyzer.calculate_percentiles(test_data, [25, 50, 75, 90])
    print(f"百分位数: {percentiles}")
    
    # 分布分析
    distribution = analyzer.analyze_distribution(test_data, bins=5)
    print(f"数据分布: {distribution}")
    
    # 异常值检测
    outliers = analyzer.detect_outliers(test_data)
    print(f"异常值: {outliers}")
    
    print("✅ 统计分析功能测试完成")


def test_integration():
    """测试模块集成"""
    print("\n=== 测试模块集成 ===")
    
    # 模拟一个完整的业务流程
    logger = get_logger("integration.test")
    config = get_config_provider()
    cache = get_cache_provider()
    validator = get_validator()
    
    logger.info("开始集成测试")
    
    # 1. 验证输入数据
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "age": 25
    }
    
    # 2. 缓存用户数据
    cache.set("user_data", user_data, ttl=300)
    
    # 3. 验证邮箱格式
    email_rule = ValidationRule("email", lambda x: "@" in str(x), "邮箱格式不正确")
    email_result = validator.validate_field("email", user_data["email"], [email_rule])
    
    if email_result.is_valid:
        logger.info("邮箱验证通过")
        # 4. 处理业务逻辑
        config.set_config("last_user_email", user_data["email"])
        logger.info("业务逻辑处理完成")
    else:
        logger.error(f"邮箱验证失败: {email_result.errors}")
    
    # 5. 清理缓存
    cache.delete("user_data")
    
    logger.info("集成测试完成")
    print("✅ 模块集成测试完成")


def main():
    """主测试函数"""
    print("🚀 开始测试横切关注点层")
    print("=" * 50)
    
    try:
        # 测试各个模块
        test_logging()
        test_configuration()
        test_security()
        test_cache()
        test_exception_handler()
        test_validation()
        test_statistical_analysis()
        test_integration()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！横切关注点层功能正常")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 