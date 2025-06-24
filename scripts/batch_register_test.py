#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分片注册测试脚本
支持批量分片注册测试，每次使用不同的分片文件，避免重复注册
"""

import os
import glob
import subprocess
import time
import json
from datetime import datetime

class BatchRegisterTest:
    def __init__(self):
        self.parts_dir = "src/tools/jmeter/bin/device_parts"
        self.jmx_template = "src/tools/jmeter/api_cases/register_test.jmx"
        self.results_dir = "src/tools/jmeter/results"
        self.threads = 200  # 进一步降低线程数确保注册成功
        self.loops = 1  # 每个分片循环1次
        self.max_parts = 5  # 限制测试分片数量，先测试前5个分片
        
    def get_part_files(self):
        """获取所有分片文件"""
        part_files = glob.glob(os.path.join(self.parts_dir, "part_*.csv"))
        part_files.sort()
        # 限制分片数量
        return part_files[:self.max_parts]
    
    def update_jmx_config(self, csv_file, part_number):
        """更新JMX文件配置"""
        try:
            # 读取JMX文件
            with open(self.jmx_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新线程数
            content = content.replace(
                'stringProp name="ThreadGroup.num_threads">1<',
                f'stringProp name="ThreadGroup.num_threads">{self.threads}<'
            )
            
            # 更新循环次数
            content = content.replace(
                'stringProp name="ThreadGroup.loop_count">1<',
                f'stringProp name="ThreadGroup.loop_count">{self.loops}<'
            )
            
            # 更新CSV文件路径
            content = content.replace(
                'stringProp name="filename">devices.csv<',
                f'stringProp name="filename">{csv_file}<'
            )
            
            # 保存更新后的JMX文件
            updated_jmx = f"src/tools/jmeter/api_cases/register_part_{part_number:02d}.jmx"
            with open(updated_jmx, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return updated_jmx
            
        except Exception as e:
            print(f"❌ 更新JMX配置失败: {e}")
            return None
    
    def run_jmeter_test(self, jmx_file, part_number):
        """运行JMeter测试"""
        try:
            # 创建结果目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_dir = os.path.join(self.results_dir, f"part_{part_number:02d}_{timestamp}")
            os.makedirs(result_dir, exist_ok=True)
            
            # 构建JMeter命令
            jmeter_cmd = [
                "src\\tools\\jmeter\\bin\\jmeter.bat",
                "-n",  # 非GUI模式
                "-t", jmx_file,  # 测试计划文件
                "-l", os.path.join(result_dir, "results.jtl"),  # 结果文件
                "-e",  # 生成HTML报告
                "-o", os.path.join(result_dir, "html_report")  # HTML报告目录
            ]
            
            print(f"🚀 开始执行分片 {part_number:02d} 注册测试...")
            print(f"   JMX文件: {jmx_file}")
            print(f"   线程数: {self.threads}")
            print(f"   循环次数: {self.loops}")
            print(f"   结果目录: {result_dir}")
            
            # 执行JMeter测试
            start_time = time.time()
            result = subprocess.run(jmeter_cmd, capture_output=True, text=True)
            end_time = time.time()
            
            duration = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ 分片 {part_number:02d} 测试完成，耗时: {duration:.2f}秒")
                return True, result_dir
            else:
                print(f"❌ 分片 {part_number:02d} 测试失败")
                print(f"   错误信息: {result.stderr}")
                return False, None
                
        except Exception as e:
            print(f"❌ 执行JMeter测试失败: {e}")
            return False, None
    
    def run_batch_test(self):
        """执行批量分片测试"""
        print(f"🔧 开始批量分片注册测试...")
        print(f"   分片目录: {self.parts_dir}")
        print(f"   线程数: {self.threads}")
        print(f"   循环次数: {self.loops}")
        
        # 获取所有分片文件
        part_files = self.get_part_files()
        if not part_files:
            print(f"❌ 未找到分片文件")
            return False
        
        print(f"   找到 {len(part_files)} 个分片文件")
        
        # 执行每个分片的测试
        success_count = 0
        total_count = len(part_files)
        
        for i, csv_file in enumerate(part_files, 1):
            part_number = i
            
            print(f"\n{'='*60}")
            print(f"📦 处理分片 {part_number:02d}/{total_count}")
            print(f"   CSV文件: {os.path.basename(csv_file)}")
            
            # 更新JMX配置
            jmx_file = self.update_jmx_config(csv_file, part_number)
            if not jmx_file:
                continue
            
            # 运行测试
            success, result_dir = self.run_jmeter_test(jmx_file, part_number)
            
            if success:
                success_count += 1
                print(f"✅ 分片 {part_number:02d} 测试成功")
            else:
                print(f"❌ 分片 {part_number:02d} 测试失败")
            
            # 清理临时JMX文件
            try:
                os.remove(jmx_file)
            except:
                pass
            
            # 等待一段时间再执行下一个分片
            if i < total_count:
                print(f"⏳ 等待5秒后执行下一个分片...")
                time.sleep(5)
        
        # 输出最终结果
        print(f"\n{'='*60}")
        print(f"🎉 批量分片注册测试完成!")
        print(f"   总分片数: {total_count}")
        print(f"   成功数: {success_count}")
        print(f"   失败数: {total_count - success_count}")
        print(f"   成功率: {success_count/total_count*100:.1f}%")
        
        return success_count == total_count

def main():
    """主函数"""
    tester = BatchRegisterTest()
    success = tester.run_batch_test()
    
    if success:
        print(f"\n✅ 所有分片测试都成功完成!")
    else:
        print(f"\n❌ 部分分片测试失败，请检查日志")

if __name__ == "__main__":
    main() 