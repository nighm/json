# 终端压测系统开发计划

## 📊 项目概览

基于DDD架构的终端接口性能测试系统，支持多接口并发测试、自动化报告生成和智能参数调优。

**核心特性：**
- 🚀 多接口并发测试（9个接口模板）
- 📊 自动化报告生成（CSV/Excel多sheet）
- 🔧 智能参数调优
- 📁 时间戳归档管理
- 🎯 真实数据驱动测试

## ✅ 已完成功能

### 🏗️ 核心系统
| 模块 | 功能 | 状态 |
|------|------|------|
| **CLI入口** | `performance_test_cli.py` - 统一测试入口 | ✅ |
| **JMeter执行器** | `jmeter_executor.py` - 自动化测试执行 | ✅ |
| **JMX处理器** | `jmx_handler.py` - 动态参数化 | ✅ |
| **结果分析器** | `test_analyzer.py` - 统计分析 | ✅ |
| **报告生成器** | `report_generator.py` - 多格式报告 | ✅ |

### ⚙️ 配置管理
| 功能 | 描述 | 状态 |
|------|------|------|
| **统一配置** | `config_manager.py` - YAML配置管理 | ✅ |
| **环境支持** | 开发/测试/生产环境配置 | ✅ |
| **向后兼容** | 现有代码无缝迁移 | ✅ |

### 📊 数据管理
| 功能 | 描述 | 状态 |
|------|------|------|
| **数据库操作** | `db_query_cli.py` - 真实数据获取 | ✅ |
| **设备生成器** | `device_generator_cli.py` - 批量设备数据 | ✅ |
| **参数化JMX** | `parameterized_jmx_service.py` - 自动化参数化 | ✅ |

### 📈 报告系统
| 功能 | 描述 | 状态 |
|------|------|------|
| **Excel多sheet** | 每个接口独立sheet | ✅ |
| **时间戳归档** | 每次执行独立目录 | ✅ |
| **智能调优** | `performance_tuning_service.py` - 自动参数优化 | ✅ |
| **多格式输出** | CSV/Excel/JSON支持 | ✅ |

### 🔌 接口支持
| 接口 | 状态 | 说明 |
|------|------|------|
| **终端注册** | ✅ 已完成 | 双重验证机制，大规模压测 |
| **获取策略** | ✅ | 复用注册设备信息 |
| **心跳接口** | ✅ | 基础性能测试 |
| **设备信息** | 📋 | 待开发 |
| **模式设置** | 📋 | 待开发 |
| **品牌设置** | 📋 | 待开发 |
| **内生守护** | 📋 | 待开发 |
| **Logo设置** | 📋 | 待开发 |
| **MQTT地址** | 📋 | 待开发 |

## ✅ Register双重验证机制 - 已完成

### 🎯 项目背景
Register接口测试已支持大规模压测（1000-10000台设备），并实现了数据唯一性与注册结果双重验证机制。

### 📋 实现要点
- **数据唯一性保证**：每次测试自动生成唯一设备数据，已用设备自动标记，防止重复注册。
- **配置驱动测试**：线程数、循环次数等参数全部由`jmeter.yaml`动态读取。
- **双重验证机制**：测试后自动对比理论注册结果与数据库实际注册状态，输出详细差异分析。
- **统一CLI体验**：register测试与其他接口命令一致，支持一条命令全自动完成。
- **大规模压测支持**：支持1000-10000台设备注册，自动分配数据、归档结果。

### 🔧 需要完善的具体任务

#### 1. SN和MAC双重唯一性检查 ✅ 已完成
- [x] **改进used_devices.json结构**：同时记录SN和MAC地址
  ```json
  {
    "used_devices": {
      "deviceSerialNumber": ["SN_REGISTER_00000001"],
      "mac": ["AA:BB:CC:01:02:03"]
    }
  }
  ```
- [x] **修改DeviceDataManager**：生成设备时同时检查SN和MAC唯一性
- [x] **修改DeviceGeneratorService**：确保SN和MAC生成算法不重复
- [x] **修复循环依赖问题**：延迟加载机制，避免初始化时的循环调用

