#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版硬件监控分析脚本
分析更多有价值的CPU、内存、硬盘参数及其对性能测试的影响
"""

import sys
import os
import time
from datetime import datetime
import subprocess

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.monitor.resource_monitor_service import ResourceMonitorService

class EnhancedHardwareMonitor:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.monitor = ResourceMonitorService(host, username, password)
    
    def analyze_cpu_detailed(self):
        """详细分析CPU参数"""
        print("🖥️  CPU详细参数分析")
        print("=" * 50)
        
        # 基础CPU使用率
        cpu_usage = self.monitor.collector.get_cpu_usage()
        print(f"基础CPU使用率: {cpu_usage:.2f}%")
        
        # 获取CPU核心数
        cpu_cores = self._get_cpu_cores()
        print(f"CPU核心数: {cpu_cores}")
        
        # 获取CPU负载
        load_avg = self._get_load_average()
        print(f"系统负载: {load_avg}")
        
        # 获取CPU频率
        cpu_freq = self._get_cpu_frequency()
        print(f"CPU频率: {cpu_freq}")
        
        # 获取CPU温度（如果可用）
        cpu_temp = self._get_cpu_temperature()
        if cpu_temp:
            print(f"CPU温度: {cpu_temp}")
        
        # 获取进程数
        process_count = self._get_process_count()
        print(f"活跃进程数: {process_count}")
        
        # 获取线程数
        thread_count = self._get_thread_count()
        print(f"活跃线程数: {thread_count}")
        
        # 获取CPU上下文切换
        context_switches = self._get_context_switches()
        print(f"上下文切换/秒: {context_switches}")
        
        # 获取中断数
        interrupts = self._get_interrupts()
        print(f"中断数/秒: {interrupts}")
        
        return {
            'cpu_usage': cpu_usage,
            'cpu_cores': cpu_cores,
            'load_avg': load_avg,
            'cpu_freq': cpu_freq,
            'cpu_temp': cpu_temp,
            'process_count': process_count,
            'thread_count': thread_count,
            'context_switches': context_switches,
            'interrupts': interrupts
        }
    
    def analyze_memory_detailed(self):
        """详细分析内存参数"""
        print("\n💾 内存详细参数分析")
        print("=" * 50)
        
        memory_info = self.monitor.collector.get_memory_usage()
        
        # 基础内存信息
        print(f"总内存: {memory_info['total'] / (1024**3):.2f} GB")
        print(f"已使用: {memory_info['used'] / (1024**3):.2f} GB")
        print(f"可用内存: {memory_info['available'] / (1024**3):.2f} GB")
        print(f"使用率: {memory_info['usage_percent']:.2f}%")
        
        # 获取交换分区信息
        swap_info = self._get_swap_info()
        print(f"交换分区: {swap_info}")
        
        # 获取内存页面信息
        page_info = self._get_page_info()
        print(f"页面信息: {page_info}")
        
        # 获取内存碎片信息
        fragmentation = self._get_memory_fragmentation()
        print(f"内存碎片: {fragmentation}")
        
        # 获取大页内存信息
        hugepages = self._get_hugepages_info()
        print(f"大页内存: {hugepages}")
        
        return {
            'memory_info': memory_info,
            'swap_info': swap_info,
            'page_info': page_info,
            'fragmentation': fragmentation,
            'hugepages': hugepages
        }
    
    def analyze_disk_detailed(self):
        """详细分析硬盘参数"""
        print("\n💿 硬盘详细参数分析")
        print("=" * 50)
        
        disk_info = self.monitor.collector.get_disk_usage()
        
        # 基础硬盘信息
        print(f"文件系统: {disk_info['filesystem']}")
        print(f"总空间: {disk_info['total'] / (1024**3):.2f} GB")
        print(f"已使用: {disk_info['used'] / (1024**3):.2f} GB")
        print(f"可用空间: {disk_info['free'] / (1024**3):.2f} GB")
        print(f"使用率: {disk_info['usage_percent']:.2f}%")
        
        # 获取IO统计
        io_stats = self._get_disk_io_stats()
        print(f"磁盘IO统计: {io_stats}")
        
        # 获取磁盘延迟
        disk_latency = self._get_disk_latency()
        print(f"磁盘延迟: {disk_latency}")
        
        # 获取文件系统类型
        fs_type = self._get_filesystem_type()
        print(f"文件系统类型: {fs_type}")
        
        # 获取inode使用情况
        inode_info = self._get_inode_info()
        print(f"Inode使用情况: {inode_info}")
        
        return {
            'disk_info': disk_info,
            'io_stats': io_stats,
            'disk_latency': disk_latency,
            'fs_type': fs_type,
            'inode_info': inode_info
        }
    
    def analyze_network_detailed(self):
        """详细分析网络参数"""
        print("\n🌐 网络详细参数分析")
        print("=" * 50)
        
        # 获取网络接口信息
        network_interfaces = self._get_network_interfaces()
        print(f"网络接口: {network_interfaces}")
        
        # 获取网络连接数
        connections = self._get_network_connections()
        print(f"网络连接数: {connections}")
        
        # 获取网络流量
        network_traffic = self._get_network_traffic()
        print(f"网络流量: {network_traffic}")
        
        return {
            'network_interfaces': network_interfaces,
            'connections': connections,
            'network_traffic': network_traffic
        }
    
    def analyze_sampling_impact(self, intervals=[1, 2, 5, 10]):
        """分析不同采样间隔的影响"""
        print("\n📊 采样间隔影响分析")
        print("=" * 50)
        
        results = {}
        
        for interval in intervals:
            print(f"\n采样间隔: {interval}秒")
            print("-" * 30)
            
            # 采集数据
            start_time = time.time()
            cpu_records = []
            memory_records = []
            disk_records = []
            
            # 采集30秒的数据
            duration = 30
            sample_count = 0
            
            while time.time() - start_time < duration:
                # CPU
                cpu_usage = self.monitor.collector.get_cpu_usage()
                cpu_records.append(cpu_usage)
                
                # 内存
                memory_info = self.monitor.collector.get_memory_usage()
                memory_records.append(memory_info['usage_percent'])
                
                # 硬盘
                disk_info = self.monitor.collector.get_disk_usage()
                disk_records.append(disk_info['usage_percent'])
                
                sample_count += 1
                time.sleep(interval)
            
            # 分析数据
            cpu_stats = self._calculate_stats(cpu_records)
            memory_stats = self._calculate_stats(memory_records)
            disk_stats = self._calculate_stats(disk_records)
            
            print(f"采样点数: {sample_count}")
            print(f"CPU - 最大值: {cpu_stats['max']:.2f}%, 平均值: {cpu_stats['avg']:.2f}%")
            print(f"内存 - 最大值: {memory_stats['max']:.2f}%, 平均值: {memory_stats['avg']:.2f}%")
            print(f"硬盘 - 最大值: {disk_stats['max']:.2f}%, 平均值: {disk_stats['avg']:.2f}%")
            
            results[interval] = {
                'sample_count': sample_count,
                'cpu_stats': cpu_stats,
                'memory_stats': memory_stats,
                'disk_stats': disk_stats
            }
        
        return results
    
    def _ssh_exec(self, command):
        """执行SSH命令"""
        try:
            ssh = self.monitor.collector._ssh_exec(command)
            return ssh
        except Exception as e:
            return f"Error: {e}"
    
    def _get_cpu_cores(self):
        """获取CPU核心数"""
        try:
            result = self._ssh_exec("nproc")
            return int(result) if result.isdigit() else "Unknown"
        except:
            return "Unknown"
    
    def _get_load_average(self):
        """获取系统负载"""
        try:
            result = self._ssh_exec("cat /proc/loadavg")
            return result.split()[:3]  # 返回1分钟、5分钟、15分钟负载
        except:
            return "Unknown"
    
    def _get_cpu_frequency(self):
        """获取CPU频率"""
        try:
            result = self._ssh_exec("cat /proc/cpuinfo | grep 'cpu MHz' | head -1")
            if ':' in result:
                return result.split(':')[1].strip() + " MHz"
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_cpu_temperature(self):
        """获取CPU温度"""
        try:
            # 尝试不同的温度传感器路径
            temp_paths = [
                "/sys/class/thermal/thermal_zone0/temp",
                "/proc/acpi/thermal_zone/THM0/temperature",
                "/sys/class/hwmon/hwmon0/temp1_input"
            ]
            
            for path in temp_paths:
                result = self._ssh_exec(f"cat {path} 2>/dev/null")
                if result.isdigit():
                    temp = int(result) / 1000.0  # 转换为摄氏度
                    return f"{temp:.1f}°C"
            
            return None
        except:
            return None
    
    def _get_process_count(self):
        """获取进程数"""
        try:
            result = self._ssh_exec("ps aux | wc -l")
            return int(result) - 1 if result.isdigit() else "Unknown"  # 减去标题行
        except:
            return "Unknown"
    
    def _get_thread_count(self):
        """获取线程数"""
        try:
            result = self._ssh_exec("ps -eLf | wc -l")
            return int(result) - 1 if result.isdigit() else "Unknown"  # 减去标题行
        except:
            return "Unknown"
    
    def _get_context_switches(self):
        """获取上下文切换数"""
        try:
            result = self._ssh_exec("cat /proc/stat | grep ctxt")
            if 'ctxt' in result:
                return result.split()[1]
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_interrupts(self):
        """获取中断数"""
        try:
            result = self._ssh_exec("cat /proc/stat | grep intr")
            if 'intr' in result:
                return result.split()[1]
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_swap_info(self):
        """获取交换分区信息"""
        try:
            result = self._ssh_exec("free -h | grep Swap")
            return result
        except:
            return "Unknown"
    
    def _get_page_info(self):
        """获取页面信息"""
        try:
            result = self._ssh_exec("cat /proc/vmstat | grep -E 'pgpgin|pgpgout'")
            return result
        except:
            return "Unknown"
    
    def _get_memory_fragmentation(self):
        """获取内存碎片信息"""
        try:
            result = self._ssh_exec("cat /proc/buddyinfo")
            return "Available" if result else "Unknown"
        except:
            return "Unknown"
    
    def _get_hugepages_info(self):
        """获取大页内存信息"""
        try:
            result = self._ssh_exec("cat /proc/meminfo | grep -i huge")
            return result
        except:
            return "Unknown"
    
    def _get_disk_io_stats(self):
        """获取磁盘IO统计"""
        try:
            result = self._ssh_exec("cat /proc/diskstats | grep -E 'sda|vda'")
            return result
        except:
            return "Unknown"
    
    def _get_disk_latency(self):
        """获取磁盘延迟"""
        try:
            result = self._ssh_exec("iostat -x 1 1")
            return result
        except:
            return "Unknown"
    
    def _get_filesystem_type(self):
        """获取文件系统类型"""
        try:
            result = self._ssh_exec("df -T / | tail -1")
            return result.split()[1] if result else "Unknown"
        except:
            return "Unknown"
    
    def _get_inode_info(self):
        """获取inode使用情况"""
        try:
            result = self._ssh_exec("df -i / | tail -1")
            return result
        except:
            return "Unknown"
    
    def _get_network_interfaces(self):
        """获取网络接口信息"""
        try:
            result = self._ssh_exec("ip addr show | grep -E 'inet|UP'")
            return result
        except:
            return "Unknown"
    
    def _get_network_connections(self):
        """获取网络连接数"""
        try:
            result = self._ssh_exec("ss -tuln | wc -l")
            return int(result) - 1 if result.isdigit() else "Unknown"
        except:
            return "Unknown"
    
    def _get_network_traffic(self):
        """获取网络流量"""
        try:
            result = self._ssh_exec("cat /proc/net/dev | grep -E 'eth0|ens|eno'")
            return result
        except:
            return "Unknown"
    
    def _calculate_stats(self, values):
        """计算统计值"""
        if not values:
            return {'max': 0, 'min': 0, 'avg': 0}
        
        return {
            'max': max(values),
            'min': min(values),
            'avg': sum(values) / len(values)
        }
    
    def close(self):
        """关闭连接"""
        if self.monitor:
            self.monitor.close()

def main():
    """主函数"""
    print("🔍 增强版硬件监控分析")
    print("=" * 60)
    
    # 服务器配置
    host = "192.168.24.45"
    username = "test"
    password = "1"
    
    try:
        # 创建监控实例
        monitor = EnhancedHardwareMonitor(host, username, password)
        
        # 1. 详细CPU分析
        cpu_data = monitor.analyze_cpu_detailed()
        
        # 2. 详细内存分析
        memory_data = monitor.analyze_memory_detailed()
        
        # 3. 详细硬盘分析
        disk_data = monitor.analyze_disk_detailed()
        
        # 4. 网络分析
        network_data = monitor.analyze_network_detailed()
        
        # 5. 采样间隔影响分析
        sampling_impact = monitor.analyze_sampling_impact()
        
        # 6. 总结和建议
        print("\n📋 分析总结和建议")
        print("=" * 60)
        
        print("\n🎯 推荐监控参数:")
        print("CPU: 使用率、负载、核心数、温度、上下文切换、中断数")
        print("内存: 使用率、交换分区、页面信息、大页内存")
        print("硬盘: 使用率、IO统计、延迟、inode使用情况")
        print("网络: 连接数、流量、接口状态")
        
        print("\n⚡ 采样间隔建议:")
        print("• 1秒: 高精度监控，适合短期压力测试")
        print("• 2秒: 平衡精度和性能，推荐默认值")
        print("• 5秒: 降低系统开销，适合长期监控")
        print("• 10秒: 最低开销，适合基线监控")
        
        print("\n🚨 性能影响:")
        print("• 采样间隔越短，系统开销越大")
        print("• 1秒间隔可能影响测试结果准确性")
        print("• 建议根据测试时长选择合适的间隔")
        
        # 关闭连接
        monitor.close()
        
        print(f"\n🎉 增强版硬件监控分析完成！")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 