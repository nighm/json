import requests
import json
import sys
import argparse

# 定义一个函数来发送注册请求
def register_device(mac_address, serial_number):
    """根据传入的MAC和序列号发送注册请求"""

    REGISTER_URL = "http://192.168.24.45:8080/protector/register"

    register_data = {
        "address": "",
        "deviceId": "",
        "deviceName": "robot",
        "ip": "1.1.1.1",
        "locate": "guestos",
        "mac": mac_address,
        "params": {
            "alone": True,
            "bootTime": "",
            "brand": "robot",
            "customerCode": "101",
            "deviceSerialNumber": serial_number,
            "deviceType": "PC",
            "hardDisk": "robot",
            "kseUser": "",
            "lastShutdownTime": "",
            "macs": mac_address, # 保持与外层mac一致
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

    headers = {"Content-Type": "application/json"}

    print(f"\n=== 发送注册请求 (MAC: {mac_address}, SN: {serial_number}) ===")
    
    try:
        resp = requests.post(REGISTER_URL, headers=headers, json=register_data, timeout=10)
        print("\n=== 接口响应 ===")
        print(f"状态码: {resp.status_code}")
        try:
            # 打印响应，确保JMeter能捕获到
            print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        except Exception:
            print("响应内容:", resp.text)
        
        # 对于JMeter的成功/失败判断，如果状态码不是200，则以非0状态码退出
        if resp.status_code != 200:
            sys.exit(1)
            
    except Exception as e:
        print(f"请求异常: {e}")
        sys.exit(1) # 发生异常时也以非0状态码退出


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="发送设备注册请求")
    parser.add_argument("mac", type=str, help="要注册的设备MAC地址")
    parser.add_argument("sn", type=str, help="要注册的设备序列号")
    args = parser.parse_args()

    register_device(args.mac, args.sn) 