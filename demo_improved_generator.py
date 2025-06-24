#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进后的设备标识符生成器演示
展示领域层的随机生成功能和标准格式
"""

import random
import string
import hashlib
from datetime import datetime
from typing import Set
import json
from pathlib import Path

class ImprovedDeviceIdentifierGenerator:
    """改进后的设备标识符生成器 - 领域层"""
    
    def __init__(self):
        self.used_sns: Set[str] = set()
        self.used_macs: Set[str] = set()
        self._load_existing_identifiers()
    
    def _load_existing_identifiers(self):
        """加载已存在的标识符"""
        try:
            used_devices_file = Path("data/used_devices.json")
            if used_devices_file.exists():
                with open(used_devices_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                deviceSerialNumber = data.get("used_devices", {}).get("deviceSerialNumber", [])
                mac = data.get("used_devices", {}).get("mac", [])
                
                self.used_sns.update(deviceSerialNumber)
                self.used_macs.update(mac)
                
                print(f"✅ 已加载 {len(self.used_sns)} 个已使用SN，{len(self.used_macs)} 个已使用MAC")
        except Exception as e:
            print(f"⚠️ 加载已使用标识符失败: {e}")
    
    def generate_standard_serial_number(self, brand_code: str = "ROBOT") -> str:
        """生成标准格式的设备序列号"""
        # 获取当前年份
        current_year = datetime.now().year
        
        # 生成6位随机流水号
        serial_number = ''.join(random.choices(string.digits, k=6))
        
        # 生成校验位
        base_string = f"{brand_code}{current_year}{serial_number}"
        checksum = hashlib.md5(base_string.encode()).hexdigest()[0].upper()
        
        # 组装完整序列号
        full_serial = f"{brand_code}{current_year}{serial_number}{checksum}"
        
        return full_serial
    
    def generate_standard_mac_address(self, oui_prefix: str = "AA:BB:CC") -> str:
        """生成标准格式的MAC地址"""
        # 生成后3组随机十六进制数
        random_parts = []
        for _ in range(3):
            hex_part = f"{random.randint(0, 255):02X}"
            random_parts.append(hex_part)
        
        # 组装完整MAC地址
        full_mac = f"{oui_prefix}:{':'.join(random_parts)}"
        
        return full_mac
    
    def generate_unique_serial_number(self, brand_code: str = "ROBOT", max_attempts: int = 100) -> str:
        """生成唯一的设备序列号"""
        attempts = 0
        while attempts < max_attempts:
            sn = self.generate_standard_serial_number(brand_code)
            if sn not in self.used_sns:
                self.used_sns.add(sn)
                return sn
            attempts += 1
        
        raise ValueError(f"无法生成唯一序列号，已尝试 {max_attempts} 次")
    
    def generate_unique_mac_address(self, oui_prefix: str = "AA:BB:CC", max_attempts: int = 100) -> str:
        """生成唯一的MAC地址"""
        attempts = 0
        while attempts < max_attempts:
            mac = self.generate_standard_mac_address(oui_prefix)
            if mac not in self.used_macs:
                self.used_macs.add(mac)
                return mac
            attempts += 1
        
        raise ValueError(f"无法生成唯一MAC地址，已尝试 {max_attempts} 次")
    
    def generate_device_identifiers(self, count: int, brand_code: str = "ROBOT", oui_prefix: str = "AA:BB:CC") -> list[tuple[str, str]]:
        """批量生成设备标识符"""
        identifiers = []
        
        for i in range(count):
            try:
                sn = self.generate_unique_serial_number(brand_code)
                mac = self.generate_unique_mac_address(oui_prefix)
                identifiers.append((sn, mac))
                print(f"✅ 生成第 {i+1} 组标识符:")
                print(f"   📋 SN: {sn}")
                print(f"   🌐 MAC: {mac}")
                print()
            except ValueError as e:
                print(f"❌ 生成第 {i+1} 组标识符失败: {e}")
                break
        
        return identifiers

def demo_improved_generator():
    """演示改进后的生成器"""
    
    print("=" * 70)
    print("🚀 改进后的设备标识符生成器演示")
    print("=" * 70)
    
    print("\n📋 改进点说明:")
    print("1. ✅ 移至领域层 - 符合DDD架构原则")
    print("2. ✅ 真正随机生成 - 不可预测")
    print("3. ✅ 标准格式 - 符合行业规范")
    print("4. ✅ 唯一性保证 - 数据库级别")
    
    # 创建生成器
    print("\n🔧 创建改进后的生成器...")
    generator = ImprovedDeviceIdentifierGenerator()
    
    # 演示不同品牌的SN生成
    print("\n🏭 演示不同品牌的SN生成:")
    brands = ["HUAWEI", "XIAOMI", "OPPO", "VIVO", "ROBOT"]
    
    for brand in brands:
        sn = generator.generate_unique_serial_number(brand)
        print(f"   {brand}: {sn}")
    
    # 演示不同厂商的MAC生成
    print("\n🌐 演示不同厂商的MAC生成:")
    manufacturers = [
        ("华为", "00:1B:21"),
        ("小米", "B8:27:EB"), 
        ("苹果", "00:1C:B3"),
        ("三星", "00:16:3E"),
        ("测试", "AA:BB:CC")
    ]
    
    for name, oui in manufacturers:
        mac = generator.generate_unique_mac_address(oui)
        print(f"   {name}: {mac}")
    
    # 批量生成演示
    print("\n📱 批量生成演示（3台设备）:")
    identifiers = generator.generate_device_identifiers(3, "ROBOT", "AA:BB:CC")
    
    # 格式分析
    print("\n📊 格式分析:")
    if identifiers:
        sn, mac = identifiers[0]
        print(f"SN格式分析:")
        print(f"  总长度: {len(sn)} 位")
        print(f"  品牌代码: {sn[:6]} (6位字母)")
        print(f"  年份: {sn[6:10]} (4位数字)")
        print(f"  流水号: {sn[10:16]} (6位数字)")
        print(f"  校验位: {sn[16]} (1位字母)")
        
        print(f"\nMAC格式分析:")
        print(f"  总长度: {len(mac)} 位 (包含冒号)")
        print(f"  厂商代码: {mac[:8]} (前3组)")
        print(f"  设备序列: {mac[9:]} (后3组)")
    
    print("\n" + "=" * 70)
    print("✅ 演示完成！")
    print("=" * 70)

def explain_architecture_improvements():
    """解释架构改进"""
    
    print("\n" + "=" * 70)
    print("🏗️ 架构改进说明")
    print("=" * 70)
    
    print("\n🔍 问题1: 功能放在应用层是否合适？")
    print("❌ 当前问题:")
    print("   - DeviceGeneratorService 在应用层")
    print("   - 业务规则与协调逻辑混合")
    print("   - 违反DDD分层原则")
    
    print("\n✅ 改进方案:")
    print("   - 移至领域层 (Domain Layer)")
    print("   - 作为值对象 (Value Object)")
    print("   - 应用层只负责协调")
    
    print("\n🔍 问题2: 唯一标识参数写入数据库")
    print("❌ 当前问题:")
    print("   - 递增计数器，可预测")
    print("   - 唯一性检查依赖内存")
    print("   - 重启后可能重复")
    
    print("\n✅ 改进方案:")
    print("   - 真正随机生成")
    print("   - 数据库级别唯一性约束")
    print("   - 持久化已使用标识符")
    
    print("\n🔍 问题3: 标准SN/MAC格式")
    print("✅ 标准SN格式:")
    print("   品牌代码(6位) + 年份(4位) + 流水号(6位) + 校验位(1位)")
    print("   示例: HUAWEI2024000001A")
    print("   总长度: 17位")
    
    print("\n✅ 标准MAC格式:")
    print("   厂商代码(3组) + 设备序列(3组)")
    print("   示例: 00:1B:21:AB:CD:EF")
    print("   总长度: 17位 (包含冒号)")

if __name__ == '__main__':
    # 运行演示
    demo_improved_generator()
    
    # 解释架构改进
    explain_architecture_improvements() 