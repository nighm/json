#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册验证服务
实现双重验证机制：理论验证（测试结果）+ 实际验证（数据库查询）
对比分析注册结果，生成详细验证报告
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

from src.application.services.device_data_manager import DeviceDataManager
from src.application.services.device_query_service import DeviceQueryService
from src.domain.entities.test_result import TestResult

class RegisterVerificationService:
    """
    注册验证服务 - 双重验证机制
    1. 理论验证：从测试结果提取成功注册的设备
    2. 实际验证：从数据库查询真实注册的设备
    3. 差异分析：对比理论vs实际结果
    """
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.device_manager = DeviceDataManager()
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据库查询服务 - 只传递MySQL相关参数
        try:
            # 确保只传递DBClient支持的参数
            mysql_config = {
                'host': db_config.get('host', 'localhost'),
                'port': db_config.get('port', 3306),
                'user': db_config.get('user', 'root'),
                'password': db_config.get('password', ''),
                'database': db_config.get('database', '')
            }
            self.db_service = DeviceQueryService(mysql_config)
        except Exception as e:
            self.logger.error(f"初始化数据库查询服务失败: {e}")
            self.db_service = None
    
    def verify_registration_results(self, test_results: List[TestResult], test_id: str) -> Dict:
        """
        双重验证注册结果
        
        Args:
            test_results: 测试结果列表
            test_id: 测试ID
            
        Returns:
            Dict: 验证报告
        """
        self.logger.info(f"开始双重验证注册结果，测试ID: {test_id}")
        
        # 1. 理论验证：从测试结果提取成功注册的设备
        theoretical_device_ids = self.extract_theoretical_success(test_results)
        self.logger.info(f"理论验证：发现 {len(theoretical_device_ids)} 台成功注册设备")
        
        # 标记为理论上已使用
        self.device_manager.mark_devices_as_theoretically_used(theoretical_device_ids, test_id)
        
        # 2. 实际验证：从数据库查询真实注册的设备
        actual_device_ids = self.query_actual_registrations(theoretical_device_ids)
        self.logger.info(f"实际验证：数据库中发现 {len(actual_device_ids)} 台设备")
        
        # 标记为实际已使用
        self.device_manager.mark_devices_as_actually_used(actual_device_ids, test_id)
        
        # 3. 差异分析
        differences = self.analyze_verification_differences(theoretical_device_ids, actual_device_ids)
        
        # 4. 生成验证报告
        verification_report = self._generate_verification_report(
            test_id, theoretical_device_ids, actual_device_ids, differences
        )
        
        self.logger.info("双重验证完成")
        return verification_report
    
    def extract_theoretical_success(self, test_results: List[TestResult]) -> List[str]:
        """
        从测试结果提取理论上成功注册的设备ID
        
        Args:
            test_results: 测试结果列表
            
        Returns:
            List[str]: 成功注册的设备ID列表
        """
        successful_device_ids = []
        
        for result in test_results:
            if not result.success:
                self.logger.warning(f"跳过失败的测试结果: {result.report_path}")
                continue
            
            # 从JMeter结果文件中提取成功注册的设备ID
            device_ids = self._extract_device_ids_from_jmeter_result(result.report_path)
            successful_device_ids.extend(device_ids)
        
        # 去重
        successful_device_ids = list(set(successful_device_ids))
        self.logger.info(f"从测试结果中提取到 {len(successful_device_ids)} 台成功注册设备")
        
        return successful_device_ids
    
    def _extract_device_ids_from_jmeter_result(self, report_path: str) -> List[str]:
        """
        从JMeter结果文件中提取设备ID
        
        Args:
            report_path: JMeter结果文件路径
            
        Returns:
            List[str]: 设备ID列表
        """
        device_ids = []
        
        try:
            # 从report_path中提取时间戳信息
            # 路径格式: src\tools\jmeter\results\20250619_141241\接口性能测试_register_1_1_20250619_141242\report
            path_parts = Path(report_path).parts
            if len(path_parts) >= 3:
                # 提取时间戳部分，如 20250619_141242
                timestamp_part = path_parts[-2]  # 接口性能测试_register_1_1_20250619_141242
                if '_' in timestamp_part:
                    timestamp = timestamp_part.split('_')[-1]  # 20250619_141242
                    self.logger.info(f"从报告路径提取到时间戳: {timestamp}")
                    
                    # 在data/generated_devices目录中查找对应时间戳的设备数据文件
                    generated_devices_dir = Path("data/generated_devices")
                    if generated_devices_dir.exists():
                        # 查找包含该时间戳的设备数据文件
                        device_files = list(generated_devices_dir.glob(f"devices_{timestamp}_*.csv"))
                        if device_files:
                            # 如果找到多个文件，取第一个（通常只有一个）
                            device_file = device_files[0]
                            self.logger.info(f"找到对应的设备数据文件: {device_file}")
                            csv_device_ids = self._parse_device_csv_file(str(device_file))
                            device_ids.extend(csv_device_ids)
                        else:
                            self.logger.warning(f"未找到时间戳为 {timestamp} 的设备数据文件")
                            # 回退到查找最新文件
                            all_device_files = list(generated_devices_dir.glob("devices_*.csv"))
                            if all_device_files:
                                latest_file = max(all_device_files, key=lambda x: x.stat().st_mtime)
                                self.logger.info(f"回退到最新设备数据文件: {latest_file}")
                                csv_device_ids = self._parse_device_csv_file(str(latest_file))
                                device_ids.extend(csv_device_ids)
                    else:
                        self.logger.warning(f"设备数据目录不存在: {generated_devices_dir}")
                else:
                    self.logger.warning(f"无法从路径中提取时间戳: {report_path}")
            else:
                self.logger.warning(f"报告路径格式不正确: {report_path}")
        
        except Exception as e:
            self.logger.error(f"解析设备数据CSV文件失败 {report_path}: {e}")
        
        return device_ids
    
    def _parse_device_csv_file(self, csv_file: str) -> List[str]:
        """解析设备数据CSV文件，提取设备ID"""
        device_ids = []
        
        try:
            import csv
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 从serial_number字段提取设备ID，因为Register接口的device_id字段为空
                    device_id = row.get('serial_number', '').strip()
                    if device_id:
                        device_ids.append(device_id)
                        self.logger.debug(f"从CSV文件中提取到设备ID: {device_id}")
        except Exception as e:
            self.logger.error(f"解析设备数据CSV文件失败 {csv_file}: {e}")
        
        self.logger.info(f"从设备数据CSV文件中提取到 {len(device_ids)} 个设备ID")
        return device_ids
    
    def query_actual_registrations(self, device_ids: List[str]) -> List[str]:
        """
        从数据库查询实际注册的设备ID
        
        Args:
            device_ids: 要查询的设备ID列表（实际是device_serial_number）
            
        Returns:
            List[str]: 实际在数据库中的设备ID列表
        """
        if not self.db_service:
            self.logger.warning("数据库服务未初始化，跳过实际验证")
            return []
        
        actual_device_ids = []
        
        try:
            # 查询数据库中的设备
            for device_id in device_ids:
                # 查询条件改为device_serial_number字段，因为Register接口注册的设备ID存储在这个字段中
                devices = self.db_service.get_devices(
                    table_name='biz_device',
                    filter_condition=f"device_serial_number='{device_id}'",
                    limit=1
                )
                
                if devices:
                    actual_device_ids.append(device_id)
                    self.logger.debug(f"设备 {device_id} 在数据库中找到")
                else:
                    self.logger.debug(f"设备 {device_id} 在数据库中未找到")
        
        except Exception as e:
            self.logger.error(f"查询数据库失败: {e}")
        
        self.logger.info(f"数据库验证：{len(actual_device_ids)}/{len(device_ids)} 台设备在数据库中找到")
        return actual_device_ids
    
    def analyze_verification_differences(self, theoretical_ids: List[str], actual_ids: List[str]) -> Dict:
        """
        分析理论vs实际的差异
        
        Args:
            theoretical_ids: 理论上成功注册的设备ID列表
            actual_ids: 实际在数据库中的设备ID列表
            
        Returns:
            Dict: 差异分析结果
        """
        theoretical_set = set(theoretical_ids)
        actual_set = set(actual_ids)
        
        missing_in_database = list(theoretical_set - actual_set)
        unexpected_in_database = list(actual_set - theoretical_set)
        
        differences = {
            "missing_in_database": missing_in_database,
            "unexpected_in_database": unexpected_in_database,
            "summary": {
                "total_theoretical": len(theoretical_ids),
                "total_actual": len(actual_ids),
                "missing_count": len(missing_in_database),
                "unexpected_count": len(unexpected_in_database),
                "success_rate": round(len(actual_ids) / len(theoretical_ids) * 100, 2) if theoretical_ids else 0.0
            }
        }
        
        self.logger.info(f"差异分析完成：")
        self.logger.info(f"  理论成功: {len(theoretical_ids)} 台")
        self.logger.info(f"  实际成功: {len(actual_ids)} 台")
        self.logger.info(f"  数据库缺失: {len(missing_in_database)} 台")
        self.logger.info(f"  意外发现: {len(unexpected_in_database)} 台")
        self.logger.info(f"  成功率: {differences['summary']['success_rate']}%")
        
        return differences
    
    def _generate_verification_report(self, test_id: str, theoretical_ids: List[str], 
                                    actual_ids: List[str], differences: Dict) -> Dict:
        """
        生成验证报告
        
        Args:
            test_id: 测试ID
            theoretical_ids: 理论成功注册的设备ID列表
            actual_ids: 实际在数据库中的设备ID列表
            differences: 差异分析结果
            
        Returns:
            Dict: 验证报告
        """
        total_tested = len(theoretical_ids)
        theoretical_success = len(theoretical_ids)
        actual_success = len(actual_ids)
        
        report = {
            "test_id": test_id,
            "verification_time": datetime.now().isoformat(),
            "test_summary": {
                "total_devices_tested": total_tested,
                "theoretical_success": theoretical_success,
                "actual_success": actual_success,
                "verification_time": datetime.now().isoformat()
            },
            "theoretical_registrations": theoretical_ids,
            "actual_registrations": actual_ids,
            "differences": differences
        }
        
        # 添加分析结果
        if total_tested > 0:
            report["analysis"] = {
                "success_rate_theoretical": round(theoretical_success / total_tested * 100, 2),
                "success_rate_actual": round(actual_success / total_tested * 100, 2),
                "data_loss_rate": round((theoretical_success - actual_success) / total_tested * 100, 2),
                "duplicate_rate": 0.0  # 暂时设为0，后续可扩展
            }
        else:
            report["analysis"] = {
                "success_rate_theoretical": 0.0,
                "success_rate_actual": 0.0,
                "data_loss_rate": 0.0,
                "duplicate_rate": 0.0
            }
        
        return report
    
    def save_verification_report(self, report: Dict, output_dir: str) -> str:
        """
        保存验证报告到文件
        
        Args:
            report: 验证报告
            output_dir: 输出目录
            
        Returns:
            str: 报告文件路径
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            report_file = output_path / f"verification_report_{report['test_id']}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"验证报告已保存: {report_file}")
            return str(report_file)
        
        except Exception as e:
            self.logger.error(f"保存验证报告失败: {e}")
            return ""
    
    def print_verification_report(self, report: Dict):
        """
        打印验证报告摘要
        
        Args:
            report: 验证报告
        """
        summary = report.get("test_summary", {})
        analysis = report.get("analysis", {})
        differences = report.get("differences", {})
        
        print("\n" + "="*60)
        print("🔍 注册结果验证报告")
        print("="*60)
        print(f"测试ID: {report.get('test_id', 'N/A')}")
        print(f"验证时间: {report.get('verification_time', 'N/A')}")
        print()
        
        print("📊 测试统计:")
        print(f"   总测试设备: {summary.get('total_devices_tested', 0)}台")
        print(f"   理论成功: {summary.get('theoretical_success', 0)}台 ({analysis.get('success_rate_theoretical', 0)}%)")
        print(f"   实际成功: {summary.get('actual_success', 0)}台 ({analysis.get('success_rate_actual', 0)}%)")
        print(f"   数据丢失: {differences.get('summary', {}).get('missing_count', 0)}台 ({analysis.get('data_loss_rate', 0)}%)")
        print(f"   重复注册: {differences.get('summary', {}).get('unexpected_count', 0)}台 ({analysis.get('duplicate_rate', 0)}%)")
        print()
        
        # 显示差异详情
        missing_devices = differences.get("missing_in_database", [])
        unexpected_devices = differences.get("unexpected_in_database", [])
        
        if missing_devices:
            print("⚠️  数据库缺失设备:")
            for device_id in missing_devices[:5]:  # 只显示前5个
                print(f"   - {device_id}")
            if len(missing_devices) > 5:
                print(f"   ... 还有 {len(missing_devices) - 5} 台设备")
            print()
        
        if unexpected_devices:
            print("⚠️  意外发现的设备:")
            for device_id in unexpected_devices[:5]:  # 只显示前5个
                print(f"   - {device_id}")
            if len(unexpected_devices) > 5:
                print(f"   ... 还有 {len(unexpected_devices) - 5} 台设备")
            print()
        
        # 建议
        if analysis.get('data_loss_rate', 0) > 5:
            print("💡 建议:")
            print("   - 检查网络连接稳定性")
            print("   - 检查数据库性能")
            print("   - 检查并发冲突处理")
            print("   - 考虑降低并发压力")
        elif analysis.get('success_rate_actual', 0) >= 95:
            print("✅ 测试结果良好，注册功能稳定")
        
        print("="*60)
    
    def close(self):
        """关闭数据库连接"""
        if self.db_service:
            try:
                self.db_service.close()
            except Exception as e:
                self.logger.error(f"关闭数据库连接失败: {e}")
    
    def sync_actual_registered_devices(self, table_name: str = 'biz_device', limit: int = 10000):
        """
        批量同步数据库真实注册设备到 actual_used_devices.json
        支持按表名和数量限制，默认同步全部
        """
        if not self.db_service:
            self.logger.error("数据库服务未初始化，无法同步实际注册设备")
            return False
        
        self.logger.info(f"开始同步数据库注册设备，表名: {table_name}，最大数量: {limit}")
        devices = self.db_service.get_devices(table_name=table_name, limit=limit)
        
        deviceSerialNumber = []
        mac = []
        device_ids = []
        for device in devices:
            # 只收集非空且唯一的SN、MAC、device_id
            if getattr(device, 'device_serial_number', None):
                deviceSerialNumber.append(device.device_serial_number)
            if getattr(device, 'mac', None):
                mac.append(device.mac)
            if getattr(device, 'device_id', None):
                device_ids.append(device.device_id)
        # 去重
        deviceSerialNumber = list(set(deviceSerialNumber))
        mac = list(set(mac))
        device_ids = list(set(device_ids))
        
        # 统计信息
        result = {
            "actual_registrations": {
                "deviceSerialNumber": deviceSerialNumber,
                "mac": mac,
                "device_ids": device_ids
            },
            "verification_results": {
                "theoretical_count": 0,  # 仅同步，不做对比
                "actual_count": len(deviceSerialNumber),
                "missing_devices": [],
                "success_rate": 0.0
            },
            "last_verification_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "verification_history": []
        }
        # 写入文件
        output_path = Path('data/actual_used_devices.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        self.logger.info(f"已同步 {len(deviceSerialNumber)} 台设备到 actual_used_devices.json")
        return True 