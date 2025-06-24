#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册参数遍历自动化脚本
自动遍历注册接口所有参数，每次只修改一个参数，测试其对注册成功的影响。
多线程加速，自动输出详细结论。
"""
import requests
import json
import copy
import csv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import sys
import os
import random
import string
import time

REGISTER_URL = "http://192.168.24.45:8080/protector/register"
DB_QUERY_CMD = [sys.executable, "src/interfaces/cli/db_query_cli.py", "--limit", "5", "--export-json", "--output-file", "param_sweep_result"]

# 生成特殊值/随机值
SPECIAL_VALUES = ["", "NULL", "0", "1", "test", "random", "!@#$%^&*()"]
def random_value():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_baseline_device():
    """读取数据库中真实存在的一条设备数据作为基线"""
    subprocess.run(DB_QUERY_CMD, cwd=os.getcwd())
    with open("data/device_samples/param_sweep_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        raise Exception("数据库无设备数据！")
    return data[0]

def build_register_data(base, param_path=None, new_value=None):
    """根据基线设备数据构造注册请求数据，可指定参数路径和新值"""
    # param_path: ['params', 'deviceSerialNumber']
    data = {
        "address": base.get("address", ""),
        "deviceId": base.get("device_id", ""),
        "deviceName": base.get("device_name", ""),
        "ip": base.get("ip", ""),
        "locate": "guestos",
        "mac": base.get("mac", ""),
        "params": {
            "alone": True,
            "bootTime": "",
            "brand": base.get("brand", ""),
            "customerCode": "101",
            "deviceSerialNumber": base.get("device_serial_number", ""),
            "deviceType": base.get("type", ""),
            "hardDisk": base.get("hard_disk", ""),
            "kseUser": "",
            "lastShutdownTime": "",
            "macs": base.get("macs", ""),
            "mainBoard": base.get("main_board", ""),
            "memory": base.get("memory", ""),
            "model": base.get("model", ""),
            "operatingSystem": base.get("operating_system", ""),
            "outsideIp": base.get("outside_ip", ""),
            "processor": base.get("processor", ""),
            "protectorVersion": "robot",
            "remark": base.get("remark", ""),
            "starter2Version": "robot",
            "virtualMachine": False
        }
    }
    if param_path:
        d = data
        for k in param_path[:-1]:
            d = d[k]
        d[param_path[-1]] = new_value
    return data

def send_and_check(param_path, new_value, base_device):
    """发起注册请求并返回结果"""
    register_data = build_register_data(base_device, param_path, new_value)
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(REGISTER_URL, headers=headers, json=register_data, timeout=10)
        code = resp.status_code
        try:
            resp_json = resp.json()
        except Exception:
            resp_json = {"raw": resp.text}
    except Exception as e:
        code = -1
        resp_json = {"error": str(e)}
    
    # 查询数据库，确认是否有新设备或字段变化
    try:
        subprocess.run(DB_QUERY_CMD, cwd=os.getcwd(), capture_output=True)
        json_file = "data/device_samples/param_sweep_result.json"
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    db_data = json.loads(content)
                else:
                    db_data = []
        else:
            db_data = []
    except Exception as e:
        db_data = [{"error": f"数据库查询失败: {e}"}]
    
    return {
        "param_path": ".".join(param_path) if param_path else "(baseline)",
        "new_value": new_value,
        "status_code": code,
        "response": resp_json,
        "db_snapshot": db_data
    }

def get_all_param_paths():
    """获取所有可变更参数路径（顶层和params下所有字段）"""
    paths = [[k] for k in ["address", "deviceId", "deviceName", "ip", "locate", "mac"]]
    params_fields = [
        "alone", "bootTime", "brand", "customerCode", "deviceSerialNumber", "deviceType", "hardDisk", "kseUser", "lastShutdownTime", "macs", "mainBoard", "memory", "model", "operatingSystem", "outsideIp", "processor", "protectorVersion", "remark", "starter2Version", "virtualMachine"
    ]
    for k in params_fields:
        paths.append(["params", k])
    return paths

def main():
    base_device = get_baseline_device()
    param_paths = get_all_param_paths()
    test_cases = []
    # baseline
    test_cases.append((None, None))
    # 单参数变更
    for path in param_paths:
        for val in SPECIAL_VALUES + [random_value()]:
            test_cases.append((path, val))
    print(f"共需测试 {len(test_cases)} 组参数...")
    results = []
    lock = threading.Lock()
    def worker(args):
        path, val = args
        res = send_and_check(path, val, base_device)
        with lock:
            results.append(res)
        print(f"测试 {res['param_path']}={val}，状态码: {res['status_code']}，响应: {res['response'].get('msg', res['response'])}")
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(worker, test_cases))
    # 汇总输出
    with open("register_param_sweep_result.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["param_path", "new_value", "status_code", "response_msg", "response_code"])
        for r in results:
            writer.writerow([
                r["param_path"], r["new_value"], r["status_code"],
                r["response"].get("msg", r["response"]),
                r["response"].get("code", r["response"])])
    print("\n=== 测试完成，结果已保存为 register_param_sweep_result.csv ===")
    # 统计结论
    success_params = [r for r in results if r["response"].get("msg") == "激活成功"]
    fail_params = [r for r in results if r["response"].get("msg") != "激活成功"]
    print(f"\n【结论】\n可影响注册成功的参数变更有：")
    for r in fail_params:
        print(f"  {r['param_path']}={r['new_value']} => {r['response'].get('msg', r['response'])}")
    print("\n不影响注册成功的参数变更有：")
    for r in success_params:
        print(f"  {r['param_path']}={r['new_value']}")

if __name__ == "__main__":
    main() 