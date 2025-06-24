#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API发送服务
负责发送HTTP请求到服务器，支持各种接口的调用
特别针对注册接口进行优化，确保请求格式正确
"""

import json
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from src.domain.entities.device_info import DeviceInfo

class APISendService:
    """
    API发送服务 - 统一管理所有API请求
    支持设备注册、心跳、策略获取等接口
    """
    
    def __init__(self, base_url: str = "http://192.168.24.45:8080", timeout: int = 30):
        """
        初始化API发送服务
        
        Args:
            base_url: 服务器基础URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PerformanceTest/1.0'
        })
    
    def send_register_request(self, device: DeviceInfo) -> Dict[str, Any]:
        """
        发送设备注册请求
        
        Args:
            device: 设备信息对象
            
        Returns:
            Dict: 响应结果，包含状态码、响应内容等
        """
        try:
            # 构建注册请求数据
            register_data = self._build_register_data(device)
            
            # 注册接口URL
            url = f"{self.base_url}/protector/register"
            
            self.logger.info(f"发送注册请求: {url}")
            self.logger.info(f"设备ID: {device.device_id}")
            self.logger.info(f"设备名称: {device.device_name}")
            self.logger.info(f"注册数据: {json.dumps(register_data, ensure_ascii=False, indent=2)}")
            
            # 发送POST请求
            response = self.session.post(
                url=url,
                json=register_data,
                timeout=self.timeout
            )
            
            # 解析响应
            result = self._parse_response(response)
            
            self.logger.info(f"注册响应: 状态码={response.status_code}, 成功={result.get('success', False)}")
            self.logger.info(f"响应内容: {json.dumps(result.get('raw_response', {}), ensure_ascii=False, indent=2)}")
            
            return result
            
        except requests.exceptions.Timeout:
            self.logger.error(f"注册请求超时: {device.device_id}")
            return {
                'success': False,
                'error': '请求超时',
                'status_code': 408,
                'response_message': '请求超时'
            }
        except requests.exceptions.ConnectionError:
            self.logger.error(f"注册请求连接失败: {device.device_id}")
            return {
                'success': False,
                'error': '连接失败',
                'status_code': 0,
                'response_message': '连接失败'
            }
        except Exception as e:
            self.logger.error(f"注册请求异常: {device.device_id}, 错误: {e}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 0,
                'response_message': str(e)
            }
    
    def send_batch_register_requests(self, devices: List[DeviceInfo]) -> List[Dict[str, Any]]:
        """
        批量发送设备注册请求
        
        Args:
            devices: 设备信息列表
            
        Returns:
            List[Dict]: 每个设备的注册结果列表
        """
        results = []
        
        for i, device in enumerate(devices, 1):
            self.logger.info(f"发送第 {i}/{len(devices)} 个注册请求: {device.device_id}")
            
            result = self.send_register_request(device)
            result['device_id'] = device.device_id
            result['device_name'] = device.device_name
            result['request_index'] = i
            
            results.append(result)
            
            # 添加小延迟，避免请求过于密集
            if i < len(devices):
                import time
                time.sleep(0.1)
        
        return results
    
    def _build_register_data(self, device: DeviceInfo) -> Dict[str, Any]:
        """
        构建注册请求数据 - 根据测试结果优化
        确保：deviceId为空、params.alone为true、SN和MAC唯一
        """
        return {
            "address": "",
            "deviceId": "",  # 必须为空，根据测试结果
            "deviceName": device.device_name or "",
            "ip": device.ip or "1.1.1.1",
            "locate": "guestos",
            "mac": device.mac,
            "params": {
                "alone": True,  # 必须为true，根据测试结果
                "bootTime": "",
                "brand": device.brand or "robot",
                "customerCode": "101",
                "deviceSerialNumber": device.device_serial_number,  # 唯一SN号
                "deviceType": device.type or "PC",
                "hardDisk": device.hard_disk or "robot",
                "kseUser": "",
                "lastShutdownTime": "",
                "macs": device.mac,  # 与mac保持一致
                "mainBoard": device.main_board or "robot",
                "memory": device.memory or "robot",
                "model": device.model or "robot",
                "operatingSystem": device.operating_system or "robot",
                "outsideIp": device.outside_ip or "",
                "processor": device.processor or "robot",
                "protectorVersion": "robot",
                "remark": device.remark or "",
                "starter2Version": "robot",
                "virtualMachine": False
            }
        }
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        解析HTTP响应
        
        Args:
            response: requests响应对象
            
        Returns:
            Dict: 解析后的响应结果
        """
        try:
            # 尝试解析JSON响应
            response_json = response.json()
            
            # 判断是否成功
            success = response.status_code == 200 and response_json.get('code') == 200
            
            return {
                'success': success,
                'status_code': response.status_code,
                'response_code': response_json.get('code'),
                'response_message': response_json.get('msg', ''),
                'response_data': response_json.get('data', {}),
                'raw_response': response_json
            }
            
        except json.JSONDecodeError:
            # 如果不是JSON格式，返回文本内容
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_message': response.text,
                'raw_response': response.text
            }
    
    def send_heartbeat_request(self, device_id: str) -> Dict[str, Any]:
        """
        发送心跳请求
        
        Args:
            device_id: 设备ID
            
        Returns:
            Dict: 响应结果
        """
        try:
            # 构建心跳请求数据
            heartbeat_data = {
                "deviceId": device_id,
                "locate": "guestos",
                "ip": "192.168.12.10"  # 可以从设备信息中获取
            }
            
            # 心跳接口URL
            url = f"{self.base_url}/protector/heartbeat"
            
            self.logger.info(f"发送心跳请求: {url}, 设备ID: {device_id}")
            
            # 发送POST请求
            response = self.session.post(
                url=url,
                json=heartbeat_data,
                timeout=self.timeout
            )
            
            # 解析响应
            result = self._parse_response(response)
            
            self.logger.info(f"心跳响应: 状态码={response.status_code}, 成功={result.get('success', False)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"心跳请求异常: {device_id}, 错误: {e}")
            return {
                'success': False,
                'error': str(e),
                'status_code': 0,
                'response_message': str(e)
            }
    
    def test_connection(self) -> bool:
        """
        测试服务器连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 尝试获取MQTT地址接口（通常不需要认证）
            url = f"{self.base_url}/protector/mqtt/url"
            
            response = self.session.post(
                url=url,
                json={},
                timeout=10
            )
            
            success = response.status_code == 200
            self.logger.info(f"连接测试: {url}, 状态码={response.status_code}, 成功={success}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 