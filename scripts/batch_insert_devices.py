#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量插入设备数据脚本
从CSV文件读取设备数据并批量插入数据库，用于性能测试数据准备
"""

import sys
import os
import time
import csv
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.db_query.db_client import DBClient
from src.config.config_manager import ConfigManager

class BatchDeviceInserter:
    """批量设备数据插入器"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.config = ConfigManager()
        db_config = self.config.get_database_config()
        
        self.db_client = DBClient(
            host=db_config.get('mysql', {}).get('host', 'localhost'),
            port=db_config.get('mysql', {}).get('port', 3306),
            user=db_config.get('mysql', {}).get('user', 'root'),
            password=db_config.get('mysql', {}).get('password', ''),
            database=db_config.get('mysql', {}).get('database', '')
        )

    def read_csv_devices(self, csv_file_path, limit=None):
        """从CSV文件读取设备数据"""
        print(f"📖 正在读取CSV文件: {csv_file_path}")
        
        devices = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    if limit and i >= limit:
                        break
                    
                    # 处理时间字段
                    if row.get('create_time'):
                        try:
                            row['create_time'] = datetime.strptime(row['create_time'], '%Y-%m-%d %H:%M:%S')
                        except:
                            row['create_time'] = datetime.now()
                    
                    if row.get('update_time'):
                        try:
                            row['update_time'] = datetime.strptime(row['update_time'], '%Y-%m-%d %H:%M:%S')
                        except:
                            row['update_time'] = datetime.now()
                    
                    if row.get('last_heartbeat_time') and row['last_heartbeat_time'].strip():
                        try:
                            row['last_heartbeat_time'] = datetime.strptime(row['last_heartbeat_time'], '%Y-%m-%d %H:%M:%S')
                        except:
                            row['last_heartbeat_time'] = None
                    else:
                        row['last_heartbeat_time'] = None
                    
                    if row.get('last_login_time') and row['last_login_time'].strip():
                        try:
                            row['last_login_time'] = datetime.strptime(row['last_login_time'], '%Y-%m-%d %H:%M:%S')
                        except:
                            row['last_login_time'] = None
                    else:
                        row['last_login_time'] = None
                    
                    if row.get('offline_time') and row['offline_time'].strip():
                        try:
                            row['offline_time'] = datetime.strptime(row['offline_time'], '%Y-%m-%d %H:%M:%S')
                        except:
                            row['offline_time'] = None
                    else:
                        row['offline_time'] = None
                    
                    if row.get('image_backup_time') and row['image_backup_time'].strip():
                        try:
                            row['image_backup_time'] = datetime.strptime(row['image_backup_time'], '%Y-%m-%d %H:%M:%S')
                        except:
                            row['image_backup_time'] = None
                    else:
                        row['image_backup_time'] = None
                    
                    devices.append(row)
                    
                    if i % 10000 == 0 and i > 0:
                        print(f"   📊 已读取: {i} 条记录")
            
            print(f"✅ CSV文件读取完成，共 {len(devices)} 条记录")
            return devices
            
        except Exception as e:
            print(f"❌ 读取CSV文件失败: {e}")
            return []

    def insert_devices_batch(self, devices_data, batch_size=1000):
        """批量插入设备数据"""
        if not devices_data:
            print("❌ 没有设备数据需要插入")
            return 0
        
        print(f"🚀 开始批量插入设备数据...")
        print(f"📊 目标数量: {len(devices_data)}台")
        print(f"📦 批次大小: {batch_size}")
        print("=" * 60)
        
        total_inserted = 0
        start_time = time.time()
        
        for batch_start in range(0, len(devices_data), batch_size):
            batch_end = min(batch_start + batch_size, len(devices_data))
            batch_data = devices_data[batch_start:batch_end]
            
            print(f"📦 处理批次 {batch_start//batch_size + 1}/{(len(devices_data) + batch_size - 1)//batch_size}")
            print(f"   📈 进度: {batch_start}/{len(devices_data)} ({batch_start/len(devices_data)*100:.1f}%)")
            
            # 执行批量插入
            if batch_data:
                inserted_count = self._insert_batch(batch_data)
                total_inserted += inserted_count
                
                # 显示进度
                elapsed_time = time.time() - start_time
                avg_time_per_device = elapsed_time / total_inserted if total_inserted > 0 else 0
                remaining_devices = len(devices_data) - total_inserted
                estimated_remaining_time = remaining_devices * avg_time_per_device
                
                print(f"   ✅ 已插入: {total_inserted}/{len(devices_data)}")
                print(f"   ⏱️  耗时: {elapsed_time:.1f}秒")
                print(f"   🎯 预计剩余时间: {estimated_remaining_time:.1f}秒")
                print(f"   📊 平均速度: {total_inserted/elapsed_time:.1f}台/秒")
                print("-" * 40)
        
        total_time = time.time() - start_time
        print("=" * 60)
        print(f"🎉 批量插入完成!")
        print(f"📊 总计插入: {total_inserted}台设备")
        print(f"⏱️  总耗时: {total_time:.1f}秒")
        print(f"🚀 平均速度: {total_inserted/total_time:.1f}台/秒")
        
        return total_inserted

    def _insert_batch(self, devices_data):
        """执行批量插入"""
        if not devices_data:
            return 0
        
        # 构建INSERT语句
        fields = list(devices_data[0].keys())
        placeholders = ', '.join(['%s'] * len(fields))
        field_names = ', '.join(fields)
        
        sql = f"""
        INSERT INTO biz_device ({field_names}) 
        VALUES ({placeholders})
        """
        
        # 准备数据
        values = []
        for device in devices_data:
            row_values = []
            for field in fields:
                value = device[field]
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif value is None:
                    value = None
                row_values.append(value)
            values.append(row_values)
        
        # 执行批量插入
        try:
            # 由于DBClient没有execute_many方法，我们逐条插入
            success_count = 0
            for device_values in values:
                try:
                    self._insert_single(fields, device_values)
                    success_count += 1
                except Exception as single_e:
                    print(f"❌ 单条插入失败: {single_e}")
                    continue
            return success_count
        except Exception as e:
            print(f"❌ 批量插入失败: {e}")
            return 0

    def _insert_single(self, fields, values):
        """插入单条设备数据"""
        placeholders = ', '.join(['%s'] * len(fields))
        field_names = ', '.join(fields)
        
        sql = f"""
        INSERT INTO biz_device ({field_names}) 
        VALUES ({placeholders})
        """
        
        return self.db_client.execute(sql, values)

    def get_current_device_count(self):
        """获取当前数据库中的设备数量"""
        sql = "SELECT COUNT(*) FROM biz_device"
        result = self.db_client.query(sql, [])
        if result and len(result) > 0:
            return result[0][0] if isinstance(result[0], (list, tuple)) else result[0]
        return 0

    def close(self):
        """关闭数据库连接"""
        if self.db_client:
            self.db_client.close()

