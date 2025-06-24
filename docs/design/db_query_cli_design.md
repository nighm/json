# db_query_cli.py 设计文档

## 1. 架构设计

### 1.1 DDD分层架构

本项目采用领域驱动设计（DDD）的分层架构，分为以下几层：

```
┌─────────────────────────────────────┐
│           Interfaces Layer           │  ← 接口层（CLI、API）
├─────────────────────────────────────┤
│         Application Layer            │  ← 应用层（应用服务、用例）
├─────────────────────────────────────┤
│           Domain Layer               │  ← 领域层（实体、值对象、领域服务）
├─────────────────────────────────────┤
│        Infrastructure Layer          │  ← 基础设施层（数据库、外部服务）
└─────────────────────────────────────┘
```

#### 1.1.1 接口层（Interfaces Layer）
- **职责**: 处理用户输入，展示结果
- **组件**: 
  - `db_query_cli.py` - 命令行界面
  - 参数解析器
  - 结果展示器

#### 1.1.2 应用层（Application Layer）
- **职责**: 协调领域对象，实现用例
- **组件**:
  - `DeviceQueryApplicationService` - 设备查询应用服务
  - `ExportApplicationService` - 导出应用服务
  - 用例协调器

#### 1.1.3 领域层（Domain Layer）
- **职责**: 核心业务逻辑，领域规则
- **组件**:
  - `DeviceQuery` - 设备查询实体
  - `ExportTask` - 导出任务实体
  - `QueryCriteria` - 查询条件值对象
  - `DeviceQueryDomainService` - 领域服务

#### 1.1.4 基础设施层（Infrastructure Layer）
- **职责**: 技术实现，外部依赖
- **组件**:
  - `DeviceQueryRepository` - 设备查询仓储
  - `DatabaseConnection` - 数据库连接
  - `ExportService` - 导出服务

### 1.2 模块依赖关系

```
Interfaces Layer
    ↓
Application Layer
    ↓
Domain Layer
    ↓
Infrastructure Layer
```

- 上层依赖下层
- 领域层不依赖其他层
- 基础设施层实现领域层定义的接口

## 2. 领域模型设计

### 2.1 核心实体

#### 2.1.1 DeviceQuery（设备查询实体）
```python
@dataclass
class DeviceQuery:
    id: str                    # 查询ID
    query_name: str            # 查询名称
    database_config: Dict      # 数据库配置
    table_name: str            # 表名
    filter_conditions: Dict    # 筛选条件
    field_selection: List      # 字段选择
    limit: int                 # 查询限制
    status: QueryStatus        # 查询状态
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
    result_count: int          # 结果数量
    error_message: str         # 错误信息
```

#### 2.1.2 ExportTask（导出任务实体）
```python
@dataclass
class ExportTask:
    id: str                    # 任务ID
    query_id: str              # 关联查询ID
    export_format: ExportFormat # 导出格式
    output_path: str           # 输出路径
    status: QueryStatus        # 任务状态
    created_at: datetime       # 创建时间
    completed_at: datetime     # 完成时间
    file_size: int             # 文件大小
    error_message: str         # 错误信息
```

### 2.2 值对象

#### 2.2.1 QueryCriteria（查询条件值对象）
```python
@dataclass(frozen=True)
class QueryCriteria:
    table_name: str            # 表名
    filter_conditions: Dict    # 筛选条件
    field_selection: List      # 字段选择
    limit: int                 # 查询限制
    offset: int                # 偏移量
    order_by: str              # 排序字段
    order_direction: str       # 排序方向
```

#### 2.2.2 DatabaseConfig（数据库配置值对象）
```python
@dataclass(frozen=True)
class DatabaseConfig:
    host: str                  # 主机地址
    port: int                  # 端口
    user: str                  # 用户名
    password: str              # 密码
    database: str              # 数据库名
    charset: str               # 字符集
    timeout: int               # 超时时间
    max_connections: int       # 最大连接数
```

