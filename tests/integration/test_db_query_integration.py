"""
db_query_cli.py 集成测试
测试与真实数据库的集成
"""
import pytest
import tempfile
import os
import json
import csv
from unittest.mock import patch, Mock
import pymysql
from datetime import datetime

# 导入被测试的模块
from src.interfaces.cli.db_query_cli import (
    export_to_csv,
    export_to_json,
    auto_discover_databases,
    auto_discover_tables,
    export_actual_used_devices
)


class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.fixture
    def test_database_config(self):
        """测试数据库配置"""
        return {
            'host': 'localhost',
            'port': 3306,
            'user': 'test_user',
            'password': 'test_password',
            'database': 'test_db',
            'charset': 'utf8mb4'
        }
    
    @pytest.fixture
    def mock_database_connection(self):
        """模拟数据库连接"""
        with patch('pymysql.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            
            # 模拟数据库查询结果
            mock_cursor.fetchall.return_value = [
                ('test_db',),
                ('other_db',)
            ]
            mock_cursor.fetchone.return_value = (5,)  # 模拟记录数
            
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            yield mock_connect
    
    def test_database_connection_integration(self, test_database_config, mock_database_connection):
        """测试数据库连接集成"""
        # 模拟连接成功
        mock_database_connection.return_value.ping.return_value = True
        
        # 测试连接
        connection = pymysql.connect(**test_database_config)
        assert connection is not None
        
        # 验证连接参数
        mock_database_connection.assert_called_once_with(**test_database_config)
    
    def test_database_query_integration(self, test_database_config, mock_database_connection):
        """测试数据库查询集成"""
        # 模拟查询结果
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, '设备001', '华为', 'active'),
            (2, '设备002', '小米', 'inactive'),
            (3, '设备003', '苹果', 'active')
        ]
        
        mock_connection = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_database_connection.return_value = mock_connection
        
        # 执行查询
        connection = pymysql.connect(**test_database_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM biz_device LIMIT 3")
            results = cursor.fetchall()
        
        # 验证结果
        assert len(results) == 3
        assert results[0][1] == '设备001'
        assert results[1][2] == '小米'
        assert results[2][3] == 'active'


class TestExportIntegration:
    """导出功能集成测试"""
    
    @pytest.fixture
    def sample_devices(self):
        """示例设备数据"""
        devices = []
        for i in range(3):
            device = Mock()
            device.__dict__ = {
                'id': i + 1,
                'name': f'设备{i+1:03d}',
                'brand': ['华为', '小米', '苹果'][i],
                'model': f'Model{i+1}',
                'status': 'active' if i < 2 else 'inactive',
                'created_at': datetime(2025, 1, i+1, 10, 0, 0)
            }
            devices.append(device)
        return devices
    
    def test_csv_export_integration(self, sample_devices):
        """测试CSV导出集成"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, 'test_export.csv')
            
            # 执行导出
            result = export_to_csv(sample_devices, 'test_export.csv')
            
            # 验证文件创建
            assert os.path.exists(result)
            assert result.endswith('test_export.csv')
            
            # 验证CSV内容
            with open(result, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                assert len(rows) == 3
                assert rows[0]['id'] == '1'
                assert rows[0]['name'] == '设备001'
                assert rows[0]['brand'] == '华为'
                assert rows[0]['status'] == 'active'
                
                assert rows[1]['id'] == '2'
                assert rows[1]['brand'] == '小米'
                
                assert rows[2]['id'] == '3'
                assert rows[2]['brand'] == '苹果'
                assert rows[2]['status'] == 'inactive'
    
    def test_json_export_integration(self, sample_devices):
        """测试JSON导出集成"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, 'test_export.json')
            
            # 执行导出
            result = export_to_json(sample_devices, 'test_export.json')
            
            # 验证文件创建
            assert os.path.exists(result)
            assert result.endswith('test_export.json')
            
            # 验证JSON内容
            with open(result, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                assert len(data) == 3
                assert data[0]['id'] == 1
                assert data[0]['name'] == '设备001'
                assert data[0]['brand'] == '华为'
                assert data[0]['status'] == 'active'
                assert data[0]['created_at'] == '2025-01-01T10:00:00'
                
                assert data[1]['id'] == 2
                assert data[1]['brand'] == '小米'
                
                assert data[2]['id'] == 3
                assert data[2]['brand'] == '苹果'
                assert data[2]['status'] == 'inactive'
    
    def test_export_with_special_characters(self):
        """测试包含特殊字符的导出"""
        device = Mock()
        device.__dict__ = {
            'id': 1,
            'name': '设备"测试"',
            'brand': '华为&小米',
            'description': '包含\n换行符\r\n和制表符\t',
            'status': 'active'
        }
        
        devices = [device]
        
        # 测试CSV导出
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_result = export_to_csv(devices, 'special_chars.csv')
            
            with open(csv_result, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '设备"测试"' in content
                assert '华为&小米' in content
                assert '包含\n换行符\r\n和制表符\t' in content
        
        # 测试JSON导出
        with tempfile.TemporaryDirectory() as temp_dir:
            json_result = export_to_json(devices, 'special_chars.json')
            
            with open(json_result, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data[0]['name'] == '设备"测试"'
                assert data[0]['brand'] == '华为&小米'
                assert data[0]['description'] == '包含\n换行符\r\n和制表符\t'


class TestAutoDiscoverIntegration:
    """自动发现功能集成测试"""
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_auto_discover_databases_integration(self, mock_service_class):
        """测试数据库自动发现集成"""
        # 模拟服务
        mock_service = Mock()
        mock_service.discover_databases.return_value = [
            'yangguan',
            'device_management',
            'user_system',
            'other_db'
        ]
        mock_service_class.return_value = mock_service
        
        # 执行自动发现
        result = auto_discover_databases('localhost', 3306, 'root', 'password')
        
        # 验证结果
        assert result == 'yangguan'  # 应该返回第一个匹配的数据库
        
        # 验证服务调用
        mock_service.discover_databases.assert_called_once()
        mock_service.close.assert_called_once()
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_auto_discover_tables_integration(self, mock_service_class):
        """测试表自动发现集成"""
        # 模拟服务
        mock_service = Mock()
        mock_service.discover_tables.return_value = [
            'biz_device',
            'device_info',
            'device_status',
            'user_info',
            'system_config'
        ]
        mock_service_class.return_value = mock_service
        
        # 执行自动发现
        result = auto_discover_tables('localhost', 3306, 'root', 'password', 'yangguan')
        
        # 验证结果
        assert result == 'biz_device'  # 应该返回第一个匹配的表
        
        # 验证服务调用
        mock_service.discover_tables.assert_called_once()
        mock_service.close.assert_called_once()
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_auto_discover_with_no_matches(self, mock_service_class):
        """测试没有匹配项的自动发现"""
        # 模拟服务
        mock_service = Mock()
        mock_service.discover_databases.return_value = ['user_system', 'other_db']
        mock_service.discover_tables.return_value = ['user_info', 'system_config']
        mock_service_class.return_value = mock_service
        
        # 执行数据库自动发现
        db_result = auto_discover_databases('localhost', 3306, 'root', 'password')
        assert db_result == 'user_system'  # 应该返回第一个数据库
        
        # 执行表自动发现
        table_result = auto_discover_tables('localhost', 3306, 'root', 'password', 'user_system')
        assert table_result == 'user_info'  # 应该返回第一个表


class TestActualUsedDevicesIntegration:
    """实际使用设备导出集成测试"""
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_export_actual_used_devices_integration(self, mock_service_class):
        """测试实际使用设备导出集成"""
        # 模拟服务
        mock_service = Mock()
        
        # 模拟设备数据
        mock_device1 = Mock()
        mock_device1.deviceSerialNumber = "SN202501001"
        mock_device1.mac = "00:11:22:33:44:55"
        mock_device1.macs = "00:11:22:33:44:55,66:77:88:99:AA:BB"
        mock_device1.device_id = "DEV001"
        
        mock_device2 = Mock()
        mock_device2.deviceSerialNumber = "SN202501002"
        mock_device2.mac = "AA:BB:CC:DD:EE:FF"
        mock_device2.macs = None
        mock_device2.device_id = "DEV002"
        
        mock_device3 = Mock()
        mock_device3.deviceSerialNumber = "SN202501003"
        mock_device3.mac = "11:22:33:44:55:66"
        mock_device3.macs = "11:22:33:44:55:66,77:88:99:AA:BB:CC"
        mock_device3.device_id = "DEV003"
        
        mock_service.get_device_count.return_value = 3
        mock_service.get_devices.return_value = [mock_device1, mock_device2, mock_device3]
        mock_service_class.return_value = mock_service
        
        # 执行导出
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'actual_used_devices.json')
            
            result = export_actual_used_devices(
                host='localhost',
                port=3306,
                user='root',
                password='password',
                database='yangguan',
                table='biz_device',
                output_path=output_path
            )
            
            # 验证结果
            assert result is True
            assert os.path.exists(output_path)
            
            # 验证文件内容
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 验证结构
                assert 'actual_registrations' in data
                assert 'verification_results' in data
                assert 'last_verification_time' in data
                assert 'verification_history' in data
                
                # 验证设备序列号
                registrations = data['actual_registrations']
                assert len(registrations['deviceSerialNumbers']) == 3
                assert "SN202501001" in registrations['deviceSerialNumbers']
                assert "SN202501002" in registrations['deviceSerialNumbers']
                assert "SN202501003" in registrations['deviceSerialNumbers']
                
                # 验证MAC地址
                assert len(registrations['mac']) == 3
                assert "00:11:22:33:44:55" in registrations['mac']
                assert "AA:BB:CC:DD:EE:FF" in registrations['mac']
                assert "11:22:33:44:55:66" in registrations['mac']
                
                # 验证多个MAC地址
                assert len(registrations['macs']) == 2
                assert "00:11:22:33:44:55,66:77:88:99:AA:BB" in registrations['macs']
                assert "11:22:33:44:55:66,77:88:99:AA:BB:CC" in registrations['macs']
                
                # 验证设备ID
                assert len(registrations['device_ids']) == 3
                assert "DEV001" in registrations['device_ids']
                assert "DEV002" in registrations['device_ids']
                assert "DEV003" in registrations['device_ids']
                
                # 验证统计信息
                verification = data['verification_results']
                assert verification['actual_count'] == 3
                assert verification['theoretical_count'] == 0
                assert verification['success_rate'] == 0.0
                assert len(verification['missing_devices']) == 0
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_export_actual_used_devices_with_duplicates(self, mock_service_class):
        """测试包含重复数据的导出"""
        # 模拟服务
        mock_service = Mock()
        
        # 模拟包含重复数据的设备
        mock_device1 = Mock()
        mock_device1.deviceSerialNumber = "SN001"
        mock_device1.mac = "00:11:22:33:44:55"
        mock_device1.macs = "00:11:22:33:44:55"
        mock_device1.device_id = "DEV001"
        
        mock_device2 = Mock()
        mock_device2.deviceSerialNumber = "SN001"  # 重复的序列号
        mock_device2.mac = "00:11:22:33:44:55"     # 重复的MAC
        mock_device2.macs = "00:11:22:33:44:55"    # 重复的多个MAC
        mock_device2.device_id = "DEV001"          # 重复的设备ID
        
        mock_service.get_device_count.return_value = 2
        mock_service.get_devices.return_value = [mock_device1, mock_device2]
        mock_service_class.return_value = mock_service
        
        # 执行导出
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'actual_used_devices.json')
            
            result = export_actual_used_devices(
                host='localhost',
                port=3306,
                user='root',
                password='password',
                database='yangguan',
                table='biz_device',
                output_path=output_path
            )
            
            # 验证结果
            assert result is True
            
            # 验证去重效果
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                registrations = data['actual_registrations']
                
                # 应该去重，只保留一个
                assert len(registrations['deviceSerialNumbers']) == 1
                assert len(registrations['mac']) == 1
                assert len(registrations['macs']) == 1
                assert len(registrations['device_ids']) == 1


class TestErrorHandlingIntegration:
    """错误处理集成测试"""
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_database_connection_error_handling(self, mock_service_class):
        """测试数据库连接错误处理"""
        # 模拟连接失败
        mock_service_class.side_effect = Exception("Connection failed")
        
        # 测试自动发现
        result = auto_discover_databases('localhost', 3306, 'root', 'password')
        assert result is None
        
        # 测试表发现
        result = auto_discover_tables('localhost', 3306, 'root', 'password', 'test_db')
        assert result is None
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_export_error_handling(self, mock_service_class):
        """测试导出错误处理"""
        # 模拟服务抛出异常
        mock_service_class.side_effect = Exception("Export failed")
        
        # 测试导出
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'actual_used_devices.json')
            
            result = export_actual_used_devices(
                host='localhost',
                port=3306,
                user='root',
                password='password',
                database='yangguan',
                table='biz_device',
                output_path=output_path
            )
            
            # 验证失败处理
            assert result is False
            assert not os.path.exists(output_path)
    
    def test_file_system_error_handling(self):
        """测试文件系统错误处理"""
        # 测试无权限目录
        with patch('src.interfaces.cli.db_query_cli.os.makedirs', side_effect=PermissionError):
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = os.path.join(temp_dir, 'test.csv')
                
                # 应该抛出异常
                with pytest.raises(PermissionError):
                    export_to_csv([], output_path)


if __name__ == '__main__':
    pytest.main([__file__]) 