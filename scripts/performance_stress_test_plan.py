#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能压力测试计划脚本
- 基于10万CSV数据的科学测试方案
- 渐进式压力测试策略
- 重点关注CPU硬件影响
- 生成有价值的性能报告
"""
import os
import sys
import subprocess
import time
from datetime import datetime
import argparse

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

# 设置标准输出为UTF-8编码
if sys.stdout.encoding is None or sys.stdout.encoding.lower() != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

class PerformanceStressTestPlan:
    """性能压力测试计划管理器"""
    
    def __init__(self):
        """初始化测试计划"""
        self.test_phases = {
            'baseline': {
                'name': '基础性能测试',
                'description': '小规模测试，建立性能基线',
                'configs': [
                    {'threads': 10, 'loops': 1, 'expected_requests': 10},
                    {'threads': 20, 'loops': 1, 'expected_requests': 20},
                    {'threads': 50, 'loops': 1, 'expected_requests': 50},
                    {'threads': 100, 'loops': 1, 'expected_requests': 100}
                ],
                'cpu_threshold': 30,  # CPU使用率阈值
                'purpose': '建立性能基线，验证系统基本功能'
            },
            'medium_stress': {
                'name': '中等压力测试',
                'description': '中等规模测试，测试系统稳定性',
                'configs': [
                    {'threads': 200, 'loops': 1, 'expected_requests': 200},
                    {'threads': 500, 'loops': 1, 'expected_requests': 500},
                    {'threads': 1000, 'loops': 1, 'expected_requests': 1000}
                ],
                'cpu_threshold': 60,  # CPU使用率阈值
                'purpose': '测试系统在中等负载下的稳定性'
            },
            'high_stress': {
                'name': '高压力测试',
                'description': '大规模测试，测试系统极限',
                'configs': [
                    {'threads': 2000, 'loops': 1, 'expected_requests': 2000},
                    {'threads': 5000, 'loops': 1, 'expected_requests': 5000},
                    {'threads': 10000, 'loops': 1, 'expected_requests': 10000}
                ],
                'cpu_threshold': 80,  # CPU使用率阈值
                'purpose': '测试系统在高负载下的性能表现'
            },
            'extreme_stress': {
                'name': '极限压力测试',
                'description': '超大规模测试，测试系统崩溃点',
                'configs': [
                    {'threads': 20000, 'loops': 1, 'expected_requests': 20000},
                    {'threads': 50000, 'loops': 1, 'expected_requests': 50000}
                ],
                'cpu_threshold': 95,  # CPU使用率阈值
                'purpose': '测试系统极限承载能力'
            }
        }
        
        self.results_dir = os.path.join(project_root, "src", "tools", "jmeter", "results")
        
    def print_test_plan(self):
        """打印测试计划"""
        print("性能压力测试计划")
        print("="*80)
        print("测试数据: 10万CSV参数")
        print("测试目标: 批量注册性能 & CPU硬件影响分析")
        print("="*80)
        
        total_configs = 0
        total_requests = 0
        
        for phase_name, phase_info in self.test_phases.items():
            print(f"\n{phase_info['name']}")
            print(f"描述: {phase_info['description']}")
            print(f"目的: {phase_info['purpose']}")
            print(f"CPU阈值: {phase_info['cpu_threshold']}%")
            print("配置详情:")
            
            for i, config in enumerate(phase_info['configs'], 1):
                print(f"  {i}. {config['threads']}线程 x {config['loops']}循环 = {config['expected_requests']}请求")
                total_configs += 1
                total_requests += config['expected_requests']
        
        print(f"\n测试统计:")
        print(f"  总测试配置: {total_configs}个")
        print(f"  总预期请求: {total_requests:,}个")
        print(f"  测试阶段: {len(self.test_phases)}个")
        
        print(f"\n预估时间:")
        print(f"  基础测试: ~5分钟")
        print(f"  中等压力: ~10分钟") 
        print(f"  高压力: ~15分钟")
        print(f"  极限压力: ~20分钟")
        print(f"  总计: ~50分钟")
        
        print(f"\n结果文件:")
        print(f"  位置: {self.results_dir}")
        print(f"  格式: CSV + JSON + HTML报告")
        
    def run_phase_test(self, phase_name, test_type="register"):
        """运行单个阶段的测试"""
        phase_info = self.test_phases[phase_name]
        
        print(f"\n开始{phase_info['name']}")
        print("="*60)
        print(f"描述: {phase_info['description']}")
        print(f"目的: {phase_info['purpose']}")
        print(f"CPU阈值: {phase_info['cpu_threshold']}%")
        print("="*60)
        
        # 构建线程数列表
        thread_list = [config['threads'] for config in phase_info['configs']]
        
        # 执行测试
        cmd = [
            "python", "scripts\\jmeter_batch_register_enhanced.py",
            "--threads"
        ] + [str(t) for t in thread_list] + [
            "--loops", "1",
            "--test-type", test_type
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 执行测试
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root, encoding='utf-8')
            
            if result.returncode == 0:
                print(f"完成: {phase_info['name']}")
                return True
            else:
                print(f"失败: {phase_info['name']}")
                print(f"错误信息: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"执行{phase_info['name']}失败: {e}")
            return False
    
    def run_full_test(self, test_type="register", phases=None):
        """运行完整测试计划，将所有阶段合并到一次执行中，并生成单个报告。"""
        if phases is None:
            phases = list(self.test_phases.keys())

        print("开始完整性能压力测试 (合并执行)")
        print("="*80)
        print(f"测试类型: {test_type}")
        print(f"执行阶段: {', '.join(phases)}")
        print("="*80)

        all_threads = []
        for phase_name in phases:
            if phase_name in self.test_phases:
                print(f"整合阶段: {self.test_phases[phase_name]['name']}")
                phase_threads = [str(config['threads']) for config in self.test_phases[phase_name]['configs']]
                all_threads.extend(phase_threads)

        if not all_threads:
            print("没有找到任何测试配置，测试中止。")
            return False

        print(f"\n整合后的线程数配置: {' '.join(all_threads)}")
        print(f"总计 {len(all_threads)} 个测试配置。")

        cmd = [
            "python", "scripts\\jmeter_batch_register_enhanced.py",
            "--threads"
        ] + all_threads + [
            "--loops", "1",
            "--test-type", test_type
        ]

        print(f"\n执行合并测试命令: {' '.join(cmd)}")
        start_time = datetime.now()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root,
                encoding='utf-8'
            )
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "="*80)
            print("合并测试执行总结")
            print("="*80)
            print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"总耗时: {duration/60:.1f} 分钟")

            if result.returncode == 0:
                print("✅ 合并测试成功完成！")
                print(f"📄 详细报告已生成在: {self.results_dir}")
                print("\n--- 子脚本输出 ---")
                print(result.stdout)
                print("--- 子脚本输出结束 ---")
                return True
            else:
                print("❌ 合并测试失败。")
                print(f"错误信息:\n{result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 执行合并测试时发生异常: {e}")
            return False

    def generate_test_summary(self, results, start_time, end_time, duration):
        """生成测试总结"""
        print("\n" + "="*80)
        print("性能压力测试总结")
        print("="*80)
        
        print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration/60:.1f}分钟")
        
        print(f"\n阶段执行结果:")
        for phase_name, success in results.items():
            status = "成功" if success else "失败"
            print(f"  {self.test_phases[phase_name]['name']}: {status}")
        
        success_count = sum(results.values())
        total_count = len(results)
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        print(f"\n整体成功率: {success_rate:.1f}% ({success_count}/{total_count})")
        
        print(f"\n结果文件位置: {self.results_dir}")
        print("请查看生成的CSV和JSON报告进行详细分析")
        
        print(f"\n建议分析重点:")
        print("  1. 响应时间随并发增加的变化趋势")
        print("  2. CPU使用率与并发数的关系")
        print("  3. 系统性能拐点（响应时间急剧上升的点）")
        print("  4. 最大承载能力（成功率开始下降的点）")
        print("  5. CPU使用率与系统稳定性的关系")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='性能压力测试计划')
    parser.add_argument('--plan', action='store_true',
                       help='显示测试计划')
    parser.add_argument('--run', action='store_true',
                       help='执行完整测试')
    parser.add_argument('--phase', type=str, choices=['baseline', 'medium_stress', 'high_stress', 'extreme_stress'],
                       help='执行单个阶段测试')
    parser.add_argument('--test-type', choices=['register', 'login'], default='register',
                       help='测试类型')
    parser.add_argument('--phases', nargs='+', 
                       choices=['baseline', 'medium_stress', 'high_stress', 'extreme_stress'],
                       help='指定要执行的阶段')
    
    args = parser.parse_args()
    
    test_plan = PerformanceStressTestPlan()
    
    if args.plan:
        # 显示测试计划
        test_plan.print_test_plan()
        
    elif args.phase:
        # 执行单个阶段
        test_plan.run_phase_test(args.phase, args.test_type)
        
    elif args.run:
        # 执行完整测试
        test_plan.run_full_test(args.test_type, args.phases)
        
    else:
        # 默认显示测试计划
        test_plan.print_test_plan()
        print(f"\n使用说明:")
        print(f"  --plan: 显示测试计划")
        print(f"  --run: 执行完整测试")
        print(f"  --phase baseline: 执行基础测试")
        print(f"  --test-type login: 指定测试类型")

if __name__ == '__main__':
    main() 