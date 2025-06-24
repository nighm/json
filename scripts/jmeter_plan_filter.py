#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter测试计划过滤脚本
- 支持多个不同并发级别的JMX文件
- 根据测试结果过滤JMX文件，只保留成功的接口
- 生成新的JMX文件，文件名包含并发级别信息
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict

JMX_DIR = os.path.join('src', 'tools', 'jmeter')

def get_success_labels(result_file):
    """从result.jtl中获取所有成功的接口标签"""
    stats = defaultdict(lambda: {'fail': 0})
    with open(result_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('timeStamp') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) < 8:
                continue
            label = parts[2]
            success = parts[7].lower() == 'true'
            if not success:
                stats[label]['fail'] += 1
    return [label for label, stat in stats.items() if stat['fail'] == 0]

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

def get_concurrent_level(jmx_file):
    """从JMX文件名中提取并发级别"""
    try:
        # 假设文件名格式为：jmeter_100.jmx 或 jmeter_1000.jmx
        return int(jmx_file.split('_')[-1].replace('.jmx', ''))
    except (ValueError, IndexError):
        return 0

def main():
    # 1. 获取所有JMX文件并按并发级别排序
    jmx_files = [f for f in os.listdir(JMX_DIR) if f.endswith('.jmx')]
    jmx_files.sort(key=get_concurrent_level)
    
    if not jmx_files:
        print('未找到JMX文件！')
        return
    
    # 2. 处理每个JMX文件
    for jmx_file in jmx_files:
        concurrent_level = get_concurrent_level(jmx_file)
        if concurrent_level == 0:
            print(f'跳过文件 {jmx_file}：无法识别并发级别')
            continue
            
        # 2.1 获取对应的result.jtl文件
        result_file = f'result_{concurrent_level}.jtl'
        if not os.path.exists(result_file):
            print(f'跳过文件 {jmx_file}：未找到对应的结果文件 {result_file}')
            continue
            
        # 2.2 获取成功的接口标签
        success_labels = get_success_labels(result_file)
        
        # 2.3 生成新的JMX文件
        jmx_path = os.path.join(JMX_DIR, jmx_file)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_jmx = os.path.join(JMX_DIR, f'filtered_{concurrent_level}_{timestamp}.jmx')
        filter_jmx_by_labels(jmx_path, success_labels, new_jmx)

if __name__ == '__main__':
    main() 