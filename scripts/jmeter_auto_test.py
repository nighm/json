#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter自动化测试脚本
- 使用已有的filtered JMX文件作为基础
- 支持多个并发级别的自动化测试
- 自动生成综合报告
"""
import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入现有模块
from jmeter_csv_report import parse_result_jtl, write_csv, merge_stats

# 配置项
JMX_DIR = os.path.join('src', 'tools', 'jmeter')
JMETER_HOME = os.getenv('JMETER_HOME', '')  # JMeter安装目录
CONCURRENT_LEVELS = [100, 500, 1000, 2000]  # 要测试的并发级别

def get_latest_filtered_jmx():
    """获取最新的filtered JMX文件"""
    jmx_files = [f for f in os.listdir(JMX_DIR) if f.startswith('filtered_') and f.endswith('.jmx')]
    if not jmx_files:
        raise FileNotFoundError('未找到任何filtered JMX文件！')
    jmx_files.sort(reverse=True)  # 按文件名倒序排序
    return os.path.join(JMX_DIR, jmx_files[0])

def modify_jmx_concurrent(jmx_path, concurrent_level, output_path):
    """修改JMX文件中的并发数"""
    tree = ET.parse(jmx_path)
    root = tree.getroot()
    
    # 查找并修改线程组配置
    for tg in root.iter('ThreadGroup'):
        # 修改线程数
        for elem in tg.iter('stringProp'):
            if elem.get('name') == 'ThreadGroup.num_threads':
                elem.text = str(concurrent_level)
        # 修改循环次数
        for elem in tg.iter('stringProp'):
            if elem.get('name') == 'LoopController.loops':
                elem.text = '1'  # 每个线程只执行一次
    
    # 保存修改后的JMX文件
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f'已生成并发数为 {concurrent_level} 的JMX文件：{output_path}')

def run_jmeter_test(jmx_path, result_file):
    """执行JMeter测试"""
    if not JMETER_HOME:
        raise ValueError('请设置JMETER_HOME环境变量')
    
    # 构建JMeter命令
    jmeter_cmd = os.path.join(JMETER_HOME, 'bin', 'jmeter')
    cmd = [
        jmeter_cmd,
        '-n',  # 非GUI模式
        '-t', jmx_path,  # 测试计划文件
        '-l', result_file,  # 结果文件
        '-e',  # 测试完成后生成报告
        '-o', f'report_{os.path.basename(result_file).replace(".jtl", "")}'  # 报告输出目录
    ]
    
    print(f'开始执行测试：{jmx_path}')
    print(f'命令：{" ".join(cmd)}')
    
    # 执行JMeter测试
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # 实时输出测试进度
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    # 检查测试是否成功
    if process.returncode != 0:
        error = process.stderr.read()
        raise Exception(f'JMeter测试失败：{error}')
    
    print(f'测试完成，结果保存在：{result_file}')

def main():
    # 1. 获取最新的filtered JMX文件
    print('获取最新的filtered JMX文件...')
    base_jmx_path = get_latest_filtered_jmx()
    print(f'使用基础JMX文件：{base_jmx_path}')
    
    # 2. 为每个并发级别执行测试
    all_stats = []
    for concurrent_level in CONCURRENT_LEVELS:
        print(f'\n开始测试并发级别：{concurrent_level}')
        
        # 2.1 生成对应并发数的JMX文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        jmx_file = f'jmeter_{concurrent_level}_{timestamp}.jmx'
        jmx_path = os.path.join(JMX_DIR, jmx_file)
        modify_jmx_concurrent(base_jmx_path, concurrent_level, jmx_path)
        
        # 2.2 执行JMeter测试
        result_file = f'result_{concurrent_level}.jtl'
        run_jmeter_test(jmx_path, result_file)
        
        # 2.3 解析测试结果
        stats = parse_result_jtl(result_file)
        all_stats.append(stats)
        
        # 2.4 等待一段时间，避免系统负载过高
        if concurrent_level != CONCURRENT_LEVELS[-1]:
            print('等待30秒后继续下一个测试...')
            time.sleep(30)
    
    # 3. 生成综合报告
    print('\n生成综合报告...')
    merged_stats = merge_stats(all_stats)
    write_csv(merged_stats, os.path.join(JMX_DIR, 'jmeter_report_summary.csv'))
    
    print('\n所有测试完成！')

if __name__ == '__main__':
    main() 