#### 2. 实际已使用设备数据库查询 ✅ 已完成
- [x] **新增actual_used_devices.json**：记录数据库真实注册的设备
  ```json
  {
    "actual_registrations": {
      "deviceSerialNumber": ["SN_REGISTER_00000001"],
      "mac": ["AA:BB:CC:01:02:03"],
      "device_ids": ["device_id_1"]
    },
    "verification_results": {
      "theoretical_count": 1000,
      "actual_count": 998,
      "missing_devices": ["SN_REGISTER_00000002"],
      "success_rate": 99.8
    }
  }
  ```
- [x] **完善RegisterVerificationService**：实现数据库查询逻辑
- [x] **添加数据库查询接口**：根据SN和MAC查询真实注册设备

#### 3. 理论vs实际对比分析 ✅ 已完成
- [x] **差异分析算法**：对比理论注册vs实际注册的设备
- [x] **丢失设备识别**：找出理论成功但实际未注册的设备
- [x] **重复注册检测**：识别重复注册的情况
- [x] **数据质量报告**：生成详细的数据质量分析报告

#### 4. 数据清理和恢复机制 ⚠️ 待完善
- [ ] **安全数据清理**：基于actual_used_devices.json清理未成功注册的设备
- [ ] **数据恢复功能**：从数据库恢复真实设备状态
- [ ] **备份和恢复**：防止数据文件被误删或损坏

#### 5. CLI命令扩展 ⚠️ 待完善
- [ ] **设备状态查询命令**：查看当前设备使用状态
- [ ] **数据清理命令**：清理未成功注册的设备数据
- [ ] **验证报告命令**：单独生成验证报告
- [ ] **数据库同步命令**：同步数据库真实状态到本地文件

### 🏗️ 技术架构与流程
- 设备数据管理：`DeviceDataManager`，负责唯一设备生成、状态跟踪、数据归档。
- 注册验证服务：`RegisterVerificationService`，负责理论与实际注册结果对比、差异分析、报告生成。
- CLI集成：`performance_test_cli.py`，一条命令自动完成设备准备、JMX注入、压测、验证、报告归档。

### 🚀 CLI用法示例
```bash
# 终端注册接口压测与双重验证（全自动）
python src/interfaces/cli/performance_test_cli.py --test-type register --thread-counts 1000 --loop-counts 1

# 生成Excel多sheet报告
python src/interfaces/cli/performance_test_cli.py --test-type register --excel-report

# 待实现：设备状态查询
python src/interfaces/cli/device_status_cli.py --query-status

# 待实现：数据清理
python src/interfaces/cli/device_cleanup_cli.py --clean-unused

# 待实现：验证报告生成
python src/interfaces/cli/verification_report_cli.py --generate-report
```

### 📁 数据与报告归档说明
- 设备数据文件：`data/generated_devices/devices_时间戳_数量.csv`
- 设备元信息：`data/device_metadata.json`
- 理论已用设备记录：`data/used_devices.json` ⚠️ 需要改进结构
- 实际已用设备记录：`data/actual_used_devices.json` ⚠️ 需要新增
- 验证日志：`data/verification_log.json`
- 验证报告：`data/verification_reports/时间戳_verification.json`
- 所有测试结果、报告均自动归档到以时间戳命名的独立目录，便于追溯与分析。

### 📈 典型验证报告格式
```json
{
  "test_id": "20250618_181533",
  "test_summary": {
    "total_devices_tested": 1000,
    "theoretical_success": 998,
    "actual_success": 995,
    "verification_time": "2025-06-18 18:20:00"
  },
  "theoretical_registrations": ["device_id_1", ...],
  "actual_registrations": ["device_id_1", ...],
  "differences": {
    "missing_in_database": ["device_id_3"],
    "unexpected_in_database": ["device_id_5"]
  },
  "analysis": {
    "success_rate_theoretical": 99.8,
    "success_rate_actual": 99.5,
    "data_loss_rate": 0.3,
    "duplicate_rate": 0.0
  }
}
```

---

## 🔄 当前进行中

