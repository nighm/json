from dataclasses import dataclass
from typing import List, Tuple
from datetime import datetime

@dataclass
class HardwareMetrics:
    """硬件指标值对象"""
    max_cpu: float
    min_cpu: float
    avg_cpu: float
    p90_cpu: float
    p95_cpu: float
    cpu_change_rate: float
    records: List[Tuple[datetime, float]]
    
    @property
    def sample_count(self) -> int:
        """采样点数"""
        return len(self.records)
    
    @property
    def start_time(self) -> datetime:
        """采集开始时间"""
        return self.records[0][0] if self.records else None
    
    @property
    def end_time(self) -> datetime:
        """采集结束时间"""
        return self.records[-1][0] if self.records else None 