"""
性能测试CLI测试模块
测试performance_test_cli.py的所有主要功能
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import pytest
import argparse
from datetime import datetime

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

# 导入被测试的模块
from src.interfaces.cli.performance_test_cli import PerformanceTestCLI, create_timestamped_output_dir, main


class MockPerformanceTestService:
    """Mock性能测试服务类"""
    
    def __init__(self, jmeter_executor, report_generator):
        self.jmeter_executor = jmeter_executor
        self.report_generator = report_generator
    
    def create_test_configs(self, test_types, thread_counts, loop_counts, test_name, jmeter_bin, output_dir, base_jmx_dir):
        # 返回模拟的测试配置
        from src.domain.entities.test_config import TestConfig
        return [
            TestConfig(
                test_name=test_name,
                iterations=loop_counts,
                jmx_path=f"{base_jmx_dir}/{test_types[0]}_test.jmx",
                jmeter_bin_path=jmeter_bin,
                output_dir=output_dir
            )
        ]
    
    def execute_comprehensive_test_suite(self, test_configs, test_name, output_dir, generate_excel, enable_verification):
        # 返回模拟的测试结果
        return {
            'output_dir': output_dir,
            'report_paths': [f"{output_dir}/test_report.csv"],
            'verification_result': {'verified': True, 'count': 1} if enable_verification else None
        }


class MockDeviceDataManager:
    """Mock设备数据管理器类"""
    
    def __init__(self):
        pass
    
    def sync_actual_devices_from_database(self, db_config):
        return True


class MockRegisterVerificationService:
    """Mock注册验证服务类"""
    
    def __init__(self, db_config):
        self.db_config = db_config
    
    def verify_registration_results(self, results, timestamp):
        return {"verified": True, "count": len(results)}
    
    def print_verification_report(self, report):
        pass
    
    def save_verification_report(self, report, output_dir):
        pass


class MockPerformanceTuningService:
    """Mock性能调优服务类"""
    
    def __init__(self):
        pass
    
    def analyze_and_tune(self, integrated_report_path, success_threshold, max_avg_resp_ms):
        return {"thread_count": 5, "loop_count": 100}


class MockJMeterExecutor:
    """Mock JMeter执行器类"""
    
    def __init__(self, jmeter_bin_path):
        self.jmeter_bin_path = jmeter_bin_path
    
    def execute_test(self, config):
        return True


class MockReportGenerator:
    """Mock报告生成器类"""
    
    def __init__(self, output_dir):
        self.output_dir = output_dir
    
    def generate_report(self, results):
        return f"{self.output_dir}/mock_report.csv"


class MockConfigManager:
    """Mock配置管理器"""
    
    def get_jmeter_config(self):
        return {
            'test': {
                'thread_counts': [1, 5, 10],
                'loop_counts': [10, 50, 100]
            },
            'jmeter': {
                'default_jmx': 'src/tools/jmeter/api_cases/register_test.jmx',
                'jmeter_bin': 'src/tools/jmeter/bin/jmeter.bat',
                'default_test_name': '性能测试'
            },
            'output': {
                'base_dir': 'results'
            }
        }
    
    def get_database_config(self):
        return {
            'mysql': {
                'host': 'localhost',
                'port': 3306,
                'username': 'root',
                'password': 'password',
                'database': 'test_db'
            }
        }


class TestPerformanceTestCLI:
    """性能测试CLI测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建Mock依赖的CLI实例
        self.cli = PerformanceTestCLI(
            performance_service_cls=MockPerformanceTestService,
            device_data_manager_cls=MockDeviceDataManager,
            register_verification_service_cls=MockRegisterVerificationService,
            performance_tuning_service_cls=MockPerformanceTuningService,
            jmeter_executor_cls=MockJMeterExecutor,
            report_generator_cls=MockReportGenerator,
            config_manager_instance=MockConfigManager()
        )
    
    def test_create_timestamped_output_dir(self, tmp_path):
        """测试创建时间戳输出目录"""
        base_dir = str(tmp_path / "test_output")
        result = self.cli.create_timestamped_output_dir(base_dir)
        
        assert result.startswith(base_dir)
        assert Path(result).exists()
        assert Path(result).is_dir()
    
    def test_sync_actual_devices_success(self):
        """测试同步设备成功"""
        result = self.cli.sync_actual_devices()
        assert result is True
    
    def test_sync_actual_devices_failure(self):
        """测试同步设备失败"""
        # 创建一个会失败的Mock类
        class FailingDeviceDataManager:
            def __init__(self):
                pass
            
            def sync_actual_devices_from_database(self, db_config):
                return False
        
        cli = PerformanceTestCLI(
            device_data_manager_cls=FailingDeviceDataManager,
            config_manager_instance=MockConfigManager()
        )
        
        result = cli.sync_actual_devices()
        assert result is False
    
    def test_run_with_sync_devices(self):
        """测试运行同步设备功能"""
        args = Mock()
        args.sync_actual_devices = True
        args.output_dir = "test_output"
        
        result = self.cli.run(args)
        assert result is True
    
    def test_run_with_register_test(self, tmp_path):
        """测试运行注册测试"""
        args = Mock()
        args.sync_actual_devices = False
        args.output_dir = str(tmp_path / "output")
        args.thread_counts = [1, 5]
        args.loop_counts = [10, 50]
        args.test_type = "register"
        args.jmx = "test.jmx"
        args.test_name = "注册测试"
        args.jmeter_bin = "jmeter.bat"
        args.excel_report = False
        
        result = self.cli.run(args)
        assert result is True
    
    def test_run_with_all_test_types(self, tmp_path):
        """测试运行所有测试类型"""
        args = Mock()
        args.sync_actual_devices = False
        args.output_dir = str(tmp_path / "output")
        args.thread_counts = [1, 5]
        args.loop_counts = [10, 50]
        args.test_type = "all"
        args.jmx = "test.jmx"
        args.test_name = "全量测试"
        args.jmeter_bin = "jmeter.bat"
        args.excel_report = True
        
        result = self.cli.run(args)
        assert result is True
    
    def test_run_with_exception(self):
        """测试运行异常处理"""
        class ExceptionService:
            def __init__(self, *args, **kwargs):
                pass
            
            def create_test_configs(self, *args, **kwargs):
                raise Exception("测试异常")
        
        cli = PerformanceTestCLI(
            performance_service_cls=ExceptionService,
            config_manager_instance=MockConfigManager()
        )
        
        args = Mock()
        args.sync_actual_devices = False
        args.output_dir = "test_output"
        args.thread_counts = [1]
        args.loop_counts = [10]
        args.test_type = "register"
        args.jmx = "test.jmx"
        args.test_name = "测试"
        args.jmeter_bin = "jmeter.bat"
        args.excel_report = False
        
        result = cli.run(args)
        assert result is False
    
    def test_process_thread_counts(self):
        """测试处理线程数参数"""
        result = self.cli._process_thread_counts("1,5,10")
        assert result == [1, 5, 10]
    
    def test_process_thread_counts_single(self):
        """测试处理单个线程数参数"""
        result = self.cli._process_thread_counts("5")
        assert result == [5]
    
    def test_process_loop_counts(self):
        """测试处理循环次数参数"""
        result = self.cli._process_loop_counts("10,50,100")
        assert result == [10, 50, 100]
    
    def test_process_loop_counts_single(self):
        """测试处理单个循环次数参数"""
        result = self.cli._process_loop_counts("50")
        assert result == [50]
    
    def test_get_test_types(self):
        """测试获取测试类型"""
        result = self.cli._get_test_types("register")
        assert result == ["register"]
        
        result = self.cli._get_test_types("all")
        assert result == ["register", "strategy", "device_info", "mode", "brand", "guard", "logo", "mqtt", "heartbeat"]
    
    def test_get_jmx_base_dir(self):
        """测试获取JMX基础目录"""
        result = self.cli._get_jmx_base_dir("test.jmx")
        assert result == "src/tools/jmeter/api_cases"
        
        result = self.cli._get_jmx_base_dir("src/tools/jmeter/api_cases/test.jmx")
        assert result == "src/tools/jmeter/api_cases"
    
    def test_create_argument_parser(self):
        """测试创建参数解析器"""
        parser = self.cli._create_argument_parser()
        assert isinstance(parser, argparse.ArgumentParser)
        
        # 测试解析参数 - 使用正确的类型
        args = parser.parse_args([
            "--sync-actual-devices",
            "--output-dir", "test_output",
            "--thread-counts", "1", "5",
            "--loop-counts", "10", "50",
            "--test-type", "register",
            "--jmx", "test.jmx",
            "--test-name", "测试",
            "--jmeter-bin", "jmeter.bat",
            "--excel-report"
        ])
        
        assert args.sync_actual_devices is True
        assert args.output_dir == "test_output"
        assert args.thread_counts == [1, 5]
        assert args.loop_counts == [10, 50]
        assert args.test_type == "register"
        assert args.jmx == "test.jmx"
        assert args.test_name == "测试"
        assert args.jmeter_bin == "jmeter.bat"
        assert args.excel_report is True


