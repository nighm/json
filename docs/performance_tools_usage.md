# 性能测试工具使用指南

## 快速安装

### Windows系统
```powershell
# 以管理员权限运行PowerShell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\tools\install_performance_tools.ps1
```

### Linux/macOS系统
```bash
# 给脚本添加执行权限
chmod +x tools/install_performance_tools.sh

# 运行安装脚本
./tools/install_performance_tools.sh
```

## 工具详细说明

### 1. jPerf - 网络性能测试

#### 功能特点
- 基于JPerf的图形化网络测试工具
- 支持TCP/UDP带宽测试
- 提供延迟、丢包率等网络指标
- 跨平台支持

#### 基本使用
```bash
# 启动jPerf GUI
jperf

# 命令行模式测试带宽
iperf -c server_ip -t 60 -i 1

# 测试UDP带宽
iperf -c server_ip -u -b 100M -t 60
```

#### 在项目中的应用
```python
# 网络性能测试配置
network_test_config = {
    "target_host": "192.168.1.100",
    "port": 5201,
    "duration": 60,
    "bandwidth": "100M",
    "protocol": "tcp"
}
```

### 2. Iometer - 存储I/O性能测试

#### 功能特点
- 专业的存储设备I/O性能测试
- 支持多种I/O模式（随机/顺序读写）
- 可模拟真实工作负载
- 提供详细的性能报告

#### 基本使用
```bash
# 启动Iometer GUI
iometer

# 命令行模式（需要配置文件）
iometer -i config.icf
```

#### 测试场景
- **数据库性能测试**: 模拟数据库读写操作
- **文件服务器测试**: 测试文件系统性能
- **RAID性能评估**: 评估存储阵列性能

### 3. IOzone - 文件系统性能测试

#### 功能特点
- 文件系统性能基准测试
- 支持多种文件大小和访问模式
- 测试随机访问和顺序访问性能
- 生成详细的性能报告

#### 基本使用
```bash
# 基本文件系统测试
iozone -a -n 512M -g 4G -i 0 -i 1 -i 2

# 测试特定文件大小
iozone -s 1G -r 4k -i 0 -i 1

# 生成Excel报告
iozone -a -n 512M -g 4G -i 0 -i 1 -i 2 -Rb report.xls
```

#### 测试参数说明
- `-a`: 自动模式，测试所有文件大小
- `-s`: 起始文件大小
- `-g`: 最大文件大小
- `-i`: 测试类型（0=写, 1=重写, 2=读, 3=重读等）
- `-r`: 记录大小

### 4. Memtester - 内存测试

#### 功能特点
- 内存硬件测试工具
- 检测内存错误和稳定性
- 支持多种测试算法
- 轻量级，资源占用少

#### 基本使用
```bash
# 测试1GB内存
memtester 1G 1

# 测试指定内存范围
memtester 512M 2

# 持续测试直到发现错误
memtester 256M
```

#### 测试算法
- **随机值测试**: 写入随机数据并验证
- **地址测试**: 测试内存地址线
- **移动反转测试**: 检测位翻转错误
- **8位写入测试**: 测试字节级写入

### 5. Netdata - 实时系统监控

#### 功能特点
- 实时系统性能监控
- 低延迟、高精度数据收集
- Web界面展示
- 支持多种数据源

#### 基本使用
```bash
# 启动Netdata
sudo systemctl start netdata

# 访问Web界面
# http://localhost:19999
```

#### 监控指标
- **CPU使用率**: 用户、系统、空闲时间
- **内存使用**: 物理内存、交换空间
- **磁盘I/O**: 读写速度、IOPS
- **网络流量**: 带宽使用、连接数
- **进程监控**: 进程数量、资源使用

### 6. Grafana - 数据可视化

#### 功能特点
- 数据可视化和监控仪表板
- 支持多种数据源
- 丰富的图表类型
- 报警和通知功能

#### 基本使用
```bash
# 启动Grafana
sudo systemctl start grafana-server

# 访问Web界面
# http://localhost:3000
# 默认用户名/密码: admin/admin
```

#### 数据源配置
- **InfluxDB**: 时间序列数据库
- **Prometheus**: 监控数据
- **MySQL/PostgreSQL**: 关系型数据库
- **Elasticsearch**: 日志数据

## 集成到项目

