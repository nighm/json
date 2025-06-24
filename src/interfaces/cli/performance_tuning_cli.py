import argparse
from src.application.services.performance_tuning_service import PerformanceTuningService


def main():
    parser = argparse.ArgumentParser(description='JMeter性能测试智能调优闭环入口')
    parser.add_argument('--report', type=str, required=True, help='集成报告CSV文件路径')
    parser.add_argument('--success-threshold', type=float, default=95.0, help='成功率阈值，低于此值则降低压力')
    parser.add_argument('--max-avg-resp-ms', type=float, default=2000.0, help='平均响应时间阈值，超出则降低压力')
    args = parser.parse_args()

    # 实例化性能调优服务
    tuning_service = PerformanceTuningService()
    # 调用分析与调优
    optimal = tuning_service.analyze_and_tune(
        integrated_report_path=args.report,
        success_threshold=args.success_threshold,
        max_avg_resp_ms=args.max_avg_resp_ms
    )
    print('【智能调优结果】')
    print(f'推荐线程数: {optimal.get("thread_count")}, 推荐循环次数: {optimal.get("loop_count")}')
    print('策略已自动更新。')

if __name__ == '__main__':
    main() 