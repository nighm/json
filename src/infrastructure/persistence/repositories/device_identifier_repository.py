"""
设备标识符仓储 - 基础设施层
负责设备标识符的数据库持久化操作
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
import sqlite3
import os

from src.domain.value_objects.device_identifier import DeviceIdentifier


class DeviceIdentifierRepository:
    """设备标识符仓储"""
    
    def __init__(self, db_path: str = "data/device_identifiers.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化数据库表结构"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建设备标识符表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS device_identifiers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        serial_number TEXT UNIQUE NOT NULL,
                        mac_address TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        used_at TIMESTAMP,
                        is_used INTEGER DEFAULT 0
                    )
                ''')
                
                # 创建索引以提高查询性能
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_serial_number ON device_identifiers(serial_number)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_mac_address ON device_identifiers(mac_address)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON device_identifiers(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_used ON device_identifiers(is_used)')
                
                conn.commit()
                self.logger.info("设备标识符数据库初始化完成")
        except Exception as e:
            self.logger.error(f"初始化数据库失败: {e}")
            raise
    
    def save_batch(self, devices: List[DeviceIdentifier]) -> None:
        """
        批量保存设备标识符
        
        Args:
            devices: 设备标识符列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for device in devices:
                    cursor.execute('''
                        INSERT OR IGNORE INTO device_identifiers 
                        (serial_number, mac_address, created_at) 
                        VALUES (?, ?, ?)
                    ''', (device.serial_number, device.mac_address, device.created_at))
                
                conn.commit()
                self.logger.info(f"成功保存 {len(devices)} 个设备标识符到数据库")
        except Exception as e:
            self.logger.error(f"批量保存设备标识符失败: {e}")
            raise
    
    def get_batch(self, count: int) -> List[DeviceIdentifier]:
        """
        获取指定数量的未使用设备标识符
        
        Args:
            count: 需要的设备数量
            
        Returns:
            List[DeviceIdentifier]: 设备标识符列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT serial_number, mac_address, created_at 
                    FROM device_identifiers 
                    WHERE is_used = 0 
                    ORDER BY created_at ASC 
                    LIMIT ?
                ''', (count,))
                
                rows = cursor.fetchall()
                devices = []
                
                for row in rows:
                    device = DeviceIdentifier(
                        serial_number=row[0],
                        mac_address=row[1],
                        created_at=datetime.fromisoformat(row[2])
                    )
                    devices.append(device)
                
                self.logger.info(f"从数据库获取到 {len(devices)} 个未使用的设备标识符")
                return devices
        except Exception as e:
            self.logger.error(f"获取设备标识符失败: {e}")
            raise
    
    def mark_as_used(self, deviceSerialNumber: List[str]) -> None:
        """
        标记设备标识符为已使用
        
        Args:
            deviceSerialNumber: 序列号列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for sn in deviceSerialNumber:
                    cursor.execute('''
                        UPDATE device_identifiers 
                        SET is_used = 1, used_at = ? 
                        WHERE serial_number = ?
                    ''', (datetime.now(), sn))
                
                conn.commit()
                self.logger.info(f"标记 {len(deviceSerialNumber)} 个设备标识符为已使用")
        except Exception as e:
            self.logger.error(f"标记设备标识符为已使用失败: {e}")
            raise
    
    def count_all(self) -> int:
        """
        获取数据库中的设备总数
        
        Returns:
            int: 设备总数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM device_identifiers')
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            self.logger.error(f"获取设备总数失败: {e}")
            raise
    
    def count_unused(self) -> int:
        """
        获取未使用的设备数量
        
        Returns:
            int: 未使用的设备数量
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM device_identifiers WHERE is_used = 0')
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            self.logger.error(f"获取未使用设备数量失败: {e}")
            raise
    
    def count_used(self) -> int:
        """
        获取已使用的设备数量
        
        Returns:
            int: 已使用的设备数量
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM device_identifiers WHERE is_used = 1')
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            self.logger.error(f"获取已使用设备数量失败: {e}")
            raise
    
    def delete_old_devices(self, days: int) -> int:
        """
        删除指定天数前的旧设备数据
        
        Args:
            days: 保留天数
            
        Returns:
            int: 删除的设备数量
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM device_identifiers 
                    WHERE created_at < ?
                ''', (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"删除了 {deleted_count} 个 {days} 天前的旧设备数据")
                return deleted_count
        except Exception as e:
            self.logger.error(f"删除旧设备数据失败: {e}")
            raise
    
    def get_statistics(self) -> dict:
        """
        获取设备标识符统计信息
        
        Returns:
            dict: 统计信息
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总数量
                cursor.execute('SELECT COUNT(*) FROM device_identifiers')
                total_count = cursor.fetchone()[0]
                
                # 未使用数量
                cursor.execute('SELECT COUNT(*) FROM device_identifiers WHERE is_used = 0')
                unused_count = cursor.fetchone()[0]
                
                # 已使用数量
                cursor.execute('SELECT COUNT(*) FROM device_identifiers WHERE is_used = 1')
                used_count = cursor.fetchone()[0]
                
                # 最早创建时间
                cursor.execute('SELECT MIN(created_at) FROM device_identifiers')
                earliest_created = cursor.fetchone()[0]
                
                # 最晚创建时间
                cursor.execute('SELECT MAX(created_at) FROM device_identifiers')
                latest_created = cursor.fetchone()[0]
                
                # 最早使用时间
                cursor.execute('SELECT MIN(used_at) FROM device_identifiers WHERE is_used = 1')
                earliest_used = cursor.fetchone()[0]
                
                # 最晚使用时间
                cursor.execute('SELECT MAX(used_at) FROM device_identifiers WHERE is_used = 1')
                latest_used = cursor.fetchone()[0]
                
                stats = {
                    'total_count': total_count,
                    'unused_count': unused_count,
                    'used_count': used_count,
                    'usage_rate': (used_count / total_count * 100) if total_count > 0 else 0,
                    'earliest_created': earliest_created,
                    'latest_created': latest_created,
                    'earliest_used': earliest_used,
                    'latest_used': latest_used
                }
                
                return stats
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            raise
    
    def reset_usage_status(self) -> int:
        """
        重置所有设备的使用状态（用于测试）
        
        Returns:
            int: 重置的设备数量
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE device_identifiers 
                    SET is_used = 0, used_at = NULL
                ''')
                
                reset_count = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"重置了 {reset_count} 个设备的使用状态")
                return reset_count
        except Exception as e:
            self.logger.error(f"重置使用状态失败: {e}")
            raise 