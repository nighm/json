from dataclasses import dataclass
from typing import List, Optional
from .hardware_metrics import HardwareMetrics
from .test_summary import TestSummary

@dataclass
class HardwareMonitorReport:
    """硬件监控报告实体"""
    summary: TestSummary
    metrics: HardwareMetrics
    conclusion: Optional[str] = None
    recommendations: Optional[List[str]] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于生成报告"""
        return {
            'summary': {
                'test_name': self.summary.test_name,
                'concurrent_users': self.summary.concurrent_users,
                'start_time': self.summary.start_time,
                'end_time': self.summary.end_time,
                'sample_interval': self.summary.sample_interval,
                'notes': self.summary.notes
            },
            'metrics': {
                'max_cpu': self.metrics.max_cpu,
                'min_cpu': self.metrics.min_cpu,
                'avg_cpu': self.metrics.avg_cpu,
                'p90_cpu': self.metrics.p90_cpu,
                'p95_cpu': self.metrics.p95_cpu,
                'cpu_change_rate': self.metrics.cpu_change_rate,
                'sample_count': self.metrics.sample_count
            },
            'conclusion': self.conclusion,
            'recommendations': self.recommendations
        } 