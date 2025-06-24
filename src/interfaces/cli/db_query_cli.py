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

from src.application.services.device_query_service import DeviceQueryService

class DateTimeEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime对象"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def export_to_csv(devices, filename=None):
    """导出设备信息到CSV文件"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"device_info_{timestamp}.csv"
    
    # 确保输出目录存在
    output_dir = "data/device_samples"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
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

def export_to_json(devices, filename=None):
    """导出设备信息到JSON文件"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"device_info_{timestamp}.json"
    
    # 确保输出目录存在
    output_dir = "data/device_samples"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
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
        json.dump(device_list, jsonfile, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
    
    print(f"设备信息已导出到: {filepath}")
    return filepath

def auto_discover_databases(host, port, user, password):
    """自动发现数据库"""
    print("正在自动发现数据库...")
    
    # 先连接MySQL服务器（不指定数据库）
    temp_config = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': ''  # 不指定数据库
    }
    
    try:
        service = DeviceQueryService(temp_config)
        databases = service.discover_databases()
        service.close()
        
        if databases:
            print(f"发现 {len(databases)} 个数据库:")
            for i, db in enumerate(databases, 1):
                print(f"  {i}. {db}")
            
            # 查找可能包含设备信息的数据库
            device_dbs = []
            for db in databases:
                if any(keyword in db.lower() for keyword in ['device', 'terminal', 'protector', 'asset', 'business']):
                    device_dbs.append(db)
            
            if device_dbs:
                print(f"\n可能包含设备信息的数据库: {device_dbs}")
                return device_dbs[0]  # 返回第一个匹配的数据库
            else:
                print("未发现明显的设备信息数据库，使用第一个数据库")
                return databases[0]
        else:
            print("未发现任何数据库")
            return None
            
    except Exception as e:
        print(f"数据库发现失败: {e}")
        return None

def auto_discover_tables(host, port, user, password, database):
    """自动发现表"""
    print(f"正在发现数据库 {database} 中的表...")
    
    config = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }
    
    try:
        service = DeviceQueryService(config)
        tables = service.discover_tables()
        service.close()
        
        if tables:
            print(f"发现 {len(tables)} 个表:")
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table}")
            
            # 查找可能包含设备信息的表
            device_tables = []
            for table in tables:
                if any(keyword in table.lower() for keyword in ['device', 'terminal', 'register', 'info', 'asset']):
                    device_tables.append(table)
            
            if device_tables:
                print(f"\n可能包含设备信息的表: {device_tables}")
                return device_tables[0]  # 返回第一个匹配的表
            else:
                print("未发现明显的设备信息表，使用第一个表")
                return tables[0]
        else:
            print("未发现任何表")
            return None
            
    except Exception as e:
        print(f"表发现失败: {e}")
        return None

def export_actual_used_devices(
    host='192.168.24.45', port=3307, user='root', password='At6mj*1ygb2', 
    database='yangguan', table='biz_device', limit=None, 
    output_path='data/actual_used_devices.json'
):
    """
    查询数据库注册设备并导出actual_used_devices.json，结构符合开发计划要求。
    """
    db_config = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }
    service = DeviceQueryService(db_config)
    try:
        # 如果limit为None，先获取总记录数，然后查询所有记录
        if limit is None:
            total_count = service.get_device_count(table_name=table)
            print(f"[db_query_cli] 数据库中共有 {total_count} 条设备记录，开始同步所有记录...")
            # 设置一个很大的数值来获取所有记录
            limit = total_count
        
        devices = service.get_devices(table_name=table, limit=limit)
        if not devices:
            print("[db_query_cli] 未查到任何设备，未写入actual_used_devices.json")
            return False
        
        deviceSerialNumbers = set()
        mac = set()  # 单个设备的MAC地址
        macs = set()  # 多个MAC地址列表
        device_ids = set()
        
        for device in devices:
            if hasattr(device, 'deviceSerialNumber') and device.deviceSerialNumber:
                deviceSerialNumbers.add(device.deviceSerialNumber)
            if hasattr(device, 'mac') and device.mac:
                mac.add(device.mac)
            if hasattr(device, 'macs') and device.macs:
                macs.add(device.macs)
            if hasattr(device, 'device_id') and device.device_id:
                device_ids.add(device.device_id)
        
        result = {
            "actual_registrations": {
                "deviceSerialNumbers": list(deviceSerialNumbers),
                "mac": list(mac),
                "macs": list(macs),  # 多个MAC地址列表
                "device_ids": list(device_ids)
            },
            "verification_results": {
                "theoretical_count": 0,
                "actual_count": len(deviceSerialNumbers),
                "missing_devices": [],
                "success_rate": 0.0
            },
            "last_verification_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "verification_history": []
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"[db_query_cli] 已同步 {len(deviceSerialNumbers)} 台设备到 {output_path}")
        return True
        
    except Exception as e:
        print(f"[db_query_cli] 同步失败: {e}")
        return False
    finally:
        service.close()