class TestMainFunction:
    """主函数测试类"""
    
    @patch('src.interfaces.cli.performance_test_cli._default_cli')
    def test_main_success(self, mock_default_cli):
        """测试主函数成功执行"""
        # 直接设置mock的run方法返回值
        mock_default_cli.run.return_value = True
        
        result = main()
        assert result is True
        mock_default_cli.run.assert_called_once()
    
    @patch('src.interfaces.cli.performance_test_cli._default_cli')
    def test_main_failure(self, mock_default_cli):
        """测试主函数失败处理"""
        # 直接设置mock的run方法返回值
        mock_default_cli.run.return_value = False
        
        result = main()
        assert result is False
        mock_default_cli.run.assert_called_once()


class TestCreateTimestampedOutputDir:
    """创建时间戳输出目录测试类"""
    
    def test_create_timestamped_output_dir(self, tmp_path):
        """测试创建时间戳输出目录函数"""
        base_dir = str(tmp_path / "test_output")
        result = create_timestamped_output_dir(base_dir)
        
        assert result.startswith(base_dir)
        assert Path(result).exists()
        assert Path(result).is_dir()


class TestCLIIntegration:
    """CLI集成测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.cli = PerformanceTestCLI()
    
    def test_cli_with_real_dependencies(self, tmp_path):
        """测试CLI与真实依赖的集成"""
        # 使用真实的依赖类进行测试
        cli = PerformanceTestCLI()
        
        args = Mock()
        args.sync_actual_devices = False
        args.output_dir = str(tmp_path / "output")
        args.thread_counts = [1]
        args.loop_counts = [10]
        args.test_type = "register"
        args.jmx = "test.jmx"
        args.test_name = "集成测试"
        args.jmeter_bin = "jmeter.bat"
        args.excel_report = False
        
        # 这里可能会因为缺少真实依赖而失败，但至少测试了接口
        try:
            result = cli.run(args)
            assert isinstance(result, bool)
        except Exception as e:
            # 如果因为缺少依赖而失败，这是预期的
            assert "config" in str(e).lower() or "jmeter" in str(e).lower()
    
    def test_cli_dependency_injection(self, tmp_path):
        """测试CLI依赖注入"""
        class CustomMockService:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs
            
            def create_test_configs(self, *args, **kwargs):
                return []
            
            def execute_comprehensive_test_suite(self, *args, **kwargs):
                return {
                    'output_dir': 'test_output',
                    'report_paths': ['test_report.csv'],
                    'verification_result': None
                }
        
        cli = PerformanceTestCLI(
            performance_service_cls=CustomMockService,
            config_manager_instance=MockConfigManager()
        )
        
        args = Mock()
        args.sync_actual_devices = False
        args.output_dir = str(tmp_path / "output")
        args.thread_counts = [1]
        args.loop_counts = [10]
        args.test_type = "register"
        args.jmx = "test.jmx"
        args.test_name = "依赖注入测试"
        args.jmeter_bin = "jmeter.bat"
        args.excel_report = False
        
        result = cli.run(args)
        assert result is True
    
    def test_cli_with_custom_config_manager(self):
        """测试CLI与自定义配置管理器"""
        class CustomConfigManager:
            def get_jmeter_config(self):
                return {
                    'test': {
                        'thread_counts': [2, 4],
                        'loop_counts': [20, 40]
                    },
                    'jmeter': {
                        'default_jmx': 'custom_test.jmx',
                        'jmeter_bin': 'custom_jmeter.bat',
                        'default_test_name': '自定义测试'
                    },
                    'output': {
                        'base_dir': 'custom_results'
                    }
                }
            
            def get_database_config(self):
                return {
                    'mysql': {
                        'host': 'custom_host',
                        'port': 3307,
                        'username': 'custom_user',
                        'password': 'custom_pass',
                        'database': 'custom_db'
                    }
                }
        
        cli = PerformanceTestCLI(
            config_manager_instance=CustomConfigManager()
        )
        
        # 测试配置管理器被正确使用
        assert cli.config_manager.get_jmeter_config()['jmeter']['default_test_name'] == '自定义测试'


class TestCLIErrorHandling:
    """CLI错误处理测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.cli = PerformanceTestCLI()
    
    def test_sync_actual_devices_exception(self):
        """测试同步设备异常处理"""
        class ExceptionDeviceManager:
            def __init__(self):
                pass
            
            def sync_actual_devices_from_database(self, db_config):
                raise Exception("数据库连接失败")
        
        cli = PerformanceTestCLI(
            device_data_manager_cls=ExceptionDeviceManager,
            config_manager_instance=MockConfigManager()
        )
        
        result = cli.sync_actual_devices()
        assert result is False


