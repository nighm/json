from datetime import datetime
from pathlib import Path
from src.application.monitor.resource_monitor_service import ResourceMonitorService
from src.application.services.device_query_service import DeviceQueryService
import csv
import glob
import json
import os
import subprocess
import sys
import threading
import time

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量登录测试脚本
使用现有数据进行重复注册测试，验证批量登录功能
固定线程数500，测试不同循环次数的效果
包含CPU、内存、硬盘监控
"""


# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class BatchLoginTest:
    """批量登录测试类"""
    
    def __init__(self):
        # 配置路径
        self.jmeter_bin = "src/tools/jmeter/bin/jmeter.bat"
        self.jmx_template = "src/tools/jmeter/api_cases/register_test.jmx"
        self.results_dir = "src/tools/jmeter/results"
        
        # 数据库配置
        self.db_config = {
            'host': '192.168.24.45',
            'port': 3306,
            'user': 'test',
            'password': '1',
            'database': 'kunlun_guardian'
        }
        
        # 服务器监控配置
        self.server_config = {
            'host': '192.168.24.45',
            'username': 'test',
            'password': '1'
        }
        
        # 测试配置
        self.thread_count = 500  # 固定线程数
        self.loop_configs = [1, 2, 5, 10, 20]  # 不同的循环次数
        
        # 监控相关
        self.cpu_monitoring = False
        self.cpu_monitor = None
        self.cpu_data = []
        self.memory_data = []
        self.disk_data = []
        
        # 确保结果目录存在
        os.makedirs(self.results_dir, exist_ok=True)
        
        print("🚀 批量登录测试初始化完成")
        print(f"📊 固定线程数: {self.thread_count}")
        print(f"🔄 循环次数配置: {self.loop_configs}")
        print(f"🖥️  服务器监控: {self.server_config['host']}")
    
    def check_prerequisites(self):
        """检查前置条件"""
        print("\n🔍 检查前置条件...")
        
        # 检查JMeter
        if not os.path.exists(self.jmeter_bin):
            print(f"❌ JMeter不存在: {self.jmeter_bin}")
            return False
        
        # 检查JMX模板
        if not os.path.exists(self.jmx_template):
            print(f"❌ JMX模板不存在: {self.jmx_template}")
            return False
        
        # 检查数据库连接
        try:
            service = DeviceQueryService(self.db_config)
            count = service.get_device_count('biz_device')
            service.close()
            print(f"✅ 数据库连接正常，现有设备数: {count}")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
        
        print("✅ 前置条件检查通过")
        return True
    
    def get_device_count(self):
        """获取当前设备数量"""
        try:
            service = DeviceQueryService(self.db_config)
            count = service.get_device_count('biz_device')
            service.close()
            return count
        except Exception as e:
            print(f"❌ 获取设备数量失败: {e}")
            return 0
    
    def modify_jmx_threads(self, thread_count, loops=1):
        """修改JMX文件的线程数和循环次数"""
        print(f"🔧 修改JMX配置: 线程数={thread_count}, 循环次数={loops}")
        
        # 读取原始JMX文件
        with open(self.jmx_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改线程数
        content = content.replace(
            'stringProp name="ThreadGroup.num_threads">1<',
            f'stringProp name="ThreadGroup.num_threads">{thread_count}<'
        )
        
        # 修改循环次数
        content = content.replace(
            'stringProp name="ThreadGroup.loop_count">1<',
            f'stringProp name="ThreadGroup.loop_count">{loops}<'
        )
        
        # 生成修改后的JMX文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        modified_jmx = os.path.join(
            self.results_dir, 
            f"login_test_{thread_count}threads_{loops}loops_{timestamp}.jmx"
        )
        
        with open(modified_jmx, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ JMX文件已生成: {modified_jmx}")
        return modified_jmx
    
    def start_resource_monitoring(self, duration, interval=2):
        """启动系统资源监控"""
        print(f"🖥️  启动系统资源监控: 时长={duration}秒, 间隔={interval}秒")
        
        try:
            self.cpu_monitor = ResourceMonitorService(
                self.server_config['host'],
                self.server_config['username'],
                self.server_config['password']
            )
            self.cpu_monitoring = True
            self.cpu_data = []
            self.memory_data = []
            self.disk_data = []
            
            # 在后台线程中启动系统资源监控
            def monitor_resources():
                start_time = time.time()
                while self.cpu_monitoring and (time.time() - start_time) < duration:
                    try:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 采集CPU使用率
                        cpu_usage = self.cpu_monitor.collector.get_cpu_usage()
                        self.cpu_data.append((timestamp, cpu_usage))
                        
                        # 采集内存使用率
                        memory_info = self.cpu_monitor.collector.get_memory_usage()
                        self.memory_data.append((timestamp, memory_info))
                        
                        # 采集硬盘使用率
                        disk_info = self.cpu_monitor.collector.get_disk_usage()
                        self.disk_data.append((timestamp, disk_info))
                        
                        time.sleep(interval)
                    except Exception as e:
                        print(f"⚠️  系统资源监控异常: {e}")
                        time.sleep(interval)
            
            self.monitor_thread = threading.Thread(target=monitor_resources)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            print("✅ 系统资源监控已启动 (CPU + 内存 + 硬盘)")
            
        except Exception as e:
            print(f"❌ 启动系统资源监控失败: {e}")
            self.cpu_monitoring = False
    
    def stop_resource_monitoring(self):
        """停止系统资源监控"""
        if self.cpu_monitoring:
            self.cpu_monitoring = False
            if hasattr(self, 'monitor_thread'):
                self.monitor_thread.join(timeout=5)
            print("🛑 系统资源监控已停止")
        
        if self.cpu_monitor:
            self.cpu_monitor.close()
            self.cpu_monitor = None
    
    def analyze_cpu_data(self):
        """分析CPU数据"""
        if not self.cpu_data:
            return {}
        
        cpu_values = [usage for _, usage in self.cpu_data]
        
        stats = {
            'max_cpu': max(cpu_values),
            'min_cpu': min(cpu_values),
            'avg_cpu': sum(cpu_values) / len(cpu_values),
            'sample_count': len(cpu_values),
            'records': self.cpu_data
        }
        
        # 计算P90和P95
        if len(cpu_values) > 0:
            sorted_values = sorted(cpu_values)
            p90_index = int(len(sorted_values) * 0.9)
            p95_index = int(len(sorted_values) * 0.95)
            stats['p90_cpu'] = sorted_values[p90_index] if p90_index < len(sorted_values) else sorted_values[-1]
            stats['p95_cpu'] = sorted_values[p95_index] if p95_index < len(sorted_values) else sorted_values[-1]
        else:
            stats['p90_cpu'] = 0
            stats['p95_cpu'] = 0
        
        return stats

    def analyze_memory_data(self):
        """分析内存数据"""
        if not self.memory_data:
            return {}
        
        memory_usages = [info['usage_percent'] for _, info in self.memory_data]
        
        stats = {
            'max_memory': max(memory_usages),
            'min_memory': min(memory_usages),
            'avg_memory': sum(memory_usages) / len(memory_usages),
            'sample_count': len(memory_usages),
            'records': self.memory_data
        }
        
        # 计算P90和P95
        if len(memory_usages) > 0:
            sorted_values = sorted(memory_usages)
            p90_index = int(len(sorted_values) * 0.9)
            p95_index = int(len(sorted_values) * 0.95)
            stats['p90_memory'] = sorted_values[p90_index] if p90_index < len(sorted_values) else sorted_values[-1]
            stats['p95_memory'] = sorted_values[p95_index] if p95_index < len(sorted_values) else sorted_values[-1]
        else:
            stats['p90_memory'] = 0
            stats['p95_memory'] = 0
        
        return stats

    def analyze_disk_data(self):
        """分析硬盘数据"""
        if not self.disk_data:
            return {}
        
        disk_usages = [info['usage_percent'] for _, info in self.disk_data]
        
        stats = {
            'max_disk': max(disk_usages),
            'min_disk': min(disk_usages),
            'avg_disk': sum(disk_usages) / len(disk_usages),
            'sample_count': len(disk_usages),
            'records': self.disk_data
        }
        
        # 计算P90和P95
        if len(disk_usages) > 0:
            sorted_values = sorted(disk_usages)
            p90_index = int(len(sorted_values) * 0.9)
            p95_index = int(len(sorted_values) * 0.95)
            stats['p90_disk'] = sorted_values[p90_index] if p90_index < len(sorted_values) else sorted_values[-1]
            stats['p95_disk'] = sorted_values[p95_index] if p95_index < len(sorted_values) else sorted_values[-1]
        else:
            stats['p90_disk'] = 0
            stats['p95_disk'] = 0
        
        return stats
    
    def run_jmeter_test(self, jmx_path, test_name, test_duration=60):
        """运行JMeter测试"""
        print(f"🚀 开始执行JMeter测试: {test_name}")
        
        # 生成结果文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        jtl_file = os.path.join(self.results_dir, f"{test_name}_{timestamp}.jtl")
        log_file = os.path.join(self.results_dir, f"{test_name}_{timestamp}.log")
        report_dir = os.path.join(self.results_dir, f"{test_name}_{timestamp}_report")
        
        # 构建JMeter命令
        cmd = [
            self.jmeter_bin,
            "-n",  # 非GUI模式
            "-t", jmx_path,  # 测试计划文件
            "-l", jtl_file,  # 结果文件
            "-j", log_file,  # 日志文件
            "-e",  # 生成HTML报告
            "-o", report_dir  # 报告输出目录
        ]
        
        print(f"📋 执行命令: {' '.join(cmd)}")
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 启动资源监控
        self.start_resource_monitoring(test_duration + 30)  # 多监控30秒
        
        try:
            # 执行JMeter命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=os.path.dirname(self.jmeter_bin)
            )
            
            # 实时输出进度
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"   {output.strip()}")
            
            # 等待进程完成
            return_code = process.wait()
            
            # 记录结束时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 停止资源监控
            self.stop_resource_monitoring()
            
            if return_code == 0:
                print(f"✅ JMeter测试完成: {test_name}")
                print(f"⏱️  执行时间: {duration:.2f}秒")
                print(f"📊 结果文件: {jtl_file}")
                print(f"📈 报告目录: {report_dir}")
                return True, jtl_file, report_dir, duration
            else:
                error_output = process.stderr.read()
                print(f"❌ JMeter测试失败: {test_name}")
                print(f"错误信息: {error_output}")
                return False, None, None, duration
                
        except Exception as e:
            print(f"❌ 执行JMeter命令失败: {e}")
            self.stop_resource_monitoring()
            return False, None, None, 0
    
    def analyze_jtl_file(self, jtl_file):
        """分析JTL文件，统计测试结果"""
        print(f"📊 分析测试结果: {jtl_file}")
        
        if not os.path.exists(jtl_file):
            print(f"❌ JTL文件不存在: {jtl_file}")
            return {}
        
        stats = {
            'total_requests': 0,
            'success_count': 0,
            'fail_count': 0,
            'avg_response_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0,
            'response_times': []
        }
        
        try:
            with open(jtl_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stats['total_requests'] += 1
                    
                    # 统计成功/失败
                    if row.get('success', '').lower() == 'true':
                        stats['success_count'] += 1
                    else:
                        stats['fail_count'] += 1
                    
                    # 统计响应时间
                    try:
                        response_time = float(row.get('elapsed', 0))
                        stats['response_times'].append(response_time)
                        stats['min_response_time'] = min(stats['min_response_time'], response_time)
                        stats['max_response_time'] = max(stats['max_response_time'], response_time)
                    except (ValueError, TypeError):
                        pass
            
            # 计算平均响应时间
            if stats['response_times']:
                stats['avg_response_time'] = sum(stats['response_times']) / len(stats['response_times'])
                stats['min_response_time'] = stats['min_response_time'] if stats['min_response_time'] != float('inf') else 0
            else:
                stats['avg_response_time'] = 0
                stats['min_response_time'] = 0
            
            print(f"📊 总请求数: {stats['total_requests']}")
            print(f"📊 成功数: {stats['success_count']}")
            print(f"📊 失败数: {stats['fail_count']}")
            print(f"📊 平均响应时间: {stats['avg_response_time']:.2f}ms")
            
            return stats
            
        except Exception as e:
            print(f"❌ 分析JTL文件失败: {e}")
            return stats
    
    def run_batch_login_test(self):
        """运行批量登录测试"""
        print(f"\n🚀 开始批量登录测试")
        print(f"📊 固定线程数: {self.thread_count}")
        print(f"🔄 循环次数配置: {self.loop_configs}")
        
        # 获取测试前设备数量
        count_before = self.get_device_count()
        print(f"📈 测试前设备总数: {count_before}")
        
        test_results = []
        
        for i, loops in enumerate(self.loop_configs):
            print(f"\n{'='*20} 测试 {i+1}/{len(self.loop_configs)}: {loops} 循环 {'='*20}")
            
            # 修改JMX文件
            modified_jmx = self.modify_jmx_threads(self.thread_count, loops)
            test_name = f"login_test_{self.thread_count}threads_{loops}loops"
            
            # 估算测试时长
            estimated_duration = max(60, self.thread_count * loops * 0.1)
            
            # 运行测试
            success, jtl_file, report_dir, duration = self.run_jmeter_test(
                modified_jmx, test_name, estimated_duration
            )
            
            if success:
                # 分析测试结果
                stats = self.analyze_jtl_file(jtl_file)
                
                # 分析系统资源数据
                cpu_stats = self.analyze_cpu_data()
                memory_stats = self.analyze_memory_data()
                disk_stats = self.analyze_disk_data()
                
                # 获取测试后设备数量
                count_after = self.get_device_count()
                registered_count = count_after - count_before
                
                # 记录测试结果
                result = {
                    'test_name': test_name,
                    'thread_count': self.thread_count,
                    'loops': loops,
                    'expected_requests': self.thread_count * loops,
                    'actual_requests': stats.get('total_requests', 0),
                    'success_count': stats.get('success_count', 0),
                    'fail_count': stats.get('fail_count', 0),
                    'success_rate': stats.get('success_count', 0) / stats.get('total_requests', 1) * 100 if stats.get('total_requests', 0) > 0 else 0,
                    'avg_response_time': stats.get('avg_response_time', 0),
                    'min_response_time': stats.get('min_response_time', 0),
                    'max_response_time': stats.get('max_response_time', 0),
                    'duration': duration,
                    'count_before': count_before,
                    'count_after': count_after,
                    'registered_count': registered_count,
                    'jtl_file': jtl_file,
                    'report_dir': report_dir,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    # CPU监控数据
                    'cpu_max': cpu_stats.get('max_cpu', 0),
                    'cpu_min': cpu_stats.get('min_cpu', 0),
                    'cpu_avg': cpu_stats.get('avg_cpu', 0),
                    'cpu_p90': cpu_stats.get('p90_cpu', 0),
                    'cpu_p95': cpu_stats.get('p95_cpu', 0),
                    'cpu_sample_count': cpu_stats.get('sample_count', 0),
                    # 内存监控数据
                    'memory_max': memory_stats.get('max_memory', 0),
                    'memory_min': memory_stats.get('min_memory', 0),
                    'memory_avg': memory_stats.get('avg_memory', 0),
                    'memory_p90': memory_stats.get('p90_memory', 0),
                    'memory_p95': memory_stats.get('p95_memory', 0),
                    'memory_sample_count': memory_stats.get('sample_count', 0),
                    # 硬盘监控数据
                    'disk_max': disk_stats.get('max_disk', 0),
                    'disk_min': disk_stats.get('min_disk', 0),
                    'disk_avg': disk_stats.get('avg_disk', 0),
                    'disk_p90': disk_stats.get('p90_disk', 0),
                    'disk_p95': disk_stats.get('p95_disk', 0),
                    'disk_sample_count': disk_stats.get('sample_count', 0)
                }
                
                test_results.append(result)
                
                print(f"✅ 测试完成: {test_name}")
                print(f"📊 实际注册数量: {registered_count}")
                print(f"📈 注册成功率: {registered_count/(self.thread_count*loops)*100:.2f}%" if self.thread_count*loops > 0 else "📈 注册成功率: 0%")
                print(f"🖥️  CPU使用率: 最大={cpu_stats.get('max_cpu', 0):.1f}%, 平均={cpu_stats.get('avg_cpu', 0):.1f}%")
                print(f"💾 内存使用率: 最大={memory_stats.get('max_memory', 0):.1f}%, 平均={memory_stats.get('avg_memory', 0):.1f}%")
                print(f"💿 硬盘使用率: 最大={disk_stats.get('max_disk', 0):.1f}%, 平均={disk_stats.get('avg_disk', 0):.1f}%")
                
                # 更新基准数量
                count_before = count_after
                
            else:
                print(f"❌ 测试失败: {test_name}")
            
            # 测试间隔
            if i < len(self.loop_configs) - 1:
                print(f"\n⏳ 等待10秒后继续下一个测试...")
                time.sleep(10)
        
        # 生成综合报告
        self.generate_summary_report(test_results)
        
        return test_results
    
    def generate_summary_report(self, test_results):
        """生成综合报告"""
        print("\n📋 生成综合报告...")
        
        # 生成CSV报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = os.path.join(self.results_dir, f"batch_login_test_summary_{timestamp}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                '测试名称', '线程数', '循环次数', '预期请求数', '实际请求数',
                '成功数', '失败数', '成功率(%)', '平均响应时间(ms)',
                '最小响应时间(ms)', '最大响应时间(ms)', '执行时间(秒)',
                '注册前设备数', '注册后设备数', '实际注册数', '注册成功率(%)',
                'CPU最大值(%)', 'CPU最小值(%)', 'CPU平均值(%)', 'CPU_P90(%)', 'CPU_P95(%)', 'CPU采样点数',
                '内存最大值(%)', '内存最小值(%)', '内存平均值(%)', '内存_P90(%)', '内存_P95(%)', '内存采样点数',
                '硬盘最大值(%)', '硬盘最小值(%)', '硬盘平均值(%)', '硬盘_P90(%)', '硬盘_P95(%)', '硬盘采样点数',
                'JTL文件', '报告目录', '测试时间'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in test_results:
                writer.writerow({
                    '测试名称': result['test_name'],
                    '线程数': result['thread_count'],
                    '循环次数': result['loops'],
                    '预期请求数': result['expected_requests'],
                    '实际请求数': result['actual_requests'],
                    '成功数': result['success_count'],
                    '失败数': result['fail_count'],
                    '成功率(%)': f"{result['success_rate']:.2f}",
                    '平均响应时间(ms)': f"{result['avg_response_time']:.2f}",
                    '最小响应时间(ms)': f"{result['min_response_time']:.2f}",
                    '最大响应时间(ms)': f"{result['max_response_time']:.2f}",
                    '执行时间(秒)': f"{result['duration']:.2f}",
                    '注册前设备数': result['count_before'],
                    '注册后设备数': result['count_after'],
                    '实际注册数': result['registered_count'],
                    '注册成功率(%)': f"{result['registered_count']/result['expected_requests']*100:.2f}" if result['expected_requests'] > 0 else "0.00",
                    'CPU最大值(%)': f"{result['cpu_max']:.2f}",
                    'CPU最小值(%)': f"{result['cpu_min']:.2f}",
                    'CPU平均值(%)': f"{result['cpu_avg']:.2f}",
                    'CPU_P90(%)': f"{result['cpu_p90']:.2f}",
                    'CPU_P95(%)': f"{result['cpu_p95']:.2f}",
                    'CPU采样点数': result['cpu_sample_count'],
                    '内存最大值(%)': f"{result['memory_max']:.2f}",
                    '内存最小值(%)': f"{result['memory_min']:.2f}",
                    '内存平均值(%)': f"{result['memory_avg']:.2f}",
                    '内存_P90(%)': f"{result['memory_p90']:.2f}",
                    '内存_P95(%)': f"{result['memory_p95']:.2f}",
                    '内存采样点数': result['memory_sample_count'],
                    '硬盘最大值(%)': f"{result['disk_max']:.2f}",
                    '硬盘最小值(%)': f"{result['disk_min']:.2f}",
                    '硬盘平均值(%)': f"{result['disk_avg']:.2f}",
                    '硬盘_P90(%)': f"{result['disk_p90']:.2f}",
                    '硬盘_P95(%)': f"{result['disk_p95']:.2f}",
                    '硬盘采样点数': result['disk_sample_count'],
                    'JTL文件': result['jtl_file'],
                    '报告目录': result['report_dir'],
                    '测试时间': result['timestamp']
                })
        
        print(f"📊 CSV报告已生成: {csv_file}")
        
        # 生成JSON报告
        json_file = os.path.join(self.results_dir, f"batch_login_test_summary_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📋 JSON报告已生成: {json_file}")
        
        # 打印总结
        print("\n" + "="*60)
        print(f"🎯 批量登录测试总结")
        print("="*60)
        
        total_expected = sum(r['expected_requests'] for r in test_results)
        total_actual = sum(r['actual_requests'] for r in test_results)
        total_success = sum(r['success_count'] for r in test_results)
        total_registered = sum(r['registered_count'] for r in test_results)
        
        # CPU统计
        all_cpu_avg = [r['cpu_avg'] for r in test_results if r['cpu_avg'] > 0]
        avg_cpu_usage = sum(all_cpu_avg) / len(all_cpu_avg) if all_cpu_avg else 0
        max_cpu_usage = max([r['cpu_max'] for r in test_results]) if test_results else 0
        
        # 内存统计
        all_memory_avg = [r['memory_avg'] for r in test_results if r['memory_avg'] > 0]
        avg_memory_usage = sum(all_memory_avg) / len(all_memory_avg) if all_memory_avg else 0
        max_memory_usage = max([r['memory_max'] for r in test_results]) if test_results else 0
        
        # 硬盘统计
        all_disk_avg = [r['disk_avg'] for r in test_results if r['disk_avg'] > 0]
        avg_disk_usage = sum(all_disk_avg) / len(all_disk_avg) if all_disk_avg else 0
        max_disk_usage = max([r['disk_max'] for r in test_results]) if test_results else 0
        
        print(f"📊 总预期请求数: {total_expected}")
        print(f"📊 总实际请求数: {total_actual}")
        print(f"📊 总成功请求数: {total_success}")
        print(f"📊 总注册设备数: {total_registered}")
        print(f"📈 整体成功率: {total_success/total_actual*100:.2f}%" if total_actual > 0 else "📈 整体成功率: 0%")
        print(f"📈 整体注册率: {total_registered/total_expected*100:.2f}%" if total_expected > 0 else "📈 整体注册率: 0%")
        print(f"🖥️  平均CPU使用率: {avg_cpu_usage:.2f}%")
        print(f"🖥️  最大CPU使用率: {max_cpu_usage:.2f}%")
        print(f"💾 平均内存使用率: {avg_memory_usage:.2f}%")
        print(f"💾 最大内存使用率: {max_memory_usage:.2f}%")
        print(f"💿 平均硬盘使用率: {avg_disk_usage:.2f}%")
        print(f"💿 最大硬盘使用率: {max_disk_usage:.2f}%")
        
        print(f"\n📁 所有结果文件保存在: {self.results_dir}")

def main():
    """主函数"""
    print("🚀 批量登录测试工具")
    print("="*50)
    
    # 创建测试实例
    tester = BatchLoginTest()
    
    # 检查前置条件
    if not tester.check_prerequisites():
        print("❌ 前置条件检查失败，退出测试")
        return
    
    # 运行批量测试
    try:
        test_results = tester.run_batch_login_test()
        print(f"\n✅ 批量登录测试完成，共执行 {len(test_results)} 个测试")
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
        tester.stop_resource_monitoring()
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        tester.stop_resource_monitoring()

if __name__ == "__main__":
    main() 