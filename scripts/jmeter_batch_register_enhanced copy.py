            from src.infrastructure.monitor.remote_resource_collector import RemoteResourceCollector
        import io
from datetime import datetime
from pathlib import Path
from src.application.monitor.resource_monitor_service import ResourceMonitorService
from src.application.services.device_query_service import DeviceQueryService
import argparse
import csv
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版JMETER批量注册脚本
- 完全替代图形界面操作
- 支持不同线程数的批量注册
- 支持批量注册和批量登录两种测试场景
- 集成CPU监控功能
- 自动验证注册数量
- 生成综合报告
"""

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)


# 设置标准输出为UTF-8编码
if sys.stdout.encoding is None or sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

# 固定模板文件路径（只读，严格引用实际位置）
JMX_TEMPLATE_PATH = os.path.join('src', 'tools', 'jmeter', 'bin', 'register_test_python_format.jmx')
CSV_TEMPLATE_PATH = os.path.join('src', 'tools', 'jmeter', 'bin', 'new_devices_100000.csv')
RESULTS_DIR = os.path.join('src', 'tools', 'jmeter', 'results')

class EnhancedJMeterBatchRegister:
    """增强版JMETER批量注册管理器"""
    
    def __init__(self):
        """初始化批量注册测试类"""
        # 修复：使用绝对路径
        self.jmeter_bin = os.path.abspath(os.path.join('src', 'tools', 'jmeter', 'bin', 'jmeter.bat'))
        self.results_dir = RESULTS_DIR
        os.makedirs(self.results_dir, exist_ok=True)
        
        # 加载服务器配置
        self.server_config = {
            'host': '192.168.24.45',
            'username': 'test',
            'password': '1'
        }
        
        # 初始化监控服务
        try:
            self.cpu_monitor = RemoteResourceCollector(
                host=self.server_config['host'],
                username=self.server_config['username'],
                password=self.server_config['password']
            )
            # 测试SSH连接
            test_result = self.cpu_monitor.get_cpu_usage()
            if test_result is None:
                print("⚠️ SSH连接测试失败，硬件监控将被禁用")
                self.cpu_monitor = None
            else:
                print("✅ SSH连接测试成功，硬件监控已启用")
        except Exception as e:
            print(f"⚠️ 初始化硬件监控失败: {e}，硬件监控将被禁用")
            self.cpu_monitor = None
        
        # 初始化监控数据结构（统一使用monitoring_data）
        self.monitoring_data = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'process': []
        }
        
        # 数据库配置
        self.db_config = {
            'host': '192.168.24.45',
            'port': 3307,
            'user': 'root',
            'password': 'At6mj*1ygb2',
            'database': 'yangguan'
        }
        
        # 增量测试相关
        self.last_device_count = 0
        self.current_device_count = 0
        # 修复：初始化cpu_monitoring属性
        self.cpu_monitoring = False

    def check_prerequisites(self):
        """检查前置条件"""
        # 检查JMeter可执行文件
        if not os.path.exists(self.jmeter_bin):
            print(f"❌ JMeter可执行文件不存在: {self.jmeter_bin}")
            return False
            
        # 检查JMX模板文件
        if not os.path.exists(JMX_TEMPLATE_PATH):
            print(f"❌ JMX模板文件不存在: {JMX_TEMPLATE_PATH}")
            return False
            
        # 检查结果目录
        if not os.path.exists(self.results_dir):
            try:
                os.makedirs(self.results_dir)
                print(f"✅ 创建结果目录: {self.results_dir}")
            except Exception as e:
                print(f"❌ 创建结果目录失败: {e}")
                return False
                
        return True
    
    def get_device_count_before(self):
        """获取注册前的设备数量"""
        print("📊 获取注册前的设备数量...")
        try:
            service = DeviceQueryService(self.db_config)
            count = service.get_device_count('biz_device')
            service.close()
            print(f"📈 注册前设备总数: {count}")
            return count
        except Exception as e:
            print(f"❌ 获取设备数量失败: {e}")
            return 0
    
    def modify_jmx_threads(self, thread_count, loops=1):
        """以固定模板生成新JMX，线程数/循环数可变，输出到results目录，并校验循环次数参数是否生效"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_jmx = os.path.join(self.results_dir, f'register_test_{thread_count}threads_{loops}loops_{timestamp}.jmx')
        try:
            shutil.copy2(JMX_TEMPLATE_PATH, new_jmx)
            with open(new_jmx, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(r'<stringProp name="ThreadGroup.num_threads">\d+</stringProp>',
                            f'<stringProp name="ThreadGroup.num_threads">{thread_count}</stringProp>', content)
            content = re.sub(r'<stringProp name="LoopController.loops">\d+</stringProp>',
                            f'<stringProp name="LoopController.loops">{loops}</stringProp>', content)
            with open(new_jmx, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"🔧 修改后的JMX文件已保存: {new_jmx}")
            # 校验循环次数参数
            with open(new_jmx, 'r', encoding='utf-8') as f:
                check_content = f.read()
            match = re.search(r'<stringProp name="LoopController.loops">(\d+)</stringProp>', check_content)
            if match:
                actual_loops = int(match.group(1))
                print(f"✅ JMX循环次数参数已设置为: {actual_loops}")
                if actual_loops != loops:
                    print(f"❌ [循环次数校验失败] 期望: {loops}，实际: {actual_loops}，请检查模板替换逻辑！")
                    raise ValueError("JMX循环次数参数未正确替换")
            else:
                print("❌ [循环次数校验失败] 未找到LoopController.loops字段！")
                raise ValueError("JMX循环次数参数未找到")
            return new_jmx
        except Exception as e:
            print(f"❌ 修改JMX文件失败: {e}")
            return None
    
    def prepare_csv(self):
        """始终以固定CSV模板生成新CSV，输出到results目录，命名带时间戳"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_csv = os.path.join(self.results_dir, f'new_devices_for_test_{timestamp}.csv')
        shutil.copy2(CSV_TEMPLATE_PATH, new_csv)
        print(f"✅ 生成测试用CSV: {new_csv}")
        return new_csv
    
    def start_cpu_monitoring(self, duration, interval=2):
        """启动CPU监控"""
        if not self.cpu_monitor:
            print("⚠️ 硬件监控未启用，跳过监控")
            return
            
        self.monitoring_start_time = time.time()
        self.monitoring_duration = duration
        self.monitoring_interval = interval
        # 修复：启动时设置cpu_monitoring为True
        self.cpu_monitoring = True

        def monitor_resources():
            while time.time() - self.monitoring_start_time < self.monitoring_duration and self.cpu_monitoring:
                try:
                    # 采集CPU使用率
                    cpu_usage = self.cpu_monitor.get_cpu_usage()
                    if cpu_usage is not None:
                        self.monitoring_data['cpu'].append((time.time(), cpu_usage))

                    # 采集内存使用率
                    memory_info = self.cpu_monitor.get_memory_usage()
                    if memory_info is not None:
                        self.monitoring_data['memory'].append((time.time(), memory_info))

                    # 采集磁盘使用率
                    disk_info = self.cpu_monitor.get_disk_usage()
                    if disk_info is not None:
                        self.monitoring_data['disk'].append((time.time(), disk_info))

                    # 采集进程信息
                    process_info = self.cpu_monitor.get_process_info()
                    if process_info is not None:
                        self.monitoring_data['process'].append((time.time(), process_info))

                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    print(f"⚠️ 监控数据采集异常: {e}")
                    time.sleep(1)

        self.monitoring_thread = threading.Thread(target=monitor_resources)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        print("🔄 硬件监控已启动")
    
    def stop_cpu_monitoring(self):
        """停止系统资源监控并关闭连接"""
        if self.cpu_monitoring:
            self.cpu_monitoring = False
            if hasattr(self, 'monitoring_thread'):
                self.monitoring_thread.join(timeout=5)
            print("🛑 系统资源监控已停止")
        # 确保关闭SSH连接
        if self.cpu_monitor:
            # 修复：RemoteResourceCollector没有close方法，需判断后再调用
            if hasattr(self.cpu_monitor, 'close') and callable(self.cpu_monitor.close):
                self.cpu_monitor.close()
            # 否则仅置为None
            self.cpu_monitor = None
    
    def analyze_cpu_data(self):
        """分析CPU数据，采集所有核总数和所有核平均使用率"""
        if not self.monitoring_data['cpu']:
            return {}
        cpu_values = [usage for _, usage in self.monitoring_data['cpu']]
        stats = {
            'max_cpu': max(cpu_values),
            'min_cpu': min(cpu_values),
            'avg_cpu': sum(cpu_values) / len(cpu_values),
            'sample_count': len(cpu_values),
            'records': self.monitoring_data['cpu']
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
        # 计算CPU变化率
        if stats['min_cpu'] > 0:
            stats['cpu_change_rate'] = ((stats['max_cpu'] - stats['min_cpu']) / stats['min_cpu'] * 100)
        else:
            stats['cpu_change_rate'] = 0
        # 获取所有核总数
        try:
            if not self.cpu_monitor:
                stats['cpu_cores'] = 0
                return stats
            cpu_cores = self._ssh_exec("nproc")
            if cpu_cores.isdigit():
                stats['cpu_cores'] = int(cpu_cores)
                print(f"✅ [硬件监控] 服务器CPU总核数: {stats['cpu_cores']}")
            else:
                stats['cpu_cores'] = 0
                print(f"❌ [硬件监控] 获取CPU核数失败，返回: {cpu_cores}")
        except Exception as e:
            print(f"❌ [硬件监控] 获取CPU核数异常: {e}")
            stats['cpu_cores'] = 0
        return stats

    def analyze_memory_data(self):
        """分析内存数据"""
        if not self.monitoring_data['memory']:
            return {}
        
        memory_usages = [info['usage_percent'] for _, info in self.monitoring_data['memory']]
        
        stats = {
            'max_memory': max(memory_usages),
            'min_memory': min(memory_usages),
            'avg_memory': sum(memory_usages) / len(memory_usages),
            'sample_count': len(memory_usages),
            'records': self.monitoring_data['memory']
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
        
        # 计算内存变化率
        if stats['min_memory'] > 0:
            stats['memory_change_rate'] = ((stats['max_memory'] - stats['min_memory']) / stats['min_memory'] * 100)
        else:
            stats['memory_change_rate'] = 0
        
        return stats

    def analyze_disk_data(self):
        """分析硬盘数据"""
        if not self.monitoring_data['disk']:
            return {}
        
        disk_usages = [info['usage_percent'] for _, info in self.monitoring_data['disk']]
        
        stats = {
            'max_disk': max(disk_usages),
            'min_disk': min(disk_usages),
            'avg_disk': sum(disk_usages) / len(disk_usages),
            'sample_count': len(disk_usages),
            'records': self.monitoring_data['disk']
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
        
        # 计算硬盘变化率
        if stats['min_disk'] > 0:
            stats['disk_change_rate'] = ((stats['max_disk'] - stats['min_disk']) / stats['min_disk'] * 100)
        else:
            stats['disk_change_rate'] = 0
        
        return stats
    
    def run_jmeter_test(self, jmx_path, test_name, test_duration=60):
        """运行JMETER测试"""
        print(f"🚀 开始执行JMETER测试: {test_name}")
        
        # 生成结果文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        jtl_file = os.path.join(self.results_dir, f"{test_name}_{timestamp}.jtl")
        log_file = os.path.join(self.results_dir, f"{test_name}_{timestamp}.log")
        report_dir = os.path.join(self.results_dir, f"{test_name}_{timestamp}_report")
        
        # 构建JMETER命令
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
        
        # 启动CPU监控
        self.start_cpu_monitoring(test_duration + 30)  # 多监控30秒
        
        try:
            # 修复：去掉cwd参数，直接在当前目录下执行
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
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
            
            # 停止CPU监控
            self.stop_cpu_monitoring()
            
            if return_code == 0:
                print(f"✅ JMETER测试完成: {test_name}")
                print(f"⏱️  执行时间: {duration:.2f}秒")
                print(f"📊 结果文件: {jtl_file}")
                print(f"📈 报告目录: {report_dir}")
                return True, jtl_file, report_dir, duration
            else:
                error_output = process.stderr.read()
                print(f"❌ JMETER测试失败: {test_name}")
                print(f"错误信息: {error_output}")
                return False, None, None, duration
                
        except Exception as e:
            print(f"❌ 执行JMETER命令失败: {e}")
            self.stop_cpu_monitoring()
            return False, None, None, 0
    
    def get_device_count_after(self):
        """获取注册后的设备数量"""
        print("📊 获取注册后的设备数量...")
        try:
            service = DeviceQueryService(self.db_config)
            count = service.get_device_count('biz_device')
            service.close()
            print(f"📈 注册后设备总数: {count}")
            return count
        except Exception as e:
            print(f"❌ 获取设备数量失败: {e}")
            return 0
    
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
            'response_times': [],
            'jtl_duration_sec': 0,  # 新增：JTL文件真实执行时间
            'jtl_start_time': None,  # 新增：JTL开始时间
            'jtl_end_time': None,    # 新增：JTL结束时间
            # 新增：JMeter标准参数
            'response_time_std': 0,  # 响应时间标准差
            'throughput': 0,         # 吞吐量
            'received_kb_per_sec': 0, # 每秒接收KB数
            'sent_kb_per_sec': 0,    # 每秒发送KB数
            'avg_bytes': 0,          # 平均字节数
            'total_received_bytes': 0, # 总接收字节数
            'total_sent_bytes': 0,   # 总发送字节数
            'labels': set()          # 标签集合
        }
        
        try:
            timestamps = []  # 存储所有时间戳
            bytes_received = []  # 存储接收字节数
            bytes_sent = []      # 存储发送字节数
            
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
                    
                    # 收集时间戳用于计算JTL执行时间
                    try:
                        timestamp = int(row.get('timeStamp', 0))
                        if timestamp > 0:
                            timestamps.append(timestamp)
                    except (ValueError, TypeError):
                        pass
                    
                    # 收集字节数信息
                    try:
                        bytes_val = int(row.get('bytes', 0))
                        bytes_received.append(bytes_val)
                        stats['total_received_bytes'] += bytes_val
                    except (ValueError, TypeError):
                        pass
                    
                    try:
                        sent_bytes = int(row.get('sentBytes', 0))
                        bytes_sent.append(sent_bytes)
                        stats['total_sent_bytes'] += sent_bytes
                    except (ValueError, TypeError):
                        pass
                    
                    # 收集标签
                    label = row.get('label', '')
                    if label:
                        stats['labels'].add(label)
            
            # 计算JTL文件真实执行时间
            if timestamps:
                start_timestamp = min(timestamps)
                end_timestamp = max(timestamps)
                stats['jtl_duration_sec'] = (end_timestamp - start_timestamp) / 1000.0
                stats['jtl_start_time'] = datetime.fromtimestamp(start_timestamp / 1000.0).strftime('%H:%M:%S.%f')[:-3]
                stats['jtl_end_time'] = datetime.fromtimestamp(end_timestamp / 1000.0).strftime('%H:%M:%S.%f')[:-3]
            
            # 计算平均响应时间
            if stats['response_times']:
                stats['avg_response_time'] = sum(stats['response_times']) / len(stats['response_times'])
                stats['min_response_time'] = min(stats['response_times'])
                stats['max_response_time'] = max(stats['response_times'])
                
                # 计算响应时间标准差
                mean_response = stats['avg_response_time']
                variance = sum((x - mean_response) ** 2 for x in stats['response_times']) / len(stats['response_times'])
                stats['response_time_std'] = variance ** 0.5
            
            # 计算吞吐量
            if stats['jtl_duration_sec'] > 0:
                stats['throughput'] = stats['total_requests'] / stats['jtl_duration_sec']
            
            # 计算网络指标
            if stats['jtl_duration_sec'] > 0:
                stats['received_kb_per_sec'] = (stats['total_received_bytes'] / 1024) / stats['jtl_duration_sec']
                stats['sent_kb_per_sec'] = (stats['total_sent_bytes'] / 1024) / stats['jtl_duration_sec']
            
            # 计算平均字节数
            if stats['total_requests'] > 0:
                stats['avg_bytes'] = stats['total_received_bytes'] / stats['total_requests']
            
            # 转换标签集合为列表
            stats['labels'] = list(stats['labels'])
            
            print(f"📈 测试统计:")
            print(f"   总请求数: {stats['total_requests']}")
            print(f"   成功数: {stats['success_count']}")
            print(f"   失败数: {stats['fail_count']}")
            print(f"   成功率: {stats['success_count']/stats['total_requests']*100:.2f}%" if stats['total_requests'] > 0 else "   成功率: 0%")
            print(f"   错误率: {stats['fail_count']/stats['total_requests']*100:.2f}%" if stats['total_requests'] > 0 else "   错误率: 0%")
            print(f"   平均响应时间: {stats['avg_response_time']:.2f}ms")
            print(f"   最小响应时间: {stats['min_response_time']:.2f}ms")
            print(f"   最大响应时间: {stats['max_response_time']:.2f}ms")
            print(f"   响应时间标准差: {stats['response_time_std']:.2f}ms")
            print(f"   吞吐量: {stats['throughput']:.2f} 请求/秒")
            print(f"   每秒接收KB数: {stats['received_kb_per_sec']:.2f}")
            print(f"   每秒发送KB数: {stats['sent_kb_per_sec']:.2f}")
            print(f"   平均字节数: {stats['avg_bytes']:.2f}")
            print(f"   JTL执行时间: {stats['jtl_duration_sec']:.3f}秒")
            print(f"   JTL开始时间: {stats['jtl_start_time']}")
            print(f"   JTL结束时间: {stats['jtl_end_time']}")
            print(f"   标签: {', '.join(stats['labels'])}")
            
            return stats
            
        except Exception as e:
            print(f"❌ 分析JTL文件失败: {e}")
            return {}
    
    def run_batch_test(self, thread_configs, test_type="register", iteration_num=1):
        """运行批量测试"""
        print(f"🎯 开始批量{test_type}测试")
        print("=" * 60)
        
        # 检查前置条件
        self.check_prerequisites()
        
        # 获取注册前的设备数量
        count_before = self.get_device_count_before()
        
        # 存储测试结果
        test_results = []
        
        # 执行每个配置的测试
        for i, config in enumerate(thread_configs):
            thread_count = config['threads']
            loops = config.get('loops', 1)
            
            print(f"\n{'='*20} 测试配置 {i+1}/{len(thread_configs)} {'='*20}")
            print(f"🧵 线程数: {thread_count}")
            print(f"🔄 循环次数: {loops}")
            print(f"📊 预期总请求数: {thread_count * loops}")
            print(f"🎯 测试类型: {test_type}")
            
            # 修改JMX文件
            modified_jmx = self.modify_jmx_threads(thread_count, loops)
            
            # 估算测试时长
            estimated_duration = max(60, thread_count * loops * 0.1)  # 至少60秒
            
            # 运行测试
            test_name = f"iter{iteration_num}_{test_type}_{thread_count}threads_{loops}loops"
            success, jtl_file, report_dir, duration = self.run_jmeter_test(modified_jmx, test_name, estimated_duration)
            
            if success:
                # 分析测试结果
                stats = self.analyze_jtl_file(jtl_file)
                
                # 分析系统资源数据
                cpu_stats = self.analyze_cpu_data()
                memory_stats = self.analyze_memory_data()
                disk_stats = self.analyze_disk_data()
                
                # 获取注册后的设备数量
                count_after = self.get_device_count_after()
                registered_count = count_after - count_before
                
                # 记录测试结果
                result = {
                    'test_name': test_name,
                    'test_type': test_type,
                    'thread_count': thread_count,
                    'loops': loops,
                    'expected_requests': thread_count * loops,
                    'actual_requests': stats.get('total_requests', 0),
                    'success_count': stats.get('success_count', 0),
                    'fail_count': stats.get('fail_count', 0),
                    'success_rate': stats.get('success_count', 0) / stats.get('total_requests', 1) * 100 if stats.get('total_requests', 0) > 0 else 0,
                    'avg_response_time': stats.get('avg_response_time', 0),
                    'min_response_time': stats.get('min_response_time', 0),
                    'max_response_time': stats.get('max_response_time', 0),
                    'response_time_std': stats.get('response_time_std', 0),  # 新增：响应时间标准差
                    'duration': duration,  # 脚本执行时间（包含进程开销）
                    'jtl_duration_sec': stats.get('jtl_duration_sec', 0),  # 新增：JTL文件真实执行时间
                    'jtl_start_time': stats.get('jtl_start_time', ''),  # 新增：JTL开始时间
                    'jtl_end_time': stats.get('jtl_end_time', ''),  # 新增：JTL结束时间
                    # 新增：JMeter标准参数
                    'throughput': stats.get('throughput', 0),
                    'received_kb_per_sec': stats.get('received_kb_per_sec', 0),
                    'sent_kb_per_sec': stats.get('sent_kb_per_sec', 0),
                    'avg_bytes': stats.get('avg_bytes', 0),
                    'labels': stats.get('labels', []),
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
                    'cpu_change_rate': cpu_stats.get('cpu_change_rate', 0),
                    'cpu_sample_count': cpu_stats.get('sample_count', 0),
                    # 新增：CPU详细信息
                    'cpu_cores': cpu_stats.get('cpu_cores', 0),
                    'load_1min': cpu_stats.get('load_1min', 0),
                    'load_5min': cpu_stats.get('load_5min', 0),
                    'load_15min': cpu_stats.get('load_15min', 0),
                    'cpu_temperature': cpu_stats.get('cpu_temperature', 0),
                    'process_count': cpu_stats.get('process_count', 0),
                    'system_thread_count': cpu_stats.get('thread_count', 0),  # 修复：重命名为system_thread_count
                    'context_switches': cpu_stats.get('context_switches', 0),
                    # 内存监控数据
                    'memory_max': memory_stats.get('max_memory', 0),
                    'memory_min': memory_stats.get('min_memory', 0),
                    'memory_avg': memory_stats.get('avg_memory', 0),
                    'memory_p90': memory_stats.get('p90_memory', 0),
                    'memory_p95': memory_stats.get('p95_memory', 0),
                    'memory_change_rate': memory_stats.get('memory_change_rate', 0),
                    'memory_sample_count': memory_stats.get('sample_count', 0),
                    # 硬盘监控数据
                    'disk_max': disk_stats.get('max_disk', 0),
                    'disk_min': disk_stats.get('min_disk', 0),
                    'disk_avg': disk_stats.get('avg_disk', 0),
                    'disk_p90': disk_stats.get('p90_disk', 0),
                    'disk_p95': disk_stats.get('p95_disk', 0),
                    'disk_change_rate': disk_stats.get('disk_change_rate', 0),
                    'disk_sample_count': disk_stats.get('sample_count', 0)
                }
                
                # 调试信息：打印result中的thread_count
                print(f"🔍 调试信息 - result['thread_count']: {result['thread_count']}")
                
                test_results.append(result)
                
                print(f"✅ 测试完成: {test_name}")
                print(f"📊 实际注册数量: {registered_count}")
                print(f"📈 注册成功率: {registered_count/(thread_count*loops)*100:.2f}%" if thread_count*loops > 0 else "📈 注册成功率: 0%")
                print(f"🖥️  CPU使用率: 最大={cpu_stats.get('max_cpu', 0):.1f}%, 平均={cpu_stats.get('avg_cpu', 0):.1f}%")
                print(f"💾 内存使用率: 最大={memory_stats.get('max_memory', 0):.1f}%, 平均={memory_stats.get('avg_memory', 0):.1f}%")
                print(f"💿 硬盘使用率: 最大={disk_stats.get('max_disk', 0):.1f}%, 平均={disk_stats.get('avg_disk', 0):.1f}%")
                
                # 更新基准数量
                count_before = count_after
                
            else:
                print(f"❌ 测试失败: {test_name}")
            
            # 测试间隔
            if i < len(thread_configs) - 1:
                print(f"\n⏳ 等待10秒后继续下一个测试...")
                time.sleep(10)
        
        # 生成综合报告
        self.generate_summary_report(test_results, f"{test_type}_iterative_summary")
        
        return test_results
    
    def generate_summary_report(self, test_results, test_type):
        """生成综合报告"""
        print("\n📋 生成综合报告...")
        
        # 定义字段重要级别排序（重要程度从高到低）
        field_priority = [
            # 核心测试信息
            '测试名称', '测试类型', '线程数', '循环次数', '预期请求数', '实际请求数',
            '成功数', '失败数', '成功率(%)', '错误率(%)',
            # 响应时间指标
            '平均响应时间(ms)', '最小响应时间(ms)', '最大响应时间(ms)', '响应时间标准差(ms)',
            # 执行时间
            '脚本执行时间(秒)', 'JTL执行时间(秒)', 'JTL开始时间', 'JTL结束时间',
            # 吞吐量指标
            '吞吐量(请求/秒)', '每秒接收KB数', '每秒发送KB数', '平均字节数',
            # 注册结果
            '注册前设备数', '注册后设备数', '实际注册数', '注册成功率(%)',
            # CPU监控（按重要程度排序）
            'CPU平均值(%)', 'CPU最大值(%)', 'CPU_P95(%)', 'CPU_P90(%)', 'CPU最小值(%)', 'CPU变化率(%)', 'CPU采样点数',
            'CPU核心数', '系统负载_1分钟', '系统负载_5分钟', '系统负载_15分钟', 'CPU温度(°C)', '进程数', '系统线程数', '上下文切换数',
            # 内存监控（按重要程度排序）
            '内存平均值(%)', '内存最大值(%)', '内存_P95(%)', '内存_P90(%)', '内存最小值(%)', '内存变化率(%)', '内存采样点数',
            # 硬盘监控（按重要程度排序）
            '硬盘平均值(%)', '硬盘最大值(%)', '硬盘_P95(%)', '硬盘_P90(%)', '硬盘最小值(%)', '硬盘变化率(%)', '硬盘采样点数',
            # 文件信息
            'JTL文件', '报告目录', '测试时间'
        ]
        
        # 生成横标题报告（标准CSV格式）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file_horizontal = os.path.join(self.results_dir, f"enhanced_{test_type}_summary_horizontal_{timestamp}.csv")
        
        with open(csv_file_horizontal, 'w', newline='', encoding='utf-8') as f:
            # 按重要级别排序字段
            ordered_fieldnames = [field for field in field_priority if field in self._get_all_fieldnames()]
            
            writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
            writer.writeheader()
            
            for result in test_results:
                row_data = self._prepare_report_row(result, ordered_fieldnames)
                writer.writerow(row_data)
        
        print(f"📊 横标题CSV报告已生成: {csv_file_horizontal}")
        
        # 生成列标题报告（转置格式）
        csv_file_vertical = os.path.join(self.results_dir, f"enhanced_{test_type}_summary_vertical_{timestamp}.csv")
        
        with open(csv_file_vertical, 'w', newline='', encoding='utf-8') as f:
            # 按重要级别排序字段
            ordered_fieldnames = [field for field in field_priority if field in self._get_all_fieldnames()]
            
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow(['指标名称'] + [result['test_name'] for result in test_results])
            
            # 按重要级别写入每行数据
            for field in ordered_fieldnames:
                row_data = [field]
                for result in test_results:
                    value = self._get_field_value(result, field)
                    row_data.append(value)
                writer.writerow(row_data)
        
        print(f"📊 列标题CSV报告已生成: {csv_file_vertical}")
        
        # 生成JSON报告
        json_file = os.path.join(self.results_dir, f"enhanced_{test_type}_summary_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📋 JSON报告已生成: {json_file}")
        
        # 打印总结
        self._print_summary_report(test_results)
        
        print(f"\n📁 所有结果文件保存在: {self.results_dir}")
        print(f"📄 横标题报告: {csv_file_horizontal}")
        print(f"📄 列标题报告: {csv_file_vertical}")
        print(f"📄 JSON报告: {json_file}")
    
    def _get_all_fieldnames(self):
        """获取所有可能的字段名"""
        return [
            '测试名称', '测试类型', '线程数', '循环次数', '预期请求数', '实际请求数',
            '成功数', '失败数', '成功率(%)', '错误率(%)',
            '平均响应时间(ms)', '最小响应时间(ms)', '最大响应时间(ms)', '响应时间标准差(ms)',
            '脚本执行时间(秒)', 'JTL执行时间(秒)', 'JTL开始时间', 'JTL结束时间',
            '吞吐量(请求/秒)', '每秒接收KB数', '每秒发送KB数', '平均字节数',
            '注册前设备数', '注册后设备数', '实际注册数', '注册成功率(%)',
            'CPU平均值(%)', 'CPU最大值(%)', 'CPU_P95(%)', 'CPU_P90(%)', 'CPU最小值(%)', 'CPU变化率(%)', 'CPU采样点数',
            'CPU核心数', '系统负载_1分钟', '系统负载_5分钟', '系统负载_15分钟', 'CPU温度(°C)', '进程数', '系统线程数', '上下文切换数',
            '内存平均值(%)', '内存最大值(%)', '内存_P95(%)', '内存_P90(%)', '内存最小值(%)', '内存变化率(%)', '内存采样点数',
            '硬盘平均值(%)', '硬盘最大值(%)', '硬盘_P95(%)', '硬盘_P90(%)', '硬盘最小值(%)', '硬盘变化率(%)', '硬盘采样点数',
            'JTL文件', '报告目录', '测试时间'
        ]
    
    def _prepare_report_row(self, result, fieldnames):
        """准备报告行数据"""
        row_data = {}
        for field in fieldnames:
            row_data[field] = self._get_field_value(result, field)
        return row_data
    
    def _get_field_value(self, result, field):
        """获取字段值"""
        field_mapping = {
            '测试名称': result['test_name'],
            '测试类型': result['test_type'],
            '线程数': result['thread_count'],
            '循环次数': result['loops'],
            '预期请求数': result['expected_requests'],
            '实际请求数': result['actual_requests'],
            '成功数': result['success_count'],
            '失败数': result['fail_count'],
            '成功率(%)': f"{result['success_rate']:.2f}",
            '错误率(%)': f"{100 - result['success_rate']:.2f}",
            '平均响应时间(ms)': f"{result['avg_response_time']:.2f}",
            '最小响应时间(ms)': f"{result['min_response_time']:.2f}" if result['min_response_time'] != float('inf') else "0.00",
            '最大响应时间(ms)': f"{result['max_response_time']:.2f}",
            '响应时间标准差(ms)': f"{result.get('response_time_std', 0):.2f}",
            '脚本执行时间(秒)': f"{result['duration']:.2f}",
            'JTL执行时间(秒)': f"{result['jtl_duration_sec']:.3f}",
            'JTL开始时间': result['jtl_start_time'] if result['jtl_start_time'] else "",
            'JTL结束时间': result['jtl_end_time'] if result['jtl_end_time'] else "",
            '吞吐量(请求/秒)': f"{result.get('throughput', 0):.2f}",
            '每秒接收KB数': f"{result.get('received_kb_per_sec', 0):.2f}",
            '每秒发送KB数': f"{result.get('sent_kb_per_sec', 0):.2f}",
            '平均字节数': f"{result.get('avg_bytes', 0):.2f}",
            '注册前设备数': result['count_before'],
            '注册后设备数': result['count_after'],
            '实际注册数': result['registered_count'],
            '注册成功率(%)': f"{result['registered_count']/result['expected_requests']*100:.2f}" if result['expected_requests'] > 0 else "0.00",
            'CPU平均值(%)': f"{result['cpu_avg']:.2f}",
            'CPU最大值(%)': f"{result['cpu_max']:.2f}",
            'CPU_P95(%)': f"{result['cpu_p95']:.2f}",
            'CPU_P90(%)': f"{result['cpu_p90']:.2f}",
            'CPU最小值(%)': f"{result['cpu_min']:.2f}",
            'CPU变化率(%)': f"{result['cpu_change_rate']:.2f}",
            'CPU采样点数': result['cpu_sample_count'],
            'CPU核心数': result.get('cpu_cores', 0),
            '系统负载_1分钟': f"{result.get('load_1min', 0):.2f}",
            '系统负载_5分钟': f"{result.get('load_5min', 0):.2f}",
            '系统负载_15分钟': f"{result.get('load_15min', 0):.2f}",
            'CPU温度(°C)': f"{result.get('cpu_temperature', 0):.1f}",
            '进程数': result.get('process_count', 0),
            '系统线程数': result.get('system_thread_count', 0),  # 修复：重命名为系统线程数
            '上下文切换数': result.get('context_switches', 0),
            '内存平均值(%)': f"{result['memory_avg']:.2f}",
            '内存最大值(%)': f"{result['memory_max']:.2f}",
            '内存_P95(%)': f"{result['memory_p95']:.2f}",
            '内存_P90(%)': f"{result['memory_p90']:.2f}",
            '内存最小值(%)': f"{result['memory_min']:.2f}",
            '内存变化率(%)': f"{result['memory_change_rate']:.2f}",
            '内存采样点数': result['memory_sample_count'],
            '硬盘平均值(%)': f"{result['disk_avg']:.2f}",
            '硬盘最大值(%)': f"{result['disk_max']:.2f}",
            '硬盘_P95(%)': f"{result['disk_p95']:.2f}",
            '硬盘_P90(%)': f"{result['disk_p90']:.2f}",
            '硬盘最小值(%)': f"{result['disk_min']:.2f}",
            '硬盘变化率(%)': f"{result['disk_change_rate']:.2f}",
            '硬盘采样点数': result['disk_sample_count'],
            'JTL文件': result['jtl_file'],
            '报告目录': result['report_dir'],
            '测试时间': result['timestamp']
        }
        
        return field_mapping.get(field, '')
    
    def _print_summary_report(self, test_results):
        """打印总结报告"""
        print("\n" + "="*60)
        print(f"🎯 批量测试总结")
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

    def run_csv_sharding_batch_test(self, csv_dir, csv_pattern, thread_count=5000, loops=1):
        """
        自动循环20次，每次切换CSV文件，线程数5000，循环1次，自动调用JMeter注册。
        :param csv_dir: CSV文件目录
        :param csv_pattern: CSV文件通配符，如'new_devices_part_*.csv'
        :param thread_count: 每批线程数
        :param loops: 每批循环次数
        """
        print(f"\n🚀 启动分片批量注册测试，目录: {csv_dir}，模式: {csv_pattern}")
        csv_files = sorted(glob.glob(os.path.join(csv_dir, csv_pattern)))
        if not csv_files:
            print(f"❌ 未找到任何分片CSV文件: {csv_pattern}")
            return
        print(f"📂 共检测到{len(csv_files)}个分片CSV文件")
        all_results = []
        for idx, csv_file in enumerate(csv_files):
            print(f"\n{'='*20} 分片 {idx+1}/{len(csv_files)} {'='*20}")
            self.csv_file = csv_file  # 切换当前CSV
            # 修改JMX文件，线程数5000，循环1次，CSV路径为当前分片
            modified_jmx = self.modify_jmx_threads(thread_count, loops)
            test_name = f"shard_{idx+1:02d}_{thread_count}threads_{loops}loops"
            estimated_duration = max(60, thread_count * loops * 0.1)
            success, jtl_file, report_dir, duration = self.run_jmeter_test(modified_jmx, test_name, estimated_duration)
            if success:
                stats = self.analyze_jtl_file(jtl_file)
                cpu_stats = self.analyze_cpu_data()
                memory_stats = self.analyze_memory_data()
                disk_stats = self.analyze_disk_data()
                count_before = self.get_device_count_before()
                count_after = self.get_device_count_after()
                registered_count = count_after - count_before
                result = {
                    'test_name': test_name,
                    'thread_count': thread_count,
                    'loops': loops,
                    'csv_file': csv_file,
                    'actual_requests': stats.get('total_requests', 0),
                    'success_count': stats.get('success_count', 0),
                    'fail_count': stats.get('fail_count', 0),
                    'success_rate': stats.get('success_count', 0) / stats.get('total_requests', 1) * 100 if stats.get('total_requests', 0) > 0 else 0,
                    'avg_response_time': stats.get('avg_response_time', 0),
                    'min_response_time': stats.get('min_response_time', 0),
                    'max_response_time': stats.get('max_response_time', 0),
                    'duration': duration,
                    'registered_count': registered_count,
                    'jtl_file': jtl_file,
                    'report_dir': report_dir,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'cpu_max': cpu_stats.get('max_cpu', 0),
                    'cpu_min': cpu_stats.get('min_cpu', 0),
                    'cpu_avg': cpu_stats.get('avg_cpu', 0),
                    'cpu_p90': cpu_stats.get('p90_cpu', 0),
                    'cpu_p95': cpu_stats.get('p95_cpu', 0),
                    'cpu_change_rate': cpu_stats.get('cpu_change_rate', 0),
                    'cpu_sample_count': cpu_stats.get('sample_count', 0),
                    'memory_max': memory_stats.get('max_memory', 0),
                    'memory_min': memory_stats.get('min_memory', 0),
                    'memory_avg': memory_stats.get('avg_memory', 0),
                    'memory_p90': memory_stats.get('p90_memory', 0),
                    'memory_p95': memory_stats.get('p95_memory', 0),
                    'memory_change_rate': memory_stats.get('memory_change_rate', 0),
                    'memory_sample_count': memory_stats.get('sample_count', 0),
                    'disk_max': disk_stats.get('max_disk', 0),
                    'disk_min': disk_stats.get('min_disk', 0),
                    'disk_avg': disk_stats.get('avg_disk', 0),
                    'disk_p90': disk_stats.get('p90_disk', 0),
                    'disk_p95': disk_stats.get('p95_disk', 0),
                    'disk_change_rate': disk_stats.get('disk_change_rate', 0),
                    'disk_sample_count': disk_stats.get('sample_count', 0)
                }
                all_results.append(result)
                print(f"✅ 分片{idx+1}注册完成，注册数: {registered_count}")
            else:
                print(f"❌ 分片{idx+1}注册失败")
            if idx < len(csv_files) - 1:
                print("⏳ 等待10秒后继续下一分片...")
                time.sleep(10)
        # 汇总报告
        self.generate_summary_report(all_results, "sharding_register")
        print("\n🎉 分片批量注册全部完成！")

    def run_batch_login_test(self, loop_configs=None):
        """
        批量登录测试：固定线程数500，测试不同循环次数
        Args:
            loop_configs: 循环次数列表，默认[1, 2, 5, 10, 20]
        """
        if loop_configs is None:
            loop_configs = [1, 2, 5, 10, 20]
        
        print(f"\n🚀 开始批量登录测试")
        print(f"📊 固定线程数: {500}")
        print(f"🔄 循环次数配置: {loop_configs}")
        
        # 检查前置条件（登录测试跳过CSV文件检查）
        if not self.check_prerequisites():
            print("❌ 前置条件检查失败，退出测试")
            return []
        
        # 构建测试配置，强制使用500线程
        thread_configs = []
        for loops in loop_configs:
            thread_configs.append({
                'threads': 500,  # 固定线程数500
                'loops': loops
            })
        
        # 获取测试前设备数量
        count_before = self.get_device_count_before()
        print(f"📈 测试前设备总数: {count_before}")
        
        # 复用现有的批量测试方法，但传入固定线程数的配置
        test_results = self.run_batch_test(thread_configs, test_type="login", iteration_num=1)
        
        # 生成专门的登录测试报告
        self.generate_login_summary_report(test_results)
        
        return test_results
    
    def generate_login_summary_report(self, test_results):
        """生成专门的登录测试报告"""
        print("\n📋 生成登录测试专用报告...")
        
        # 定义字段重要级别排序（重要程度从高到低）
        field_priority = [
            # 核心测试信息
            '测试名称', '测试类型', '线程数', '循环次数', '预期请求数', '实际请求数',
            '成功数', '失败数', '成功率(%)', '错误率(%)',
            # 响应时间指标
            '平均响应时间(ms)', '最小响应时间(ms)', '最大响应时间(ms)', '响应时间标准差(ms)',
            # 执行时间
            '脚本执行时间(秒)', 'JTL执行时间(秒)', 'JTL开始时间', 'JTL结束时间',
            # 吞吐量指标
            '吞吐量(请求/秒)', '每秒接收KB数', '每秒发送KB数', '平均字节数',
            # 登录结果
            '注册前设备数', '注册后设备数', '实际注册数', '注册成功率(%)',
            # CPU监控（按重要程度排序）
            'CPU平均值(%)', 'CPU最大值(%)', 'CPU_P95(%)', 'CPU_P90(%)', 'CPU最小值(%)', 'CPU变化率(%)', 'CPU采样点数',
            'CPU核心数', '系统负载_1分钟', '系统负载_5分钟', '系统负载_15分钟', 'CPU温度(°C)', '进程数', '系统线程数', '上下文切换数',
            # 内存监控（按重要程度排序）
            '内存平均值(%)', '内存最大值(%)', '内存_P95(%)', '内存_P90(%)', '内存最小值(%)', '内存变化率(%)', '内存采样点数',
            # 硬盘监控（按重要程度排序）
            '硬盘平均值(%)', '硬盘最大值(%)', '硬盘_P95(%)', '硬盘_P90(%)', '硬盘最小值(%)', '硬盘变化率(%)', '硬盘采样点数',
            # 文件信息
            'JTL文件', '报告目录', '测试时间'
        ]
        
        # 生成横标题报告（标准CSV格式）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file_horizontal = os.path.join(self.results_dir, f"batch_login_test_summary_horizontal_{timestamp}.csv")
        
        with open(csv_file_horizontal, 'w', newline='', encoding='utf-8') as f:
            # 按重要级别排序字段
            ordered_fieldnames = [field for field in field_priority if field in self._get_all_fieldnames()]
            
            writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
            writer.writeheader()
            
            for result in test_results:
                row_data = self._prepare_report_row(result, ordered_fieldnames)
                writer.writerow(row_data)
        
        print(f"📊 横标题CSV报告已生成: {csv_file_horizontal}")
        
        # 生成列标题报告（转置格式）
        csv_file_vertical = os.path.join(self.results_dir, f"batch_login_test_summary_vertical_{timestamp}.csv")
        
        with open(csv_file_vertical, 'w', newline='', encoding='utf-8') as f:
            # 按重要级别排序字段
            ordered_fieldnames = [field for field in field_priority if field in self._get_all_fieldnames()]
            
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow(['指标名称'] + [result['test_name'] for result in test_results])
            
            # 按重要级别写入每行数据
            for field in ordered_fieldnames:
                row_data = [field]
                for result in test_results:
                    value = self._get_field_value(result, field)
                    row_data.append(value)
                writer.writerow(row_data)
        
        print(f"📊 列标题CSV报告已生成: {csv_file_vertical}")
        
        # 生成JSON报告
        json_file = os.path.join(self.results_dir, f"batch_login_test_summary_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📋 登录测试JSON报告已生成: {json_file}")
        
        # 打印登录测试专用总结
        print("\n" + "="*60)
        print(f"🎯 批量登录测试总结 (固定线程数500)")
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
        
        # 按循环次数分析
        print(f"\n📊 按循环次数分析:")
        for result in test_results:
            loops = result['loops']
            success_rate = result['success_rate']
            avg_response = result['avg_response_time']
            cpu_avg = result['cpu_avg']
            memory_avg = result['memory_avg']
            disk_avg = result['disk_avg']
            print(f"   {loops}循环: 成功率={success_rate:.1f}%, 响应时间={avg_response:.1f}ms, CPU={cpu_avg:.1f}%, 内存={memory_avg:.1f}%, 硬盘={disk_avg:.1f}%")
        
        print(f"\n📁 所有结果文件保存在: {self.results_dir}")
        print(f"📄 横标题报告: {csv_file_horizontal}")
        print(f"📄 列标题报告: {csv_file_vertical}")
        print(f"📄 JSON报告: {json_file}")

    def _ssh_exec(self, command):
        """执行SSH命令获取硬件信息"""
        try:
            if hasattr(self, 'cpu_monitor') and self.cpu_monitor:
                # 检查cpu_monitor是否有collector属性
                if hasattr(self.cpu_monitor, 'collector') and self.cpu_monitor.collector:
                    return self.cpu_monitor.collector._ssh_exec(command)
                # 如果没有collector属性，直接尝试执行
                elif hasattr(self.cpu_monitor, '_ssh_exec'):
                    return self.cpu_monitor._ssh_exec(command)
                else:
                    print(f"⚠️ cpu_monitor对象缺少SSH执行方法")
                    return "0"
            else:
                return "0"
        except Exception as e:
            print(f"⚠️  SSH命令执行失败: {e}")
            return "0"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='增强版JMETER批量注册脚本')
    parser.add_argument('--threads', nargs='+', type=int, default=[100, 500, 1000],
                       help='线程数列表，例如: 100 500 1000')
    parser.add_argument('--loops', nargs='+', type=int, default=[1],
                       help='循环次数列表，例如: 1 5 10')
    parser.add_argument('--single', action='store_true',
                       help='单次测试模式，只执行一个配置')
    parser.add_argument('--test-type', choices=['register', 'login'], default='register',
                       help='测试类型: register(批量注册) 或 login(批量登录)')
    parser.add_argument('--server-host', type=str, default='192.168.24.45',
                       help='服务器IP地址')
    parser.add_argument('--server-user', type=str, default='test',
                       help='服务器SSH用户名')
    parser.add_argument('--server-password', type=str, default='1',
                       help='服务器SSH密码')
    parser.add_argument('--filter-registered', action='store_true',
                       help='执行增量注册，自动过滤数据库中已存在的设备。')
    parser.add_argument('--iterations', type=int, default=1,
                       help='迭代执行次数，用于持续压力测试。每次迭代都会重新进行数据过滤。')
    parser.add_argument('--csv-dir', type=str, default='src/tools/jmeter/bin', help='分片CSV文件目录')
    parser.add_argument('--csv-pattern', type=str, default='new_devices_part_*.csv', help='分片CSV文件通配符')
    parser.add_argument('--sharding', action='store_true', help='启用分片批量注册模式')
    parser.add_argument('--login-test', action='store_true', help='启用批量登录测试模式（固定线程数500，测试不同循环次数）')
    parser.add_argument('--login-loops', nargs='+', type=int, default=[1, 2, 5, 10, 20],
                       help='登录测试的循环次数列表')
    parser.add_argument('--login-range', type=str, help='登录测试循环次数范围，格式：start-end，例如：1-100')
    parser.add_argument('--login-step', type=int, default=1, help='登录测试循环次数步长，默认1')
    
    args = parser.parse_args()
    
    # 构建测试配置
    if args.single:
        # 单次测试模式
        thread_configs = [
            {'threads': args.threads[0], 'loops': args.loops[0]}
        ]
    else:
        # 批量测试模式
        thread_configs = []
        for thread_count in args.threads:
            for loops in args.loops:
                thread_configs.append({
                    'threads': thread_count,
                    'loops': loops
                })
    
    print("增强版JMETER批量注册脚本")
    print("="*60)
    print(f"📋 测试类型: {args.test_type}")
    
    # 创建测试实例
    tester = EnhancedJMeterBatchRegister()
    
    # 更新服务器配置
    tester.server_config['host'] = args.server_host
    tester.server_config['username'] = args.server_user
    tester.server_config['password'] = args.server_password
    
    # 检查前置条件
    if args.login_test:
        # 登录测试模式跳过CSV文件检查
        if not tester.check_prerequisites():
            print("❌ 前置条件检查失败，退出测试")
            return
    else:
        # 其他模式需要检查所有前置条件
        if not tester.check_prerequisites():
            print("❌ 前置条件检查失败，退出测试")
            return
    
    try:
        if args.login_test:
            # 批量登录测试模式
            if args.login_range:
                # 解析范围参数
                try:
                    start, end = map(int, args.login_range.split('-'))
                    step = args.login_step
                    login_loops = list(range(start, end + 1, step))
                    print(f"📋 登录测试循环次数范围: {start}-{end}，步长: {step}")
                    print(f"📋 实际循环次数: {login_loops}")
                except ValueError:
                    print("❌ 循环次数范围格式错误，请使用 start-end 格式，例如：1-100")
                    return
            else:
                login_loops = args.login_loops
                print(f"📋 登录测试循环次数: {login_loops}")
            
            test_results = tester.run_batch_login_test(login_loops)
            print(f"\n✅ 批量登录测试完成，共执行 {len(test_results)} 个测试")
        elif args.sharding:
            # 分片批量注册模式
            print(f"📋 分片CSV目录: {args.csv_dir}")
            print(f"📋 分片CSV模式: {args.csv_pattern}")
            tester.run_csv_sharding_batch_test(args.csv_dir, args.csv_pattern)
        else:
            # 常规批量测试模式
            print(f"📋 测试配置数量: {len(thread_configs)}")
            for i, config in enumerate(thread_configs):
                print(f"   配置 {i+1}: {config['threads']}线程 × {config['loops']}循环")
            
            if args.filter_registered:
                print("🔍 启用增量注册模式，将自动过滤已注册设备")
                tester._prepare_fresh_csv()
            
            test_results = tester.run_batch_test(thread_configs, args.test_type, args.iterations)
            print(f"\n✅ 批量{args.test_type}测试完成，共执行 {len(test_results)} 个测试")
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
        tester.stop_cpu_monitoring()
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        tester.stop_cpu_monitoring()

if __name__ == '__main__':
    main() 