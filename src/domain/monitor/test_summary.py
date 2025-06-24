from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TestSummary:
    """测试概览值对象"""
    test_name: str
    concurrent_users: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sample_interval: Optional[int] = None
    notes: Optional[str] = None 