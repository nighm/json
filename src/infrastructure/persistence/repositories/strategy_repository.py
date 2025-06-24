import yaml
from pathlib import Path
from src.domain.strategy.performance_strategy import PerformanceStrategy

class StrategyRepository:
    """
    性能参数策略持久化仓库，负责读写YAML配置文件
    """
    def __init__(self, config_path: str = 'performance_params.yaml'):
        self.config_path = Path(config_path)

    def load(self) -> PerformanceStrategy:
        """
        加载参数策略配置
        """
        if not self.config_path.exists():
            # 文件不存在则返回空策略
            return PerformanceStrategy()
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        return PerformanceStrategy(
            thread_counts=data.get('thread_counts', []),
            loop_counts=data.get('loop_counts', []),
            last_optimal=data.get('last_optimal'),
            history=data.get('history', [])
        )

    def save(self, strategy: PerformanceStrategy):
        """
        保存参数策略配置
        """
        data = {
            'thread_counts': strategy.thread_counts,
            'loop_counts': strategy.loop_counts,
            'last_optimal': strategy.last_optimal,
            'history': strategy.history
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True) 