def main():
    parser = argparse.ArgumentParser(description='数据库查询工具')
    parser.add_argument('--host', default='192.168.24.45', help='数据库主机地址')
    parser.add_argument('--port', type=int, default=3307, help='数据库端口')
    parser.add_argument('--user', default='root', help='数据库用户名')
    parser.add_argument('--password', default='At6mj*1ygb2', help='数据库密码')
    parser.add_argument('--database', help='数据库名称（留空则自动发现）')
    parser.add_argument('--limit', type=int, default=10, help='查询数量')
    parser.add_argument('--table', help='查询的表名（留空则自动发现）')
    parser.add_argument('--export-csv', action='store_true', help='导出为CSV文件')
    parser.add_argument('--export-json', action='store_true', help='导出为JSON文件')
    parser.add_argument('--output-file', help='输出文件名（不含扩展名）')
    parser.add_argument('--analyze-schema', action='store_true', help='分析表结构')
    parser.add_argument('--filter', help='筛选条件，格式：字段名=值')
    parser.add_argument('--fields', help='指定查询字段，用逗号分隔')
    parser.add_argument('--auto-discover', action='store_true', help='自动发现数据库和表')
    parser.add_argument('--delete', action='store_true', help='删除符合条件的设备')
    parser.add_argument('--delete-count', type=int, help='删除数量限制')
    parser.add_argument('--confirm', action='store_true', help='确认删除操作（必须指定此参数才会执行删除）')
    args = parser.parse_args()

    # 自动发现数据库和表
    if args.auto_discover or not args.database:
        print("=== 自动发现模式 ===")
        database = auto_discover_databases(args.host, args.port, args.user, args.password)
        if not database:
            print("无法发现数据库，请手动指定 --database 参数")
            return
        
        if not args.table:
            table = auto_discover_tables(args.host, args.port, args.user, args.password, database)
            if not table:
                print("无法发现表，请手动指定 --table 参数")
                return
        else:
            table = args.table
    else:
        database = args.database
        table = args.table or 'biz_device'  # 默认表名

    print(f"\n=== 使用配置 ===")
    print(f"数据库: {database}")
    print(f"表: {table}")
    print(f"主机: {args.host}:{args.port}")
    print(f"用户: {args.user}")

    db_config = {
        'host': args.host,
        'port': args.port,
        'user': args.user,
        'password': args.password,
        'database': database
    }
    
    service = DeviceQueryService(db_config)
    try:
        # 删除操作
        if args.delete:
            if not args.confirm:
                print("⚠️  警告：删除操作不可恢复！")
                print("请使用 --confirm 参数确认删除操作")
                return
            
            print(f"\n=== 删除操作 ===")
            print(f"筛选条件: {args.filter or '无'}")
            print(f"删除限制: {args.delete_count or '无限制'}")
            
            # 先查询要删除的设备数量
            count = service.get_device_count(table_name=table, filter_condition=args.filter)
            print(f"符合条件的设备总数: {count}")
            
            if count == 0:
                print("没有找到符合条件的设备")
                return
            
            # 执行删除
            deleted_count = service.delete_devices(
                table_name=table,
                filter_condition=args.filter,
                limit=args.delete_count
            )
            
            print(f"成功删除 {deleted_count} 台设备")
            return
        
        # 分析表结构
        if args.analyze_schema:
            print(f"\n=== 表结构分析 ===")
            print(f"表名: {table}")
            schema_info = service.analyze_table_schema(table)
            print(json.dumps(schema_info, ensure_ascii=False, indent=2))
            return
        
        # 查询设备信息
        print(f"\n正在查询表 {table} 的设备信息...")
        devices = service.get_devices(
            table_name=table,
            limit=args.limit,
            filter_condition=args.filter,
            fields=args.fields
        )
        
        if not devices:
            print("未找到设备信息")
            return
        
        print(f"找到 {len(devices)} 条设备信息:")
        print("-" * 80)
        
        # 显示设备信息
        for i, device in enumerate(devices, 1):
            print(f"设备 {i}:")
            for key, value in device.__dict__.items():
                print(f"  {key}: {value}")
            print()
        
        # 导出功能
        if args.export_csv:
            export_to_csv(devices, f"{args.output_file}.csv" if args.output_file else None)
        
        if args.export_json:
            export_to_json(devices, f"{args.output_file}.json" if args.output_file else None)
        
        # 统计信息
        print("=== 统计信息 ===")
        print(f"总设备数: {len(devices)}")
        
        # 品牌统计
        brands = {}
        for device in devices:
            brand = device.brand or '未知'
            brands[brand] = brands.get(brand, 0) + 1
        
        print("品牌分布:")
        for brand, count in brands.items():
            print(f"  {brand}: {count}台")
        
    except Exception as e:
        print(f"操作失败: {e}")
    finally:
        service.close()

if __name__ == '__main__':
    main() 