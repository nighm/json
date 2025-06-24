#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMETER批量注册脚本
- 完全替代图形界面操作
- 支持不同线程数的批量注册
- 自动验证注册数量
- 生成综合报告
"""
import os
import sys
import subprocess
import time
import json
import csv
from datetime import datetime
from pathlib import Path
import argparse

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from src.application.services.device_query_service import DeviceQueryService

class JMeterBatchRegister:
    """JMETER批量注册管理器"""
    
    def __init__(self):
        """初始化配置"""
        self.jmeter_bin = os.path.join(project_root, "src", "tools", "jmeter", "bin", "jmeter.bat")
        self.jmx_file = os.path.join(project_root, "src", "tools", "jmeter", "bin", "register_test_python_format.jmx")
        self.csv_file = os.path.join(project_root, "src", "tools", "jmeter", "bin", "new_devices_100000.csv")
        self.results_dir = os.path.join(project_root, "src", "tools", "jmeter", "results")
        
        # 数据库配置
        self.db_config = {
            'host': '192.168.24.45',
            'port': 3307,
            'user': 'root',
            'password': 'At6mj*1ygb2',
            'database': 'yangguan'
        }
        
        # 确保结果目录存在
        os.makedirs(self.results_dir, exist_ok=True)
        
    def check_prerequisites(self):
        """检查前置条件"""
        print("🔍 检查前置条件...")
        
        # 检查JMETER可执行文件
        if not os.path.exists(self.jmeter_bin):
            raise FileNotFoundError(f"JMETER可执行文件不存在: {self.jmeter_bin}")
        
        # 检查JMX文件
        if not os.path.exists(self.jmx_file):
            raise FileNotFoundError(f"JMX文件不存在: {self.jmx_file}")
        
        # 检查CSV文件
        if not os.path.exists(self.csv_file):
            raise FileNotFoundError(f"CSV文件不存在: {self.csv_file}")
        
        print("✅ 前置条件检查通过")
        
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
        """修改JMX文件中的线程数和循环次数"""
        print(f"🔧 修改JMX配置: 线程数={thread_count}, 循环次数={loops}")
        
        # 读取JMX文件
        with open(self.jmx_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改线程数
        import re
        content = re.sub(
            r'<intProp name="ThreadGroup\.num_threads">\d+</intProp>',
            f'<intProp name="ThreadGroup.num_threads">{thread_count}</intProp>',
            content
        )
        
        # 修改循环次数
        content = re.sub(
            r'<stringProp name="LoopController\.loops">\d+</stringProp>',
            f'<stringProp name="LoopController.loops">{loops}</stringProp>',
            content
        )
        
        # 保存修改后的JMX文件
        modified_jmx = os.path.join(self.results_dir, f"register_test_{thread_count}threads_{loops}loops.jmx")
        with open(modified_jmx, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📝 修改后的JMX文件已保存: {modified_jmx}")
        return modified_jmx
    
    def run_jmeter_test(self, jmx_path, test_name):
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
        
        try:
            # 执行JMETER命令
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
                stats['min_response_time'] = min(stats['response_times'])
                stats['max_response_time'] = max(stats['response_times'])
            
            print(f"📈 测试统计:")
            print(f"   总请求数: {stats['total_requests']}")
            print(f"   成功数: {stats['success_count']}")
            print(f"   失败数: {stats['fail_count']}")
            print(f"   成功率: {stats['success_count']/stats['total_requests']*100:.2f}%" if stats['total_requests'] > 0 else "   成功率: 0%")
            print(f"   平均响应时间: {stats['avg_response_time']:.2f}ms")
            print(f"   最小响应时间: {stats['min_response_time']:.2f}ms")
            print(f"   最大响应时间: {stats['max_response_time']:.2f}ms")
            
            return stats
            
        except Exception as e:
            print(f"❌ 分析JTL文件失败: {e}")
            return {}
    
    def run_batch_test(self, thread_configs):
        """运行批量测试"""
        print("🎯 开始批量注册测试")
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
            
            # 修改JMX文件
            modified_jmx = self.modify_jmx_threads(thread_count, loops)
            
            # 运行测试
            test_name = f"register_{thread_count}threads_{loops}loops"
            success, jtl_file, report_dir, duration = self.run_jmeter_test(modified_jmx, test_name)
            
            if success:
                # 分析测试结果
                stats = self.analyze_jtl_file(jtl_file)
                
                # 获取注册后的设备数量
                count_after = self.get_device_count_after()
                registered_count = count_after - count_before
                
                # 记录测试结果
                result = {
                    'test_name': test_name,
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
                    'duration': duration,
                    'count_before': count_before,
                    'count_after': count_after,
                    'registered_count': registered_count,
                    'jtl_file': jtl_file,
                    'report_dir': report_dir,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                test_results.append(result)
                
                print(f"✅ 测试完成: {test_name}")
                print(f"📊 实际注册数量: {registered_count}")
                print(f"📈 注册成功率: {registered_count/(thread_count*loops)*100:.2f}%" if thread_count*loops > 0 else "📈 注册成功率: 0%")
                
                # 更新基准数量
                count_before = count_after
                
            else:
                print(f"❌ 测试失败: {test_name}")
            
            # 测试间隔
            if i < len(thread_configs) - 1:
                print(f"\n⏳ 等待30秒后继续下一个测试...")
                time.sleep(30)
        
        # 生成综合报告
        self.generate_summary_report(test_results)
        
        return test_results
    
    def generate_summary_report(self, test_results):
        """生成综合报告"""
        print("\n📋 生成综合报告...")
        
        # 生成CSV报告
        csv_file = os.path.join(self.results_dir, f"batch_register_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                '测试名称', '线程数', '循环次数', '预期请求数', '实际请求数',
                '成功数', '失败数', '成功率(%)', '平均响应时间(ms)',
                '最小响应时间(ms)', '最大响应时间(ms)', '执行时间(秒)',
                '注册前设备数', '注册后设备数', '实际注册数', '注册成功率(%)',
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
                    'JTL文件': result['jtl_file'],
                    '报告目录': result['report_dir'],
                    '测试时间': result['timestamp']
                })
        
        print(f"📊 CSV报告已生成: {csv_file}")
        
        # 生成JSON报告
        json_file = os.path.join(self.results_dir, f"batch_register_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📋 JSON报告已生成: {json_file}")
        
        # 打印总结
        print("\n" + "="*60)
        print("🎯 批量注册测试总结")
        print("="*60)
        
        total_expected = sum(r['expected_requests'] for r in test_results)
        total_actual = sum(r['actual_requests'] for r in test_results)
        total_success = sum(r['success_count'] for r in test_results)
        total_registered = sum(r['registered_count'] for r in test_results)
        
        print(f"📊 总预期请求数: {total_expected}")
        print(f"📊 总实际请求数: {total_actual}")
        print(f"📊 总成功请求数: {total_success}")
        print(f"📊 总注册设备数: {total_registered}")
        print(f"📈 整体成功率: {total_success/total_actual*100:.2f}%" if total_actual > 0 else "📈 整体成功率: 0%")
        print(f"📈 整体注册率: {total_registered/total_expected*100:.2f}%" if total_expected > 0 else "📈 整体注册率: 0%")
        
        print(f"\n📁 所有结果文件保存在: {self.results_dir}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='JMETER批量注册脚本')
    parser.add_argument('--threads', nargs='+', type=int, default=[100, 500, 1000],
                       help='线程数列表，例如: 100 500 1000')
    parser.add_argument('--loops', nargs='+', type=int, default=[1],
                       help='循环次数列表，例如: 1 5 10')
    parser.add_argument('--single', action='store_true',
                       help='单次测试模式，只执行一个配置')
    
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
    
    print("🎯 JMETER批量注册脚本")
    print("="*60)
    print(f"📋 测试配置数量: {len(thread_configs)}")
    for i, config in enumerate(thread_configs):
        print(f"   配置 {i+1}: {config['threads']}线程 × {config['loops']}循环")
    print("="*60)
    
    # 创建注册管理器并执行测试
    register_manager = JMeterBatchRegister()
    results = register_manager.run_batch_test(thread_configs)
    
    print("\n🎉 所有测试完成！")

if __name__ == '__main__':
    main() 