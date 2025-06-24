from src.infrastructure.strategy.strategy_repository import StrategyRepository
from src.domain.strategy.performance_strategy import PerformanceStrategy
import pandas as pd
from typing import Optional

class PerformanceTuningService:
    """
    性能调优服务：自动分析集成报告，根据结果智能调整线程数/循环次数，更新参数策略配置
    """
    def __init__(self, strategy_repo: Optional[StrategyRepository] = None):
        self.strategy_repo = strategy_repo or StrategyRepository()

    def analyze_and_tune(self, integrated_report_path: str, success_threshold: float = 95.0, max_avg_resp_ms: float = 2000.0):
        """
        分析集成报告，根据成功率和平均响应时间自动调整参数，并更新策略配置
        :param integrated_report_path: 集成报告CSV路径
        :param success_threshold: 成功率阈值，低于此值则降低压力
        :param max_avg_resp_ms: 平均响应时间阈值，超出则降低压力
        """
        # 读取当前策略
        strategy = self.strategy_repo.load()
        # 读取集成报告
        df = pd.read_csv(integrated_report_path, encoding='utf-8')
        # 记录本次测试历史
        history_entry = df.to_dict(orient='records')
        strategy.history.append({'report': integrated_report_path, 'data': history_entry})
        # 简单调优算法：
        # 1. 找到成功率最高且平均响应时间最低的组合，作为last_optimal
        # 2. 如果所有组合成功率都低于阈值或响应时间都超阈，则自动降低线程数/循环次数
        best = None
        for row in history_entry:
            try:
                success_rate = float(row.get('成功率(%)', 0))
                avg_resp = float(row.get('平均响应时间(ms)', 0))
                if success_rate >= success_threshold and avg_resp <= max_avg_resp_ms:
                    if not best or avg_resp < float(best.get('平均响应时间(ms)', 1e9)):
                        best = row
            except Exception:
                continue
        if best:
            strategy.last_optimal = {'thread_count': int(best['线程数']), 'loop_count': int(best['循环次数'])}
        else:
            # 没有任何组合达标，自动降低压力（取最小线程数/循环次数）
            if strategy.thread_counts and strategy.loop_counts:
                strategy.last_optimal = {'thread_count': min(strategy.thread_counts), 'loop_count': min(strategy.loop_counts)}
        # 可选：自动调整策略（如递增/递减/二分法等）
        # 这里只做简单示例：如果最优组合已达极限，则可尝试增加压力，否则减少
        # ...可扩展更智能算法...
        # 保存策略
        self.strategy_repo.save(strategy)
        return strategy.last_optimal 