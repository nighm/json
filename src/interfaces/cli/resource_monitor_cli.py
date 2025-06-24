import sys
import os
import traceback
# 自动将项目根目录加入sys.path，兼容直接运行
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from src.application.monitor.resource_monitor_service import ResourceMonitorService
from src.infrastructure.monitor.report_generator import ReportGenerator
from src.infrastructure.monitor.excel_report_generator import ExcelReportGenerator
import argparse
import csv
from datetime import datetime

def safe_print(msg):
    print(f"\n{'='*10}\n{msg}\n{'='*10}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='服务器资源监控采集')
    parser.add_argument('--host', type=str, default='192.168.24.45', help='服务器IP')
    parser.add_argument('--username', type=str, default='test', help='SSH用户名')
    parser.add_argument('--password', type=str, default='1', help='SSH密码')
    parser.add_argument('--duration', type=int, default=60, help='采集总时长（秒）')
    parser.add_argument('--interval', type=int, default=5, help='采样间隔（秒）')
    parser.add_argument('--output', type=str, default='cpu_usage.csv', help='输出CSV文件名')
    parser.add_argument('--stress', action='store_true', help='是否在采集期间对服务器CPU加压')
    parser.add_argument('--stress-cores', type=int, default=2, help='加压核数（yes进程数）')
    parser.add_argument('--stress-seconds', type=int, default=None, help='加压持续时间（秒），默认与采集时长一致')
    parser.add_argument('--test-name', type=str, default='CPU监控测试', help='测试名称')
    parser.add_argument('--concurrent-users', type=int, help='并发用户数')
    parser.add_argument('--notes', type=str, help='测试备注')
    parser.add_argument('--generate-charts', action='store_true', help='是否生成图表')
    parser.add_argument('--charts-dir', type=str, default='charts', help='图表输出目录')
    args = parser.parse_args()

    try:
        safe_print('开始采集服务器资源数据...')
        monitor = ResourceMonitorService(args.host, args.username, args.password)
        if args.stress:
            stress_seconds = args.stress_seconds if args.stress_seconds else args.duration
            print(f"[加压模式] 服务器将在采集期间自动启动{args.stress_cores}核CPU压力，持续{stress_seconds}秒...")
            monitor.collector.start_cpu_stress(stress_seconds, args.stress_cores)
        report = monitor.generate_hardware_report(
            test_name=args.test_name,
            duration=args.duration,
            interval=args.interval,
            concurrent_users=args.concurrent_users,
            notes=args.notes
        )
        safe_print('采集与分析完成')
    except Exception as e:
        print(f"[错误] 采集或分析阶段失败：{e}\n请检查服务器连通性、账号密码、网络等。详细信息如下：")
        traceback.print_exc()
        sys.exit(1)

    try:
        safe_print('正在生成CSV报告...')
        ReportGenerator.generate_csv(report, args.output)
        print(f"详细趋势数据已保存到: {args.output}")
    except Exception as e:
        print(f"[错误] 生成CSV报告失败：{e}\n请检查磁盘权限、文件是否被占用。详细信息如下：")
        traceback.print_exc()
        sys.exit(2)

    if args.generate_charts:
        try:
            safe_print('正在生成图表...')
            os.makedirs(args.charts_dir, exist_ok=True)
            ReportGenerator.generate_charts(report, args.charts_dir)
            print(f"图表已保存到: {args.charts_dir} 目录")
        except Exception as e:
            print(f"[错误] 生成图表失败：{e}\n请检查matplotlib依赖、图片目录权限等。详细信息如下：")
            traceback.print_exc()
            sys.exit(3)

    try:
        safe_print('正在生成Excel报告...')
        summary_info = {
            '测试名称': report.summary.test_name,
            '采集时段': f"{report.metrics.start_time} - {report.metrics.end_time}",
            '采样点数': report.metrics.sample_count,
            '采样间隔(s)': report.summary.sample_interval,
            'CPU最大值(%)': f"{report.metrics.max_cpu:.2f}",
            'CPU最小值(%)': f"{report.metrics.min_cpu:.2f}",
            'CPU平均值(%)': f"{report.metrics.avg_cpu:.2f}",
            'CPU P90(%)': f"{report.metrics.p90_cpu:.2f}",
            'CPU P95(%)': f"{report.metrics.p95_cpu:.2f}",
            'CPU变化率(%)': f"{report.metrics.cpu_change_rate:.2f}",
            '备注': report.summary.notes or ''
        }
        excel_name = f"{report.summary.test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ExcelReportGenerator.generate_excel_report(
            csv_file=args.output,
            trend_img=os.path.join(args.charts_dir, 'cpu_trend.png'),
            dist_img=os.path.join(args.charts_dir, 'cpu_distribution.png'),
            dist_explain=os.path.join(args.charts_dir, 'cpu_distribution_explain.txt'),
            output_file=excel_name,
            summary_info=summary_info,
            conclusion=report.conclusion or '',
            recommendations=report.recommendations or []
        )
        print(f"Excel报告已自动生成: {excel_name}")
    except Exception as e:
        print(f"[错误] Excel报告生成失败：{e}\n请检查openpyxl、pandas依赖、图片/CSV/说明文件是否存在。详细信息如下：")
        traceback.print_exc()
        sys.exit(4)

    print(f"\n全部流程已完成！\n当前采集参数：服务器={args.host} 用户={args.username} 时长={args.duration}s 间隔={args.interval}s 输出={args.output}")
    # print(f"内存使用率: {snapshot.memory}")
    # print(f"磁盘使用率: {snapshot.disk}") 