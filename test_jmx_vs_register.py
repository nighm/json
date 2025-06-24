#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较JMX生成的请求和register_param_tester.py的请求格式
"""

import csv
import json

def test_jmx_request_format():
    """测试JMX请求格式"""
    print("=== 测试JMX请求格式 ===")
    
    # 读取CSV文件
    csv_file = "data/generated_devices/devices_20250618_231637_2.csv"
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)
    
    print(f"CSV数据: {row}")
    
    # 模拟JMX中的JSON请求
    jmx_json = {
        "address": "",
        "deviceId": "",
        "deviceName": row['device_name'],
        "ip": row['ip'],
        "locate": "guestos",
        "mac": row['mac'],
        "params": {
            "alone": True,
            "bootTime": "",
            "brand": row['brand'],
            "customerCode": "101",
            "deviceSerialNumber": row['device_serial_number'],
            "deviceType": row['type'],
            "hardDisk": "",
            "kseUser": "",
            "lastShutdownTime": "",
            "macs": row['mac'],
            "mainBoard": "",
            "memory": "",
            "model": row['model'],
            "operatingSystem": "",
            "outsideIp": "",
            "processor": "",
            "protectorVersion": "robot",
            "remark": "",
            "starter2Version": "robot",
            "virtualMachine": False
        }
    }
    
    print(f"JMX生成的JSON请求:")
    print(json.dumps(jmx_json, indent=2, ensure_ascii=False))
    
    return jmx_json

def test_register_param_tester_format():
    """测试register_param_tester.py的请求格式"""
    print("\n=== 测试register_param_tester.py请求格式 ===")
    
    # 模拟register_param_tester.py的请求
    base_device = {
        "device_id": "",
        "device_name": "robot",
        "ip": "1.1.1.1",
        "mac": "AA:BB:CC:12:D6:04",
        "brand": "robot",
        "model": "robot",
        "type": "PC",
        "processor": "",
        "operating_system": "",
        "hard_disk": "",
        "memory": "",
        "main_board": "",
        "outside_ip": "",
        "remark": ""
    }
    
    changes = {
        "deviceId": "",
        "params.deviceSerialNumber": "SN_REGISTER_00004566",
        "mac": "AA:BB:CC:12:D6:04",
        "params.macs": "AA:BB:CC:12:D6:04",
        "params.alone": True
    }
    
    # 构建请求数据
    data = {
        "address": "",
        "deviceId": base_device.get("device_id", ""),
        "deviceName": base_device.get("device_name", ""),
        "ip": base_device.get("ip", ""),
        "locate": "guestos",
        "mac": base_device.get("mac", ""),
        "params": {
            "alone": True,
            "bootTime": "",
            "brand": base_device.get("brand", ""),
            "customerCode": "101",
            "deviceSerialNumber": base_device.get("device_serial_number", ""),
            "deviceType": base_device.get("type", ""),
            "hardDisk": base_device.get("hard_disk", ""),
            "kseUser": "",
            "lastShutdownTime": "",
            "macs": base_device.get("macs", ""),
            "mainBoard": base_device.get("main_board", ""),
            "memory": base_device.get("memory", ""),
            "model": base_device.get("model", ""),
            "operatingSystem": base_device.get("operating_system", ""),
            "outsideIp": base_device.get("outside_ip", ""),
            "processor": base_device.get("processor", ""),
            "protectorVersion": "robot",
            "remark": base_device.get("remark", ""),
            "starter2Version": "robot",
            "virtualMachine": False
        }
    }
    
    # 应用changes
    if changes:
        for param_path, new_value in changes.items():
            d = data
            keys = param_path.split('.')
            for k in keys[:-1]:
                d = d[k]
            d[keys[-1]] = new_value
    
    print(f"register_param_tester.py生成的JSON请求:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    return data

def compare_requests():
    """比较两种请求格式"""
    print("\n=== 比较请求格式 ===")
    
    jmx_request = test_jmx_request_format()
    register_request = test_register_param_tester_format()
    
    # 比较关键字段
    key_fields = [
        "deviceId",
        "deviceName", 
        "ip",
        "mac",
        "params.deviceSerialNumber",
        "params.brand",
        "params.model",
        "params.deviceType",
        "params.macs"
    ]
    
    print("\n关键字段比较:")
    for field in key_fields:
        if '.' in field:
            # 嵌套字段
            keys = field.split('.')
            jmx_value = jmx_request
            register_value = register_request
            for k in keys:
                jmx_value = jmx_value.get(k, '')
                register_value = register_value.get(k, '')
        else:
            # 顶层字段
            jmx_value = jmx_request.get(field, '')
            register_value = register_request.get(field, '')
        
        match = "✅" if jmx_value == register_value else "❌"
        print(f"{match} {field}: JMX='{jmx_value}' vs Register='{register_value}'")

if __name__ == "__main__":
    compare_requests() 