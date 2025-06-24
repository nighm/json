#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册测试CLI工具
集成设备生成、API发送、数据库验证等功能的完整注册测试流程
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 设置项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from src.application.services.device_data_manager import DeviceDataManager
from src.application.services.api_send_service import APISendService
from src.application.services.register_verification_service import RegisterVerificationService
from src.application.services.device_query_service import DeviceQueryService

def export_register_results_to_csv(results, filename=None):
    """导出注册结果到CSV文件"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"register_results_{timestamp}.csv"
    
    # 确保输出目录存在
    output_dir = "data/register_results"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if results:
            # 定义字段名
            fieldnames = [
                'request_index', 'device_id', 'device_name', 'success', 
                'status_code', 'response_code', 'response_message', 'error'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # 只写入需要的字段
                row = {
                    'request_index': result.get('request_index', ''),
                    'device_id': result.get('device_id', ''),
                    'device_name': result.get('device_name', ''),
                    'success': result.get('success', False),
                    'status_code': result.get('status_code', ''),
                    'response_code': result.get('response_code', ''),
                    'response_message': result.get('response_message', ''),
                    'error': result.get('error', '')
                }
                writer.writerow(row)
    
    print(f"注册结果已导出到: {filepath}")
    return filepath

def export_verification_report_to_json(report, filename=None):
    """导出验证报告到JSON文件"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"verification_report_{timestamp}.json"
    
    # 确保输出目录存在
    output_dir = "data/register_results"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(report, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"验证报告已导出到: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='设备注册测试工具')
    parser.add_argument('--count', type=int, default=10, help='注册设备数量')
    parser.add_argument('--server-url', default='http://192.168.24.45:8080', help='服务器URL')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间（秒）')
    parser.add_argument('--db-host', default='192.168.24.45', help='数据库主机地址')
    parser.add_argument('--db-port', type=int, default=3307, help='数据库端口')
    parser.add_argument('--db-user', default='root', help='数据库用户名')
    parser.add_argument('--db-password', default='At6mj*1ygb2', help='数据库密码')
    parser.add_argument('--db-name', help='数据库名称（留空则自动发现）')
    parser.add_argument('--export-csv', action='store_true', help='导出注册结果为CSV文件')
    parser.add_argument('--export-json', action='store_true', help='导出验证报告为JSON文件')
    parser.add_argument('--output-file', help='输出文件名（不含扩展名）')
    parser.add_argument('--skip-verification', action='store_true', help='跳过数据库验证')
    parser.add_argument('--test-connection', action='store_true', help='仅测试服务器连接')
    args = parser.parse_args()

    print("=== 设备注册测试工具 ===")
    print(f"服务器URL: {args.server_url}")
    print(f"注册数量: {args.count}")
    print(f"超时时间: {args.timeout}秒")
    
    # 初始化API发送服务
    api_service = APISendService(base_url=args.server_url, timeout=args.timeout)
    
    # 测试连接
    if args.test_connection:
        print("\n正在测试服务器连接...")
        if api_service.test_connection():
            print("✅ 服务器连接成功")
        else:
            print("❌ 服务器连接失败")
        api_service.close()
        return
    
    # 测试连接
    print("\n正在测试服务器连接...")
    if not api_service.test_connection():
        print("❌ 服务器连接失败，请检查服务器URL和网络连接")
        api_service.close()
        return
    print("✅ 服务器连接成功")
    
    # 初始化设备数据管理器
    print("\n正在初始化设备数据管理器...")
    device_manager = DeviceDataManager()
    
    # 获取可用设备数据
    print(f"\n正在获取 {args.count} 台可用设备数据...")
    device_data_file = device_manager.get_available_devices(args.count)
    
    # 从文件加载设备信息
    from src.domain.entities.device_info import DeviceInfo
    devices = []
    
    try:
        with open(device_data_file, 'r', encoding='utf-8') as f:
            if device_data_file.endswith('.csv'):
                import csv
                reader = csv.DictReader(f)
                for row in reader:
                    # 将CSV行转换为DeviceInfo对象
                    device = DeviceInfo()
                    for key, value in row.items():
                        if hasattr(device, key):
                            setattr(device, key, value)
                    devices.append(device)
            else:
                # JSON格式
                device_list = json.load(f)
                for device_dict in device_list:
                    device = DeviceInfo(**device_dict)
                    devices.append(device)
    except Exception as e:
        print(f"❌ 加载设备数据失败: {e}")
        api_service.close()
        return
    
    print(f"✅ 成功加载 {len(devices)} 台设备数据")
    
    # 显示设备信息摘要
    print("\n=== 设备信息摘要 ===")
    for i, device in enumerate(devices[:5], 1):  # 只显示前5台
        print(f"设备 {i}: {device.device_name} ({device.device_id})")
    if len(devices) > 5:
        print(f"... 还有 {len(devices) - 5} 台设备")
    
    # 开始注册测试
    print(f"\n=== 开始注册测试 ===")
    print(f"正在发送 {len(devices)} 个注册请求...")
    
    register_results = api_service.send_batch_register_requests(devices)
    
    # 统计结果
    success_count = sum(1 for result in register_results if result.get('success', False))
    total_count = len(register_results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n=== 注册测试结果 ===")
    print(f"总请求数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_rate:.2f}%")
    
    # 显示详细结果
    print("\n=== 详细结果 ===")
    for result in register_results[:10]:  # 只显示前10个结果
        status = "✅" if result.get('success', False) else "❌"
        print(f"{status} {result.get('device_name', 'Unknown')}: {result.get('response_message', 'No message')}")
    
    if len(register_results) > 10:
        print(f"... 还有 {len(register_results) - 10} 个结果")
    
    # 数据库验证
    if not args.skip_verification:
        print(f"\n=== 数据库验证 ===")
        
        # 构建数据库配置
        db_config = {
            'host': args.db_host,
            'port': args.db_port,
            'user': args.db_user,
            'password': args.db_password,
            'database': args.db_name or 'protector'  # 默认数据库名
        }
        
        # 初始化验证服务
        verification_service = RegisterVerificationService(db_config)
        
        # 提取成功注册的设备ID
        successful_device_ids = [
            result['device_id'] for result in register_results 
            if result.get('success', False)
        ]
        
        print(f"正在验证 {len(successful_device_ids)} 台成功注册的设备...")
        
        # 执行双重验证
        test_id = f"register_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        verification_report = verification_service.verify_registration_results(
            register_results, test_id
        )
        
        # 显示验证结果
        print(f"\n=== 验证结果 ===")
        print(f"理论成功注册: {len(successful_device_ids)} 台")
        print(f"实际数据库验证: {len(verification_report.get('actual_registrations', []))} 台")
        
        if successful_device_ids:
            actual_success_rate = len(verification_report.get('actual_registrations', [])) / len(successful_device_ids) * 100
            print(f"数据库验证成功率: {actual_success_rate:.2f}%")
        
        # 显示差异分析
        differences = verification_report.get('differences', {})
        if differences.get('missing_in_database'):
            print(f"❌ 数据库中缺失: {len(differences['missing_in_database'])} 台")
        if differences.get('unexpected_in_database'):
            print(f"⚠️ 数据库中意外存在: {len(differences['unexpected_in_database'])} 台")
    
    # 导出结果
    if args.export_csv:
        csv_file = export_register_results_to_csv(
            register_results, 
            f"{args.output_file}.csv" if args.output_file else None
        )
    
    if args.export_json and not args.skip_verification:
        json_file = export_verification_report_to_json(
            verification_report, 
            f"{args.output_file}.json" if args.output_file else None
        )
    
    # 清理资源
    api_service.close()
    
    print(f"\n=== 测试完成 ===")
    print(f"注册成功率: {success_rate:.2f}%")
    if not args.skip_verification:
        print(f"数据库验证成功率: {actual_success_rate:.2f}%")
    print("测试完成！")

if __name__ == '__main__':
    main() 