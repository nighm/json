import random
import string
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.domain.entities.device_info import DeviceInfo
from src.domain.value_objects.device_identifier import DeviceIdentifierGenerator
import json
from pathlib import Path

class DeviceGeneratorService:
    """
    设备信息生成器服务 - 应用层
    负责协调设备信息生成，使用领域层的标识符生成器
    遵循DDD架构原则，应用层只负责协调，具体生成逻辑在领域层
    """
    
    def __init__(self):
        # 使用领域层的设备标识符生成器
        self.identifier_generator = DeviceIdentifierGenerator()
        
        # Register接口专用设备模板
        self.device_templates = {
            'register': {
                'brand': 'robot',
                'model': 'robot',
                'processor': 'robot',
                'operating_system': 'robot',
                'hard_disk': 'robot',
                'memory': 'robot',
                'main_board': 'robot',
                'type': 'PC',
                'device_type': 'PC',  # params.deviceType
                'customer_code': '101',  # params.customerCode
                'protector_version': 'robot',  # params.protectorVersion
                'starter2_version': 'robot',  # params.starter2Version
                'remark': 'robot',  # params.remark
                'virtual_machine': False  # params.virtualMachine
            }
        }

    def generate_devices(self, count: int, template_name: str = 'register') -> List[DeviceInfo]:
        """
        批量生成设备信息 - 应用层协调方法
        使用领域层的标识符生成器确保唯一性和随机性
        """
        print(f"[DeviceGeneratorService] 开始生成 {count} 台设备...")
        
        # 1. 批量生成唯一标识符
        identifiers = self.identifier_generator.generate_batch(count)
        if not identifiers:
            print("[DeviceGeneratorService] 未能生成任何设备标识符，操作中止。")
            return []
            
        print(f"[DeviceGeneratorService] 成功生成 {len(identifiers)} 个唯一标识符。")
        
        devices = []
        template = self.device_templates[template_name]
        
        # 2. 组装设备信息
        for i, identifier in enumerate(identifiers):
            # 构造设备信息 - Register接口专用
            device = DeviceInfo(
                id=random.randint(1000000000000000000, 9999999999999999999),
                device_id="",  # 必须为空，Register接口要求
                device_serial_number=identifier.serial_number,  # 使用领域层生成的SN
                device_name="robot",  # 设置为robot，与register_param_tester.py保持一致
                ip="1.1.1.1",  # 固定值
                mac=identifier.mac_address,  # 使用领域层生成的MAC
                macs=identifier.mac_address,  # 同步唯一MAC
                outside_ip="",
                type=template['type'],
                model=template['model'],
                brand=template['brand'],
                supplier="",
                processor=template['processor'],
                operating_system=template['operating_system'],
                hard_disk=template['hard_disk'],
                memory=template['memory'],
                main_board=template['main_board'],
                resolution="",
                online="0",
                status="0",
                last_heartbeat_time="",
                last_login_time="",
                offline_time="",
                device_group_id=random.randint(1000000000000000000, 9999999999999999999),
                device_user_group_id=-1,
                user_id=-1,
                login_user_id=-1,
                login_status=0,
                image_id=-1,
                image_snapshot_id="",
                local_image_status="0",
                image_backup_time="",
                purchase_batch="",
                remark="",
                create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                create_by="system",
                update_time="",
                update_by="",
                del_flag="0"
            )
            
            # 添加Register接口专用字段
            device.device_type = template['device_type']
            device.customer_code = template['customer_code']
            device.protector_version = template['protector_version']
            device.starter2_version = template['starter2_version']
            device.remark = template['remark']
            device.virtual_machine = template['virtual_machine']
            
            devices.append(device)
            
            # 每生成100台设备显示进度
            if (i + 1) % 100 == 0:
                print(f"[DeviceGeneratorService] 已组装 {i + 1}/{len(identifiers)} 台设备")
        
        print(f"[DeviceGeneratorService] 成功生成 {len(devices)} 台设备")
        
        # 保存已使用的标识符
        self.identifier_generator.save_used_identifiers()
        
        return devices

    def generate_devices_from_sample(self, count: int, sample_devices: List[DeviceInfo]) -> List[DeviceInfo]:
        """
        基于样本设备生成新设备 - 应用层协调方法
        保持样本设备的属性，但生成新的唯一标识符
        """
        if not sample_devices:
            raise ValueError("样本设备列表不能为空")
        
        # 1. 批量生成唯一标识符
        identifiers = self.identifier_generator.generate_batch(count)
        if not identifiers:
            print("[DeviceGeneratorService] 未能生成任何设备标识符，操作中止。")
            return []
            
        print(f"[DeviceGeneratorService] 成功生成 {len(identifiers)} 个唯一标识符。")

        devices = []
        sample = sample_devices[0]  # 使用第一个样本作为模板
        
        # 2. 组装设备信息
        for identifier in identifiers:
            # 复制样本设备的所有属性，但使用新的标识符
            device = DeviceInfo(
                id=random.randint(1000000000000000000, 9999999999999999999),
                device_id=sample.device_id,
                device_serial_number=identifier.serial_number,  # 新的SN
                device_name=sample.device_name,
                ip=sample.ip,
                mac=identifier.mac_address,  # 新的MAC
                macs=identifier.mac_address,  # 新的MAC
                outside_ip=sample.outside_ip,
                type=sample.type,
                model=sample.model,
                brand=sample.brand,
                supplier=sample.supplier,
                processor=sample.processor,
                operating_system=sample.operating_system,
                hard_disk=sample.hard_disk,
                memory=sample.memory,
                main_board=sample.main_board,
                resolution=sample.resolution,
                online=sample.online,
                status=sample.status,
                last_heartbeat_time=sample.last_heartbeat_time,
                last_login_time=sample.last_login_time,
                offline_time=sample.offline_time,
                device_group_id=sample.device_group_id,
                device_user_group_id=sample.device_user_group_id,
                user_id=sample.user_id,
                login_user_id=sample.login_user_id,
                login_status=sample.login_status,
                image_id=sample.image_id,
                image_snapshot_id=sample.image_snapshot_id,
                local_image_status=sample.local_image_status,
                image_backup_time=sample.image_backup_time,
                purchase_batch=sample.purchase_batch,
                remark=sample.remark,
                create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                create_by="system",
                update_time="",
                update_by="",
                del_flag=sample.del_flag
            )
            
            # 复制Register接口专用字段
            if hasattr(sample, 'device_type'):
                device.device_type = sample.device_type
            if hasattr(sample, 'customer_code'):
                device.customer_code = sample.customer_code
            if hasattr(sample, 'protector_version'):
                device.protector_version = sample.protector_version
            if hasattr(sample, 'starter2_version'):
                device.starter2_version = sample.starter2_version
            if hasattr(sample, 'remark'):
                device.remark = sample.remark
            if hasattr(sample, 'virtual_machine'):
                device.virtual_machine = sample.virtual_machine
            
            devices.append(device)
        
        # 保存已使用的标识符
        self.identifier_generator.save_used_identifiers()
        
        return devices

    def reset_unique_tracking(self):
        """重置唯一性跟踪 - 仅用于测试"""
        self.identifier_generator.used_sns.clear()
        self.identifier_generator.used_macs.clear()
        print("[DeviceGeneratorService] 已重置唯一性跟踪")

    def get_unique_stats(self) -> Dict[str, Any]:
        """获取唯一性统计信息"""
        stats = self.identifier_generator.get_statistics()
        return {
            "used_deviceSerialNumber": stats["used_deviceSerialNumber"],
            "used_mac": stats["used_mac"],
            "brand_codes_available": stats["brand_codes_available"],
            "last_updated": stats["last_updated"],
            "generator_type": "domain_layer_random"  # 标识使用领域层随机生成器
        } 