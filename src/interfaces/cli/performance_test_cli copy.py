import argparse
from pathlib import Path
import sys
import os

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from src.application.services.performance_test_service import PerformanceTestService
from src.domain.entities.test_config import TestConfig
from src.infrastructure.jmeter.jmeter_executor import JMeterExecutor
from src.infrastructure.report.report_generator import ReportGenerator
from src.config.config_manager import config_manager
from src.application.services.performance_tuning_service import PerformanceTuningService

def main():
    """命令行入口函数，所有参数均可选，未传递时自动读取配置文件默认值"""
    parser = argparse.ArgumentParser(description='JMeter性能测试工具')
    parser.add_argument('--thread-counts', default=config_manager.get_jmeter_config()['test']['thread_counts'], nargs='+', type=int, help='线程数列表，默认读取配置文件')
    parser.add_argument('--loop-counts', default=config_manager.get_jmeter_config()['test']['loop_counts'], nargs='+', type=int, help='循环次数列表，默认读取配置文件')
    parser.add_argument('--jmx', default=config_manager.get_jmeter_config()['jmeter']['default_jmx'], help='JMX文件路径，默认读取配置文件')
    parser.add_argument('--jmeter-bin', default=config_manager.get_jmeter_config()['jmeter']['jmeter_bin'], help='JMeter可执行文件路径，默认读取配置文件')
    parser.add_argument('--output-dir', default=config_manager.get_jmeter_config()['output']['base_dir'], help='输出目录，默认读取配置文件')
    parser.add_argument('--test-name', default=config_manager.get_jmeter_config()['jmeter']['default_test_name'], help='测试名称，默认读取配置文件')
    parser.add_argument('--auto-tune', action='store_true', help='启用自动调优，测试完成后自动分析报告并优化参数')
    parser.add_argument('--success-threshold', type=float, default=95.0, help='成功率阈值，低于此值则降低压力')
    parser.add_argument('--max-avg-resp-ms', type=float, default=2000.0, help='平均响应时间阈值，超出则降低压力')
    args = parser.parse_args()

    # 兼容命令行未传递参数时，类型转换
    thread_counts = args.thread_counts
    if isinstance(thread_counts, str):
        thread_counts = [int(x) for x in thread_counts.split(',') if x.strip()]
    elif not isinstance(thread_counts, list):
        thread_counts = [int(thread_counts)]
    loop_counts = args.loop_counts
    if isinstance(loop_counts, str):
        loop_counts = [int(x) for x in loop_counts.split(',') if x.strip()]
    elif not isinstance(loop_counts, list):
        loop_counts = [int(loop_counts)]

    # 创建测试配置，所有参数均有默认值
    config = TestConfig(
        test_name=args.test_name,
        iterations=loop_counts,  # 兼容旧字段名，实际服务层已用loop_counts
        jmx_path=args.jmx,
        jmeter_bin_path=args.jmeter_bin,
        output_dir=args.output_dir
    )
    # 将线程数和循环次数传递到服务层（通过全局配置或参数）
    config_manager.get_jmeter_config()['test']['thread_counts'] = thread_counts
    config_manager.get_jmeter_config()['test']['loop_counts'] = loop_counts
    
    # 创建依赖对象
    jmeter_executor = JMeterExecutor(config.jmeter_bin_path)
    report_generator = ReportGenerator(config.output_dir)
    
    # 创建服务并执行测试
    service = PerformanceTestService(jmeter_executor, report_generator)
    results = service.run_tests(config)
    
    # 打印测试结果
    print("\n测试执行完成！")
    print(f"测试名称: {config.test_name}")
    print(f"测试次数: {config.iterations}")
    print("\n详细结果:")
    for result in results:
        print(f"\n循环次数: {result.iterations}")
        print(f"执行时长: {result.duration:.2f}秒")
        print(f"是否成功: {'成功' if result.success else '失败'}")
        print(f"报告路径: {result.report_path}")

    # 自动查找并输出集成报告路径
    from datetime import datetime
    output_dir = Path(config.output_dir)
    # 查找最新的集成报告（测试名称_时间戳.csv）
    report_files = sorted(output_dir.glob(f"{config.test_name}_*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)
    if report_files:
        latest_report = report_files[0]
        print(f"\n集成报告已生成，路径如下：\n{latest_report}")
        print("请用Excel等工具打开查看所有详细数据，包括服务端CPU使用率等。")
        
        # 如果启用了自动调优，则调用调优服务
        if args.auto_tune:
            print("\n开始自动调优分析...")
            tuning_service = PerformanceTuningService()
            optimal = tuning_service.analyze_and_tune(
                integrated_report_path=str(latest_report),
                success_threshold=args.success_threshold,
                max_avg_resp_ms=args.max_avg_resp_ms
            )
            print('【智能调优结果】')
            print(f'推荐线程数: {optimal.get("thread_count")}, 推荐循环次数: {optimal.get("loop_count")}')
            print('策略已自动更新，可再次运行测试验证新参数效果。')
    else:
        print("未找到集成报告，请检查测试流程是否全部完成。")

    # === 新版：直接用TestResult列表生成对外/对内报告 ===
    try:
        from src.application.services.report_service import ReportService
        external_report_csv = str(output_dir / f"{config.test_name}_对外整合版.csv")
        internal_report_csv = str(output_dir / f"{config.test_name}_内部分析版.csv")
        param_doc_csv = str(output_dir / f"{config.test_name}_参数说明表.csv")
        report_service = ReportService(str(output_dir))
        report_service.generate_external_report_from_results(results, external_report_csv)
        print(f"\n【对外标准报告已生成】：{external_report_csv}")
        report_service.generate_internal_report_from_results(results, internal_report_csv, param_doc_csv)
        print(f"【内部详细分析报告已生成】：{internal_report_csv}")
        print(f"【参数说明表已生成】：{param_doc_csv}")
    except Exception as e:
        print(f"生成对外/内部分析报告时发生异常: {e}")

if __name__ == '__main__':
    main() 