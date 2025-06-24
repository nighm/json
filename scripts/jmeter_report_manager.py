#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter报告自动管理脚本（增强版）
- 每次生成新报告时，自动将旧报告移动到old子文件夹
- 新报告以report-时间戳命名，便于区分和归档
- 自动调用JMeter命令生成HTML报告
- 自动清空result.jtl，检测报告是否为空并友好提示
"""
import os
import shutil
import subprocess
from datetime import datetime
import re
import csv
from glob import glob

JMETER_BIN = os.path.join('src', 'tools', 'jmeter', 'bin', 'jmeter.bat')
JMX_FILE = None  # 需传入或自动查找最新的jmx文件
RESULT_FILE = 'result.jtl'
REPORT_ROOT = os.path.join('src', 'tools', 'jmeter', 'report')
OLD_DIR = os.path.join(REPORT_ROOT, 'old')


def move_old_reports():
    """将report目录下所有report-*文件夹移动到old子文件夹"""
    if not os.path.exists(REPORT_ROOT):
        os.makedirs(REPORT_ROOT)
    if not os.path.exists(OLD_DIR):
        os.makedirs(OLD_DIR)
    for name in os.listdir(REPORT_ROOT):
        path = os.path.join(REPORT_ROOT, name)
        if name.startswith('report-') and os.path.isdir(path):
            print(f'归档旧报告: {name}')
            shutil.move(path, os.path.join(OLD_DIR, name))


def get_latest_jmx():
    """自动查找所有.jmx文件，按文件名中的时间戳排序，取最新"""
    jmx_dir = os.path.join('src', 'tools', 'jmeter')
    jmx_files = [f for f in os.listdir(jmx_dir) if f.endswith('.jmx')]
    if not jmx_files:
        raise FileNotFoundError('未找到任何JMX文件，请先生成测试计划！')
    # 提取时间戳并排序
    def extract_ts(f):
        m = re.search(r'_(\d{8}_\d{6})', f)
        return m.group(1) if m else ''
    jmx_files = sorted(jmx_files, key=lambda f: extract_ts(f), reverse=True)
    return os.path.join(jmx_dir, jmx_files[0])


def clear_result_file():
    """清空result.jtl文件"""
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, 'w', encoding='utf-8') as f:
            f.truncate(0)
        print('已清空 result.jtl 文件')


def run_jmeter_report(jmx_file, result_file, report_dir):
    """调用JMeter生成HTML报告"""
    cmd = [JMETER_BIN, '-n', '-t', jmx_file, '-l', result_file, '-e', '-o', report_dir]
    print('运行JMeter命令:', ' '.join(cmd))
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print(f'报告已生成：{report_dir}')
    else:
        print('JMeter报告生成失败，请检查日志！')


def check_result_file():
    """检测result.jtl是否有内容"""
    if not os.path.exists(RESULT_FILE):
        print('未生成 result.jtl 文件，报告为空！')
        return False
    size = os.path.getsize(RESULT_FILE)
    if size == 0:
        print('警告：result.jtl 文件为空，报告无数据！')
        print('请检查：1）接口token/参数是否正确 2）接口是否可用 3）JMX配置是否有误')
        return False
    print(f'result.jtl 文件大小：{size} 字节')
    return True


def merge_performance_reports(
    analysis_csv_path: str,
    summary_csv_path: str,
    output_dir: str,
    test_name: str,
    timestamp: str,
    cpu_usage_map: dict = None
):
    """
    自动合并分析报告和汇总报告，生成"测试名称_时间戳.csv"格式的新报告，包含所有关键信息和服务端CPU使用率列。
    :param analysis_csv_path: 分析报告CSV路径（含性能数据）
    :param summary_csv_path: 汇总报告CSV路径（含时间、报告路径等）
    :param output_dir: 输出目录
    :param test_name: 测试名称
    :param timestamp: 时间戳字符串
    :param cpu_usage_map: 可选，{(线程数,循环次数): cpu使用率}，无则全部填'-'
    """
    # 读取分析报告
    with open(analysis_csv_path, 'r', encoding='utf-8') as f:
        analysis_rows = list(csv.DictReader(f))
    # 读取汇总报告
    with open(summary_csv_path, 'r', encoding='utf-8') as f:
        summary_rows = list(csv.DictReader(f))
    # 构建主键索引（线程数+循环次数）
    summary_index = {}
    for row in summary_rows:
        key = (str(row.get('线程数', row.get('迭代次数', row.get('循环次数', '')))), str(row.get('循环次数', row.get('迭代次数', ''))))
        summary_index[key] = row
    # 合并字段顺序
    fieldnames = [
        '测试名称', '线程数', '循环次数', '总请求数', '成功数', '失败数', '成功率(%)',
        '最小响应时间(ms)', '最大响应时间(ms)', '平均响应时间(ms)', 'TP90响应时间(ms)', 'TP99响应时间(ms)',
        '开始时间', '结束时间', '执行时长(秒)', '报告路径', '是否成功', '服务端CPU使用率'
    ]
    merged_rows = []
    for arow in analysis_rows:
        key = (str(arow.get('线程数', arow.get('迭代次数', arow.get('循环次数', '')))), str(arow.get('循环次数', arow.get('迭代次数', ''))))
        srow = summary_index.get(key, {})
        merged = {
            '测试名称': test_name,
            '线程数': arow.get('线程数', ''),
            '循环次数': arow.get('循环次数', arow.get('迭代次数', '')),
            '总请求数': arow.get('总请求数', arow.get('总样本数', '')),
            '成功数': arow.get('成功数', ''),
            '失败数': arow.get('失败数', ''),
            '成功率(%)': arow.get('成功率(%)', ''),
            '最小响应时间(ms)': arow.get('最小响应时间(ms)', ''),
            '最大响应时间(ms)': arow.get('最大响应时间(ms)', ''),
            '平均响应时间(ms)': arow.get('平均响应时间(ms)', ''),
            'TP90响应时间(ms)': arow.get('TP90响应时间(ms)', ''),
            'TP99响应时间(ms)': arow.get('TP99响应时间(ms)', ''),
            '开始时间': srow.get('开始时间', ''),
            '结束时间': srow.get('结束时间', ''),
            '执行时长(秒)': srow.get('执行时长(秒)', ''),
            '报告路径': srow.get('报告路径', ''),
            '是否成功': srow.get('是否成功', ''),
            '服务端CPU使用率': '-',
        }
        # 如果有CPU使用率映射，自动填充
        if cpu_usage_map:
            cpu_key = (str(merged['线程数']), str(merged['循环次数']))
            merged['服务端CPU使用率'] = cpu_usage_map.get(cpu_key, '-')
        merged_rows.append(merged)
    # 输出新CSV
    output_path = os.path.join(output_dir, f"{test_name}_{timestamp}.csv")
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)
    print(f"已生成集成报告: {output_path}")


def main():
    # 1. 归档旧报告
    move_old_reports()
    # 2. 新建新报告目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_report_dir = os.path.join(REPORT_ROOT, f'report-{timestamp}')
    os.makedirs(new_report_dir, exist_ok=True)
    # 3. 查找最新JMX
    jmx_file = get_latest_jmx()
    # 4. 清空result.jtl
    clear_result_file()
    # 5. 生成报告
    run_jmeter_report(jmx_file, RESULT_FILE, new_report_dir)
    # 6. 检查报告内容
    check_result_file()


if __name__ == '__main__':
    main() 