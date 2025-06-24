import sys
import os
# 自动将项目根目录和src目录加入sys.path，保证import src.xxx能成功
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
import subprocess
import time
from src.infrastructure.jmeter.jmeter_executor import JMeterExecutor
from src.domain.entities.test_result import TestResult
from src.infrastructure.report.report_generator import ReportGenerator


def run_resource_monitor(host, username, password, duration, interval, output, extra_args=None):
    """
    启动资源监控，调用resource_monitor_cli.py，采集CPU/内存/磁盘等数据
    """
    cmd = [
        "python", "src/interfaces/cli/resource_monitor_cli.py",
        "--host", host,
        "--username", username,
        "--password", password,
        "--duration", str(duration),
        "--interval", str(interval),
        "--output", output,
        "--generate-charts"
    ]
    if extra_args:
        cmd += extra_args
    # 启动监控进程（异步）
    proc = subprocess.Popen(cmd)
    return proc


def main():
    # 1. 解析命令行参数
    parser = argparse.ArgumentParser(description="批量注册/登录性能测试主控脚本")
    parser.add_argument('--host', type=str, default='192.168.24.45', help='被测服务器IP')
    parser.add_argument('--username', type=str, default='test', help='SSH用户名')
    parser.add_argument('--password', type=str, default='1', help='SSH密码')
    parser.add_argument('--threads', type=int, default=500, help='JMeter线程数')
    parser.add_argument('--loops', type=int, default=10, help='JMeter循环次数')
    parser.add_argument('--duration', type=int, default=60, help='资源监控时长（秒）')
    parser.add_argument('--interval', type=int, default=5, help='资源监控采样间隔（秒）')
    parser.add_argument('--test-type', choices=['register', 'login'], default='register', help='测试类型')
    parser.add_argument('--jmx-template', type=str, default='src/tools/jmeter/api_cases/register_test.jmx', help='JMX模板路径')
    parser.add_argument('--csv-output', type=str, default='cpu_usage.csv', help='资源监控CSV输出')
    parser.add_argument('--output-dir', type=str, default='test_output', help='测试结果输出目录')
    args = parser.parse_args()

    # 2. 启动资源监控（异步）
    print("【主控】启动资源监控...")
    monitor_proc = run_resource_monitor(
        args.host, args.username, args.password, args.duration, args.interval, args.csv_output
    )
    time.sleep(2)  # 可选：确保监控已启动

    # 3. 执行JMeter测试（调用已有JMeterExecutor等模块）
    print("【主控】执行JMeter性能测试...")
    jmeter_bin = "src/tools/jmeter/bin/jmeter.bat"  # 可根据实际情况调整
    executor = JMeterExecutor(jmeter_bin)
    test_name = f"{args.test_type}_test"
    result: TestResult = executor.execute_test(
        jmx_path=args.jmx_template,
        iterations=args.loops,
        output_dir=args.output_dir,
        test_name=test_name,
        thread_count=args.threads
    )

    # 4. 等待资源监控结束
    print("【主控】等待资源监控结束...")
    monitor_proc.wait()

    # 5. 生成最终报告（调用ReportGenerator）
    print("【主控】生成最终报告...")
    report_gen = ReportGenerator(args.output_dir)
    report_path = report_gen.generate_summary_report([result])
    print(f"【主控】全部流程完成，报告已生成于: {report_path}")

if __name__ == '__main__':
    main() 