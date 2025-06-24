#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter执行器基础设施
- 执行JMeter测试命令
- 处理测试结果输出
"""
import os
import subprocess
import csv
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config.config_manager import config_manager
from src.domain.entities.test_result import TestResult

class JMeterExecutor:
    """JMeter测试执行器"""
    
    def __init__(self, jmeter_bin_path: str):
        """
        初始化JMeter执行器
        
        Args:
            jmeter_bin_path: JMeter可执行文件路径
        """
        self.jmeter_bin_path = jmeter_bin_path
        
    def execute_test(self, 
                    jmx_path: str, 
                    iterations: int,
                    output_dir: str,
                    test_name: str,
                    thread_count: int) -> TestResult:
        """
        执行JMeter测试
        
        Args:
            jmx_path: JMX文件路径
            iterations: 测试迭代次数
            output_dir: 输出目录
            test_name: 测试名称
            thread_count: 线程数
            
        Returns:
            TestResult: 测试结果
        """
        # 生成当前时间戳字符串
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 结果目录命名包含测试名称、线程数、循环次数和时间戳，便于区分不同批次
        result_dir = Path(output_dir) / f"{test_name}_{thread_count}_{iterations}_{timestamp}"
        result_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置输出文件路径
        jtl_path = result_dir / "result.jtl"
        report_path = result_dir / "report"
        
        # === 强制使用register_test.jmx文件 ===
        # 无论传入什么JMX路径，都强制使用原始的register_test.jmx
        original_jmx_path = "src/tools/jmeter/api_cases/register_test.jmx"
        print(f"🎯 [强制使用] JMeter将执行原始JMX文件: {original_jmx_path}")
        
        # 构建JMeter命令
        cmd = [
            self.jmeter_bin_path,
            "-n",  # 非GUI模式
            "-t", original_jmx_path,  # 使用原始JMX文件
            "-l", str(jtl_path),
            "-e",  # 生成HTML报告
            "-o", str(report_path),
            "-Jthread_count", str(thread_count),
            "-Jiterations", str(iterations),
            "-Jdevice_csv_file=data/generated_devices/devices.csv"
        ]
        
        # === 添加调试输出：打印JMeter实际读取的JMX文件内容 ===
        print(f"\n🔍 [JMeter调试] 即将执行的JMX文件内容:")
        print("=" * 100)
        try:
            with open(original_jmx_path, 'r', encoding='utf-8') as f:
                jmx_content = f.read()
                print(f"📄 JMX文件路径: {original_jmx_path}")
                print(f"📊 JMX文件大小: {len(jmx_content)} 字符")
                print("-" * 100)
                print("📋 JMX文件完整内容:")
                print(jmx_content)
                print("-" * 100)
        except Exception as e:
            print(f"❌ 读取JMX文件失败: {e}")
        print("=" * 100)
        
        start_time = datetime.now()
        print(f"[DEBUG] 执行JMeter命令: {' '.join(cmd)}")
        try:
            # 执行JMeter命令
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[DEBUG] JMeter执行成功，返回码: {process.returncode}")
            print(f"[DEBUG] JMeter输出: {process.stdout}")
            success = True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] JMeter执行失败: {e}")
            print(f"[ERROR] JMeter返回码: {e.returncode}")
            print(f"[ERROR] JMeter错误输出: {e.stderr}")
            print(f"[ERROR] JMeter标准输出: {e.stdout}")
            success = False
        end_time = datetime.now()
        
        # 检查JTL文件是否存在
        if jtl_path.exists():
            print(f"[DEBUG] JTL文件已生成: {jtl_path}")
        else:
            print(f"[ERROR] JTL文件未生成: {jtl_path}")
            print(f"[DEBUG] 结果目录内容: {list(result_dir.iterdir()) if result_dir.exists() else '目录不存在'}")
        
        # === 新增：解析JTL文件，统计性能指标 ===
        total_requests = 0
        success_count = 0
        fail_count = 0
        resp_times = []
        min_resp_time = max_resp_time = avg_resp_time = tp90_resp_time = tp99_resp_time = 0.0
        if jtl_path.exists():
            with open(jtl_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_requests += 1
                    if row.get('success', 'true').lower() == 'true':
                        success_count += 1
                    else:
                        fail_count += 1
                    try:
                        resp_times.append(float(row.get('elapsed', 0)))
                    except Exception:
                        pass
            if resp_times:
                min_resp_time = float(np.min(resp_times))
                max_resp_time = float(np.max(resp_times))
                avg_resp_time = float(np.mean(resp_times))
                tp90_resp_time = float(np.percentile(resp_times, 90))
                tp99_resp_time = float(np.percentile(resp_times, 99))
        # 成功率
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0.0
        # === 构造完整TestResult ===
        return TestResult(
            test_name=test_name,
            thread_count=thread_count,
            iterations=iterations,
            total_requests=total_requests,
            success_count=success_count,
            fail_count=fail_count,
            success_rate=success_rate,
            min_resp_time=min_resp_time,
            max_resp_time=max_resp_time,
            avg_resp_time=avg_resp_time,
            tp90_resp_time=tp90_resp_time,
            tp99_resp_time=tp99_resp_time,
            start_time=start_time,
            end_time=end_time,
            duration=(end_time - start_time).total_seconds(),
            report_path=str(report_path),
            success=success,
            server_cpu='-'
        )
    
    def get_report_path(self, result_file: str) -> str:
        """
        获取测试报告路径
        
        Args:
            result_file: 结果文件路径
            
        Returns:
            str: 测试报告路径
        """
        return f'report_{os.path.basename(result_file).replace(".jtl", "")}' 
