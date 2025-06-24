from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class TestResult:
    """测试结果实体类，包含所有报告所需核心指标"""
    test_name: str  # 测试名称
    thread_count: int  # 线程数
    iterations: int  # 循环次数
    total_requests: int  # 总请求数
    success_count: int  # 成功数
    fail_count: int  # 失败数
    success_rate: float  # 成功率（%）
    min_resp_time: float  # 最小响应时间(ms)
    max_resp_time: float  # 最大响应时间(ms)
    avg_resp_time: float  # 平均响应时间(ms)
    tp90_resp_time: float  # TP90响应时间(ms)
    tp99_resp_time: float  # TP99响应时间(ms)
    start_time: datetime  # 开始时间
    end_time: datetime  # 结束时间
    duration: float  # 执行时长(秒)
    report_path: str  # 报告路径
    success: bool  # 是否成功
    server_cpu: Optional[str] = '-'  # 服务端CPU使用率（可选）
    registered_count: Optional[int] = None  # 实际注册数量
    cpu_stats: Optional[Dict[str, Any]] = field(default=None)  # CPU监控数据
    memory_stats: Optional[Dict[str, Any]] = field(default=None)  # 内存监控数据
    disk_stats: Optional[Dict[str, Any]] = field(default=None)  # 硬盘监控数据
    
    @property
    def execution_time(self) -> float:
        """计算执行时间"""
        return (self.end_time - self.start_time).total_seconds() 