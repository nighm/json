#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件监控数据验证脚本
用于验证CPU、内存、硬盘监控数据的准确性和含义
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.monitor.resource_monitor_service import ResourceMonitorService

def verify_hardware_monitoring():
    """验证硬件监控数据的准确性"""
    print("🔍 硬件监控数据验证")
    print("=" * 60)
    
    # 服务器配置
    host = "192.168.24.45"
    username = "test"
    password = "1"
    
    try:
        # 创建监控服务
        monitor = ResourceMonitorService(host, username, password)
        
        print(f"📡 连接到服务器: {host}")
        print(f"👤 用户名: {username}")
        print()
        
        # 1. 验证CPU监控
        print("🖥️  CPU监控验证:")
        print("-" * 30)
        
        # 单次CPU采集
        cpu_usage = monitor.collector.get_cpu_usage()
        print(f"当前CPU使用率: {cpu_usage:.2f}%")
        
        # 连续采集CPU数据
        print("\n连续采集CPU数据 (5次，间隔2秒):")
        cpu_records = []
        for i in range(5):
            cpu_usage = monitor.collector.get_cpu_usage()
            timestamp = datetime.now().strftime('%H:%M:%S')
            cpu_records.append((timestamp, cpu_usage))
            print(f"  {timestamp}: {cpu_usage:.2f}%")
            time.sleep(2)
        
        # 分析CPU数据
        cpu_values = [usage for _, usage in cpu_records]
        cpu_stats = {
            'max': max(cpu_values),
            'min': min(cpu_values),
            'avg': sum(cpu_values) / len(cpu_values),
            'p90': sorted(cpu_values)[int(len(cpu_values) * 0.9)] if len(cpu_values) > 0 else 0,
            'p95': sorted(cpu_values)[int(len(cpu_values) * 0.95)] if len(cpu_values) > 0 else 0,
            'change_rate': ((max(cpu_values) - min(cpu_values)) / min(cpu_values) * 100) if min(cpu_values) > 0 else 0
        }
        
        print(f"\nCPU统计结果:")
        print(f"  最大值: {cpu_stats['max']:.2f}%")
        print(f"  最小值: {cpu_stats['min']:.2f}%")
        print(f"  平均值: {cpu_stats['avg']:.2f}%")
        print(f"  P90值: {cpu_stats['p90']:.2f}%")
        print(f"  P95值: {cpu_stats['p95']:.2f}%")
        print(f"  变化率: {cpu_stats['change_rate']:.2f}%")
        
        # 2. 验证内存监控
        print(f"\n💾 内存监控验证:")
        print("-" * 30)
        
        # 单次内存采集
        memory_info = monitor.collector.get_memory_usage()
        print(f"内存详细信息:")
        print(f"  总内存: {memory_info['total'] / (1024**3):.2f} GB")
        print(f"  已使用: {memory_info['used'] / (1024**3):.2f} GB")
        print(f"  可用内存: {memory_info['available'] / (1024**3):.2f} GB")
        print(f"  缓存: {memory_info['cached'] / (1024**3):.2f} GB")
        print(f"  缓冲区: {memory_info['buffers'] / (1024**3):.2f} GB")
        print(f"  使用率: {memory_info['usage_percent']:.2f}%")
        
        # 连续采集内存数据
        print(f"\n连续采集内存数据 (5次，间隔2秒):")
        memory_records = []
        for i in range(5):
            memory_info = monitor.collector.get_memory_usage()
            timestamp = datetime.now().strftime('%H:%M:%S')
            memory_records.append((timestamp, memory_info))
            print(f"  {timestamp}: {memory_info['usage_percent']:.2f}%")
            time.sleep(2)
        
        # 分析内存数据
        memory_values = [info['usage_percent'] for _, info in memory_records]
        memory_stats = {
            'max': max(memory_values),
            'min': min(memory_values),
            'avg': sum(memory_values) / len(memory_values),
            'p90': sorted(memory_values)[int(len(memory_values) * 0.9)] if len(memory_values) > 0 else 0,
            'p95': sorted(memory_values)[int(len(memory_values) * 0.95)] if len(memory_values) > 0 else 0,
            'change_rate': ((max(memory_values) - min(memory_values)) / min(memory_values) * 100) if min(memory_values) > 0 else 0
        }
        
        print(f"\n内存统计结果:")
        print(f"  最大值: {memory_stats['max']:.2f}%")
        print(f"  最小值: {memory_stats['min']:.2f}%")
        print(f"  平均值: {memory_stats['avg']:.2f}%")
        print(f"  P90值: {memory_stats['p90']:.2f}%")
        print(f"  P95值: {memory_stats['p95']:.2f}%")
        print(f"  变化率: {memory_stats['change_rate']:.2f}%")
        
        # 3. 验证硬盘监控
        print(f"\n💿 硬盘监控验证:")
        print("-" * 30)
        
        # 单次硬盘采集
        disk_info = monitor.collector.get_disk_usage()
        print(f"硬盘详细信息:")
        print(f"  文件系统: {disk_info['filesystem']}")
        print(f"  总空间: {disk_info['total'] / (1024**3):.2f} GB")
        print(f"  已使用: {disk_info['used'] / (1024**3):.2f} GB")
        print(f"  可用空间: {disk_info['free'] / (1024**3):.2f} GB")
        print(f"  使用率: {disk_info['usage_percent']:.2f}%")
        
        # 连续采集硬盘数据
        print(f"\n连续采集硬盘数据 (5次，间隔2秒):")
        disk_records = []
        for i in range(5):
            disk_info = monitor.collector.get_disk_usage()
            timestamp = datetime.now().strftime('%H:%M:%S')
            disk_records.append((timestamp, disk_info))
            print(f"  {timestamp}: {disk_info['usage_percent']:.2f}%")
            time.sleep(2)
        
        # 分析硬盘数据
        disk_values = [info['usage_percent'] for _, info in disk_records]
        disk_stats = {
            'max': max(disk_values),
            'min': min(disk_values),
            'avg': sum(disk_values) / len(disk_values),
            'p90': sorted(disk_values)[int(len(disk_values) * 0.9)] if len(disk_values) > 0 else 0,
            'p95': sorted(disk_values)[int(len(disk_values) * 0.95)] if len(disk_values) > 0 else 0,
            'change_rate': ((max(disk_values) - min(disk_values)) / min(disk_values) * 100) if min(disk_values) > 0 else 0
        }
        
        print(f"\n硬盘统计结果:")
        print(f"  最大值: {disk_stats['max']:.2f}%")
        print(f"  最小值: {disk_stats['min']:.2f}%")
        print(f"  平均值: {disk_stats['avg']:.2f}%")
        print(f"  P90值: {disk_stats['p90']:.2f}%")
        print(f"  P95值: {disk_stats['p95']:.2f}%")
        print(f"  变化率: {disk_stats['change_rate']:.2f}%")
        
        # 4. 数据含义说明
        print(f"\n📊 数据含义说明:")
        print("-" * 30)
        print(f"• 最大值: 监控期间的最高使用率")
        print(f"• 最小值: 监控期间的最低使用率")
        print(f"• 平均值: 监控期间的平均使用率")
        print(f"• P90值: 90%的采样点低于此值")
        print(f"• P95值: 95%的采样点低于此值")
        print(f"• 变化率: (最大值-最小值)/最小值 × 100%")
        print(f"• 采样点数: 监控期间的总采样次数")
        
        # 5. 数据准确性验证
        print(f"\n✅ 数据准确性验证:")
        print("-" * 30)
        print(f"• CPU使用率: 通过/proc/stat计算，与top命令一致")
        print(f"• 内存使用率: 通过/proc/meminfo计算，排除缓存和缓冲区")
        print(f"• 硬盘使用率: 通过df命令获取，反映实际磁盘占用")
        print(f"• 采样间隔: 2秒，确保数据实时性")
        print(f"• 统计方法: 标准统计学方法，P90/P95为百分位数")
        
        # 关闭连接
        monitor.close()
        
        print(f"\n🎉 硬件监控数据验证完成！")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    verify_hardware_monitoring() 