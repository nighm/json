#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SN和MAC生成过程演示脚本
用通俗易懂的方式展示设备序列号和MAC地址的生成过程
"""

import sys
import os
# 添加项目根目录到系统路径
sys.path.append('.')

from src.application.services.device_generator_service import DeviceGeneratorService

def demo_sn_mac_generation():
    """演示SN和MAC的生成过程"""
    
    print("=" * 60)
    print("🔧 SN和MAC地址生成过程演示")
    print("=" * 60)
    
    # 第一步：创建设备生成器
    print("\n📦 第一步：创建设备生成器")
    generator = DeviceGeneratorService()
    print("✅ 设备生成器创建成功")
    
    # 第二步：演示单个SN生成
    print("\n🔢 第二步：演示SN（设备序列号）生成")
    print("SN格式：SN_REGISTER_ + 8位数字（如：SN_REGISTER_00000001）")
    print("-" * 40)
    
    for i in range(5):  # 生成5个SN
        sn = generator.generate_unique_sn()
        print(f"第{i+1}个SN：{sn}")
    
    # 第三步：演示单个MAC生成
    print("\n🌐 第三步：演示MAC地址生成")
    print("MAC格式：AA:BB:CC:XX:YY:ZZ（前3段固定，后3段变化）")
    print("-" * 40)
    
    for i in range(5):  # 生成5个MAC
        mac = generator.generate_unique_mac()
        print(f"第{i+1}个MAC：{mac}")
    
    # 第四步：演示批量设备生成
    print("\n📱 第四步：演示批量设备生成")
    print("生成3台设备的完整信息：")
    print("-" * 40)
    
    devices = generator.generate_devices(3)  # 生成3台设备
    
    for i, device in enumerate(devices, 1):
        print(f"\n设备 {i}:")
        print(f"  📋 设备序列号(SN): {device.device_serial_number}")
        print(f"  🌐 MAC地址: {device.mac}")
        print(f"  🏷️  设备名称: {device.device_name}")
        print(f"  📍 IP地址: {device.ip}")
        print(f"  🏭 品牌: {device.brand}")
        print(f"  📱 型号: {device.model}")
    
    # 第五步：显示统计信息
    print("\n📊 第五步：生成统计信息")
    print("-" * 40)
    
    stats = generator.get_unique_stats()
    print(f"已生成SN数量: {stats['used_sns_count']}")
    print(f"已生成MAC数量: {stats['used_macs_count']}")
    print(f"SN计数器: {stats['sn_counter']}")
    print(f"MAC计数器: {stats['mac_counter']}")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)

def explain_generation_logic():
    """详细解释生成逻辑"""
    
    print("\n" + "=" * 60)
    print("📚 生成逻辑详细解释")
    print("=" * 60)
    
    print("\n🔢 SN生成逻辑：")
    print("1. 使用计数器 sn_counter，从1开始递增")
    print("2. 格式：SN_REGISTER_ + 8位数字")
    print("3. 示例：")
    print("   - 第1次：sn_counter=1 → SN_REGISTER_00000001")
    print("   - 第2次：sn_counter=2 → SN_REGISTER_00000002")
    print("   - 第100次：sn_counter=100 → SN_REGISTER_00000100")
    
    print("\n🌐 MAC生成逻辑：")
    print("1. 使用计数器 mac_counter，从1开始递增")
    print("2. 格式：AA:BB:CC:XX:YY:ZZ")
    print("3. XX、YY、ZZ的计算：")
    print("   - XX = (mac_counter//256)%256")
    print("   - YY = mac_counter%256")
    print("   - ZZ = (mac_counter//65536)%256")
    print("4. 示例：")
    print("   - 第1次：mac_counter=1 → AA:BB:CC:00:01:00")
    print("   - 第2次：mac_counter=2 → AA:BB:CC:00:02:00")
    print("   - 第256次：mac_counter=256 → AA:BB:CC:01:00:00")
    
    print("\n🔄 唯一性保证：")
    print("1. 每次生成前检查是否已存在")
    print("2. 如果已存在，继续生成下一个")
    print("3. 如果不存在，标记为已使用并返回")
    print("4. 确保每个SN和MAC都是唯一的")

if __name__ == '__main__':
    # 运行演示
    demo_sn_mac_generation()
    
    # 详细解释
    explain_generation_logic() 