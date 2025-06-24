#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动注册接口测试脚本
直接用《终端压测主要接口及时序.txt》里的注册参数，向注册接口发POST请求并打印返回结果。
"""
import requests
import json
import subprocess
import sys
import os

REGISTER_URL = "http://192.168.24.45:8080/protector/register"

# 测试2：使用不存在的设备ID和序列号，测试是否能创建新设备
register_data = {
    "address": "",
    "deviceId": "TEST_DEVICE_001",  # 新的设备ID
    "deviceName": "robot",
    "ip": "1.1.1.1",
    "locate": "guestos",
    "mac": "TEST:MAC:001",  # 新的MAC地址
    "params": {
        "alone": True,
        "bootTime": "",
        "brand": "robot",
        "customerCode": "101",
        "deviceSerialNumber": "TEST_SN_001",  # 新的序列号
        "deviceType": "PC",
        "hardDisk": "robot",
        "kseUser": "",
        "lastShutdownTime": "",
        "macs": "TEST:MAC:001",  # 新的MAC地址
        "mainBoard": "robot",
        "memory": "robot",
        "model": "robot",
        "operatingSystem": "robot",
        "outsideIp": "",
        "processor": "robot",
        "protectorVersion": "robot",
        "remark": "robot",
        "starter2Version": "robot",
        "virtualMachine": False
    }
}

def query_database():
    """查询数据库确认注册结果"""
    try:
        result = subprocess.run([
            sys.executable, "src/interfaces/cli/db_query_cli.py", 
            "--limit", "5", "--export-json", "--output-file", "test_result"
        ], capture_output=True, text=True, cwd=os.getcwd())
        print("\n=== 数据库查询结果 ===")
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
    except Exception as e:
        print(f"查询数据库失败: {e}")

if __name__ == "__main__":
    headers = {"Content-Type": "application/json"}
    print("=== 测试2：使用不存在的设备ID和序列号 ===")
    print("发送注册请求...\n请求数据:")
    print(json.dumps(register_data, ensure_ascii=False, indent=2))
    
    try:
        resp = requests.post(REGISTER_URL, headers=headers, json=register_data, timeout=10)
        print("\n=== 接口响应 ===")
        print(f"状态码: {resp.status_code}")
        try:
            response_json = resp.json()
            print(json.dumps(response_json, ensure_ascii=False, indent=2))
        except Exception:
            print("响应内容:", resp.text)
        
        # 查询数据库确认结果
        query_database()
        
    except Exception as e:
        print(f"请求异常: {e}") 