# 横切层自动化测试说明

本目录包含横切关注点（cross_cutting）各核心模块的自动化测试用例，旨在保障基础设施层的健壮性、可维护性和业务价值。

## 目录结构与说明

- `test_logger.py`：日志模块单元测试，覆盖日志输出、级别过滤、格式化、异常日志等。
- `test_config_provider.py`：配置模块单元测试，覆盖配置获取、动态更新、多环境切换、校验等。
- `test_cache_provider.py`：缓存模块单元测试，覆盖存取、清理、过期、并发、Mock依赖等。
- `test_security_provider.py`：安全模块单元测试，覆盖密码哈希、加解密、算法切换、权限校验等。
- `test_exception_handler.py`：异常处理模块单元测试，覆盖自定义异常、嵌套异常、业务异常等。
- `test_validator.py`：验证模块单元测试，覆盖必填、邮箱、手机号、URL等多种校验，采用参数化覆盖边界场景。
- `test_statistical_analyzer.py`：统计分析模块单元测试，覆盖基础统计、分布、百分位、异常值检测等。
- `test_i18n_provider.py`：国际化模块单元测试，覆盖多语言切换、参数化文本、动态语言包等。
- `test_dependency_container.py`：依赖注入容器集成测试，验证服务注册、单例、异常分发等。

## 设计原则

- **高覆盖率**：用例覆盖常规、异常、边界和高并发等多种场景。
- **独立性**：各测试用例互不依赖，便于并行和持续集成。
- **Mock隔离**：对外部依赖采用Mock，提升测试速度和稳定性。
- **参数化**：批量测试多组输入，提升健壮性。
- **中文注释**：所有用例均有详细中文注释，便于团队协作和维护。

## 使用方法

- 推荐通过一键入口脚本运行：
  ```bash
  python scripts/python/run_all_tests.py
  ```
- 也可单独运行本目录下所有测试：
  ```bash
  pytest tests/infrastructure/cross_cutting -v
  ```

## 最佳实践

- 每次修改横切层代码后，务必运行本目录下所有测试，确保功能和兼容性。
- 新增功能或修复bug时，及时补充相应测试用例。
- 定期用pytest-cov等工具检查测试覆盖率，发现遗漏及时补测。

---
如有测试相关问题或优化建议，请在本目录下补充说明或联系维护者。 