#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter结果过滤与报告脚本
- 解析result.jtl，统计每个接口的详细压测数据
- 只保留无任何失败的接口，自动生成新JMX文件
- 生成csv明细表，便于后续多轮对比
"""
import os
import csv
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

RESULT_FILE = 'result.jtl'
JMX_DIR = os.path.join('src', 'tools', 'jmeter')
CSV_FILE = os.path.join(JMX_DIR, 'jmeter_report_summary.csv')

# 1. 解析result.jtl，统计每个接口的详细数据
def parse_result_jtl(result_file):
    """解析result.jtl，返回接口统计字典"""
    stats = defaultdict(lambda: {
        'label': '', 'total': 0, 'success': 0, 'fail': 0,
        'avg': 0, 'max': 0, 'min': float('inf'), 'sum': 0
    })
    with open(result_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('timeStamp') or not line.strip():
                continue  # 跳过表头或空行
            parts = line.strip().split(',')
            # JMeter默认字段顺序：timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,...
            if len(parts) < 8:
                continue
            label = parts[2]
            elapsed = int(parts[1])
            success = parts[7].lower() == 'true'
            s = stats[label]
            s['label'] = label
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

# 2. 生成csv明细表
def write_csv(stats, csv_file):
    """写入csv明细表"""
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['接口名称', '总请求数', '成功数', '失败数', '平均响应时间(ms)', '最大响应时间(ms)', '最小响应时间(ms)', '错误率'])
        for s in stats.values():
            writer.writerow([
                s['label'], s['total'], s['success'], s['fail'],
                s['avg'], s['max'], s['min'], s['error_rate']
            ])
    print(f'已生成csv明细表：{csv_file}')

# 3. 只保留无任何失败的接口，生成新JMX
def filter_jmx_by_labels(jmx_path, keep_labels, output_path):
    """根据label过滤JMX文件，只保留keep_labels中的接口"""
    tree = ET.parse(jmx_path)
    root = tree.getroot()
    # 遍历所有ThreadGroup下的hashTree
    for tg in root.iter('ThreadGroup'):
        # 找到ThreadGroup对应的hashTree（父节点的下一个兄弟节点）
        parent = None
        for elem in root.iter():
            for i, child in enumerate(list(elem)):
                if child is tg and i + 1 < len(elem):
                    parent = elem
                    tg_hash = elem[i + 1]
                    # tg_hash下的children: HTTPSamplerProxy, hashTree, HTTPSamplerProxy, hashTree...
                    children = list(tg_hash)
                    remove_idx = []
                    for idx in range(0, len(children), 2):
                        if idx < len(children) and children[idx].tag == 'HTTPSamplerProxy':
                            label = children[idx].attrib.get('testname', '')
                            if label not in keep_labels:
                                remove_idx.append(idx)
                    # 倒序删除HTTPSamplerProxy及其hashTree
                    for idx in reversed(remove_idx):
                        del tg_hash[idx:idx+2]
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f'已生成新JMX文件：{output_path}')

# 4. 主流程
def main():
    # 1. 解析result.jtl
    result_path = os.path.join(os.getcwd(), RESULT_FILE)
    stats = parse_result_jtl(result_path)
    # 2. 生成csv明细表
    write_csv(stats, CSV_FILE)
    # 3. 过滤无失败接口，生成新JMX
    keep_labels = [s['label'] for s in stats.values() if s['fail'] == 0]
    # 找到最新JMX
    jmx_files = [f for f in os.listdir(JMX_DIR) if f.endswith('.jmx')]
    jmx_files.sort(reverse=True)
    if not jmx_files:
        print('未找到JMX文件！')
        return
    latest_jmx = os.path.join(JMX_DIR, jmx_files[0])
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_jmx = os.path.join(JMX_DIR, f'filtered_{timestamp}.jmx')
    filter_jmx_by_labels(latest_jmx, keep_labels, new_jmx)

if __name__ == '__main__':
    main() 