def main():
    """主函数"""
    print("🔧 批量设备数据插入工具")
    print("=" * 60)
    
    # 解析命令行参数
    csv_file = "src/tools/jmeter/bin/new_devices_100000.csv"  # 默认CSV文件
    target_count = 90000  # 目标设备数量
    batch_size = 1000     # 批次大小
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            target_count = int(sys.argv[2])
        except ValueError:
            print("❌ 无效的设备数量参数")
            return
    
    if len(sys.argv) > 3:
        try:
            batch_size = int(sys.argv[3])
        except ValueError:
            print("❌ 无效的批次大小参数")
            return
    
    # 检查CSV文件是否存在
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件不存在: {csv_file}")
        return
    
    inserter = BatchDeviceInserter()
    
    try:
        # 获取当前设备数量
        current_count = inserter.get_current_device_count()
        print(f"📊 当前数据库设备数量: {current_count}")
        
        # 计算需要插入的数量
        need_insert = max(0, target_count - current_count)
        
        if need_insert == 0:
            print("✅ 数据库设备数量已达到目标，无需插入")
            return
        
        print(f"🎯 需要插入设备数量: {need_insert}")
        
        # 读取CSV数据
        devices_data = inserter.read_csv_devices(csv_file, limit=need_insert)
        
        if not devices_data:
            print("❌ 无法读取设备数据")
            return
        
        # 开始插入
        inserted_count = inserter.insert_devices_batch(devices_data, batch_size)
        
        # 验证结果
        final_count = inserter.get_current_device_count()
        print(f"📊 插入后数据库设备数量: {final_count}")
        
        if final_count >= target_count:
            print("🎉 目标达成！数据库设备数量已满足要求")
        else:
            print(f"⚠️  目标未完全达成，还需要 {target_count - final_count} 台设备")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        inserter.close()

if __name__ == "__main__":
    main() 