#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备数据管理器
负责设备数据的生成、存储、状态跟踪和智能管理
支持大规模压测场景下的数据唯一性保证
"""

import json
import os
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

from src.application.services.device_identifier_service import DeviceIdentifierService
from src.domain.entities.device_info import DeviceInfo
from src.domain.value_objects.device_identifier import DeviceIdentifier

class DeviceDataManager:
    """
    设备数据管理器 - 负责设备数据的生成、存储和状态管理
    确保每次测试使用唯一设备数据，避免重复注册
    """
    
    def __init__(self):
        print(f"[DeviceDataManager] 开始初始化...")
        self.data_dir = Path("data")
        self.generated_devices_dir = self.data_dir / "generated_devices"
        self.new_created_devices_file = self.data_dir / "new_created_devices.json"
        self.used_devices_file = self.data_dir / "used_devices.json"
        self.actual_devices_file = self.data_dir / "actual_used_devices.json"
        self.verification_log_file = self.data_dir / "verification_log.json"
        
        # 初始化日志器
        self.logger = logging.getLogger(__name__)
        
        # 确保目录存在
        print(f"[DeviceDataManager] 创建目录: {self.generated_devices_dir}")
        self.generated_devices_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化新的设备标识符服务
        print(f"[DeviceDataManager] 初始化设备标识符服务...")
        self.device_identifier_service = DeviceIdentifierService()
        
        # 初始化新创建设备元信息
        print(f"[DeviceDataManager] 初始化新创建设备元信息...")
        self._init_new_created_devices()
        
        # 初始化已使用设备状态
        print(f"[DeviceDataManager] 初始化已使用设备状态...")
        self._init_used_devices()
        
        # 检查并修复数据一致性
        print(f"[DeviceDataManager] 检查数据一致性...")
        self.fix_data_consistency()
        
        print(f"[DeviceDataManager] 初始化完成，数据目录: {self.data_dir}")
    
    def _init_new_created_devices(self):
        """初始化新创建设备元信息"""
        if not self.new_created_devices_file.exists():
            metadata = {
                "generation_history": [],
                "current_available_start": 1,
                "total_generated": 0,
                "last_generation_time": None,
                "device_identifier_stats": {}  # 新增：设备标识符统计信息
            }
            self._save_new_created_devices(metadata)
            logging.info(f"[DeviceDataManager] 创建设备元信息文件: {self.new_created_devices_file}")
    
    def _init_used_devices(self):
        """初始化已使用设备状态 - 优先从actual_used_devices.json智能初始化"""
        if not self.used_devices_file.exists():
            # 文件不存在，创建新文件
            used_devices = {
                "used_devices": {
                    "deviceSerialNumbers": [],
                    "mac": []  # 存储单个MAC地址
                },
                "last_used_index": 0,
                "total_used": 0,
                "last_verification_time": None,
                "verification_history": []
            }
            self._save_used_devices(used_devices)
            logging.info(f"[DeviceDataManager] 创建已使用设备文件: {self.used_devices_file}")
        
        # 检查是否需要从actual_used_devices.json初始化
        self._initialize_from_actual_devices_if_needed()
        
        # 兼容旧格式，自动迁移
        self._migrate_old_used_devices_format()
    
    def _initialize_from_actual_devices_if_needed(self):
        """如果需要，从actual_used_devices.json初始化used_devices.json"""
        try:
            # 加载当前used_devices.json
            current_used_devices = self._load_used_devices()
            current_serial_count = len(current_used_devices["used_devices"]["deviceSerialNumbers"])
            current_mac_count = len(current_used_devices["used_devices"]["mac"])
            
            # 检查actual_used_devices.json是否存在且有效
            if self.actual_devices_file.exists():
                logging.info("[DeviceDataManager] 检测到actual_used_devices.json，开始同步数据...")
                
                with open(self.actual_devices_file, 'r', encoding='utf-8') as f:
                    actual_data = json.load(f)
                
                # 获取数据库中的实际设备数据 - 修复字段名匹配
                actual_deviceSerialNumber = actual_data.get("actual_registrations", {}).get("deviceSerialNumber", [])
                actual_mac = actual_data.get("actual_registrations", {}).get("mac", [])  # 使用mac而不是macs
                
                if actual_deviceSerialNumber or actual_mac:
                    # 合并数据（去重）
                    all_serials = list(set(current_used_devices["used_devices"]["deviceSerialNumbers"] + actual_deviceSerialNumber))
                    all_macs = list(set(current_used_devices["used_devices"]["mac"] + actual_mac))
                    
                    # 更新used_devices.json
                    current_used_devices["used_devices"]["deviceSerialNumbers"] = all_serials
                    current_used_devices["used_devices"]["mac"] = all_macs
                    current_used_devices["total_used"] = len(all_serials)
                    current_used_devices["last_verification_time"] = datetime.now().isoformat()
                    
                    # 添加同步记录到验证历史
                    sync_record = {
                        "timestamp": datetime.now().isoformat(),
                        "event_type": "sync_from_actual",
                        "deviceSerialNumber_count": len(actual_deviceSerialNumber),
                        "mac_count": len(actual_mac),
                        "description": "从actual_used_devices.json同步设备数据"
                    }
                    current_used_devices["verification_history"].append(sync_record)
                    
                    self._save_used_devices(current_used_devices)
                    logging.info(f"[DeviceDataManager] 成功同步 {len(actual_deviceSerialNumber)} 个序列号和 {len(actual_mac)} 个MAC地址")
                else:
                    logging.info("[DeviceDataManager] actual_used_devices.json中没有设备数据")
            else:
                logging.info("[DeviceDataManager] actual_used_devices.json不存在，跳过同步")
                
        except Exception as e:
            logging.error(f"[DeviceDataManager] 从actual_used_devices.json同步失败: {e}")
            # 同步失败不影响正常流程，继续使用当前used_devices.json
    
    def _migrate_old_used_devices_format(self):
        """迁移旧格式的used_devices.json到新格式"""
        try:
            with open(self.used_devices_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # 检查是否为旧格式
            if isinstance(old_data.get("used_devices"), list):
                logging.info("[DeviceDataManager] 检测到旧格式，开始迁移...")
                
                # 迁移到新格式
                new_data = {
                    "used_devices": {
                        "deviceSerialNumbers": old_data.get("used_devices", []),
                        "mac": []  # 旧格式没有MAC记录，初始化为空
                    },
                    "last_used_index": old_data.get("last_used_index", 0),
                    "total_used": old_data.get("total_used", 0),
                    "last_verification_time": old_data.get("last_verification_time"),
                    "verification_history": old_data.get("verification_history", [])
                }
                
                # 保存新格式
                self._save_used_devices(new_data)
                logging.info("[DeviceDataManager] 旧格式迁移完成")
                
        except Exception as e:
            logging.error(f"[DeviceDataManager] 迁移旧格式失败: {e}")
            # 如果迁移失败，创建默认新格式
            used_devices = {
                "used_devices": {
                    "deviceSerialNumbers": [],
                    "mac": []
                },
                "last_used_index": 0,
                "total_used": 0,
                "last_verification_time": None,
                "verification_history": []
            }
            self._save_used_devices(used_devices)
    
    def _load_new_created_devices(self) -> Dict:
        """加载新创建设备元信息"""
        try:
            with open(self.new_created_devices_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"[DeviceDataManager] 加载新创建设备元信息失败: {e}")
            return {"generation_history": [], "current_available_start": 1, "total_generated": 0}
    
    def _save_new_created_devices(self, new_created_devices: Dict):
        """保存新创建设备元信息"""
        try:
            with open(self.new_created_devices_file, 'w', encoding='utf-8') as f:
                json.dump(new_created_devices, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"[DeviceDataManager] 保存新创建设备元信息失败: {e}")
    
    def _load_used_devices(self) -> Dict:
        """加载已使用设备状态 - 支持新格式"""
        try:
            with open(self.used_devices_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 兼容旧格式
            if isinstance(data.get("used_devices"), list):
                # 旧格式，返回兼容结构
                return {
                    "used_devices": {
                        "deviceSerialNumbers": data.get("used_devices", []),
                        "mac": []
                    },
                    "last_used_index": data.get("last_used_index", 0),
                    "total_used": data.get("total_used", 0),
                    "last_verification_time": data.get("last_verification_time"),
                    "verification_history": data.get("verification_history", [])
                }
            else:
                # 新格式，直接返回
                return data
                
        except Exception as e:
            logging.error(f"[DeviceDataManager] 加载已使用设备失败: {e}")
            return {
                "used_devices": {
                    "deviceSerialNumbers": [],
                    "mac": []
                },
                "last_used_index": 0,
                "total_used": 0,
                "last_verification_time": None,
                "verification_history": []
            }
    
    def _save_used_devices(self, used_devices: Dict):
        """保存已使用设备状态"""
        try:
            with open(self.used_devices_file, 'w', encoding='utf-8') as f:
                json.dump(used_devices, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"[DeviceDataManager] 保存已使用设备失败: {e}")
    
    def get_next_available_index(self) -> int:
        """
        获取下一个可用的设备索引
        注意：现在使用领域层生成器，不再依赖索引计数
        """
        # 由于现在使用领域层的随机生成器，不再需要索引计数
        # 返回一个默认值，实际生成由领域层处理
        return 1
    
    def get_available_devices(self, count: int) -> str:
        """
        获取可用的设备数据文件
        确保设备数据唯一性，避免重复注册
        
        Args:
            count: 需要的设备数量
            
        Returns:
            str: 设备数据文件路径
        """
        try:
            print(f"[DeviceDataManager] 开始获取 {count} 个可用设备...")
            
            # === 新增：检查现有devices.csv文件 ===
            standard_csv_path = self.generated_devices_dir / "devices.csv"
            if standard_csv_path.exists():
                # 检查现有文件是否有效
                try:
                    with open(standard_csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        
                        # 检查文件格式和内容
                        if len(rows) >= count and 'mac' in rows[0] and 'serial_number' in rows[0]:
                            # 检查MAC地址是否不为空
                            valid_rows = [row for row in rows[:count] if row.get('mac', '').strip()]
                            
                            if len(valid_rows) >= count:
                                print(f"[DeviceDataManager] 发现现有devices.csv文件，包含 {len(rows)} 条记录")
                                print(f"[DeviceDataManager] 其中 {len(valid_rows)} 条记录MAC地址有效")
                                print(f"[DeviceDataManager] 跳过重新生成，直接使用现有文件: {standard_csv_path}")
                                
                                # 返回现有文件路径
                                return str(standard_csv_path)
                            else:
                                print(f"[DeviceDataManager] 现有devices.csv文件中有效记录不足 ({len(valid_rows)} < {count})，将重新生成")
                        else:
                            print(f"[DeviceDataManager] 现有devices.csv文件格式不正确，将重新生成")
                except Exception as e:
                    print(f"[DeviceDataManager] 检查现有devices.csv文件失败: {e}，将重新生成")
            
            # === 原有逻辑：重新生成设备数据 ===
            print(f"[DeviceDataManager] 开始重新生成设备数据...")
            
            # 使用新的设备标识符服务获取设备
            device_identifiers = self.device_identifier_service.get_devices_for_test(count)
            
            if not device_identifiers:
                print(f"[DeviceDataManager] 无法获取设备标识符")
                return ""
            
            # 转换为DeviceInfo格式
            devices = []
            for device_id in device_identifiers:
                device_info = DeviceInfo(
                    device_id=device_id.serial_number,  # 设备唯一标识
                    device_serial_number=device_id.serial_number,  # 设备序列号
                    mac=device_id.mac_address,  # MAC地址
                    create_time=device_id.created_at.isoformat() if device_id.created_at else ''
                )
                devices.append(device_info)
            
            # 保存到文件
            csv_path = self.generated_devices_dir / f"devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{count}.csv"
            self._save_devices_to_csv(devices, csv_path)
            print(f"[DeviceDataManager] 设备数据已保存到CSV: {csv_path}")
            
            # 自动生成标准JMX专用CSV，只保留mac和serial_number两列，表头为mac,serial_number
            try:
                with open(csv_path, 'r', encoding='utf-8') as fin, open(standard_csv_path, 'w', encoding='utf-8', newline='') as fout:
                    reader = csv.DictReader(fin)
                    writer = csv.DictWriter(fout, fieldnames=['mac', 'serial_number'])
                    writer.writeheader()
                    for row in reader:
                        writer.writerow({'mac': row.get('mac_address', ''), 'serial_number': row.get('serial_number', '')})
                print(f"[DeviceDataManager] 标准JMX专用CSV已生成: {standard_csv_path}")
            except Exception as e:
                print(f"[DeviceDataManager] 生成标准JMX专用CSV失败: {e}")
            
            # 更新元信息
            self._update_metadata_with_new_devices(count)
            
            print(f"[DeviceDataManager] 成功获取 {len(devices)} 个设备，文件: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            print(f"[DeviceDataManager] 获取可用设备失败: {e}")
            logging.error(f"[DeviceDataManager] 获取可用设备失败: {e}")
            return ""
    
    def _save_devices_to_csv(self, devices: List[DeviceInfo], csv_path: Path):
        """
        保存设备数据到CSV文件
        
        这个方法将设备数据列表写入到指定的CSV文件中，支持多种CSV格式：
        1. 标准格式：包含device_id, serial_number, mac_address, created_at
        2. 简化格式：只包含mac, serial_number（用于JMeter测试）
        
        Args:
            devices (List[DeviceInfo]): 需要保存的设备数据列表
            csv_path (Path): CSV文件的路径
        """
        try:
            # 确保目录存在
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 根据文件名判断使用哪种格式
            is_simplified_format = csv_path.name == "devices.csv" or "simplified" in csv_path.name.lower()
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                if is_simplified_format:
                    # 简化格式：只包含mac和serial_number，用于JMeter测试
                    fieldnames = ['mac', 'serial_number']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for device in devices:
                        writer.writerow({
                            'mac': device.mac or '',
                            'serial_number': device.device_serial_number or ''
                        })
                    
                    self.logger.info(f"[DeviceDataManager] 简化格式CSV已保存: {csv_path} ({len(devices)} 条记录)")
                else:
                    # 标准格式：包含完整字段信息
                    fieldnames = ['device_id', 'serial_number', 'mac_address', 'created_at']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for device in devices:
                        writer.writerow({
                            'device_id': '',  # Register接口要求device_id为空
                            'serial_number': device.device_serial_number or '',
                            'mac_address': device.mac or '',
                            'created_at': device.create_time or datetime.now().isoformat()
                        })
                    
                    self.logger.info(f"[DeviceDataManager] 标准格式CSV已保存: {csv_path} ({len(devices)} 条记录)")
            
            # 验证生成的文件
            self._validate_generated_csv(csv_path, len(devices))
            
            print(f"[DeviceDataManager] 设备数据已保存到CSV: {csv_path}")
            return True
            
        except Exception as e:
            error_msg = f"[DeviceDataManager] 保存CSV失败: {e}"
            print(error_msg)
            self.logger.error(error_msg)
            return False
    
    def _validate_generated_csv(self, csv_path: Path, expected_count: int):
        """
        验证生成的CSV文件
        
        Args:
            csv_path (Path): CSV文件路径
            expected_count (int): 期望的记录数量
        """
        try:
            if not csv_path.exists():
                self.logger.warning(f"[DeviceDataManager] CSV文件不存在: {csv_path}")
                return
            
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                actual_count = sum(1 for _ in reader)
                
                if actual_count != expected_count:
                    self.logger.warning(
                        f"[DeviceDataManager] CSV记录数量不匹配: 期望 {expected_count}, 实际 {actual_count}"
                    )
                else:
                    self.logger.info(f"[DeviceDataManager] CSV验证通过: {actual_count} 条记录")
                    
        except Exception as e:
            self.logger.warning(f"[DeviceDataManager] CSV验证失败: {e}")
    
    def _update_metadata(self, count: int, start_index: int, end_index: int, timestamp: str):
        """更新设备元信息"""
        try:
            metadata = self._load_new_created_devices()
            
            # 添加生成历史记录
            generation_record = {
                "timestamp": timestamp,
                "count": count,
                "start_index": start_index,
                "end_index": end_index,
                "file_path": f"generated_devices/devices_{timestamp}.csv"
            }
            
            metadata["generation_history"].append(generation_record)
            metadata["total_generated"] += count
            metadata["last_generation_time"] = timestamp
            
            # 更新设备标识符统计信息
            try:
                stats = self.device_identifier_service.get_statistics()
                metadata["device_identifier_stats"] = stats
            except Exception as e:
                logging.warning(f"[DeviceDataManager] 获取设备标识符统计信息失败: {e}")
            
            self._save_new_created_devices(metadata)
            print(f"[DeviceDataManager] 元信息已更新，总生成数: {metadata['total_generated']}")
        except Exception as e:
            print(f"[DeviceDataManager] 更新元信息失败: {e}")
            logging.error(f"[DeviceDataManager] 更新元信息失败: {e}")
    
    def _mark_devices_as_used(self, devices: List[DeviceInfo]):
        """标记设备为已使用"""
        try:
            used_devices = self._load_used_devices()
            
            # 提取序列号和MAC地址
            deviceSerialNumber = [device.device_serial_number for device in devices]
            mac = [device.mac for device in devices]
            
            # 添加到已使用列表
            used_devices["used_devices"]["deviceSerialNumbers"].extend(deviceSerialNumber)
            used_devices["used_devices"]["mac"].extend(mac)
            
            # 更新统计信息
            used_devices["total_used"] += len(devices)
            used_devices["last_used_index"] += len(devices)
            
            # 标记为已使用（在数据库中）
            try:
                self.device_identifier_service.repository.mark_as_used(deviceSerialNumber)
            except Exception as e:
                logging.warning(f"[DeviceDataManager] 标记设备为已使用失败: {e}")
            
            self._save_used_devices(used_devices)
            print(f"[DeviceDataManager] 已标记 {len(devices)} 个设备为已使用")
        except Exception as e:
            print(f"[DeviceDataManager] 标记设备为已使用失败: {e}")
            logging.error(f"[DeviceDataManager] 标记设备为已使用失败: {e}")
    
    def get_device_statistics(self) -> Dict:
        """获取设备统计信息"""
        try:
            # 获取基础统计信息
            metadata = self._load_new_created_devices()
            used_devices = self._load_used_devices()
            
            # 获取设备标识符统计信息
            device_stats = {}
            try:
                device_stats = self.device_identifier_service.get_statistics()
            except Exception as e:
                logging.warning(f"[DeviceDataManager] 获取设备标识符统计信息失败: {e}")
            
            stats = {
                "total_generated": metadata.get("total_generated", 0),
                "total_used": used_devices.get("total_used", 0),
                "available_count": used_devices.get("used_devices", {}).get("deviceSerialNumbers", []),
                "last_generation_time": metadata.get("last_generation_time"),
                "last_verification_time": used_devices.get("last_verification_time"),
                "device_identifier_stats": device_stats
            }
            
            return stats
        except Exception as e:
            logging.error(f"[DeviceDataManager] 获取统计信息失败: {e}")
            return {}
    
    def print_statistics(self):
        """打印设备统计信息"""
        try:
            stats = self.get_device_statistics()
            
            print("\n=== 设备数据统计信息 ===")
            print(f"总生成数: {stats.get('total_generated', 0)}")
            print(f"总使用数: {stats.get('total_used', 0)}")
            print(f"最后生成时间: {stats.get('last_generation_time', 'N/A')}")
            print(f"最后验证时间: {stats.get('last_verification_time', 'N/A')}")
            
            # 打印设备标识符统计信息
            device_stats = stats.get('device_identifier_stats', {})
            if device_stats:
                print("\n=== 设备标识符统计信息 ===")
                print(f"数据库总设备数: {device_stats.get('total_count', 0)}")
                print(f"未使用设备数: {device_stats.get('unused_count', 0)}")
                print(f"已使用设备数: {device_stats.get('used_count', 0)}")
                print(f"使用率: {device_stats.get('usage_rate', 0):.2f}%")
                print(f"最早创建时间: {device_stats.get('earliest_created', 'N/A')}")
                print(f"最晚创建时间: {device_stats.get('latest_created', 'N/A')}")
            
            print("=" * 30)
        except Exception as e:
            print(f"[DeviceDataManager] 打印统计信息失败: {e}")
            logging.error(f"[DeviceDataManager] 打印统计信息失败: {e}")
    
    def reset_device_status(self, confirm: bool = False):
        """重置设备状态（谨慎使用）"""
        if not confirm:
            print("[DeviceDataManager] 警告：此操作将重置所有设备状态！")
            print("[DeviceDataManager] 如需继续，请传入 confirm=True")
            return
        
        try:
            # 重置已使用设备状态
            used_devices = {
                "used_devices": {
                    "deviceSerialNumbers": [],
                    "mac": []
                },
                "last_used_index": 0,
                "total_used": 0,
                "last_verification_time": None,
                "verification_history": []
            }
            self._save_used_devices(used_devices)
            
            # 重置数据库中的使用状态
            try:
                self.device_identifier_service.repository.reset_usage_status()
            except Exception as e:
                logging.warning(f"[DeviceDataManager] 重置数据库使用状态失败: {e}")
            
            print("[DeviceDataManager] 设备状态已重置")
        except Exception as e:
            print(f"[DeviceDataManager] 重置设备状态失败: {e}")
            logging.error(f"[DeviceDataManager] 重置设备状态失败: {e}")
    
    def _load_devices_from_file(self, file_path: Path) -> List[DeviceInfo]:
        """从CSV文件加载设备数据"""
        devices = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    device = DeviceInfo(
                        device_id=row.get('device_id', ''),
                        device_serial_number=row.get('serial_number', ''),
                        mac=row.get('mac_address', ''),
                        create_time=row.get('created_at', '')
                    )
                    devices.append(device)
        except Exception as e:
            self.logger.error(f"加载设备文件失败 {file_path}: {e}")
        
        return devices
    
    def _save_devices_to_file(self, devices: List[DeviceInfo]) -> Path:
        """保存设备数据到CSV文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"devices_{timestamp}_{len(devices)}.csv"
        file_path = self.generated_devices_dir / filename
        
        try:
            self._save_devices_to_csv(devices, file_path)
            return file_path
        except Exception as e:
            self.logger.error(f"保存设备数据失败: {e}")
            raise
    
    def _update_metadata_with_new_devices(self, count: int):
        """更新元数据，记录新生成的设备"""
        try:
            metadata = self._load_new_created_devices()
            metadata["total_generated"] += count
            metadata["last_generation_time"] = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 更新设备标识符统计信息
            try:
                stats = self.device_identifier_service.get_statistics()
                metadata["device_identifier_stats"] = stats
            except Exception as e:
                logging.warning(f"[DeviceDataManager] 获取设备标识符统计信息失败: {e}")
            
            self._save_new_created_devices(metadata)
        except Exception as e:
            self.logger.error(f"更新元数据失败: {e}")
    
    def mark_devices_as_theoretically_used(self, device_ids: List[str], test_id: str):
        """
        标记设备为理论上已使用（基于测试结果）
        
        Args:
            device_ids: 理论上成功注册的设备ID列表
            test_id: 测试ID
        """
        self.logger.info(f"标记 {len(device_ids)} 台设备为理论上已使用")
        
        # 记录到验证日志
        self._log_verification_event(test_id, "theoretical", device_ids)
    
    def mark_devices_as_actually_used(self, device_ids: List[str], test_id: str):
        """
        标记设备为实际已使用（基于数据库验证）
        
        Args:
            device_ids: 实际在数据库中的设备ID列表
            test_id: 测试ID
        """
        self.logger.info(f"标记 {len(device_ids)} 台设备为实际已使用")
        
        # 更新已使用设备列表
        used_devices = self._load_used_devices()
        
        # 安全检查：确保数据结构正确
        if "used_devices" not in used_devices:
            used_devices["used_devices"] = {"deviceSerialNumbers": [], "mac": []}
        if "deviceSerialNumbers" not in used_devices["used_devices"]:
            used_devices["used_devices"]["deviceSerialNumbers"] = []
        if "mac" not in used_devices["used_devices"]:
            used_devices["used_devices"]["mac"] = []
        
        used_devices["used_devices"]["deviceSerialNumbers"].extend(device_ids)
        
        # 去重并保存
        used_devices["used_devices"]["deviceSerialNumbers"] = list(set(used_devices["used_devices"]["deviceSerialNumbers"]))
        used_devices["total_used"] = len(used_devices["used_devices"]["deviceSerialNumbers"])
        used_devices["last_verification_time"] = datetime.now().isoformat()
        self._save_used_devices(used_devices)
        
        # 标记为已使用（在数据库中）
        try:
            self.device_identifier_service.repository.mark_as_used(device_ids)
        except Exception as e:
            logging.warning(f"[DeviceDataManager] 标记设备为已使用失败: {e}")
        
        # 记录到验证日志
        self._log_verification_event(test_id, "actual", device_ids)
    
    def _log_verification_event(self, test_id: str, event_type: str, device_ids: List[str]):
        """记录验证事件到日志"""
        log_data = {
            "test_id": test_id,
            "event_type": event_type,
            "device_count": len(device_ids),
            "device_ids": device_ids,
            "timestamp": datetime.now().isoformat()
        }
        
        # 加载现有日志
        log_entries = []
        if self.verification_log_file.exists():
            try:
                with open(self.verification_log_file, 'r', encoding='utf-8') as f:
                    log_entries = json.load(f)
            except Exception:
                log_entries = []
        
        # 添加新日志条目
        log_entries.append(log_data)
        
        # 保存日志
        try:
            with open(self.verification_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_entries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存验证日志失败: {e}")
    
    def get_used_device_count(self) -> int:
        """获取已使用的设备数量"""
        try:
            return self.device_identifier_service.count_used()
        except Exception as e:
            self.logger.error(f"获取已使用设备数量失败: {e}")
            return 0
    
    def get_available_device_count(self) -> int:
        """获取可用的设备数量"""
        try:
            return self.device_identifier_service.count_unused()
        except Exception as e:
            self.logger.error(f"获取可用设备数量失败: {e}")
            return 0
    
    def get_total_generated_count(self) -> int:
        """获取总生成的设备数量"""
        try:
            return self.device_identifier_service.get_device_count()
        except Exception as e:
            self.logger.error(f"获取总生成设备数量失败: {e}")
            return 0
    
    def get_verification_report(self, test_id: str) -> Dict:
        """
        获取验证报告（理论vs实际对比）
        
        Args:
            test_id: 测试ID
            
        Returns:
            Dict: 验证报告数据
        """
        # 加载验证日志
        log_entries = []
        if self.verification_log_file.exists():
            try:
                with open(self.verification_log_file, 'r', encoding='utf-8') as f:
                    log_entries = json.load(f)
            except Exception:
                pass
        
        # 查找指定测试的验证记录
        test_entries = [entry for entry in log_entries if entry.get("test_id") == test_id]
        
        theoretical_entry = None
        actual_entry = None
        
        for entry in test_entries:
            if entry.get("event_type") == "theoretical":
                theoretical_entry = entry
            elif entry.get("event_type") == "actual":
                actual_entry = entry
        
        # 构建验证报告
        report = {
            "test_id": test_id,
            "verification_time": datetime.now().isoformat(),
            "theoretical_registrations": theoretical_entry.get("device_ids", []) if theoretical_entry else [],
            "actual_registrations": actual_entry.get("device_ids", []) if actual_entry else [],
            "differences": self._analyze_differences(
                theoretical_entry.get("device_ids", []) if theoretical_entry else [],
                actual_entry.get("device_ids", []) if actual_entry else []
            )
        }
        
        # 添加统计信息
        total_tested = len(report["theoretical_registrations"])
        theoretical_success = len(report["theoretical_registrations"])
        actual_success = len(report["actual_registrations"])
        
        report["test_summary"] = {
            "total_devices_tested": total_tested,
            "theoretical_success": theoretical_success,
            "actual_success": actual_success,
            "verification_time": report["verification_time"]
        }
        
        # 添加分析结果
        if total_tested > 0:
            report["analysis"] = {
                "success_rate_theoretical": round(theoretical_success / total_tested * 100, 2),
                "success_rate_actual": round(actual_success / total_tested * 100, 2),
                "data_loss_rate": round((theoretical_success - actual_success) / total_tested * 100, 2),
                "duplicate_rate": 0.0  # 暂时设为0，后续可扩展
            }
        else:
            report["analysis"] = {
                "success_rate_theoretical": 0.0,
                "success_rate_actual": 0.0,
                "data_loss_rate": 0.0,
                "duplicate_rate": 0.0
            }
        
        return report
    
    def _analyze_differences(self, theoretical_ids: List[str], actual_ids: List[str]) -> Dict:
        """分析理论vs实际的差异"""
        theoretical_set = set(theoretical_ids)
        actual_set = set(actual_ids)
        
        missing_in_database = list(theoretical_set - actual_set)
        unexpected_in_database = list(actual_set - theoretical_set)
        
        return {
            "missing_in_database": missing_in_database,
            "unexpected_in_database": unexpected_in_database
        }
    
    def get_status_summary(self) -> Dict:
        """获取设备数据状态摘要"""
        try:
            stats = self.device_identifier_service.get_statistics()
            return {
                "total_generated": stats.get('total_count', 0),
                "total_used": stats.get('used_count', 0),
                "total_available": stats.get('unused_count', 0),
                "usage_rate": stats.get('usage_rate', 0),
                "earliest_created": stats.get('earliest_created'),
                "latest_created": stats.get('latest_created')
            }
        except Exception as e:
            self.logger.error(f"获取状态摘要失败: {e}")
            return {
                "total_generated": 0,
                "total_used": 0,
                "total_available": 0,
                "usage_rate": 0,
                "earliest_created": None,
                "latest_created": None
            }
    
    def sync_actual_devices_from_database(self, db_config: dict, output_path: str = 'data/actual_used_devices.json') -> bool:
        """
        从数据库同步真实注册设备到JSON文件 - 应用层数据同步
        
        Args:
            db_config: 数据库配置
            output_path: 输出文件路径
            
        Returns:
            bool: 同步是否成功
        """
        try:
            from src.interfaces.cli.db_query_cli import export_actual_used_devices
            
            # 调用数据库导出功能，设置limit为None以同步所有设备记录
            success = export_actual_used_devices(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config.get('database', 'yangguan'),
                table='biz_device',
                limit=None,  # 修改：设置为None以同步所有设备记录，而不是限制为10000
                output_path=output_path
            )
            
            if success:
                self.logger.info(f"数据库设备同步成功，输出到: {output_path}")
            else:
                self.logger.error("数据库设备同步失败")
                
            return success
            
        except Exception as e:
            self.logger.error(f"数据库设备同步异常: {e}")
            return False
    
    def check_data_consistency(self) -> Dict:
        """
        检查三个文件之间的数据一致性
        
        Returns:
            Dict: 一致性检查结果
        """
        try:
            result = {
                "is_consistent": True,
                "issues": [],
                "statistics": {}
            }
            
            # 加载三个文件的数据
            used_devices = self._load_used_devices()
            new_created_devices = self._load_new_created_devices()
            
            # 检查actual_used_devices.json
            actual_devices_file = self.data_dir / "actual_used_devices.json"
            actual_deviceSerialNumber = set()
            actual_mac = set()
            
            if actual_devices_file.exists():
                with open(actual_devices_file, 'r', encoding='utf-8') as f:
                    actual_data = json.load(f)
                actual_deviceSerialNumber = set(actual_data.get("actual_registrations", {}).get("deviceSerialNumber", []))
                actual_mac = set(actual_data.get("actual_registrations", {}).get("mac", []))
            
            # 获取used_devices.json中的数据
            used_deviceSerialNumber = set(used_devices["used_devices"]["deviceSerialNumbers"])
            used_mac = set(used_devices["used_devices"]["mac"])
            
            # 检查一致性：used_devices.json应该包含actual_used_devices.json中的所有数据
            missing_serials = actual_deviceSerialNumber - used_deviceSerialNumber
            missing_macs = actual_mac - used_mac
            
            if missing_serials or missing_macs:
                result["is_consistent"] = False
                if missing_serials:
                    result["issues"].append(f"used_devices.json缺少 {len(missing_serials)} 个序列号")
                if missing_macs:
                    result["issues"].append(f"used_devices.json缺少 {len(missing_macs)} 个MAC地址")
            
            # 统计信息
            result["statistics"] = {
                "actual_serial_count": len(actual_deviceSerialNumber),
                "actual_mac_count": len(actual_mac),
                "used_serial_count": len(used_deviceSerialNumber),
                "used_mac_count": len(used_mac),
                "new_created_count": new_created_devices.get("total_generated", 0),
                "missing_serial_count": len(missing_serials),
                "missing_mac_count": len(missing_macs)
            }
            
            return result
            
        except Exception as e:
            logging.error(f"[DeviceDataManager] 数据一致性检查失败: {e}")
            return {
                "is_consistent": False,
                "issues": [f"检查过程出错: {e}"],
                "statistics": {}
            }
    
    def fix_data_consistency(self) -> bool:
        """
        修复数据一致性问题
        
        Returns:
            bool: 修复是否成功
        """
        try:
            consistency_result = self.check_data_consistency()
            
            if consistency_result["is_consistent"]:
                logging.info("[DeviceDataManager] 数据一致性检查通过，无需修复")
                return True
            
            logging.info("[DeviceDataManager] 检测到数据一致性问题，开始修复...")
            
            # 加载数据
            used_devices = self._load_used_devices()
            actual_devices_file = self.data_dir / "actual_used_devices.json"
            
            if actual_devices_file.exists():
                with open(actual_devices_file, 'r', encoding='utf-8') as f:
                    actual_data = json.load(f)
                
                actual_deviceSerialNumber = actual_data.get("actual_registrations", {}).get("deviceSerialNumber", [])
                actual_mac = actual_data.get("actual_registrations", {}).get("mac", [])
                
                # 合并数据（去重）
                all_serials = list(set(used_devices["used_devices"]["deviceSerialNumbers"] + actual_deviceSerialNumber))
                all_macs = list(set(used_devices["used_devices"]["mac"] + actual_mac))
                
                # 更新used_devices.json
                used_devices["used_devices"]["deviceSerialNumbers"] = all_serials
                used_devices["used_devices"]["mac"] = all_macs
                used_devices["total_used"] = len(all_serials)
                used_devices["last_verification_time"] = datetime.now().isoformat()
                
                # 添加修复记录
                fix_record = {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "consistency_fix",
                    "added_serial_count": len(all_serials) - len(used_devices["used_devices"]["deviceSerialNumbers"]),
                    "added_mac_count": len(all_macs) - len(used_devices["used_devices"]["mac"]),
                    "description": "修复数据一致性问题，合并actual_used_devices.json中的数据"
                }
                used_devices["verification_history"].append(fix_record)
                
                self._save_used_devices(used_devices)
                logging.info(f"[DeviceDataManager] 数据一致性修复完成，当前共有 {len(all_serials)} 个序列号和 {len(all_macs)} 个MAC地址")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"[DeviceDataManager] 数据一致性修复失败: {e}")
            return False 