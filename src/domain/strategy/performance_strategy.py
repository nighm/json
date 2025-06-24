from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PerformanceStrategy:
    """
    性能参数策略实体，描述推荐的线程数、循环次数、历史最优等
    """
    thread_counts: List[int] = field(default_factory=list)  # 推荐线程数列表
    loop_counts: List[int] = field(default_factory=list)    # 推荐循环次数列表
    last_optimal: Optional[dict] = None  # 历史最优参数，如 {'thread_count': 1000, 'loop_count': 500}
    history: List[dict] = field(default_factory=list)       # 每次测试的历史参数与结果记录 