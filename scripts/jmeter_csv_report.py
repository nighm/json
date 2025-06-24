#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter CSV报告生成脚本
- 支持多个JMX文件的压测结果累加统计
- 生成综合性的csv明细表，便于分析不同并发量下的性能表现
"""
import os
import csv
from collections import defaultdict
from datetime import datetime

JMX_DIR = os.path.join('src', 'tools', 'jmeter')
CSV_FILE = os.path.join(JMX_DIR, 'jmeter_report_summary.csv')

def parse_result_jtl(result_file):
    """解析单个result.jtl，返回接口统计字典"""
    stats = defaultdict(lambda: {
        'label': '', 'total': 0, 'success': 0, 'fail': 0,
        'avg': 0, 'max': 0, 'min': float('inf'), 'sum': 0,
        'concurrent_level': 0  # 新增：记录并发级别
    })
    
    # 从文件名中提取并发级别
    concurrent_level = 0
    if '_' in result_file:
        try:
            concurrent_level = int(result_file.split('_')[-1].replace('.jtl', ''))
        except ValueError:
            pass
    
    with open(result_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('timeStamp') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) < 8:
                continue
            label = parts[2]
            elapsed = int(parts[1])
            success = parts[7].lower() == 'true'
            s = stats[label]
            s['label'] = label
            s['concurrent_level'] = concurrent_level
            s['total'] += 1
            s['sum'] += elapsed
            s['max'] = max(s['max'], elapsed)
            s['min'] = min(s['min'], elapsed)
            if success:
                s['success'] += 1
            else:
                s['fail'] += 1
    
    # 计算平均值
    for s in stats.values():
        s['avg'] = round(s['sum'] / s['total'], 2) if s['total'] else 0
        s['error_rate'] = round(s['fail'] / s['total'], 4) if s['total'] else 0
    return stats

def merge_stats(all_stats):
    """合并多个统计结果"""
    merged = defaultdict(lambda: {
        'label': '', 'total': 0, 'success': 0, 'fail': 0,
        'avg': 0, 'max': 0, 'min': float('inf'), 'sum': 0,
        'concurrent_levels': set()  # 记录该接口在哪些并发级别下测试过
    })
    
    for stats in all_stats:
        for label, stat in stats.items():
            m = merged[label]
            m['label'] = label
            m['total'] += stat['total']
            m['success'] += stat['success']
            m['fail'] += stat['fail']
            m['sum'] += stat['sum']
            m['max'] = max(m['max'], stat['max'])
            m['min'] = min(m['min'], stat['min'])
            m['concurrent_levels'].add(stat['concurrent_level'])
    
    # 计算最终的平均值和错误率
    for m in merged.values():
        m['avg'] = round(m['sum'] / m['total'], 2) if m['total'] else 0
        m['error_rate'] = round(m['fail'] / m['total'], 4) if m['total'] else 0
        m['concurrent_levels'] = sorted(list(m['concurrent_levels']))
    
    return merged

def write_csv(stats, csv_file):
    """写入csv明细表"""
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            '接口名称', '总请求数', '成功数', '失败数', 
            '平均响应时间(ms)', '最大响应时间(ms)', '最小响应时间(ms)', 
            '错误率', '测试并发级别'
        ])
        for s in stats.values():
            writer.writerow([
                s['label'], s['total'], s['success'], s['fail'],
                s['avg'], s['max'], s['min'], s['error_rate'],
                ','.join(map(str, s['concurrent_levels']))
            ])
    print(f'已生成综合csv明细表：{csv_file}')

def main():
    # 1. 获取所有result.jtl文件
    result_files = []
    for file in os.listdir(os.getcwd()):
        if file.startswith('result_') and file.endswith('.jtl'):
            result_files.append(file)
    
    if not result_files:
        print('未找到任何result_*.jtl文件！')
        return
    
    # 2. 解析所有结果文件
    all_stats = []
    for result_file in result_files:
        print(f'正在解析：{result_file}')
        stats = parse_result_jtl(result_file)
        all_stats.append(stats)
    
    # 3. 合并统计结果
    merged_stats = merge_stats(all_stats)
    
    # 4. 生成综合csv报告
    write_csv(merged_stats, CSV_FILE)

if __name__ == '__main__':
    main() 