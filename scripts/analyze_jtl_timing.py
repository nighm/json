#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JTL文件时间分析脚本
用于精确分析JMeter JTL文件中的执行时间数据
"""

import csv
import sys
import os
from datetime import datetime
import argparse

def analyze_jtl_timing(jtl_file_path):
    """
    分析JTL文件的时间数据
    
    Args:
        jtl_file_path (str): JTL文件路径
    
    Returns:
        dict: 分析结果
    """
    if not os.path.exists(jtl_file_path):
        print(f"错误：文件不存在 {jtl_file_path}")
        return None
    
    # 读取JTL文件
    timestamps = []
    elapsed_times = []
    
    try:
        with open(jtl_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    try:
                        timestamp = int(row[0])  # 时间戳
                        elapsed = int(row[1])    # 响应时间
                        timestamps.append(timestamp)
                        elapsed_times.append(elapsed)
                    except (ValueError, IndexError):
                        continue
    except Exception as e:
        print(f"读取文件时出错：{e}")
        return None
    
    if not timestamps:
        print("错误：JTL文件中没有有效的时间数据")
        return None
    
    # 计算真实执行时间
    start_time = min(timestamps)
    end_time = max(timestamps)
    total_duration_ms = end_time - start_time
    total_duration_sec = total_duration_ms / 1000.0
    
    # 计算统计信息
    avg_elapsed = sum(elapsed_times) / len(elapsed_times)
    min_elapsed = min(elapsed_times)
    max_elapsed = max(elapsed_times)
    
    # 计算吞吐量
    total_requests = len(timestamps)
    throughput = total_requests / total_duration_sec if total_duration_sec > 0 else 0
    
    # 转换时间戳为可读格式
    start_datetime = datetime.fromtimestamp(start_time / 1000.0)
    end_datetime = datetime.fromtimestamp(end_time / 1000.0)
    
    result = {
        'file_path': jtl_file_path,
        'total_requests': total_requests,
        'start_time': start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        'end_time': end_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        'total_duration_ms': total_duration_ms,
        'total_duration_sec': total_duration_sec,
        'avg_response_time_ms': avg_elapsed,
        'min_response_time_ms': min_elapsed,
        'max_response_time_ms': max_elapsed,
        'throughput_rps': throughput
    }
    
    return result

def print_analysis_result(result):
    """
    打印分析结果
    
    Args:
        result (dict): 分析结果
    """
    if not result:
        return
    
    print("=" * 80)
    print("JTL文件时间分析结果")
    print("=" * 80)
    print(f"文件路径: {result['file_path']}")
    print(f"总请求数: {result['total_requests']}")
    print(f"开始时间: {result['start_time']}")
    print(f"结束时间: {result['end_time']}")
    print(f"总执行时间: {result['total_duration_ms']:.0f}ms ({result['total_duration_sec']:.3f}秒)")
    print(f"平均响应时间: {result['avg_response_time_ms']:.2f}ms")
    print(f"最小响应时间: {result['min_response_time_ms']:.2f}ms")
    print(f"最大响应时间: {result['max_response_time_ms']:.2f}ms")
    print(f"吞吐量: {result['throughput_rps']:.2f} 请求/秒")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description='分析JMeter JTL文件的时间数据')
    parser.add_argument('jtl_file', help='JTL文件路径')
    
    args = parser.parse_args()
    
    result = analyze_jtl_timing(args.jtl_file)
    print_analysis_result(result)

if __name__ == "__main__":
    main() 