### 2.3 领域服务

#### 2.3.1 DeviceQueryDomainService
- 创建查询任务
- 验证查询条件
- 计算查询统计信息
- 生成查询摘要

## 3. 数据流设计

### 3.1 查询流程

```
1. 用户输入命令
   ↓
2. CLI解析参数
   ↓
3. 应用服务协调
   ↓
4. 领域服务验证
   ↓
5. 基础设施层执行查询
   ↓
6. 返回结果
   ↓
7. 格式化输出
```

### 3.2 导出流程

```
1. 用户请求导出
   ↓
2. 创建导出任务
   ↓
3. 验证导出条件
   ↓
4. 执行数据导出
   ↓
5. 生成导出文件
   ↓
6. 返回导出结果
```

### 3.3 自动发现流程

```
1. 连接数据库服务器
   ↓
2. 获取数据库列表
   ↓
3. 智能识别设备数据库
   ↓
4. 获取表列表
   ↓
5. 智能识别设备表
   ↓
6. 返回发现结果
```

## 4. 接口设计

### 4.1 命令行接口

#### 4.1.1 基本查询命令
```bash
python db_query_cli.py [OPTIONS]
```

#### 4.1.2 主要参数
- `--host`: 数据库主机地址
- `--port`: 数据库端口
- `--user`: 数据库用户名
- `--password`: 数据库密码
- `--database`: 数据库名称
- `--table`: 表名
- `--limit`: 查询数量限制
- `--filter`: 筛选条件
- `--fields`: 指定查询字段
- `--export-csv`: 导出CSV
- `--export-json`: 导出JSON
- `--analyze-schema`: 分析表结构
- `--auto-discover`: 自动发现

### 4.2 应用服务接口

#### 4.2.1 DeviceQueryApplicationService
```python
class DeviceQueryApplicationService:
    def create_query(self, criteria: QueryCriteria) -> DeviceQuery
    def execute_query(self, query_id: str) -> QueryResult
    def export_data(self, query_id: str, format: str) -> ExportTask
    def analyze_schema(self, table_name: str) -> Dict
    def auto_discover(self) -> Dict
```

## 5. 错误处理策略

### 5.1 错误分类

#### 5.1.1 连接错误
- 数据库连接失败
- 网络超时
- 认证失败

#### 5.1.2 查询错误
- SQL语法错误
- 表不存在
- 字段不存在
- 权限不足

#### 5.1.3 导出错误
- 文件写入失败
- 磁盘空间不足
- 编码错误

### 5.2 错误处理机制

#### 5.2.1 重试机制
- 连接失败自动重试
- 指数退避策略
- 最大重试次数限制

#### 5.2.2 优雅降级
- 部分功能失败不影响整体
- 提供错误恢复建议
- 记录详细错误日志

#### 5.2.3 用户友好提示
- 清晰的错误信息
- 解决建议
- 帮助文档链接

## 6. 安全设计

### 6.1 数据安全
- 密码不在日志中显示
- 支持SSL连接
- 敏感信息加密存储

### 6.2 操作安全
- 删除操作需要确认
- 操作权限验证
- 操作日志记录

### 6.3 输入验证
- 参数格式验证
- SQL注入防护
- 文件路径验证

## 7. 性能设计

### 7.1 查询优化
- 分页查询
- 索引优化建议
- 查询超时控制

### 7.2 内存管理
- 流式处理大数据
- 及时释放资源
- 连接池管理

### 7.3 并发控制
- 连接数限制
- 查询队列
- 资源竞争处理

## 8. 可扩展性设计

### 8.1 插件机制
- 支持自定义导出格式
- 支持自定义查询条件
- 支持自定义数据源

### 8.2 配置管理
- 外部配置文件
- 环境变量支持
- 动态配置更新

### 8.3 监控和日志
- 操作日志记录
- 性能监控
- 错误追踪 