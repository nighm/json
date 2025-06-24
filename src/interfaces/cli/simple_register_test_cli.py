#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版注册测试CLI工具
根据测试结果优化：SN号唯一、MAC唯一、deviceId为空、params.alone为true
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 设置项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from src.application.services.device_generator_service import DeviceGeneratorService
from src.application.services.api_send_service import APISendService

def export_register_results_to_csv(results, filename=None):
    """导出注册结果到CSV文件"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simple_register_results_{timestamp}.csv"
    
    # 确保输出目录存在
    output_dir = "data/register_results"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        if results:
            # 定义字段
            fieldnames = [
                'request_index', 'device_id', 'device_name', 'device_serial_number', 
                'mac', 'success', 'status_code', 'response_message', 'error'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'request_index': result.get('request_index', ''),
                    'device_id': result.get('device_id', ''),
                    'device_name': result.get('device_name', ''),
                    'device_serial_number': result.get('device_serial_number', ''),
                    'mac': result.get('mac', ''),
                    'success': result.get('success', False),
                    'status_code': result.get('status_code', ''),
                    'response_message': result.get('response_message', ''),
                    'error': result.get('error', '')
                })
    
    print(f"注册结果已导出到: {filepath}")
    return filepath

def export_register_results_to_json(results, filename=None):
    """导出注册结果到JSON文件"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simple_register_results_{timestamp}.json"
    
    # 确保输出目录存在
    output_dir = "data/register_results"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"注册结果已导出到: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='简化版设备注册测试工具')
    parser.add_argument('--count', type=int, default=10, help='注册设备数量')
    parser.add_argument('--server-url', default='http://192.168.24.45:8080', help='服务器URL')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间（秒）')
    parser.add_argument('--export-csv', action='store_true', help='导出注册结果为CSV文件')
    parser.add_argument('--export-json', action='store_true', help='导出验证报告为JSON文件')
    parser.add_argument('--output-file', help='输出文件名（不含扩展名）')
    parser.add_argument('--test-connection', action='store_true', help='仅测试服务器连接')
    parser.add_argument('--reset-unique', action='store_true', help='重置唯一性跟踪')
    args = parser.parse_args()

    print("=== 简化版设备注册测试工具 ===")
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
    
    # 初始化设备生成器
    print("\n正在初始化设备生成器...")
    generator = DeviceGeneratorService()
    
    # 重置唯一性跟踪
    if args.reset_unique:
        generator.reset_unique_tracking()
        print("已重置唯一性跟踪")
    
    # 生成设备数据
    print(f"\n正在生成 {args.count} 台设备数据...")
    devices = generator.generate_devices(args.count)
    
    if not devices:
        print("❌ 未生成任何设备数据")
        api_service.close()
        return
    
    print(f"✅ 成功生成 {len(devices)} 台设备数据")
    
    # 显示设备信息摘要
    print("\n=== 设备信息摘要 ===")
    for i, device in enumerate(devices[:3], 1):  # 只显示前3台
        print(f"设备 {i}:")
        print(f"  设备ID: '{device.device_id}' (必须为空)")
        print(f"  序列号: {device.device_serial_number}")
        print(f"  MAC地址: {device.mac}")
        print(f"  IP地址: {device.ip}")
        print()
    
    if len(devices) > 3:
        print(f"... 还有 {len(devices) - 3} 台设备")
    
    # 唯一性验证
    sns = [d.device_serial_number for d in devices]
    macs = [d.mac for d in devices]
    device_ids = [d.device_id for d in devices]
    
    print("=== 唯一性验证 ===")
    print(f"设备ID为空: {'✅' if all(did == '' for did in device_ids) else '❌'}")
    print(f"SN号唯一性: {'✅' if len(sns) == len(set(sns)) else '❌'}")
    print(f"MAC地址唯一性: {'✅' if len(macs) == len(set(macs)) else '❌'}")
    
    # 开始注册测试
    print(f"\n=== 开始注册测试 ===")
    print(f"正在发送 {len(devices)} 个注册请求...")
    
    start_time = time.time()
    register_results = api_service.send_batch_register_requests(devices)
    total_time = time.time() - start_time
    
    # 统计结果
    success_count = sum(1 for result in register_results if result.get('success', False))
    total_count = len(register_results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n=== 注册测试结果 ===")
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均每个请求: {total_time/total_count:.3f}秒")
    print(f"总请求数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_rate:.2f}%")
    
    # 显示详细结果
    print("\n=== 详细结果 ===")
    for result in register_results[:10]:  # 只显示前10个结果
        status = "✅" if result.get('success', False) else "❌"
        sn = result.get('device_serial_number', 'Unknown')
        mac = result.get('mac', 'Unknown')
        msg = result.get('response_message', 'No message')
        print(f"{status} SN:{sn} MAC:{mac} => {msg}")
    
    if len(register_results) > 10:
        print(f"... 还有 {len(register_results) - 10} 个结果")
    
    # 失败原因分析
    failed_results = [r for r in register_results if not r.get('success', False)]
    if failed_results:
        print(f"\n=== 失败原因分析 ===")
        error_counts = {}
        for result in failed_results:
            error = result.get('response_message', 'Unknown error')
            error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in error_counts.items():
            print(f"  {error}: {count}次")
    
    # 导出功能
    if args.export_csv:
        export_register_results_to_csv(register_results, f"{args.output_file}.csv" if args.output_file else None)
    
    if args.export_json:
        export_register_results_to_json(register_results, f"{args.output_file}.json" if args.output_file else None)
    
    # 关闭服务
    api_service.close()
    
    print(f"\n=== 测试完成 ===")
    print("根据测试结果，注册成功的关键参数：")
    print("✅ deviceId: 必须为空")
    print("✅ params.alone: 必须为true")
    print("✅ deviceSerialNumber: 必须唯一")
    print("✅ mac: 必须唯一")
    print("✅ 其他参数: 可以保持一致")

if __name__ == '__main__':
    main() 