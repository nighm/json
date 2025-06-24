from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import itertools
import json
import multiprocessing
import os
import random
import requests
import string
import subprocess
import sys
import threading
import time

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合注册参数测试工具
合并了成功组合分析、批量注册测试、参数组合测试等功能
"""

REGISTER_URL = "http://192.168.24.45:8080/protector/register"

class RegisterParamTester:
    def __init__(self, base_url="http://192.168.24.45:8080"):
        """初始化注册参数测试器"""
        self.session = requests.Session()
        self.max_workers = min(multiprocessing.cpu_count() * 3, 100)
        self.base_url = base_url
        self.register_url = f"{base_url}/protector/register"

    def get_baseline_device(self):
        """获取基线设备数据"""
        try:
            result = subprocess.run([
                sys.executable, "src/interfaces/cli/db_query_cli.py", 
                "--limit", "1", "--export-json", "--output-file", "baseline"
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            with open("data/device_samples/baseline.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            return data[0] if data else None
        except Exception as e:
            print(f"获取基线设备失败: {e}")
            return None

    def build_register_data(self, base_device, changes=None):
        """构建注册数据"""
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
        
        if changes:
            for param_path, new_value in changes.items():
                d = data
                keys = param_path.split('.')
                for k in keys[:-1]:
                    d = d[k]
                d[keys[-1]] = new_value
        
        return data

    def generate_unique_sn_mac(self, idx):
        """生成唯一SN号和MAC地址"""
        # 从100开始，避免与现有设备重复
        sn = f"SN_TEST_{idx+100:05d}"
        mac = f"AA:BB:CC:{(idx+100)//256%256:02X}:{(idx+100)%256:02X}:{((idx+100)//65536)%256:02X}"
        return sn, mac

    def test_single_register(self, args):
        """测试单个注册请求"""
        base_device, changes, test_name = args
        
        data = self.build_register_data(base_device, changes)
        headers = {"Content-Type": "application/json"}
        
        try:
            resp = self.session.post(self.register_url, headers=headers, json=data, timeout=5)
            resp_json = resp.json()
            api_success = resp_json.get("msg") == "激活成功"
            return {
                "test_name": test_name,
                "changes": changes,
                "api_success": api_success,
                "api_response": resp_json.get("msg", str(resp_json))
            }
        except Exception as e:
            return {
                "test_name": test_name,
                "changes": changes,
                "api_success": False,
                "api_response": f"请求失败: {e}"
            }

    def test_unique_register_batch(self, count=100):
        """批量唯一设备注册测试"""
        print("=== 唯一设备注册批量测试 ===")
        print(f"使用线程数: {self.max_workers}")
        
        base_device = self.get_baseline_device()
        if not base_device:
            print("无法获取基线设备数据")
            return
        
        print(f"基线设备ID: {base_device.get('device_id')}")
        print(f"批量注册数量: {count}")
        
        # 生成测试用例
        test_cases = []
        for i in range(count):
            sn, mac = self.generate_unique_sn_mac(i)
            changes = {
                "deviceId": "",  # 必须为空
                "params.deviceSerialNumber": sn,
                "mac": mac,
                "params.macs": mac,
                "params.alone": True
            }
            test_name = f"注册_{sn}_{mac}"
            test_cases.append((base_device, changes, test_name))
        
        # 并发执行
        successful_cases = []
        failed_cases = []
        start_time = time.time()
        
        print("\n=== 开始批量注册 ===")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {executor.submit(self.test_single_register, test_case): test_case for test_case in test_cases}
            for future in as_completed(future_to_test):
                result = future.result()
                if result['api_success']:
                    successful_cases.append(result)
                    print(f"✅ {result['test_name']}: 成功")
                else:
                    failed_cases.append(result)
                    print(f"❌ {result['test_name']}: 失败 - {result['api_response']}")
        
        total_time = time.time() - start_time
        print(f"\n=== 测试完成 ===")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"成功注册: {len(successful_cases)}")
        print(f"失败注册: {len(failed_cases)}")
        
        return successful_cases, failed_cases

    def test_param_combinations(self):
        """参数组合测试"""
        print("=== 参数组合测试 ===")
        
        base_device = self.get_baseline_device()
        if not base_device:
            print("无法获取基线设备数据")
            return
        
        print(f"基线设备: {base_device.get('device_id')}")
        
        all_params = [
            "deviceId",
            "deviceName", 
            "ip",
            "mac",
            "params.deviceSerialNumber",
            "params.brand",
            "params.model",
            "params.processor",
            "params.macs",
            "params.alone",
            "params.customerCode"
        ]
        
        test_values = ["TEST_VALUE", "", "NULL", "0"]
        results = []
        
        # 1. 基线测试
        print("\n=== 基线测试 ===")
        baseline = self.test_single_register((base_device, None, "基线测试"))
        results.append(baseline)
        print(f"基线测试: 成功={baseline['api_success']}, 响应={baseline['api_response']}")
        
        # 2. 单参数变更测试
        print("\n=== 单参数变更测试 ===")
        single_success = []
        single_fail = []
        
        for param in all_params:
            for value in test_values:
                test_name = f"单参数_{param}_{value}"
                result = self.test_single_register((base_device, {param: value}, test_name))
                results.append(result)
                
                if result['api_success']:
                    single_success.append(result)
                    print(f"✅ {test_name}: 成功")
                else:
                    single_fail.append(result)
                    print(f"❌ {test_name}: 失败 - {result['api_response']}")
        
        # 3. 双参数变更测试
        print("\n=== 双参数变更测试 ===")
        double_success = []
        double_fail = []
        
        param_combinations = list(itertools.combinations(all_params, 2))
        for param1, param2 in param_combinations:
            for value1 in test_values[:2]:
                for value2 in test_values[:2]:
                    test_name = f"双参数_{param1}_{value1}_{param2}_{value2}"
                    changes = {param1: value1, param2: value2}
                    result = self.test_single_register((base_device, changes, test_name))
                    results.append(result)
                    
                    if result['api_success']:
                        double_success.append(result)
                        print(f"✅ {test_name}: 成功")
                    else:
                        double_fail.append(result)
                        print(f"❌ {test_name}: 失败 - {result['api_response']}")
        
        # 输出结论
        print("\n" + "="*50)
        print("=== 最终结论 ===")
        print(f"基线测试: {'成功' if baseline['api_success'] else '失败'}")
        print(f"单参数变更测试: 成功 {len(single_success)} 个，失败 {len(single_fail)} 个")
        print(f"双参数变更测试: 成功 {len(double_success)} 个，失败 {len(double_fail)} 个")
        
        return results

    def test_single_params(self):
        """单参数测试"""
        print("=== 注册参数影响测试 ===")
        
        base_device = self.get_baseline_device()
        if not base_device:
            print("无法获取基线设备数据")
            return
        
        print(f"基线设备: {base_device.get('device_id')}")
        
        # 定义测试参数
        test_cases = [
            (None, None),  # 基线
            (("deviceId",), "INVALID_ID"),
            (("params", "deviceSerialNumber"), "INVALID_SN"),
            (("mac",), "AA:BB:CC:DD:EE:FF"),
            (("params", "macs"), "AA:BB:CC:DD:EE:FF"),
            (("brand",), "TEST_BRAND"),
            (("params", "brand"), "TEST_BRAND"),
            (("model",), "TEST_MODEL"),
            (("params", "model"), "TEST_MODEL"),
            (("processor",), "TEST_PROC"),
            (("params", "processor"), "TEST_PROC"),
            (("params", "alone"), False),
            (("params", "customerCode"), "999"),
        ]
        
        results = []
        
        for param_path, new_value in test_cases:
            if param_path:
                param_key = ".".join(param_path)
                changes = {param_key: new_value}
            else:
                changes = None
            
            test_name = f"测试_{param_key if param_path else 'baseline'}_{new_value if new_value else 'None'}"
            result = self.test_single_register((base_device, changes, test_name))
            results.append(result)
            print(f"测试 {result['test_name']} => 成功:{result['api_success']}, 响应:{result['api_response']}")
        
        # 输出结论
        print("\n=== 测试结论 ===")
        success_cases = [r for r in results if r["api_success"]]
        fail_cases = [r for r in results if not r["api_success"]]
        
        print(f"总测试数: {len(results)}")
        print(f"成功数: {len(success_cases)}")
        print(f"失败数: {len(fail_cases)}")
        
        return results

def main():
    parser = argparse.ArgumentParser(description='综合注册参数测试工具')
    parser.add_argument('--base-url', default='http://192.168.24.45:8080', help='服务器基础URL')
    parser.add_argument('--action', choices=['unique-batch', 'param-combinations', 'single-params', 'all'], 
                       default='all', help='测试类型：unique-batch(批量唯一注册), param-combinations(参数组合), single-params(单参数), all(全部)')
    parser.add_argument('--batch-count', type=int, default=100, help='批量注册数量')
    parser.add_argument('--max-workers', type=int, default=None, help='最大线程数')
    
    args = parser.parse_args()
    
    tester = RegisterParamTester(base_url=args.base_url)
    
    if args.max_workers:
        tester.max_workers = args.max_workers
    
    try:
        if args.action == 'unique-batch' or args.action == 'all':
            tester.test_unique_register_batch(args.batch_count)
        
        if args.action == 'param-combinations' or args.action == 'all':
            tester.test_param_combinations()
        
        if args.action == 'single-params' or args.action == 'all':
            tester.test_single_params()
            
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    main() 