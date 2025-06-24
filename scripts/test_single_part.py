#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单分片测试脚本
测试单个分片的注册功能，验证脚本是否正常工作
"""

import os
import subprocess
import time
from datetime import datetime

def test_single_part():
    """测试单个分片"""
    print(f"🧪 开始单分片测试...")
    
    # 配置参数
    csv_file = "src/tools/jmeter/bin/device_parts/part_01_2000rows.csv"
    jmx_template = "src/tools/jmeter/api_cases/register_test.jmx"
    threads = 100  # 先用较小的线程数测试
    loops = 1
    
    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件不存在: {csv_file}")
        return False
    
    if not os.path.exists(jmx_template):
        print(f"❌ JMX模板文件不存在: {jmx_template}")
        return False
    
    print(f"✅ 文件检查通过")
    print(f"   CSV文件: {csv_file}")
    print(f"   JMX模板: {jmx_template}")
    print(f"   线程数: {threads}")
    print(f"   循环次数: {loops}")
    
    # 读取并更新JMX文件
    try:
        with open(jmx_template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新线程数
        content = content.replace(
            'stringProp name="ThreadGroup.num_threads">1<',
            f'stringProp name="ThreadGroup.num_threads">{threads}<'
        )
        
        # 更新循环次数
        content = content.replace(
            'stringProp name="ThreadGroup.loop_count">1<',
            f'stringProp name="ThreadGroup.loop_count">{loops}<'
        )
        
        # 更新CSV文件路径
        content = content.replace(
            'stringProp name="filename">devices.csv<',
            f'stringProp name="filename">{csv_file}<'
        )
        
        # 保存更新后的JMX文件
        updated_jmx = "src/tools/jmeter/api_cases/register_test_updated.jmx"
        with open(updated_jmx, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ JMX文件更新完成: {updated_jmx}")
        
    except Exception as e:
        print(f"❌ 更新JMX文件失败: {e}")
        return False
    
    # 创建结果目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = f"src/tools/jmeter/results/test_single_{timestamp}"
    os.makedirs(result_dir, exist_ok=True)
    
    # 构建JMeter命令
    jmeter_cmd = [
        "src\\tools\\jmeter\\bin\\jmeter.bat",
        "-n",  # 非GUI模式
        "-t", updated_jmx,  # 测试计划文件
        "-l", os.path.join(result_dir, "results.jtl"),  # 结果文件
        "-e",  # 生成HTML报告
        "-o", os.path.join(result_dir, "html_report")  # HTML报告目录
    ]
    
    print(f"🚀 开始执行JMeter测试...")
    print(f"   命令: {' '.join(jmeter_cmd)}")
    
    # 执行JMeter测试
    start_time = time.time()
    result = subprocess.run(jmeter_cmd, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    
    # 输出结果
    print(f"\n📊 测试结果:")
    print(f"   返回码: {result.returncode}")
    print(f"   耗时: {duration:.2f}秒")
    
    if result.returncode == 0:
        print(f"✅ 测试成功完成!")
        print(f"   结果文件: {result_dir}")
        print(f"   标准输出: {len(result.stdout)} 字符")
        if result.stderr:
            print(f"   错误输出: {len(result.stderr)} 字符")
        return True
    else:
        print(f"❌ 测试失败!")
        print(f"   错误信息: {result.stderr}")
        return False

if __name__ == "__main__":
    test_single_part() 