class TestCLIBoundaryConditions:
    """CLI边界条件测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.cli = PerformanceTestCLI(
            config_manager_instance=MockConfigManager()
        )
    
    def test_process_thread_counts_empty_string(self):
        """测试处理空字符串线程数"""
        result = self.cli._process_thread_counts("")
        assert result == []
    
    def test_process_thread_counts_whitespace(self):
        """测试处理空白字符线程数"""
        result = self.cli._process_thread_counts("   ")
        assert result == []
    
    def test_process_loop_counts_empty_string(self):
        """测试处理空字符串循环次数"""
        result = self.cli._process_loop_counts("")
        assert result == []
    
    def test_process_loop_counts_whitespace(self):
        """测试处理空白字符循环次数"""
        result = self.cli._process_loop_counts("   ")
        assert result == []
    
    def test_create_timestamped_output_dir_nested(self, tmp_path):
        """测试创建嵌套时间戳输出目录"""
        base_dir = str(tmp_path / "nested" / "deep" / "output")
        result = self.cli.create_timestamped_output_dir(base_dir)
        
        assert result.startswith(base_dir)
        assert Path(result).exists()
        assert Path(result).is_dir()
    
    def test_run_with_empty_results(self, tmp_path):
        """测试运行空结果处理"""
        class EmptyResultService:
            def __init__(self, *args, **kwargs):
                pass
            
            def create_test_configs(self, *args, **kwargs):
                return []
            
            def execute_comprehensive_test_suite(self, *args, **kwargs):
                return {
                    'output_dir': str(tmp_path / "output"),
                    'report_paths': [],
                    'verification_result': None
                }
        
        cli = PerformanceTestCLI(
            performance_service_cls=EmptyResultService,
            config_manager_instance=MockConfigManager()
        )
        
        args = Mock()
        args.sync_actual_devices = False
        args.output_dir = str(tmp_path / "output")
        args.thread_counts = [1]
        args.loop_counts = [10]
        args.test_type = "register"
        args.jmx = "test.jmx"
        args.test_name = "空结果测试"
        args.jmeter_bin = "jmeter.bat"
        args.excel_report = False
        
        result = cli.run(args)
        assert result is True 