#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐步测试register功能，帮助定位问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_register_step_by_step():
    """逐步测试register功能"""
    try:
        print("=== 开始逐步测试register功能 ===")
        
        # 步骤1: 导入必要的模块
        print("步骤1: 导入必要的模块...")
        from src.application.services.device_data_manager import DeviceDataManager
        from src.application.services.device_generator_service import DeviceGeneratorService
        from src.domain.entities.test_config import TestConfig
        from src.infrastructure.jmeter.jmeter_executor import JMeterExecutor
        from src.infrastructure.report.report_generator import ReportGenerator
        from src.application.services.performance_test_service import PerformanceTestService
        from src.config.config_manager import config_manager
        print("   ✓ 所有模块导入成功")
        
        # 步骤2: 初始化设备数据管理器
        print("步骤2: 初始化设备数据管理器...")
        device_data_manager = DeviceDataManager()
        print("   ✓ 设备数据管理器初始化成功")
        
        # 步骤3: 测试设备生成
        print("步骤3: 测试设备生成...")
        thread_counts = [100, 500]
        loop_counts = [10, 100, 300]
        total_devices_needed = sum(thread_counts) * max(loop_counts)
        print(f"   需要设备数量: {total_devices_needed}")
        
        device_csv_file = device_data_manager.get_available_devices(total_devices_needed)
        print(f"   设备CSV文件: {device_csv_file}")
        print("   ✓ 设备生成成功")
        
        # 步骤4: 检查JMX文件
        print("步骤4: 检查JMX文件...")
        base_dir = 'src/tools/jmeter/api_cases'
        jmx_path = os.path.join(base_dir, "register_test.jmx")
        print(f"   JMX路径: {jmx_path}")
        print(f"   JMX文件存在: {os.path.exists(jmx_path)}")
        
        if not os.path.exists(jmx_path):
            print("   ❌ JMX文件不存在，这是问题所在！")
            return False
        
        print("   ✓ JMX文件检查通过")
        
        # 步骤5: 创建测试配置
        print("步骤5: 创建测试配置...")
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"src/tools/jmeter/results/{timestamp}"
        
        config = TestConfig(
            test_name="接口性能测试_register",
            iterations=loop_counts,
            jmx_path=jmx_path,
            jmeter_bin_path=config_manager.get_jmeter_config()['jmeter']['jmeter_bin'],
            output_dir=output_dir
        )
        print("   ✓ 测试配置创建成功")
        
        # 步骤6: 创建服务对象
        print("步骤6: 创建服务对象...")
        jmeter_executor = JMeterExecutor(config.jmeter_bin_path)
        report_generator = ReportGenerator(config.output_dir)
        service = PerformanceTestService(jmeter_executor, report_generator)
        print("   ✓ 服务对象创建成功")
        
        print("=== 所有步骤测试通过 ===")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_register_step_by_step()
    sys.exit(0 if success else 1) 