### 1. 配置文件结构
```yaml
# src/config/tools/performance_tools.yaml
tools:
  network:
    jperf:
      enabled: true
      path: "/usr/bin/jperf"
      default_port: 5201
      timeout: 30
  
  storage:
    iometer:
      enabled: true
      path: "/usr/local/bin/iometer"
      max_workers: 4
    
    iozone:
      enabled: true
      path: "/usr/bin/iozone"
      test_size: "1G"
  
  memory:
    memtester:
      enabled: true
      path: "/usr/bin/memtester"
      memory_size: "1G"
  
  monitoring:
    netdata:
      enabled: true
      port: 19999
      config_path: "/etc/netdata"
    
    grafana:
      enabled: true
      port: 3000
      admin_user: admin
      admin_password: admin
```

### 2. CLI命令使用
```bash
# 激活虚拟环境
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/macOS

# 安装工具
python -m src.interfaces.cli.performance_tools_cli install

# 列出可用工具
python -m src.interfaces.cli.performance_tools_cli list

# 运行网络测试
python -m src.interfaces.cli.performance_tools_cli test --tool jperf --config network_test.yaml

# 运行存储测试
python -m src.interfaces.cli.performance_tools_cli test --tool iometer --config storage_test.yaml

# 运行内存测试
python -m src.interfaces.cli.performance_tools_cli test --tool memtester --config memory_test.yaml
```

### 3. 测试配置文件示例

#### 网络测试配置
```yaml
# network_test.yaml
test_type: "network"
tool: "jperf"
parameters:
  target_host: "192.168.1.100"
  port: 5201
  duration: 60
  bandwidth: "100M"
  protocol: "tcp"
  parallel_streams: 4
```

#### 存储测试配置
```yaml
# storage_test.yaml
test_type: "storage"
tool: "iometer"
parameters:
  test_file: "test.dat"
  file_size: "1G"
  access_pattern: "random"
  block_size: "4K"
  read_percentage: 70
  write_percentage: 30
  duration: 300
```

#### 内存测试配置
```yaml
# memory_test.yaml
test_type: "memory"
tool: "memtester"
parameters:
  memory_size: "1G"
  iterations: 1
  test_patterns:
    - "random"
    - "address"
    - "moving_inversions"
```

## 监控和报告

### 1. 实时监控
```bash
# 启动监控服务
sudo systemctl start netdata
sudo systemctl start grafana-server

# 查看监控数据
# Netdata: http://localhost:19999
# Grafana: http://localhost:3000
```

### 2. 生成报告
```python
# 生成性能测试报告
from src.infrastructure.report.report_generator import ReportGenerator

report_generator = ReportGenerator()
report = report_generator.generate_performance_report(
    test_results=test_results,
    tool_name="jperf",
    test_config=config
)
```

### 3. 数据可视化
```python
# 创建Grafana仪表板
from src.infrastructure.monitor.grafana_integration import GrafanaIntegration

grafana = GrafanaIntegration()
dashboard = grafana.create_dashboard({
    "title": "性能测试监控",
    "panels": [
        {
            "title": "网络带宽",
            "type": "graph",
            "targets": [
                {"expr": "network_bandwidth", "legendFormat": "带宽 (Mbps)"}
            ]
        }
    ]
})
```

## 最佳实践

### 1. 测试环境准备
- 确保测试环境干净，避免其他程序干扰
- 关闭不必要的服务和进程
- 记录系统基线性能数据

### 2. 测试执行
- 多次运行测试取平均值
- 在不同时间段进行测试
- 记录测试环境和配置信息

### 3. 结果分析
- 对比不同配置下的性能差异
- 识别性能瓶颈和优化点
- 生成详细的测试报告

### 4. 监控集成
- 实时监控测试过程
- 设置性能报警阈值
- 定期检查系统健康状态

## 故障排除

### 1. 常见问题
- **权限不足**: 使用管理员权限运行
- **端口冲突**: 修改默认端口配置
- **依赖缺失**: 安装必要的依赖包

### 2. 日志查看
```bash
# 查看Netdata日志
sudo journalctl -u netdata -f

# 查看Grafana日志
sudo journalctl -u grafana-server -f

# 查看系统日志
sudo journalctl -f
```

### 3. 性能调优
- 调整系统参数优化性能
- 配置合适的测试参数
- 监控系统资源使用情况

## 总结

通过以上工具的组合使用，可以全面评估系统的网络、存储、内存性能，并通过实时监控和可视化展示测试结果。这些工具与现有的DDD架构项目完美集成，为性能测试提供专业级的支持。 