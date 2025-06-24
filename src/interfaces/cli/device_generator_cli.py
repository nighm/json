import argparse
import csv
import json
import os
import sys
from datetime import datetime

# 设置项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from src.application.services.device_generator_service import DeviceGeneratorService
from src.application.services.device_query_service import DeviceQueryService

def export_devices_to_csv(devices, output_path=None):
    """导出设备信息到CSV文件"""
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_devices_{timestamp}.csv"
        # 默认输出目录
        output_dir = "data/generated_devices"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = output_path
        # 从提供的路径中提取目录并确保它存在
        output_dir = os.path.dirname(filepath)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if devices:
            # 获取字段名
            fieldnames = list(devices[0].__dict__.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for device in devices:
                writer.writerow(device.__dict__)
    
    print(f"设备信息已导出到: {filepath}")
    return filepath

def export_devices_to_json(devices, output_path=None):
    """导出设备信息到JSON文件"""
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_devices_{timestamp}.json"
        # 默认输出目录
        output_dir = "data/generated_devices"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = output_path
        # 从提供的路径中提取目录并确保它存在
        output_dir = os.path.dirname(filepath)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    
    # 转换为字典列表
    device_list = []
    for device in devices:
        device_dict = device.__dict__.copy()
        # 处理None值，转换为空字符串
        for key, value in device_dict.items():
            if value is None:
                device_dict[key] = ""
        device_list.append(device_dict)
    
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(device_list, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"设备信息已导出到: {filepath}")
    return filepath

def load_sample_devices_from_db(host='192.168.24.45', port=3307, user='root', password='At6mj*1ygb2', limit=10):
    """从数据库加载样本设备信息"""
    print("正在从数据库加载样本设备信息...")
    
    try:
        # 自动发现数据库和表
        temp_config = {'host': host, 'port': port, 'user': user, 'password': password, 'database': ''}
        service = DeviceQueryService(temp_config)
        databases = service.discover_databases()
        service.close()
        
        if not databases:
            print("未发现数据库")
            return []
        
        database = databases[0]  # 使用第一个数据库
        config = {'host': host, 'port': port, 'user': user, 'password': password, 'database': database}
        service = DeviceQueryService(config)
        
        # 查询设备信息
        devices = service.get_devices(table_name='biz_device', limit=limit)
        service.close()
        
        print(f"成功加载 {len(devices)} 条样本设备信息")
        return devices
        
    except Exception as e:
        print(f"加载样本设备信息失败: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='设备信息批量生成工具 - 简化版')
    parser.add_argument('--count', type=int, default=10, help='生成设备数量')
    parser.add_argument('--use-sample', action='store_true', help='使用数据库样本生成设备')
    parser.add_argument('--sample-limit', type=int, default=5, help='加载样本数量')
    parser.add_argument('--export-csv', action='store_true', help='导出为CSV文件')
    parser.add_argument('--export-json', action='store_true', help='导出为JSON文件')
    parser.add_argument('--output-file', help='输出文件名（不含扩展名）')
    parser.add_argument('--reset-unique', action='store_true', help='重置唯一性跟踪')
    args = parser.parse_args()

    # 创建设备生成器
    generator = DeviceGeneratorService()
    
    # 重置唯一性跟踪
    if args.reset_unique:
        generator.reset_unique_tracking()
        print("已重置唯一性跟踪")

    # 生成设备信息
    print(f"正在生成 {args.count} 台设备信息...")
    
    if args.use_sample:
        # 使用数据库样本生成
        sample_devices = load_sample_devices_from_db(limit=args.sample_limit)
        if sample_devices:
            devices = generator.generate_devices_from_sample(args.count, sample_devices)
        else:
            print("无法加载样本，使用默认模板生成")
            devices = generator.generate_devices(args.count)
    else:
        # 使用默认模板生成
        devices = generator.generate_devices(args.count)

    if not devices:
        print("未生成任何设备信息")
        return

    print(f"成功生成 {len(devices)} 台设备信息:")
    print("-" * 80)
    
    # 显示生成的设备信息
    for i, device in enumerate(devices[:5], 1):  # 只显示前5台
        print(f"设备 {i}:")
        print(f"  设备ID: '{device.device_id}' (必须为空)")
        print(f"  序列号: {device.device_serial_number}")
        print(f"  设备名称: '{device.device_name}'")
        print(f"  IP地址: {device.ip}")
        print(f"  MAC地址: {device.mac}")
        print(f"  品牌: {device.brand}")
        print(f"  型号: {device.model}")
        print()
    
    if len(devices) > 5:
        print(f"... 还有 {len(devices) - 5} 台设备")

    # 导出功能
    # 如果指定了输出文件但未指定格式，则默认为CSV
    if args.output_file and not (args.export_csv or args.export_json):
        args.export_csv = True

    if args.export_csv:
        export_devices_to_csv(devices, args.output_file)
    
    if args.export_json:
        export_devices_to_json(devices, args.output_file)

    # 统计信息
    print("=== 生成统计 ===")
    print(f"总设备数: {len(devices)}")
    
    # 唯一性验证
    sns = [d.device_serial_number for d in devices]
    macs = [d.mac for d in devices]
    device_ids = [d.device_id for d in devices]
    
    print(f"\n唯一性验证:")
    print(f"  设备ID为空: {'✅' if all(did == '' for did in device_ids) else '❌'}")
    print(f"  SN号唯一性: {'✅' if len(sns) == len(set(sns)) else '❌'}")
    print(f"  MAC地址唯一性: {'✅' if len(macs) == len(set(macs)) else '❌'}")
    
    # 显示唯一性统计
    stats = generator.get_unique_stats()
    print(f"\n唯一性统计:")
    print(f"  已使用SN号: {stats['used_sns_count']}")
    print(f"  已使用MAC: {stats['used_macs_count']}")
    print(f"  SN计数器: {stats['sn_counter']}")
    print(f"  MAC计数器: {stats['mac_counter']}")

if __name__ == '__main__':
    main() 