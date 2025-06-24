# db_query_cli.py 接口文档

## 1. 命令行接口（CLI）

### 1.1 基本语法

```bash
python db_query_cli.py [OPTIONS]
```

### 1.2 参数说明

#### 1.2.1 数据库连接参数

| 参数 | 类型 | 默认值 | 必填 | 描述 |
|------|------|--------|------|------|
| `--host` | string | 192.168.24.45 | 否 | 数据库主机地址 |
| `--port` | integer | 3307 | 否 | 数据库端口 |
| `--user` | string | root | 否 | 数据库用户名 |
| `--password` | string | At6mj*1ygb2 | 否 | 数据库密码 |
| `--database` | string | - | 否 | 数据库名称（留空则自动发现） |

#### 1.2.2 查询参数

| 参数 | 类型 | 默认值 | 必填 | 描述 |
|------|------|--------|------|------|
| `--table` | string | biz_device | 否 | 查询的表名（留空则自动发现） |
| `--limit` | integer | 10 | 否 | 查询数量限制 |
| `--filter` | string | - | 否 | 筛选条件，格式：字段名=值 |
| `--fields` | string | - | 否 | 指定查询字段，用逗号分隔 |

#### 1.2.3 导出参数

| 参数 | 类型 | 默认值 | 必填 | 描述 |
|------|------|--------|------|------|
| `--export-csv` | flag | false | 否 | 导出为CSV文件 |
| `--export-json` | flag | false | 否 | 导出为JSON文件 |
| `--output-file` | string | - | 否 | 输出文件名（不含扩展名） |

#### 1.2.4 功能参数

| 参数 | 类型 | 默认值 | 必填 | 描述 |
|------|------|--------|------|------|
| `--analyze-schema` | flag | false | 否 | 分析表结构 |
| `--auto-discover` | flag | false | 否 | 自动发现数据库和表 |
| `--delete` | flag | false | 否 | 删除符合条件的设备 |
| `--delete-count` | integer | - | 否 | 删除数量限制 |
| `--confirm` | flag | false | 否 | 确认删除操作 |

### 1.3 使用示例

#### 1.3.1 基本查询
```bash
# 查询前10条设备信息
python db_query_cli.py --limit 10

# 查询指定条件的设备
python db_query_cli.py --filter "brand=华为" --limit 50

# 查询指定字段
python db_query_cli.py --fields "id,name,brand,status" --limit 20
```

#### 1.3.2 自动发现模式
```bash
# 自动发现数据库和表
python db_query_cli.py --auto-discover

# 自动发现并导出
python db_query_cli.py --auto-discover --export-json
```

#### 1.3.3 数据导出
```bash
# 导出为CSV
python db_query_cli.py --export-csv --output-file my_devices

# 导出为JSON
python db_query_cli.py --export-json --output-file my_devices

# 同时导出多种格式
python db_query_cli.py --export-csv --export-json --output-file my_devices
```

#### 1.3.4 表结构分析
```bash
# 分析表结构
python db_query_cli.py --analyze-schema --table biz_device
```

#### 1.3.5 数据删除
```bash
# 删除指定条件的设备（需要确认）
python db_query_cli.py --delete --filter "status=inactive" --confirm

# 限制删除数量
python db_query_cli.py --delete --filter "brand=测试" --delete-count 10 --confirm
```

### 1.4 输出格式

#### 1.4.1 控制台输出
```
=== 使用配置 ===
数据库: yangguan
表: biz_device
主机: 192.168.24.45:3307
用户: root

正在查询表 biz_device 的设备信息...
找到 10 条设备信息:
--------------------------------------------------------------------------------
设备 1:
  id: 1
  name: 设备001
  brand: 华为
  status: active
  ...

=== 统计信息 ===
总设备数: 10
品牌分布:
  华为: 5台
  小米: 3台
  苹果: 2台
```

#### 1.4.2 CSV导出格式
```csv
id,name,brand,status,created_at
1,设备001,华为,active,2025-01-01 10:00:00
2,设备002,小米,inactive,2025-01-01 11:00:00
...
```

#### 1.4.3 JSON导出格式
```json
[
  {
    "id": 1,
    "name": "设备001",
    "brand": "华为",
    "status": "active",
    "created_at": "2025-01-01T10:00:00"
  },
  {
    "id": 2,
    "name": "设备002",
    "brand": "小米",
    "status": "inactive",
    "created_at": "2025-01-01T11:00:00"
  }
]
```

## 2. 应用服务接口（API）

### 2.1 DeviceQueryApplicationService

#### 2.1.1 创建查询
```python
def create_query(
    self, 
    query_name: str,
    database_config: Dict[str, Any],
    table_name: str,
    filter_conditions: Optional[Dict[str, Any]] = None,
    field_selection: Optional[List[str]] = None,
    limit: Optional[int] = None
) -> DeviceQuery
```

**参数说明**:
- `query_name`: 查询名称
- `database_config`: 数据库配置字典
- `table_name`: 表名
- `filter_conditions`: 筛选条件
- `field_selection`: 字段选择列表
- `limit`: 查询限制

**返回值**: DeviceQuery实体

#### 2.1.2 执行查询
```python
def execute_query(
    self, 
    query_id: str
) -> QueryResult
```

