"""
性能测试服务测试模块
测试PerformanceTestService的核心功能
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.application.services.performance_test_service import PerformanceTestService
from src.domain.entities.test_config import TestConfig
from src.domain.entities.test_result import TestResult


class TestPerformanceTestService:
    """测试PerformanceTestService类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_jmeter_executor = Mock()
        self.mock_report_generator = Mock()
        self.service = PerformanceTestService(self.mock_jmeter_executor, self.mock_report_generator)
        
        # 创建测试配置
        self.test_config = TestConfig(
            test_name="test_performance",
            iterations=[1, 2],
            jmx_path="mock_test.jmx",
            jmeter_bin_path="mock_jmeter_bin",
            output_dir="mock_output"
        )
    
    def test_init(self):
        """测试初始化"""
        assert self.service.jmeter_executor == self.mock_jmeter_executor
        assert self.service.report_generator == self.mock_report_generator
    
    @patch('src.application.services.performance_test_service.TestLogger')
    @patch('src.application.services.performance_test_service.config_manager')
    @patch('src.application.services.performance_test_service.JMXHandler')
    @patch('src.application.services.performance_test_service.TestAnalyzer')
    def test_run_tests_success(self, mock_analyzer_class, mock_jmx_handler_class, 
                              mock_config_manager, mock_logger_class):
        """测试成功运行测试"""
        # 设置模拟
        mock_config_manager.get_jmeter_config.return_value = {
            'test': {
                'thread_counts': [1, 2],
                'loop_counts': [1, 2],
                'ramp_up_time': 1
            }
        }
        
        mock_jmx_handler = Mock()
        mock_jmx_handler_class.return_value = mock_jmx_handler
        
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_test_results.return_value = {
            'success_rate': 95.0,
            'avg_response_time': 100.0
        }
        
        # 模拟测试结果
        mock_result = Mock()
        mock_result.duration = 10.0
        mock_result.report_path = "mock_report_path"
        self.mock_jmeter_executor.execute_test.return_value = mock_result
        
        # 执行测试
        results = self.service.run_tests(self.test_config)
        
        # 验证结果
        assert len(results) == 4  # 2个线程数 * 2个循环次数
        assert all(isinstance(result, Mock) for result in results)
        
        # 验证JMeter执行器被调用
        assert self.mock_jmeter_executor.execute_test.call_count == 4
        
        # 验证JMX处理器被调用
        assert mock_jmx_handler.update_thread_group.call_count == 4
        assert mock_jmx_handler.save.call_count == 4
    
    @patch('src.application.services.performance_test_service.TestLogger')
    @patch('src.application.services.performance_test_service.config_manager')
    @patch('src.application.services.performance_test_service.JMXHandler')
    def test_run_tests_jmeter_execution_failure(self, mock_jmx_handler_class, 
                                               mock_config_manager, mock_logger_class):
        """测试JMeter执行失败的情况"""
        # 设置模拟
        mock_config_manager.get_jmeter_config.return_value = {
            'test': {
                'thread_counts': [1],
                'loop_counts': [1],
                'ramp_up_time': 1
            }
        }
        
        mock_jmx_handler = Mock()
        mock_jmx_handler_class.return_value = mock_jmx_handler
        
        # 模拟JMeter执行失败
        self.mock_jmeter_executor.execute_test.side_effect = Exception("JMeter执行失败")
        
        # 执行测试
        results = self.service.run_tests(self.test_config)
        
        # 验证结果为空（因为执行失败）
        assert len(results) == 0
    
    @patch('src.application.services.performance_test_service.TestLogger')
    @patch('src.application.services.performance_test_service.config_manager')
    def test_run_tests_empty_config(self, mock_config_manager, mock_logger_class):
        """测试空配置的情况"""
        # 设置空配置
        mock_config_manager.get_jmeter_config.return_value = {
            'test': {
                'thread_counts': [],
                'loop_counts': [],
                'ramp_up_time': 1
            }
        }
        
        # 执行测试
        results = self.service.run_tests(self.test_config)
        
        # 验证结果为空
        assert len(results) == 0
    
    @patch('src.application.services.performance_test_service.TestLogger')
    @patch('src.application.services.performance_test_service.config_manager')
    @patch('src.application.services.performance_test_service.JMXHandler')
    @patch('src.application.services.performance_test_service.TestAnalyzer')
    def test_run_tests_with_analysis_failure(self, mock_analyzer_class, mock_jmx_handler_class,
                                           mock_config_manager, mock_logger_class):
        """测试分析失败的情况"""
        # 设置模拟
        mock_config_manager.get_jmeter_config.return_value = {
            'test': {
                'thread_counts': [1],
                'loop_counts': [1],
                'ramp_up_time': 1
            }
        }
        
        mock_jmx_handler = Mock()
        mock_jmx_handler_class.return_value = mock_jmx_handler
        
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_test_results.side_effect = Exception("分析失败")
        
        # 模拟测试结果
        mock_result = Mock()
        mock_result.duration = 10.0
        mock_result.report_path = "mock_report_path"
        self.mock_jmeter_executor.execute_test.return_value = mock_result
        
        # 执行测试
        results = self.service.run_tests(self.test_config)
        
        # 验证结果仍然返回（即使分析失败）
        assert len(results) == 1
    
    @patch('src.application.services.performance_test_service.TestLogger')
    @patch('src.application.services.performance_test_service.config_manager')
    def test_run_tests_logging(self, mock_config_manager, mock_logger_class):
        """测试日志记录功能"""
        # 设置模拟
        mock_config_manager.get_jmeter_config.return_value = {
            'test': {
                'thread_counts': [1],
                'loop_counts': [1],
                'ramp_up_time': 1
            }
        }
        
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger
        
        # 模拟测试结果
        mock_result = Mock()
        mock_result.duration = 10.0
        mock_result.report_path = "mock_report_path"
        self.mock_jmeter_executor.execute_test.return_value = mock_result
        
        # 执行测试
        self.service.run_tests(self.test_config)
        
        # 验证日志记录
        mock_logger.info.assert_called()
        assert any("开始执行测试" in str(call) for call in mock_logger.info.call_args_list)
    
    def test_run_tests_invalid_config(self):
        """测试无效配置"""
        # 使用None配置
        with pytest.raises(Exception):
            self.service.run_tests(None)
    
    @patch('src.application.services.performance_test_service.TestLogger')
    @patch('src.application.services.performance_test_service.config_manager')
    def test_run_tests_missing_config_sections(self, mock_config_manager, mock_logger_class):
        """测试缺少配置节的情况"""
        # 设置不完整的配置
        mock_config_manager.get_jmeter_config.return_value = {}
        
        # 执行测试应该抛出异常
        with pytest.raises(KeyError):
            self.service.run_tests(self.test_config) 