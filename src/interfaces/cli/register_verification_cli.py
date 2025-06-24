#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register接口验证CLI
- 验证register接口测试结果是否真实写入了数据库
- 对比测试数据和数据库记录
"""
import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 设置项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from src.application.services.device_query_service import DeviceQueryService
from src.config.config_manager import config_manager

def load_test_data(csv_file_path):
    """加载测试数据文件"""
    if not os.path.exists(csv_file_path):
        print(f"测试数据文件不存在: {csv_file_path}")
        return None
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def verify_register_results(test_data_file, db_config, table_name='biz_device'):
    """验证register接口测试结果"""
    print("=== Register接口验证报告 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试数据文件: {test_data_file}")
    print(f"数据库表: {table_name}")
    print("-" * 60)
    
    # 加载测试数据
    test_data = load_test_data(test_data_file)
    if not test_data:
        return False
    
    print(f"测试设备数量: {len(test_data)}")
    
    # 连接数据库
    try:
        service = DeviceQueryService(db_config)
        
        # 验证每个测试设备
        success_count = 0
        fail_count = 0
        
        for i, device in enumerate(test_data, 1):
            print(f"\n设备 {i}:")
            print(f"  设备ID: {device.get('device_id', 'N/A')}")
            print(f"  序列号: {device.get('device_serial_number', 'N/A')}")
            print(f"  设备名称: {device.get('device_name', 'N/A')}")
            print(f"  MAC地址: {device.get('mac', 'N/A')}")
            
            # 构建查询条件
            filter_conditions = []
            if device.get('device_id'):
                filter_conditions.append(f"device_id='{device['device_id']}'")
            if device.get('device_serial_number'):
                filter_conditions.append(f"device_serial_number='{device['device_serial_number']}'")
            if device.get('mac'):
                filter_conditions.append(f"mac='{device['mac']}'")
            
            if not filter_conditions:
                print("  ❌ 无法构建查询条件（缺少关键字段）")
                fail_count += 1
                continue
            
            # 查询数据库
            filter_str = " OR ".join(filter_conditions)
            db_devices = service.get_devices(
                table_name=table_name,
                filter_condition=filter_str,
                limit=1
            )
            
            if db_devices:
                db_device = db_devices[0]
                print(f"  ✅ 数据库中找到匹配记录")
                print(f"    数据库ID: {db_device.id}")
                print(f"    更新时间: {db_device.update_time}")
                print(f"    状态: {db_device.status}")
                success_count += 1
            else:
                print(f"  ❌ 数据库中未找到匹配记录")
                fail_count += 1
        
        # 查询最近注册的设备
        print(f"\n=== 最近注册的设备统计 ===")
        recent_time = datetime.now() - timedelta(hours=1)
        recent_devices = service.get_devices(
            table_name=table_name,
            filter_condition=f"update_time >= '{recent_time.strftime('%Y-%m-%d %H:%M:%S')}'",
            limit=10
        )
        
        if recent_devices:
            print(f"最近1小时内注册的设备数量: {len(recent_devices)}")
            for device in recent_devices:
                print(f"  - {device.device_name or 'N/A'} (ID: {device.device_id}, 时间: {device.update_time})")
        else:
            print("最近1小时内没有新注册的设备")
        
        # 统计结果
        print(f"\n=== 验证结果统计 ===")
        print(f"成功验证: {success_count} 台")
        print(f"验证失败: {fail_count} 台")
        print(f"成功率: {success_count/(success_count+fail_count)*100:.1f}%" if (success_count+fail_count) > 0 else "成功率: 0%")
        
        service.close()
        return success_count > 0
        
    except Exception as e:
        print(f"数据库验证失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Register接口验证工具')
    parser.add_argument('--test-data', required=True, help='测试数据CSV文件路径')
    parser.add_argument('--host', default='192.168.24.45', help='数据库主机地址')
    parser.add_argument('--port', type=int, default=3307, help='数据库端口')
    parser.add_argument('--user', default='root', help='数据库用户名')
    parser.add_argument('--password', default='At6mj*1ygb2', help='数据库密码')
    parser.add_argument('--database', default='yangguan', help='数据库名称')
    parser.add_argument('--table', default='biz_device', help='设备表名')
    args = parser.parse_args()
    
    db_config = {
        'host': args.host,
        'port': args.port,
        'user': args.user,
        'password': args.password,
        'database': args.database
    }
    
    success = verify_register_results(args.test_data, db_config, args.table)
    
    if success:
        print("\n✅ Register接口验证成功：测试数据已真实写入数据库")
        return 0
    else:
        print("\n❌ Register接口验证失败：测试数据未成功写入数据库")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 