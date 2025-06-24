"""
Pytest配置文件
提供测试环境和通用fixture
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, project_root)

# 测试配置
@pytest.fixture(scope="session")
def test_config():
    """测试配置fixture"""
    return {
        'jmeter': {
            'jmeter_bin': 'mock_jmeter_bin',
            'default_jmx': 'mock_test.jmx',
            'default_test_name': 'mock_test'
        },
        'test': {
            'thread_counts': [1, 2],
            'loop_counts': [1, 2],
            'ramp_up_time': 1
        },
        'output': {
            'base_dir': 'mock_output'
        }
    }

@pytest.fixture(scope="session")
def temp_test_dir():
    """临时测试目录fixture"""
    temp_dir = tempfile.mkdtemp(prefix="performance_test_")
    yield temp_dir
    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_jmx_file(temp_test_dir):
    """模拟JMX文件fixture"""
    jmx_content = '''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Test Plan" enabled="true">
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">1</stringProp>
        <stringProp name="ThreadGroup.ramp_time">1</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments">
              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">{"deviceSerialNumber":"TEST001","mac":"00:11:22:33:44:55"}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
                <boolProp name="HTTPArgument.use_equals">true</boolProp>
                <stringProp name="Argument.name">body</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.domain">localhost</stringProp>
          <stringProp name="HTTPSampler.port">8080</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/api/test</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>'''
    
    jmx_path = Path(temp_test_dir) / "mock_test.jmx"
    with open(jmx_path, 'w', encoding='utf-8') as f:
        f.write(jmx_content)
    return str(jmx_path)

@pytest.fixture
def mock_device_csv_file(temp_test_dir):
    """模拟设备CSV文件fixture"""
    csv_content = '''serial_number,mac_address,device_type,model
TEST001,00:11:22:33:44:55,terminal,model1
TEST002,00:11:22:33:44:56,terminal,model2'''
    
    csv_path = Path(temp_test_dir) / "mock_devices.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    return str(csv_path)

@pytest.fixture
def mock_jtl_file(temp_test_dir):
    """模拟JTL结果文件fixture"""
    jtl_content = '''timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
1703123456789,123,HTTP Request,200,OK,Thread Group 1-1,text,true,,1024,512,1,1,http://localhost:8080/api/test,50,0,10
1703123456889,156,HTTP Request,200,OK,Thread Group 1-1,text,true,,1024,512,1,1,http://localhost:8080/api/test,45,0,12'''
    
    jtl_path = Path(temp_test_dir) / "result.jtl"
    with open(jtl_path, 'w', encoding='utf-8') as f:
        f.write(jtl_content)
    return str(jtl_path)

@pytest.fixture
def mock_config_manager():
    """模拟配置管理器fixture"""
    with patch('src.config.config_manager.config_manager') as mock_config:
        mock_config.get_jmeter_config.return_value = {
            'jmeter': {
                'jmeter_bin': 'mock_jmeter_bin',
                'default_jmx': 'mock_test.jmx',
                'default_test_name': 'mock_test'
            },
            'test': {
                'thread_counts': [1, 2],
                'loop_counts': [1, 2],
                'ramp_up_time': 1
            },
            'output': {
                'base_dir': 'mock_output'
            }
        }
        mock_config.get_database_config.return_value = {
            'mysql': {
                'host': 'localhost',
                'port': 3306,
                'username': 'test_user',
                'password': 'test_pass',
                'database': 'test_db'
            }
        }
        yield mock_config

@pytest.fixture
def mock_performance_test_service():
    """模拟性能测试服务fixture"""
    with patch('src.application.services.performance_test_service.PerformanceTestService') as mock_service:
        mock_service.return_value.run_tests.return_value = [
            Mock(
                test_name='mock_test',
                thread_count=1,
                iterations=1,
                total_requests=10,
                success_count=9,
                fail_count=1,
                success_rate=90.0,
                min_resp_time=50.0,
                max_resp_time=200.0,
                avg_resp_time=100.0,
                tp90_resp_time=150.0,
                tp99_resp_time=180.0,
                duration=10.0,
                report_path='mock_report_path',
                success=True,
                server_cpu='50.0'
            )
        ]
        yield mock_service

@pytest.fixture
def mock_device_data_manager():
    """模拟设备数据管理器fixture"""
    with patch('src.application.services.device_data_manager.DeviceDataManager') as mock_manager:
        mock_manager.return_value.get_available_devices.return_value = 'mock_devices.csv'
        yield mock_manager

@pytest.fixture
def mock_register_verification_service():
    """模拟注册验证服务fixture"""
    with patch('src.application.services.register_verification_service.RegisterVerificationService') as mock_service:
        mock_service.return_value.verify_registration_results.return_value = {
            'total_registered': 10,
            'success_count': 9,
            'fail_count': 1,
            'verification_time': '2025-01-01 12:00:00'
        }
        yield mock_service

@pytest.fixture
def mock_report_service():
    """模拟报告服务fixture"""
    with patch('src.application.services.report_service.ReportService') as mock_service:
        mock_service.return_value.generate_external_report_from_results.return_value = 'mock_external_report.csv'
        mock_service.return_value.generate_internal_report_from_results.return_value = 'mock_internal_report.csv'
        mock_service.return_value.generate_multi_interface_excel_report.return_value = 'mock_excel_report.xlsx'
        yield mock_service

@pytest.fixture
def mock_performance_tuning_service():
    """模拟性能调优服务fixture"""
    with patch('src.application.services.performance_tuning_service.PerformanceTuningService') as mock_service:
        mock_service.return_value.analyze_and_tune.return_value = {
            'thread_count': 5,
            'loop_count': 10,
            'success_rate': 95.0,
            'avg_response_time': 150.0
        }
        yield mock_service

@pytest.fixture
def mock_db_query_cli():
    """模拟数据库查询CLI fixture"""
    with patch('src.interfaces.cli.performance_test_cli.export_actual_used_devices') as mock_export:
        mock_export.return_value = True
        yield mock_export

# 测试数据fixture
@pytest.fixture
def sample_test_results():
    """示例测试结果数据fixture"""
    return [
        Mock(
            test_name='register_test',
            thread_count=1,
            iterations=1,
            total_requests=10,
            success_count=9,
            fail_count=1,
            success_rate=90.0,
            min_resp_time=50.0,
            max_resp_time=200.0,
            avg_resp_time=100.0,
            tp90_resp_time=150.0,
            tp99_resp_time=180.0,
            duration=10.0,
            report_path='mock_report_path',
            success=True,
            server_cpu='50.0'
        ),
        Mock(
            test_name='heartbeat_test',
            thread_count=2,
            iterations=2,
            total_requests=20,
            success_count=19,
            fail_count=1,
            success_rate=95.0,
            min_resp_time=30.0,
            max_resp_time=150.0,
            avg_resp_time=80.0,
            tp90_resp_time=120.0,
            tp99_resp_time=140.0,
            duration=15.0,
            report_path='mock_heartbeat_report_path',
            success=True,
            server_cpu='60.0'
        )
    ]

# 命令行参数fixture
@pytest.fixture
def basic_cli_args():
    """基础命令行参数fixture"""
    return [
        '--thread-counts', '1', '2',
        '--loop-counts', '1', '2',
        '--test-type', 'register',
        '--test-name', 'test_performance'
    ]

@pytest.fixture
def all_tests_cli_args():
    """所有测试类型命令行参数fixture"""
    return [
        '--thread-counts', '1',
        '--loop-counts', '1',
        '--test-type', 'all',
        '--test-name', 'all_tests'
    ]

@pytest.fixture
def auto_tune_cli_args():
    """自动调优命令行参数fixture"""
    return [
        '--thread-counts', '1',
        '--loop-counts', '1',
        '--test-type', 'register',
        '--auto-tune',
        '--success-threshold', '95.0',
        '--max-avg-resp-ms', '2000.0'
    ]

@pytest.fixture
def sync_devices_cli_args():
    """同步设备命令行参数fixture"""
    return [
        '--sync-actual-devices'
    ] 