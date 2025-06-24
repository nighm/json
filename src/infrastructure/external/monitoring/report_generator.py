import csv
from datetime import datetime
from typing import List, Dict
import matplotlib.pyplot as plt
import pandas as pd
from src.domain.monitor.hardware_monitor_report import HardwareMonitorReport
import numpy as np

class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_csv(report: HardwareMonitorReport, output_file: str):
        """
        生成CSV格式报告
        Args:
            report: 硬件监控报告
            output_file: 输出文件路径
        """
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入测试基本信息
            writer.writerow(['测试基本信息'])
            writer.writerow(['测试名称', report.summary.test_name])
            writer.writerow(['测试时间', f"{report.metrics.start_time} - {report.metrics.end_time}"])
            writer.writerow(['采样间隔', f"{report.summary.sample_interval}秒"])
            if report.summary.concurrent_users:
                writer.writerow(['并发用户数', report.summary.concurrent_users])
            if report.summary.notes:
                writer.writerow(['测试备注', report.summary.notes])
            writer.writerow([])  # 空行分隔
            
            # 写入硬件指标统计表
            writer.writerow(['硬件指标统计'])
            writer.writerow(['指标类型', '最大值', '最小值', '平均值', 'P90值', 'P95值', '变化率'])
            # CPU指标
            writer.writerow([
                'CPU使用率(%)',
                f"{report.metrics.max_cpu:.2f}",
                f"{report.metrics.min_cpu:.2f}",
                f"{report.metrics.avg_cpu:.2f}",
                f"{report.metrics.p90_cpu:.2f}",
                f"{report.metrics.p95_cpu:.2f}",
                f"{report.metrics.cpu_change_rate:.2f}"
            ])
            # 预留内存指标行
            writer.writerow(['内存使用率(%)', '', '', '', '', '', ''])
            # 预留磁盘指标行
            writer.writerow(['磁盘使用率(%)', '', '', '', '', '', ''])
            writer.writerow([])  # 空行分隔
            
            # 写入趋势明细表
            writer.writerow(['趋势明细数据'])
            writer.writerow(['时间戳', 'CPU使用率(%)', '内存使用率(%)', '磁盘使用率(%)'])
            for timestamp, usage in report.metrics.records:
                writer.writerow([timestamp, f"{usage:.2f}", '', ''])
            
            # 写入结论和建议
            if report.conclusion or report.recommendations:
                writer.writerow([])  # 空行分隔
                writer.writerow(['测试结论与建议'])
                if report.conclusion:
                    writer.writerow(['结论', report.conclusion])
                if report.recommendations:
                    for rec in report.recommendations:
                        writer.writerow(['建议', rec])
    
    @staticmethod
    def generate_charts(report: HardwareMonitorReport, output_dir: str):
        """
        生成图表（含优化的CPU分布直方图，区间宽度自适应，避免重复）
        Args:
            report: 硬件监控报告
            output_dir: 输出目录
        """
        # 准备数据
        timestamps = [t for t, _ in report.metrics.records]
        usages = [u for _, u in report.metrics.records]
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 生成趋势图
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, usages, 'b-', label='CPU使用率')
        plt.title(f'{report.summary.test_name} - CPU使用率变化趋势')
        plt.xlabel('时间')
        plt.ylabel('CPU使用率（%）')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cpu_trend.png")
        plt.close()
        
        # 优化分布直方图分箱逻辑
        min_usage = int(min(usages))
        max_usage = int(max(usages)) + 1
        # 采样点少时，区间宽度大些，采样点多时区间细些
        if len(usages) <= 12:
            bin_width = 5
        elif len(usages) <= 30:
            bin_width = 3
        else:
            bin_width = 2
        bins = list(range(min_usage, max_usage + bin_width, bin_width))
        # 生成直方图
        plt.figure(figsize=(14, 7))
        n, bins, patches = plt.hist(usages, bins=bins, edgecolor='black', alpha=0.7)
        plt.title(f'{report.summary.test_name} - CPU使用率分布（每{bin_width}%区间出现次数）')
        plt.xlabel('CPU使用率（%）')
        plt.ylabel('出现次数（次）')
        plt.grid(True, axis='y')
        # X轴百分号显示
        plt.gca().set_xticks(bins)
        plt.gca().set_xticklabels([f'{int(x)}%' for x in bins], rotation=0)
        # Y轴"次"单位
        plt.gca().set_yticklabels([f'{int(y)}次' for y in plt.gca().get_yticks()])
        # 关键指标参考线
        avg = report.metrics.avg_cpu
        p90 = report.metrics.p90_cpu
        p95 = report.metrics.p95_cpu
        plt.axvline(avg, color='orange', linestyle='--', label=f'平均值：{avg:.1f}%')
        plt.axvline(p90, color='green', linestyle='--', label=f'P90：{p90:.1f}%')
        plt.axvline(p95, color='red', linestyle='--', label=f'P95：{p95:.1f}%')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cpu_distribution.png")
        plt.close()
        
        # 生成中文解读说明txt
        explain = (
            f"图表说明：本图展示了测试期间CPU使用率的分布情况。每个柱子代表CPU使用率在对应区间（如30%-35%）内出现的次数。"
            f"Y轴表示出现次数。大部分时间CPU使用率集中在{min(usages):.1f}%到{max(usages):.1f}%之间。"
            f"平均值为{avg:.1f}%，P90为{p90:.1f}%，P95为{p95:.1f}%。"
            f"如柱状图主要集中在高区间，说明系统负载较高；如分布较均匀，说明负载波动较大。"
            f"本图适合开发、测试、市场、客户等不同人群快速了解系统负载分布。"
        )
        with open(f"{output_dir}/cpu_distribution_explain.txt", 'w', encoding='utf-8') as f:
            f.write(explain) 