# 自动化接口测试与压力测试开发计划

## 1. 项目初始化
- [x] 明确需求与目标
- [x] 收集接口、Redis、认证等关键信息
- [ ] 初始化Python项目结构

## 2. 自动化登录流程开发
- [ ] 实现UUID获取接口自动请求
- [ ] 实现Redis自动查找验证码
- [ ] 实现自动登录并获取token
- [ ] token自动注入后续请求

## 3. 目标接口功能性自动化测试
- [ ] 实现心跳接口自动化测试
- [ ] 实现在线时长相关接口自动化测试
- [ ] 结果输出与校验

## 4. 压力测试开发
- [ ] 设计并实现可配置的并发压测脚本（如1000/5000/10000/50000/100000/500000）
- [ ] 支持多接口压测与性能统计
- [ ] 结果自动汇总与报告

## 5. 项目文档与交付
- [ ] 详细注释与使用说明
- [ ] 交付可运行脚本与完整文档

---

### 进度说明
- 当前阶段：项目初始化与需求梳理
- 正在进行：项目结构搭建、自动化脚本设计
- 下一步：实现自动化登录与接口测试主流程
- 已完成：需求确认、关键信息收集
- 待完成：功能性测试、压力测试、文档完善

# 昆仑卫士性能测试与设备管理平台

## 项目简介

这是一个基于领域驱动设计（DDD）架构的综合性性能测试与设备管理平台，主要用于昆仑卫士产品的API性能测试、设备数据管理和资源监控。

## 项目架构

项目采用DDD（领域驱动设计）架构，分为以下层次：

```
src/
├── domain/           # 领域层：核心业务逻辑和实体
├── application/      # 应用层：业务用例和协调服务
├── infrastructure/   # 基础设施层：外部依赖和技术实现
└── interfaces/       # 接口层：用户界面和API接口
```

## 主要功能模块

### 1. 性能测试模块
- **JMeter自动化测试**：支持批量执行JMX测试计划
- **性能数据收集**：自动收集响应时间、吞吐量等指标
- **测试报告生成**：生成详细的性能测试报告和图表

### 2. 设备管理模块
- **设备数据生成**：批量生成测试设备数据
- **设备查询服务**：支持多维度设备信息查询
- **设备标识管理**：统一的设备标识生成和管理

### 3. 资源监控模块
- **系统资源监控**：CPU、内存、磁盘、网络监控
- **性能指标分析**：资源使用趋势分析和报告
- **实时监控**：支持实时资源监控和告警

### 4. API测试模块
- **接口自动化测试**：支持多种API测试工具
- **测试用例管理**：统一的测试用例配置和管理
- **测试结果分析**：详细的测试结果分析和报告

## 项目结构

```
├── src/                          # 源代码目录
│   ├── domain/                   # 领域层
│   │   ├── entities/             # 实体
│   │   ├── services/             # 领域服务
│   │   ├── value_objects/        # 值对象
│   │   └── strategy/             # 策略
│   ├── application/              # 应用层
│   │   ├── services/             # 应用服务
│   │   ├── jmeter/               # JMeter相关服务
│   │   └── monitor/              # 监控服务
│   ├── infrastructure/           # 基础设施层
│   │   ├── persistence/          # 持久化
│   │   ├── external/             # 外部服务
│   │   ├── services/             # 基础设施服务
│   │   └── cross_cutting/        # 横切关注点
│   └── interfaces/               # 接口层
│       └── cli/                  # 命令行接口
├── config/                       # 配置文件
├── docs/                         # 文档
├── scripts/                      # 脚本文件
├── tests/                        # 测试文件
└── tools/                        # 工具目录（本地使用）
```

## 快速开始

### 环境要求

- Python 3.11+
- Windows 10/11
- 8GB+ RAM

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd json
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境**
   - 复制 `config/core/project.yaml.example` 为 `config/core/project.yaml`
   - 根据需要修改配置文件

### 使用示例

#### 1. 执行性能测试
```bash
# 激活虚拟环境
venv\Scripts\activate

# 执行性能测试
python src/interfaces/cli/performance_test_cli.py --jmx heartbeat --threads 10 --loops 100
```

#### 2. 生成设备数据
```bash
# 生成测试设备数据
python src/interfaces/cli/device_generator_cli.py --count 100 --brand huawei
```

#### 3. 监控系统资源
```bash
# 启动资源监控
python src/interfaces/cli/resource_monitor_cli.py --duration 300 --interval 5
```

## 配置说明

### 主要配置文件

- `config/core/project.yaml`：项目全局配置
- `config/core/database.yaml`：数据库配置
- `config/core/logging.yaml`：日志配置
- `config/api/endpoints.yaml`：API端点配置
- `config/test/cases.yaml`：测试用例配置

### 环境变量

- `PROJECT_ENV`：项目环境（dev/test/prod）
- `LOG_LEVEL`：日志级别
- `DATABASE_URL`：数据库连接字符串

## 开发指南

### 代码规范

- 遵循PEP 8 Python代码规范
- 使用类型注解
- 编写详细的文档字符串
- 遵循DDD架构原则

### 测试

```bash
# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行所有测试
pytest tests/
```

### 文档生成

```bash
# 生成API文档
python scripts/generate_api_docs.py

# 生成项目文档
python scripts/generate_project_docs.py
```

## 部署说明

### 生产环境部署

1. **环境准备**
   - 安装Python 3.11+
   - 配置数据库
   - 设置环境变量

2. **应用部署**
   ```bash
   # 安装依赖
   pip install -r requirements.txt

   # 初始化数据库
   python scripts/init_database.py

   # 启动应用
   python src/interfaces/main.py
   ```

### Docker部署

```bash
# 构建镜像
docker build -t kunlun-performance-test .

# 运行容器
docker run -d -p 8000:8000 kunlun-performance-test
```

## 常见问题

### Q: 如何修改JMeter测试配置？
A: 编辑 `config/test/jmeter.yaml` 文件，修改相应的配置参数。

### Q: 如何添加新的API测试接口？
A: 在 `config/api/endpoints.yaml` 中添加新的端点配置，然后在 `src/application/services/` 中实现相应的服务。

### Q: 如何自定义设备数据生成规则？
A: 修改 `src/domain/value_objects/bulk_device_generator.py` 中的生成逻辑。

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目维护者：[您的姓名]
- 邮箱：[您的邮箱]
- 项目地址：[GitHub仓库地址]

## 更新日志

### v1.0.0 (2025-01-XX)
- 初始版本发布
- 实现基础性能测试功能
- 实现设备数据管理功能
- 实现资源监控功能
