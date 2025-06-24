"""
设备标识符生成服务 - 应用层
负责协调设备标识符的生成、验证和持久化操作
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os
import json

from src.domain.value_objects.device_identifier import DeviceIdentifier
from src.domain.services.device_identifier_generator import DeviceIdentifierGenerator
from src.infrastructure.repositories.device_identifier_repository import DeviceIdentifierRepository


class DeviceIdentifierService:
    """设备标识符生成服务"""
    
    def __init__(self):
        self.generator = DeviceIdentifierGenerator()
        self.repository = DeviceIdentifierRepository()
        self.logger = logging.getLogger(__name__)
    
    def generate_single_device(self) -> DeviceIdentifier:
        """
        生成单个设备标识符
        
        Returns:
            DeviceIdentifier: 生成的设备标识符
        """
        try:
            device_id = self.generator.generate_unique_identifier()
            self.logger.info(f"成功生成设备标识符: SN={device_id.serial_number}, MAC={device_id.mac_address}")
            return device_id
        except Exception as e:
            self.logger.error(f"生成设备标识符失败: {e}")
            raise
    
    def generate_batch_devices(self, count: int) -> List[DeviceIdentifier]:
        """
        批量生成设备标识符
        
        Args:
            count: 生成数量
            
        Returns:
            List[DeviceIdentifier]: 生成的设备标识符列表
        """
        try:
            self.logger.info(f"开始批量生成 {count} 个设备标识符")
            devices = []
            
            for i in range(count):
                device_id = self.generator.generate_unique_identifier()
                devices.append(device_id)
                
                if (i + 1) % 100 == 0:
                    self.logger.info(f"已生成 {i + 1}/{count} 个设备标识符")
            
            self.logger.info(f"批量生成完成，共生成 {len(devices)} 个设备标识符")
            return devices
        except Exception as e:
            self.logger.error(f"批量生成设备标识符失败: {e}")
            raise
    
    def save_devices_to_file(self, devices: List[DeviceIdentifier], file_path: str) -> None:
        """
        将设备标识符保存到文件
        
        Args:
            devices: 设备标识符列表
            file_path: 文件路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 转换为字典格式
            device_data = []
            for device in devices:
                device_data.append({
                    'serial_number': device.serial_number,
                    'mac_address': device.mac_address,
                    'created_at': device.created_at.isoformat()
                })
            
            # 保存到JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(device_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"成功保存 {len(devices)} 个设备标识符到文件: {file_path}")
        except Exception as e:
            self.logger.error(f"保存设备标识符到文件失败: {e}")
            raise
    
    def load_devices_from_file(self, file_path: str) -> List[DeviceIdentifier]:
        """
        从文件加载设备标识符
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[DeviceIdentifier]: 加载的设备标识符列表
        """
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"设备数据文件不存在: {file_path}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                device_data = json.load(f)
            
            devices = []
            for data in device_data:
                device = DeviceIdentifier(
                    serial_number=data['serial_number'],
                    mac_address=data['mac_address'],
                    created_at=datetime.fromisoformat(data['created_at'])
                )
                devices.append(device)
            
            self.logger.info(f"成功从文件加载 {len(devices)} 个设备标识符: {file_path}")
            return devices
        except Exception as e:
            self.logger.error(f"从文件加载设备标识符失败: {e}")
            raise
    
    def save_devices_to_database(self, devices: List[DeviceIdentifier]) -> None:
        """
        将设备标识符保存到数据库
        
        Args:
            devices: 设备标识符列表
        """
        try:
            self.logger.info(f"开始保存 {len(devices)} 个设备标识符到数据库")
            self.repository.save_batch(devices)
            self.logger.info("设备标识符数据库保存完成")
        except Exception as e:
            self.logger.error(f"保存设备标识符到数据库失败: {e}")
            raise
    
    def get_device_count(self) -> int:
        """
        获取数据库中的设备总数
        
        Returns:
            int: 设备总数
        """
        try:
            count = self.repository.count_all()
            self.logger.info(f"数据库中设备总数: {count}")
            return count
        except Exception as e:
            self.logger.error(f"获取设备总数失败: {e}")
            raise
    
    def get_devices_for_test(self, count: int) -> List[DeviceIdentifier]:
        """
        获取用于测试的设备标识符
        
        Args:
            count: 需要的设备数量
            
        Returns:
            List[DeviceIdentifier]: 设备标识符列表
        """
        try:
            # 先从数据库获取
            devices = self.repository.get_batch(count)
            
            # 如果数据库中的设备不够，则生成新的
            if len(devices) < count:
                needed_count = count - len(devices)
                self.logger.info(f"数据库设备不足，需要生成 {needed_count} 个新设备")
                new_devices = self.generate_batch_devices(needed_count)
                self.save_devices_to_database(new_devices)
                devices.extend(new_devices)
            
            self.logger.info(f"获取到 {len(devices)} 个设备用于测试")
            return devices[:count]
        except Exception as e:
            self.logger.error(f"获取测试设备失败: {e}")
            raise
    
    def validate_device_data(self, devices: List[DeviceIdentifier]) -> Tuple[bool, List[str]]:
        """
        验证设备数据的有效性
        
        Args:
            devices: 设备标识符列表
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        try:
            errors = []
            
            # 检查SN和MAC的唯一性
            sn_set = set()
            mac_set = set()
            
            for device in devices:
                # 检查SN格式
                if not self.generator.is_valid_serial_number(device.serial_number):
                    errors.append(f"无效的SN格式: {device.serial_number}")
                
                # 检查MAC格式
                if not self.generator.is_valid_mac_address(device.mac_address):
                    errors.append(f"无效的MAC格式: {device.mac_address}")
                
                # 检查SN唯一性
                if device.serial_number in sn_set:
                    errors.append(f"重复的SN: {device.serial_number}")
                else:
                    sn_set.add(device.serial_number)
                
                # 检查MAC唯一性
                if device.mac_address in mac_set:
                    errors.append(f"重复的MAC: {device.mac_address}")
                else:
                    mac_set.add(device.mac_address)
            
            is_valid = len(errors) == 0
            if is_valid:
                self.logger.info(f"设备数据验证通过，共 {len(devices)} 个设备")
            else:
                self.logger.warning(f"设备数据验证失败，发现 {len(errors)} 个问题")
            
            return is_valid, errors
        except Exception as e:
            self.logger.error(f"验证设备数据失败: {e}")
            raise
    
    def cleanup_old_devices(self, days: int = 30) -> int:
        """
        清理指定天数前的旧设备数据
        
        Args:
            days: 保留天数
            
        Returns:
            int: 清理的设备数量
        """
        try:
            count = self.repository.delete_old_devices(days)
            self.logger.info(f"清理了 {count} 个 {days} 天前的旧设备数据")
            return count
        except Exception as e:
            self.logger.error(f"清理旧设备数据失败: {e}")
            raise
    
    def count_unused(self) -> int:
        """
        获取未使用的设备数量
        Returns:
            int: 未使用的设备数量
        """
        return self.repository.count_unused()

    def count_used(self) -> int:
        """
        获取已使用的设备数量
        Returns:
            int: 已使用的设备数量
        """
        return self.repository.count_used()

    def get_statistics(self) -> dict:
        """
        获取设备标识符统计信息
        Returns:
            dict: 统计信息
        """
        return self.repository.get_statistics() 