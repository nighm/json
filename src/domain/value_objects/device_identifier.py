#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备标识符值对象 - 领域层
负责生成符合标准的设备序列号和MAC地址
遵循DDD原则，将业务规则放在领域层
"""

import random
import string
import hashlib
from datetime import datetime
from typing import Set, Optional, List
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class DeviceIdentifier:
    """设备标识符值对象 - 包含序列号和MAC地址"""
    serial_number: str
    mac_address: str
    created_at: datetime
    
    def __post_init__(self):
        """验证设备标识符格式"""
        if not self._is_valid_serial_number():
            raise ValueError(f"无效的序列号格式: {self.serial_number}")
        if not self._is_valid_mac_address():
            raise ValueError(f"无效的MAC地址格式: {self.mac_address}")
    
    def _is_valid_serial_number(self) -> bool:
        """验证序列号格式是否符合标准"""
        # 标准格式：品牌代码(4-6位) + 年份(4位) + 流水号(6位) + 校验位(1位)
        # 示例：HUAWEI2024000001A, HONOR2024000001A
        if len(self.serial_number) < 15 or len(self.serial_number) > 20:
            return False
        
        # 动态检查品牌代码长度（4-6位字母）
        brand_length = 0
        for i, char in enumerate(self.serial_number):
            if char.isalpha():
                brand_length += 1
            else:
                break
        
        if brand_length < 4 or brand_length > 6:
            return False
        
        # 检查品牌代码（前4-6位应该是字母）
        brand_part = self.serial_number[:brand_length]
        if not brand_part.isalpha():
            return False
        
        # 检查年份（4位数字）
        year_start = brand_length
        year_end = year_start + 4
        if year_end > len(self.serial_number):
            return False
        
        year_part = self.serial_number[year_start:year_end]
        if not year_part.isdigit():
            return False
        
        # 检查流水号（6位数字）
        serial_start = year_end
        serial_end = serial_start + 6
        if serial_end > len(self.serial_number):
            return False
        
        serial_part = self.serial_number[serial_start:serial_end]
        if not serial_part.isdigit():
            return False
        
        # 检查校验位（1位字母）
        checksum_start = serial_end
        if checksum_start >= len(self.serial_number):
            return False
        
        checksum_part = self.serial_number[checksum_start]
        if not checksum_part.isalpha():
            return False
        
        return True
    
    def _is_valid_mac_address(self) -> bool:
        """验证MAC地址格式是否符合标准"""
        # 标准格式：XX:XX:XX:XX:XX:XX
        if len(self.mac_address) != 17:  # 6组2位十六进制 + 5个冒号
            return False
        
        parts = self.mac_address.split(':')
        if len(parts) != 6:
            return False
        
        for part in parts:
            if len(part) != 2:
                return False
            try:
                int(part, 16)  # 验证是否为有效的十六进制
            except ValueError:
                return False
        
        return True
    
    def __str__(self) -> str:
        return f"SN:{self.serial_number}, MAC:{self.mac_address}"
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'serial_number': self.serial_number,
            'mac_address': self.mac_address,
            'created_at': self.created_at.isoformat()
        }

class DeviceIdentifierGenerator:
    """设备标识符生成器 - 领域层"""
    
    def __init__(self):
        self.used_sns: Set[str] = set()
        self.used_macs: Set[str] = set()
        self._load_existing_identifiers()
        
        # 只保留4-6位品牌代码
        self.brand_codes = [
            code for code in [
                "HUAWEI", "XIAOMI", "OPPO", "VIVO", "HONOR", "REALME",
                "APPLE", "IQOO", "NOKIA", "ASUS", "DELL", "ACER", "MSI", "RAZER"
            ] if 4 <= len(code) <= 6
        ]
    
    def _load_existing_identifiers(self):
        """加载已存在的标识符"""
        try:
            used_devices_file = Path("data/used_devices.json")
            if used_devices_file.exists():
                with open(used_devices_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.used_sns.update(data.get("used_devices", {}).get("deviceSerialNumber", []))
                self.used_macs.update(data.get("used_devices", {}).get("mac", []))
                
                print(f"✅ 已加载 {len(self.used_sns)} 个SN和 {len(self.used_macs)} 个MAC地址")
        except Exception as e:
            print(f"⚠️ 加载已存在标识符失败: {e}")
    
    def generate_unique_identifier(self) -> DeviceIdentifier:
        """生成唯一的设备标识符"""
        serial_number = self._generate_serial_number()
        mac_address = self._generate_mac_address()
        
        return DeviceIdentifier(
            serial_number=serial_number,
            mac_address=mac_address,
            created_at=datetime.now()
        )
    
    def generate_batch(self, count: int) -> List[DeviceIdentifier]:
        """批量生成设备标识符"""
        devices = []
        for i in range(count):
            try:
                device = self.generate_unique_identifier()
                devices.append(device)
            except Exception as e:
                print(f"生成第{i+1}个设备标识符失败: {e}")
                break
        return devices
    
    def _generate_serial_number(self) -> str:
        """生成唯一的设备序列号，严格符合标准格式"""
        max_attempts = 1000
        for _ in range(max_attempts):
            # 随机选择品牌代码
            brand = random.choice(self.brand_codes)
            # 生成年份（当前年份到未来10年）
            current_year = datetime.now().year
            year = random.randint(current_year, current_year + 10)
            # 生成6位随机流水号，前导0补齐
            serial = f"{random.randint(0, 999999):06d}"
            # 生成基础序列号
            base_sn = f"{brand}{year}{serial}"
            # 计算校验位
            checksum = self._calculate_checksum(base_sn)
            # 完整序列号
            sn = f"{base_sn}{checksum}"
            # 严格长度校验
            if len(sn) == len(brand) + 4 + 6 + 1 and sn not in self.used_sns:
                self.used_sns.add(sn)
                return sn
        raise RuntimeError("无法生成唯一的序列号，请检查容量限制")
    
    def _generate_mac_address(self) -> str:
        """生成唯一的MAC地址"""
        max_attempts = 1000
        
        for _ in range(max_attempts):
            # 生成随机MAC地址
            mac_parts = []
            for i in range(6):
                # 生成2位十六进制数
                hex_value = f"{random.randint(0, 255):02X}"
                mac_parts.append(hex_value)
            
            mac = ":".join(mac_parts)
            
            if mac not in self.used_macs:
                self.used_macs.add(mac)
                return mac
        
        raise RuntimeError("无法生成唯一的MAC地址，请检查容量限制")
    
    def _calculate_checksum(self, base_sn: str) -> str:
        """计算序列号校验位"""
        # 使用MD5哈希计算校验位，确保返回字母
        hash_value = hashlib.md5(base_sn.encode()).hexdigest()
        # 取第一个字符，如果是数字则转换为字母
        first_char = hash_value[0]
        if first_char.isdigit():
            # 将数字转换为对应的字母 (0->A, 1->B, ..., 9->J)
            return chr(ord('A') + int(first_char))
        else:
            return first_char.upper()
    
    def is_valid_serial_number(self, serial_number: str) -> bool:
        """验证序列号格式"""
        try:
            # 创建临时对象进行验证
            temp_device = DeviceIdentifier(
                serial_number=serial_number,
                mac_address="00:00:00:00:00:00",  # 临时MAC地址
                created_at=datetime.now()
            )
            return True
        except ValueError:
            return False
    
    def is_valid_mac_address(self, mac_address: str) -> bool:
        """验证MAC地址格式"""
        try:
            # 创建临时对象进行验证
            temp_device = DeviceIdentifier(
                serial_number="HUAWEI2024000001A",  # 临时序列号
                mac_address=mac_address,
                created_at=datetime.now()
            )
            return True
        except ValueError:
            return False
    
    def save_used_identifiers(self):
        """保存已使用的标识符到文件"""
        try:
            used_devices_file = Path("data/used_devices.json")
            used_devices_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "used_devices": {
                    "deviceSerialNumber": list(self.used_sns),
                    "mac": list(self.used_macs),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(used_devices_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已保存 {len(self.used_sns)} 个SN和 {len(self.used_macs)} 个MAC地址")
        except Exception as e:
            print(f"❌ 保存标识符失败: {e}")
    
    def get_statistics(self) -> dict:
        """获取生成统计信息"""
        return {
            "used_deviceSerialNumber": len(self.used_sns),
            "used_mac": len(self.used_macs),
            "brand_codes_available": len(self.brand_codes),
            "last_updated": datetime.now().isoformat()
        }

# 使用示例
if __name__ == '__main__':
    print("=== 设备标识符生成器演示 ===")
    
    # 创建生成器
    generator = DeviceIdentifierGenerator()
    
    # 生成单个标识符
    print("\n1. 生成单个标识符:")
    device = generator.generate_unique_identifier()
    print(f"设备标识符: {device}")
    
    # 批量生成
    print("\n2. 批量生成标识符:")
    devices = generator.generate_batch(3)
    for i, device in enumerate(devices, 1):
        print(f"设备{i}: {device}")
    
    # 保存
    generator.save_used_identifiers()
    
    # 获取统计信息
    statistics = generator.get_statistics()
    print("\n3. 生成统计信息:")
    for key, value in statistics.items():
        print(f"{key}: {value}")
    
    print("\n=== 演示完成 ===") 