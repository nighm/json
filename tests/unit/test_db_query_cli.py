"""
db_query_cli.py 单元测试
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 导入被测试的模块
from src.interfaces.cli.db_query_cli import (
    export_to_csv,
    export_to_json,
    auto_discover_databases,
    auto_discover_tables,
    export_actual_used_devices,
    DateTimeEncoder
)


class TestDateTimeEncoder:
    """测试DateTimeEncoder类"""
    
    def test_default_with_datetime(self):
        """测试datetime对象的序列化"""
        encoder = DateTimeEncoder()
        dt = datetime(2025, 1, 1, 12, 0, 0)
        result = encoder.default(dt)
        assert result == "2025-01-01T12:00:00"
    
    def test_default_with_other_object(self):
        """测试其他对象的序列化"""
        encoder = DateTimeEncoder()
        obj = "test_string"
        with pytest.raises(TypeError):
            encoder.default(obj)


class TestExportFunctions:
    """测试导出功能"""
    
    def test_export_to_csv_with_devices(self):
        """测试CSV导出功能"""
        # 创建模拟设备对象
        mock_device1 = Mock()
        mock_device1.__dict__ = {
            'id': 1,
            'name': '设备001',
            'brand': '华为',
            'status': 'active'
        }
        
        mock_device2 = Mock()
        mock_device2.__dict__ = {
            'id': 2,
            'name': '设备002',
            'brand': '小米',
            'status': 'inactive'
        }
        
        devices = [mock_device1, mock_device2]
        
        # 测试导出
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.interfaces.cli.db_query_cli.os.makedirs'):
                with patch('src.interfaces.cli.db_query_cli.os.path.join', return_value=os.path.join(temp_dir, 'test.csv')):
                    result = export_to_csv(devices, 'test.csv')
                    
                    # 验证文件创建
                    assert 'test.csv' in result
                    assert os.path.exists(result)
                    
                    # 验证文件内容
                    with open(result, 'r', encoding='utf-8') as f:
                        content = f.read()
                        assert 'id,name,brand,status' in content
                        assert '1,设备001,华为,active' in content
                        assert '2,设备002,小米,inactive' in content
    
    def test_export_to_csv_with_empty_devices(self):
        """测试空设备列表的CSV导出"""
        devices = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.interfaces.cli.db_query_cli.os.makedirs'):
                with patch('src.interfaces.cli.db_query_cli.os.path.join', return_value=os.path.join(temp_dir, 'empty.csv')):
                    result = export_to_csv(devices, 'empty.csv')
                    
                    # 验证文件创建
                    assert os.path.exists(result)
                    
                    # 验证文件为空（只有表头）
                    with open(result, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        assert content == ''  # 没有设备时应该为空
    
    def test_export_to_json_with_devices(self):
        """测试JSON导出功能"""
        # 创建模拟设备对象
        mock_device1 = Mock()
        mock_device1.__dict__ = {
            'id': 1,
            'name': '设备001',
            'brand': '华为',
            'status': 'active',
            'created_at': datetime(2025, 1, 1, 12, 0, 0)
        }
        
        mock_device2 = Mock()
        mock_device2.__dict__ = {
            'id': 2,
            'name': '设备002',
            'brand': '小米',
            'status': None  # 测试None值处理
        }
        
        devices = [mock_device1, mock_device2]
        
        # 测试导出
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.interfaces.cli.db_query_cli.os.makedirs'):
                with patch('src.interfaces.cli.db_query_cli.os.path.join', return_value=os.path.join(temp_dir, 'test.json')):
                    result = export_to_json(devices, 'test.json')
                    
                    # 验证文件创建
                    assert 'test.json' in result
                    assert os.path.exists(result)
                    
                    # 验证文件内容
                    with open(result, 'r', encoding='utf-8') as f:
                        content = f.read()
                        assert '"id": 1' in content
                        assert '"name": "设备001"' in content
                        assert '"brand": "华为"' in content
                        assert '"status": "active"' in content
                        assert '"status": ""' in content  # None值应该转换为空字符串
                        assert '"created_at": "2025-01-01T12:00:00"' in content
    
    def test_export_to_json_with_none_values(self):
        """测试JSON导出中的None值处理"""
        mock_device = Mock()
        mock_device.__dict__ = {
            'id': 1,
            'name': None,
            'brand': '华为',
            'description': None
        }
        
        devices = [mock_device]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.interfaces.cli.db_query_cli.os.makedirs'):
                with patch('src.interfaces.cli.db_query_cli.os.path.join', return_value=os.path.join(temp_dir, 'test.json')):
                    result = export_to_json(devices, 'test.json')
                    
                    with open(result, 'r', encoding='utf-8') as f:
                        content = f.read()
                        assert '"name": ""' in content  # None值应该转换为空字符串
                        assert '"description": ""' in content


class TestAutoDiscoverFunctions:
    """测试自动发现功能"""
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_auto_discover_databases_success(self, mock_service_class):
        """测试成功发现数据库"""
        # 模拟服务
        mock_service = Mock()
        mock_service.discover_databases.return_value = ['yangguan', 'test_db', 'other_db']
        mock_service_class.return_value = mock_service
        
        # 测试发现
        result = auto_discover_databases('localhost', 3306, 'root', 'password')
        
        # 验证结果
        assert result == 'yangguan'  # 应该返回第一个匹配的数据库
        
        # 验证服务调用
        mock_service.discover_databases.assert_called_once()
        mock_service.close.assert_called_once()
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_auto_discover_databases_no_device_db(self, mock_service_class):
        """测试没有发现设备数据库"""
        # 模拟服务
        mock_service = Mock()
        mock_service.discover_databases.return_value = ['test_db', 'other_db']
        mock_service_class.return_value = mock_service
        
        # 测试发现
        result = auto_discover_databases('localhost', 3306, 'root', 'password')
        
        # 验证结果
        assert result == 'test_db'  # 应该返回第一个数据库
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_auto_discover_databases_failure(self, mock_service_class):
        """测试数据库发现失败"""
        # 模拟服务抛出异常
        mock_service_class.side_effect = Exception("Connection failed")
        
        # 测试发现
        result = auto_discover_databases('localhost', 3306, 'root', 'password')
        
        # 验证结果
        assert result is None
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_auto_discover_tables_success(self, mock_service_class):
        """测试成功发现表"""
        # 模拟服务
        mock_service = Mock()
        mock_service.discover_tables.return_value = ['biz_device', 'user_info', 'other_table']
        mock_service_class.return_value = mock_service
        
        # 测试发现
        result = auto_discover_tables('localhost', 3306, 'root', 'password', 'yangguan')
        
        # 验证结果
        assert result == 'biz_device'  # 应该返回第一个匹配的表
        
        # 验证服务调用
        mock_service.discover_tables.assert_called_once()
        mock_service.close.assert_called_once()
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_auto_discover_tables_no_device_table(self, mock_service_class):
        """测试没有发现设备表"""
        # 模拟服务
        mock_service = Mock()
        mock_service.discover_tables.return_value = ['user_info', 'other_table']
        mock_service_class.return_value = mock_service
        
        # 测试发现
        result = auto_discover_tables('localhost', 3306, 'root', 'password', 'yangguan')
        
        # 验证结果
        assert result == 'user_info'  # 应该返回第一个表


class TestExportActualUsedDevices:
    """测试实际使用设备导出功能"""
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_export_actual_used_devices_success(self, mock_service_class):
        """测试成功导出实际使用设备"""
        # 模拟服务
        mock_service = Mock()
        mock_device1 = Mock()
        mock_device1.deviceSerialNumber = "SN001"
        mock_device1.mac = "00:11:22:33:44:55"
        mock_device1.macs = "00:11:22:33:44:55,66:77:88:99:AA:BB"
        mock_device1.device_id = "DEV001"
        
        mock_device2 = Mock()
        mock_device2.deviceSerialNumber = "SN002"
        mock_device2.mac = "AA:BB:CC:DD:EE:FF"
        mock_device2.macs = None
        mock_device2.device_id = "DEV002"
        
        mock_service.get_device_count.return_value = 2
        mock_service.get_devices.return_value = [mock_device1, mock_device2]
        mock_service_class.return_value = mock_service
        
        # 测试导出
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'actual_used_devices.json')
            
            with patch('src.interfaces.cli.db_query_cli.os.makedirs'):
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
                import json
                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 验证结构
                    assert 'actual_registrations' in data
                    assert 'verification_results' in data
                    assert 'last_verification_time' in data
                    assert 'verification_history' in data
                    
                    # 验证数据
                    registrations = data['actual_registrations']
                    assert 'SN001' in registrations['deviceSerialNumbers']
                    assert 'SN002' in registrations['deviceSerialNumbers']
                    assert '00:11:22:33:44:55' in registrations['mac']
                    assert 'AA:BB:CC:DD:EE:FF' in registrations['mac']
                    assert '00:11:22:33:44:55,66:77:88:99:AA:BB' in registrations['macs']
                    assert 'DEV001' in registrations['device_ids']
                    assert 'DEV002' in registrations['device_ids']
                    
                    # 验证统计
                    verification = data['verification_results']
                    assert verification['actual_count'] == 2
                    assert verification['theoretical_count'] == 0
                    assert verification['success_rate'] == 0.0
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_export_actual_used_devices_no_devices(self, mock_service_class):
        """测试没有设备时的导出"""
        # 模拟服务
        mock_service = Mock()
        mock_service.get_device_count.return_value = 0
        mock_service.get_devices.return_value = []
        mock_service_class.return_value = mock_service
        
        # 测试导出
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'actual_used_devices.json')
            
            with patch('src.interfaces.cli.db_query_cli.os.makedirs'):
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
                assert result is False
                assert not os.path.exists(output_path)
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_export_actual_used_devices_failure(self, mock_service_class):
        """测试导出失败"""
        # 模拟服务抛出异常
        mock_service_class.side_effect = Exception("Database error")
        
        # 测试导出
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'actual_used_devices.json')
            
            with patch('src.interfaces.cli.db_query_cli.os.makedirs'):
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
                assert result is False


class TestCLIArgumentParsing:
    """测试命令行参数解析"""
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    @patch('src.interfaces.cli.db_query_cli.auto_discover_databases')
    @patch('src.interfaces.cli.db_query_cli.auto_discover_tables')
    def test_cli_with_auto_discover(self, mock_discover_tables, mock_discover_databases, mock_service_class):
        """测试自动发现模式的CLI"""
        # 模拟自动发现
        mock_discover_databases.return_value = 'yangguan'
        mock_discover_tables.return_value = 'biz_device'
        
        # 模拟服务
        mock_service = Mock()
        mock_device = Mock()
        mock_device.__dict__ = {'id': 1, 'name': 'test'}
        mock_service.get_devices.return_value = [mock_device]
        mock_service_class.return_value = mock_service
        
        # 模拟命令行参数
        with patch('sys.argv', ['db_query_cli.py', '--auto-discover', '--limit', '5']):
            from src.interfaces.cli.db_query_cli import main
            main()
            
            # 验证调用
            mock_discover_databases.assert_called_once()
            mock_discover_tables.assert_called_once()
            mock_service.get_devices.assert_called_once()
    
    @patch('src.interfaces.cli.db_query_cli.DeviceQueryService')
    def test_cli_with_export_options(self, mock_service_class):
        """测试导出选项的CLI"""
        # 模拟服务
        mock_service = Mock()
        mock_device = Mock()
        mock_device.__dict__ = {'id': 1, 'name': 'test'}
        mock_service.get_devices.return_value = [mock_device]
        mock_service_class.return_value = mock_service
        
        # 模拟命令行参数
        with patch('sys.argv', ['db_query_cli.py', '--export-csv', '--export-json', '--output-file', 'test']):
            with patch('src.interfaces.cli.db_query_cli.export_to_csv') as mock_csv:
                with patch('src.interfaces.cli.db_query_cli.export_to_json') as mock_json:
                    from src.interfaces.cli.db_query_cli import main
                    main()
                    
                    # 验证导出调用
                    mock_csv.assert_called_once()
                    mock_json.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__]) 