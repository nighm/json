#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMETER命令行与图形界面一致性验证脚本
- 对比相同配置下命令行和图形界面的测试结果
- 验证响应时间、成功率等关键指标的一致性
- 生成对比报告
"""
import os
import sys
import subprocess
import time
import json
import csv
import shutil
from datetime import datetime
from pathlib import Path
import argparse

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from src.application.services.device_query_service import DeviceQueryService

class JMeterConsistencyVerifier:
    """JMETER一致性验证器"""
    
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
        modified_jmx = os.path.join(self.results_dir, f"consistency_test_{thread_count}threads_{loops}loops.jmx")
        with open(modified_jmx, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📝 修改后的JMX文件已保存: {modified_jmx}")
        return modified_jmx
    
    def run_command_line_test(self, jmx_path, test_name):
        """运行命令行测试"""
        print(f"🚀 开始命令行测试: {test_name}")
        
        # 生成结果文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        jtl_file = os.path.join(self.results_dir, f"cli_{test_name}_{timestamp}.jtl")
        log_file = os.path.join(self.results_dir, f"cli_{test_name}_{timestamp}.log")
        
        # 构建JMETER命令
        cmd = [
            self.jmeter_bin,
            "-n",  # 非GUI模式
            "-t", jmx_path,  # 测试计划文件
            "-l", jtl_file,  # 结果文件
            "-j", log_file,  # 日志文件
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
                print(f"✅ 命令行测试完成: {test_name}")
                print(f"⏱️  执行时间: {duration:.2f}秒")
                return True, jtl_file, duration
            else:
                error_output = process.stderr.read()
                print(f"❌ 命令行测试失败: {test_name}")
                print(f"错误信息: {error_output}")
                return False, None, duration
                
        except Exception as e:
            print(f"❌ 执行命令行测试失败: {e}")
            return False, None, 0
    
    def run_gui_test(self, jmx_path, test_name):
        """运行图形界面测试（通过GUI模式）"""
        print(f"🖥️  开始图形界面测试: {test_name}")
        
        # 生成结果文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        jtl_file = os.path.join(self.results_dir, f"gui_{test_name}_{timestamp}.jtl")
        log_file = os.path.join(self.results_dir, f"gui_{test_name}_{timestamp}.log")
        
        # 构建JMETER GUI命令
        cmd = [
            self.jmeter_bin,
            "-t", jmx_path,  # 测试计划文件
            "-l", jtl_file,  # 结果文件
            "-j", log_file,  # 日志文件
        ]
        
        print(f"📋 执行GUI命令: {' '.join(cmd)}")
        print("⚠️  注意：GUI模式需要手动启动和停止测试")
        
        # 记录开始时间
        start_time = datetime.now()
        
        try:
            # 启动GUI模式
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=os.path.dirname(self.jmeter_bin)
            )
            
            print("🖥️  JMETER GUI已启动，请在GUI中手动启动测试...")
            print("⏳ 等待测试完成...")
            
            # 等待用户手动完成测试
            input("请按回车键确认测试已完成...")
            
            # 记录结束时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 检查结果文件是否存在
            if os.path.exists(jtl_file):
                print(f"✅ 图形界面测试完成: {test_name}")
                print(f"⏱️  执行时间: {duration:.2f}秒")
                return True, jtl_file, duration
            else:
                print(f"❌ 图形界面测试失败: 未找到结果文件")
                return False, None, duration
                
        except Exception as e:
            print(f"❌ 执行图形界面测试失败: {e}")
            return False, None, 0
    
    def analyze_jtl_file(self, jtl_file, test_type):
        """分析JTL文件，统计测试结果"""
        print(f"📊 分析{test_type}测试结果: {jtl_file}")
        
        if not os.path.exists(jtl_file):
            print(f"❌ JTL文件不存在: {jtl_file}")
            return {}
        
        stats = {
            'test_type': test_type,
            'total_requests': 0,
            'success_count': 0,
            'fail_count': 0,
            'avg_response_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0,
            'response_times': [],
            'throughput': 0,
            'error_rate': 0
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
            
            # 计算统计指标
            if stats['response_times']:
                stats['avg_response_time'] = sum(stats['response_times']) / len(stats['response_times'])
                stats['min_response_time'] = min(stats['response_times'])
                stats['max_response_time'] = max(stats['response_times'])
            
            # 计算成功率和错误率
            if stats['total_requests'] > 0:
                stats['success_rate'] = stats['success_count'] / stats['total_requests'] * 100
                stats['error_rate'] = stats['fail_count'] / stats['total_requests'] * 100
            
            print(f"📈 {test_type}测试统计:")
            print(f"   总请求数: {stats['total_requests']}")
            print(f"   成功数: {stats['success_count']}")
            print(f"   失败数: {stats['fail_count']}")
            print(f"   成功率: {stats.get('success_rate', 0):.2f}%")
            print(f"   平均响应时间: {stats['avg_response_time']:.2f}ms")
            print(f"   最小响应时间: {stats['min_response_time']:.2f}ms")
            print(f"   最大响应时间: {stats['max_response_time']:.2f}ms")
            
            return stats
            
        except Exception as e:
            print(f"❌ 分析JTL文件失败: {e}")
            return {}
    
    def compare_results(self, cli_stats, gui_stats):
        """对比命令行和图形界面的测试结果"""
        print("\n🔍 对比分析结果")
        print("="*60)
        
        comparison = {
            'metrics': {},
            'differences': {},
            'consistency_score': 0
        }
        
        # 对比关键指标
        metrics_to_compare = [
            'total_requests', 'success_count', 'fail_count', 
            'avg_response_time', 'min_response_time', 'max_response_time',
            'success_rate', 'error_rate'
        ]
        
        total_differences = 0
        total_metrics = len(metrics_to_compare)
        
        for metric in metrics_to_compare:
            cli_value = cli_stats.get(metric, 0)
            gui_value = gui_stats.get(metric, 0)
            
            comparison['metrics'][metric] = {
                'cli': cli_value,
                'gui': gui_value,
                'difference': abs(cli_value - gui_value),
                'percentage_diff': abs(cli_value - gui_value) / max(cli_value, 1) * 100
            }
            
            # 计算差异
            if metric in ['avg_response_time', 'min_response_time', 'max_response_time']:
                # 响应时间允许5%的差异
                threshold = 5.0
            else:
                # 其他指标允许1%的差异
                threshold = 1.0
            
            if comparison['metrics'][metric]['percentage_diff'] > threshold:
                total_differences += 1
                comparison['differences'][metric] = {
                    'cli_value': cli_value,
                    'gui_value': gui_value,
                    'difference': abs(cli_value - gui_value),
                    'percentage_diff': comparison['metrics'][metric]['percentage_diff']
                }
        
        # 计算一致性得分
        consistency_score = ((total_metrics - total_differences) / total_metrics) * 100
        comparison['consistency_score'] = consistency_score
        
        # 打印对比结果
        print(f"📊 一致性得分: {consistency_score:.2f}%")
        print(f"📈 差异指标数量: {total_differences}/{total_metrics}")
        
        if total_differences == 0:
            print("✅ 所有指标完全一致！")
        else:
            print("⚠️  发现差异指标:")
            for metric, diff_info in comparison['differences'].items():
                print(f"   {metric}: CLI={diff_info['cli_value']:.2f}, GUI={diff_info['gui_value']:.2f}, 差异={diff_info['percentage_diff']:.2f}%")
        
        return comparison
    
    def generate_comparison_report(self, cli_stats, gui_stats, comparison, test_config):
        """生成对比报告"""
        print("\n📋 生成对比报告...")
        
        # 生成CSV报告
        csv_file = os.path.join(self.results_dir, f"consistency_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                '测试指标', '命令行结果', '图形界面结果', '绝对差异', '百分比差异(%)', '是否一致'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for metric, comp_data in comparison['metrics'].items():
                is_consistent = metric not in comparison['differences']
                writer.writerow({
                    '测试指标': metric,
                    '命令行结果': f"{comp_data['cli']:.2f}",
                    '图形界面结果': f"{comp_data['gui']:.2f}",
                    '绝对差异': f"{comp_data['difference']:.2f}",
                    '百分比差异(%)': f"{comp_data['percentage_diff']:.2f}",
                    '是否一致': '是' if is_consistent else '否'
                })
            
            # 添加总结行
            writer.writerow({
                '测试指标': '一致性得分',
                '命令行结果': '',
                '图形界面结果': '',
                '绝对差异': '',
                '百分比差异(%)': f"{comparison['consistency_score']:.2f}%",
                '是否一致': '通过' if comparison['consistency_score'] >= 95 else '需要关注'
            })
        
        print(f"📊 对比报告已生成: {csv_file}")
        
        # 生成JSON报告
        json_file = os.path.join(self.results_dir, f"consistency_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        report_data = {
            'test_config': test_config,
            'cli_stats': cli_stats,
            'gui_stats': gui_stats,
            'comparison': comparison,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📋 JSON报告已生成: {json_file}")
        
        return csv_file, json_file
    
    def run_consistency_test(self, thread_count, loops=1):
        """运行一致性测试"""
        print(f"🎯 开始一致性验证测试")
        print("="*60)
        print(f"🧵 线程数: {thread_count}")
        print(f"🔄 循环次数: {loops}")
        print("="*60)
        
        # 修改JMX文件
        modified_jmx = self.modify_jmx_threads(thread_count, loops)
        test_name = f"{thread_count}threads_{loops}loops"
        
        # 运行命令行测试
        cli_success, cli_jtl, cli_duration = self.run_command_line_test(modified_jmx, test_name)
        
        if not cli_success:
            print("❌ 命令行测试失败，无法进行对比")
            return False
        
        # 分析命令行结果
        cli_stats = self.analyze_jtl_file(cli_jtl, "命令行")
        
        print(f"\n⏳ 等待5秒后开始图形界面测试...")
        time.sleep(5)
        
        # 运行图形界面测试
        gui_success, gui_jtl, gui_duration = self.run_gui_test(modified_jmx, test_name)
        
        if not gui_success:
            print("❌ 图形界面测试失败，无法进行对比")
            return False
        
        # 分析图形界面结果
        gui_stats = self.analyze_jtl_file(gui_jtl, "图形界面")
        
        # 对比结果
        comparison = self.compare_results(cli_stats, gui_stats)
        
        # 生成报告
        test_config = {
            'thread_count': thread_count,
            'loops': loops,
            'cli_duration': cli_duration,
            'gui_duration': gui_duration
        }
        
        self.generate_comparison_report(cli_stats, gui_stats, comparison, test_config)
        
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='JMETER命令行与图形界面一致性验证脚本')
    parser.add_argument('--threads', type=int, default=10,
                       help='线程数，例如: 10')
    parser.add_argument('--loops', type=int, default=1,
                       help='循环次数，例如: 1')
    
    args = parser.parse_args()
    
    print("🎯 JMETER一致性验证脚本")
    print("="*60)
    print(f"📋 测试配置: {args.threads}线程 × {args.loops}循环")
    print("="*60)
    
    # 创建验证器并执行测试
    verifier = JMeterConsistencyVerifier()
    success = verifier.run_consistency_test(args.threads, args.loops)
    
    if success:
        print("\n🎉 一致性验证完成！")
    else:
        print("\n❌ 一致性验证失败！")

if __name__ == '__main__':
    main() 