**参数说明**:
- `query_id`: 查询ID

**返回值**: QueryResult值对象

#### 2.1.3 导出数据
```python
def export_data(
    self, 
    query_id: str, 
    export_format: str, 
    output_path: str
) -> ExportTask
```

**参数说明**:
- `query_id`: 查询ID
- `export_format`: 导出格式（csv/json）
- `output_path`: 输出路径

**返回值**: ExportTask实体

#### 2.1.4 分析表结构
```python
def analyze_schema(
    self, 
    table_name: str
) -> Dict[str, Any]
```

**参数说明**:
- `table_name`: 表名

**返回值**: 表结构信息字典

#### 2.1.5 自动发现
```python
def auto_discover(
    self
) -> Dict[str, Any]
```

**返回值**: 发现结果字典

### 2.2 领域服务接口

#### 2.2.1 DeviceQueryDomainService

```python
class DeviceQueryDomainService:
    @staticmethod
    def create_query(...) -> DeviceQuery
    
    @staticmethod
    def validate_query_criteria(criteria: QueryCriteria) -> List[str]
    
    @staticmethod
    def create_export_task(...) -> ExportTask
    
    @staticmethod
    def calculate_query_statistics(query_results: List[Dict[str, Any]]) -> Dict[str, Any]
    
    @staticmethod
    def generate_query_summary(query: DeviceQuery, result_count: int) -> Dict[str, Any]
    
    @staticmethod
    def validate_database_config(config: Dict[str, Any]) -> List[str]
```

### 2.3 仓储接口

#### 2.3.1 DeviceQueryRepository

```python
class DeviceQueryRepository:
    def get_devices(
        self, 
        table_name: str,
        limit: Optional[int] = None,
        filter_condition: Optional[str] = None,
        fields: Optional[str] = None
    ) -> List[Any]
    
    def get_device_count(
        self, 
        table_name: str,
        filter_condition: Optional[str] = None
    ) -> int
    
    def discover_databases(self) -> List[str]
    
    def discover_tables(self) -> List[str]
    
    def analyze_table_schema(self, table_name: str) -> Dict[str, Any]
    
    def delete_devices(
        self,
        table_name: str,
        filter_condition: Optional[str] = None,
        limit: Optional[int] = None
    ) -> int
```

## 3. 错误码和错误信息

### 3.1 连接错误

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| CONN_001 | 数据库连接失败 | 检查主机地址、端口、用户名、密码 |
| CONN_002 | 网络超时 | 检查网络连接，增加超时时间 |
| CONN_003 | 认证失败 | 检查用户名和密码 |
| CONN_004 | 数据库不存在 | 检查数据库名称 |

### 3.2 查询错误

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| QUERY_001 | 表不存在 | 检查表名是否正确 |
| QUERY_002 | 字段不存在 | 检查字段名是否正确 |
| QUERY_003 | SQL语法错误 | 检查筛选条件格式 |
| QUERY_004 | 权限不足 | 检查数据库用户权限 |

### 3.3 导出错误

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| EXPORT_001 | 文件写入失败 | 检查输出路径权限 |
| EXPORT_002 | 磁盘空间不足 | 清理磁盘空间 |
| EXPORT_003 | 编码错误 | 检查字符编码设置 |

## 4. 配置说明

### 4.1 默认配置

```python
DEFAULT_CONFIG = {
    'host': '192.168.24.45',
    'port': 3307,
    'user': 'root',
    'password': 'At6mj*1ygb2',
    'database': 'yangguan',
    'table': 'biz_device',
    'limit': 10,
    'charset': 'utf8mb4',
    'timeout': 30
}
```

### 4.2 环境变量

| 环境变量 | 描述 | 默认值 |
|----------|------|--------|
| `DB_HOST` | 数据库主机 | 192.168.24.45 |
| `DB_PORT` | 数据库端口 | 3307 |
| `DB_USER` | 数据库用户 | root |
| `DB_PASSWORD` | 数据库密码 | At6mj*1ygb2 |
| `DB_DATABASE` | 数据库名称 | yangguan |

### 4.3 配置文件

支持YAML格式的配置文件：

```yaml
database:
  host: 192.168.24.45
  port: 3307
  user: root
  password: At6mj*1ygb2
  database: yangguan
  charset: utf8mb4
  timeout: 30

query:
  default_limit: 10
  default_table: biz_device

export:
  default_output_dir: data/device_samples
  default_encoding: utf-8
```

## 5. 最佳实践

### 5.1 性能优化

1. **使用索引**: 确保查询字段有适当的索引
2. **限制查询数量**: 使用 `--limit` 参数限制返回结果
3. **分页查询**: 对于大数据量，使用分页查询
4. **字段选择**: 只查询需要的字段，减少数据传输

### 5.2 安全建议

1. **密码保护**: 不要在命令行中直接输入密码
2. **权限控制**: 使用最小权限原则
3. **输入验证**: 验证所有用户输入
4. **日志记录**: 记录重要操作日志

### 5.3 错误处理

1. **优雅降级**: 部分功能失败不影响整体
2. **重试机制**: 对临时错误进行重试
3. **用户友好**: 提供清晰的错误信息和解决建议
4. **日志记录**: 记录详细错误信息用于调试 