### 📝 参数说明文档系统
- [x] **实体定义** - `parameter_doc.py` 数据结构
- [x] **服务实现** - `parameter_doc_service.py` 生成服务
- [ ] **流程集成** - 测试完成后自动生成
- [ ] **多格式输出** - CSV/Excel格式支持

## 📋 待开发功能

### 🔌 接口测试模块
- [ ] 获取终端设备信息接口
- [ ] 获取终端模式设置接口  
- [ ] 获取终端品牌设置接口
- [ ] 获取终端内生守护设置接口
- [ ] 获取终端logo设置接口
- [ ] 获取MQTT服务器地址接口

### ⚡ 系统优化
- [ ] JMX模板精简与参数核查
- [ ] 前置条件接口管理
- [ ] 批量测试执行优化
- [ ] 错误处理机制完善
- [ ] 虚拟环境管理

### 📊 报告增强
- [ ] 中文报告模板优化
- [ ] 直方图显示优化
- [ ] 多维度数据分析

## 🎯 开发里程碑

| 阶段 | 目标 | 状态 | 预计时间 |
|------|------|------|----------|
| **🔥 Register重构** | 双重验证机制 | ✅ 已完成 | 3天 |
| **第一阶段** | 基础功能完善 | ✅ 已完成 | 3天 |
| **第二阶段** | 功能扩展 | 🔄 进行中 | 2天 |
| **第三阶段** | 系统优化 | 📋 待开始 | 2天 |
| **第四阶段** | 生产就绪 | 📋 待开始 | 1天 |

## 🚀 快速开始

### 环境准备
```bash
# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 常用命令
```bash
# 心跳接口测试
python src/interfaces/cli/performance_test_cli.py --test-type heartbeat --thread-counts 2 --loop-counts 3

# 生成Excel报告
python src/interfaces/cli/performance_test_cli.py --test-type heartbeat --excel-report

# 设备信息生成
python src/interfaces/cli/device_generator_cli.py --count 100 --output csv

# 数据库查询
python src/interfaces/cli/db_query_cli.py --export csv

# 参数化JMX生成
python src/interfaces/cli/parameterized_jmx_cli.py --interface register
```

## 📐 技术规范

### 🏗️ 架构原则
- **DDD架构** - 领域驱动设计，分层清晰
- **src目录管理** - 代码与文档分离
- **依赖倒置** - main.py只调用interfaces层
- **模块化设计** - 统一命名规范

### ⚙️ 配置规范
- **YAML格式** - 统一配置文件
- **环境支持** - 多环境配置
- **默认配置** - JMX模板默认参数
- **向后兼容** - 无缝迁移

### 📊 报告规范
- **命名格式** - `性能接口测试_对外整合版_XXX_YYY.CSV`
- **多sheet支持** - Excel报告，接口分sheet
- **时间戳归档** - `YYYYMMDD_HHMMSS` 独立目录
- **多格式输出** - CSV/Excel/JSON

### 🧪 测试规范
- **参数化测试** - CSV DataSet读取设备信息
- **唯一性保证** - 每线程唯一设备
- **批量测试** - 多线程数、多循环次数组合
- **中文支持** - JMeter语言zh_CN

## 📝 开发原则

1. **避免重复** - 优先复用现有功能
2. **结构清晰** - 遵循DDD架构
3. **结果可复现** - 测试稳定可靠
4. **错误处理** - 异常情况明确处理
5. **文档同步** - 保持文档更新
6. **用户偏好** - 符合项目规范

## 📈 项目成果

### 🎯 核心指标
- **9个接口模板** - 覆盖主要终端接口
- **自动化程度** - 90%+ 自动化测试流程
- **报告格式** - 3种格式（CSV/Excel/JSON）
- **配置灵活性** - 支持多环境、多参数组合

### 🏆 技术亮点
- **真实数据驱动** - 基于数据库真实设备信息
- **智能参数调优** - 自动分析并优化测试参数
- **时间戳归档** - 历史结果完整保存
- **多sheet报告** - 接口数据清晰分离

---

**最后更新：** 2025-06-18  
**项目状态：** Register双重验证机制已完成，进入功能扩展与系统优化阶段。