"""
JMeter执行器测试模块
测试JMeterExecutor的核心功能
"""
import os
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime

from src.infrastructure.jmeter.jmeter_executor import JMeterExecutor
from src.domain.entities.test_result import TestResult


class TestJMeterExecutor:
    """测试JMeterExecutor类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.jmeter_bin_path = "mock_jmeter_bin"
        self.executor = JMeterExecutor(self.jmeter_bin_path)
        
        # 测试参数
        self.jmx_path = "mock_test.jmx"
        self.iterations = 10
        self.output_dir = "mock_output"
        self.test_name = "test_performance"
        self.thread_count = 5
    
    def test_init(self):
        """测试初始化"""
        assert self.executor.jmeter_bin_path == self.jmeter_bin_path
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_success(self, mock_path, mock_subprocess_run):
        """测试成功执行测试"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.return_value.returncode = 0
        
        # 模拟JTL文件内容
        jtl_content = '''timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
1703123456789,123,HTTP Request,200,OK,Thread Group 1-1,text,true,,1024,512,1,1,http://localhost:8080/api/test,50,0,10
1703123456889,156,HTTP Request,200,OK,Thread Group 1-1,text,true,,1024,512,1,1,http://localhost:8080/api/test,45,0,12'''
        
        with patch('builtins.open', mock_open(read_data=jtl_content)):
            result = self.executor.execute_test(
                self.jmx_path, self.iterations, self.output_dir, 
                self.test_name, self.thread_count
            )
        
        # 验证结果
        assert isinstance(result, TestResult)
        assert result.test_name == self.test_name
        assert result.thread_count == self.thread_count
        assert result.iterations == self.iterations
        assert result.total_requests == 2
        assert result.success_count == 2
        assert result.fail_count == 0
        assert result.success_rate == 100.0
        
        # 验证subprocess被调用
        mock_subprocess_run.assert_called_once()
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_jmeter_failure(self, mock_path, mock_subprocess_run):
        """测试JMeter执行失败"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.return_value.returncode = 1
        
        # 执行测试
        result = self.executor.execute_test(
            self.jmx_path, self.iterations, self.output_dir, 
            self.test_name, self.thread_count
        )
        
        # 验证结果
        assert isinstance(result, TestResult)
        assert not result.success
        assert result.total_requests == 0
        assert result.success_count == 0
        assert result.fail_count == 0
        assert result.success_rate == 0.0
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_subprocess_exception(self, mock_path, mock_subprocess_run):
        """测试subprocess异常"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.side_effect = subprocess.SubprocessError("执行失败")
        
        # 执行测试
        result = self.executor.execute_test(
            self.jmx_path, self.iterations, self.output_dir, 
            self.test_name, self.thread_count
        )
        
        # 验证结果
        assert isinstance(result, TestResult)
        assert not result.success
        assert result.total_requests == 0
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_with_failed_requests(self, mock_path, mock_subprocess_run):
        """测试包含失败请求的情况"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.return_value.returncode = 0
        
        # 模拟包含失败请求的JTL文件内容
        jtl_content = '''timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
1703123456789,123,HTTP Request,200,OK,Thread Group 1-1,text,true,,1024,512,1,1,http://localhost:8080/api/test,50,0,10
1703123456889,156,HTTP Request,500,Internal Server Error,Thread Group 1-1,text,false,Server Error,1024,512,1,1,http://localhost:8080/api/test,45,0,12'''
        
        with patch('builtins.open', mock_open(read_data=jtl_content)):
            result = self.executor.execute_test(
                self.jmx_path, self.iterations, self.output_dir, 
                self.test_name, self.thread_count
            )
        
        # 验证结果
        assert result.total_requests == 2
        assert result.success_count == 1
        assert result.fail_count == 1
        assert result.success_rate == 50.0
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_empty_jtl_file(self, mock_path, mock_subprocess_run):
        """测试空JTL文件的情况"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.return_value.returncode = 0
        
        # 模拟空JTL文件
        with patch('builtins.open', mock_open(read_data="")):
            result = self.executor.execute_test(
                self.jmx_path, self.iterations, self.output_dir, 
                self.test_name, self.thread_count
            )
        
        # 验证结果
        assert result.total_requests == 0
        assert result.success_count == 0
        assert result.fail_count == 0
        assert result.success_rate == 0.0
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_malformed_jtl_file(self, mock_path, mock_subprocess_run):
        """测试格式错误的JTL文件"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.return_value.returncode = 0
        
        # 模拟格式错误的JTL文件
        jtl_content = '''invalid,format,file
no,proper,headers'''
        
        with patch('builtins.open', mock_open(read_data=jtl_content)):
            result = self.executor.execute_test(
                self.jmx_path, self.iterations, self.output_dir, 
                self.test_name, self.thread_count
            )
        
        # 验证结果（应该能够处理格式错误）
        assert isinstance(result, TestResult)
    
    def test_get_report_path(self):
        """测试获取报告路径"""
        result_file = "test_result.jtl"
        report_path = self.executor.get_report_path(result_file)
        
        expected_path = "report_test_result"
        assert report_path == expected_path
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_command_line_arguments(self, mock_path, mock_subprocess_run):
        """测试命令行参数构建"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.return_value.returncode = 0
        
        # 执行测试
        with patch('builtins.open', mock_open(read_data="")):
            self.executor.execute_test(
                self.jmx_path, self.iterations, self.output_dir, 
                self.test_name, self.thread_count
            )
        
        # 验证subprocess调用参数
        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args
        
        # 验证命令包含必要的参数
        command = call_args[0][0]
        assert self.jmeter_bin_path in command
        assert self.jmx_path in command
        assert "-l" in command  # 日志文件参数
        assert "-e" in command  # 生成报告参数
        assert "-o" in command  # 输出目录参数
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_timestamp_generation(self, mock_path, mock_subprocess_run):
        """测试时间戳生成"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.return_value.returncode = 0
        
        # 执行测试
        with patch('builtins.open', mock_open(read_data="")):
            result = self.executor.execute_test(
                self.jmx_path, self.iterations, self.output_dir, 
                self.test_name, self.thread_count
            )
        
        # 验证时间戳字段
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.duration >= 0
    
    @patch('src.infrastructure.jmeter.jmeter_executor.subprocess.run')
    @patch('src.infrastructure.jmeter.jmeter_executor.Path')
    def test_execute_test_response_time_calculation(self, mock_path, mock_subprocess_run):
        """测试响应时间计算"""
        # 设置模拟
        mock_path.return_value.mkdir.return_value = None
        mock_subprocess_run.return_value.returncode = 0
        
        # 模拟包含响应时间的JTL文件内容
        jtl_content = '''timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
1703123456789,100,HTTP Request,200,OK,Thread Group 1-1,text,true,,1024,512,1,1,http://localhost:8080/api/test,50,0,10
1703123456889,200,HTTP Request,200,OK,Thread Group 1-1,text,true,,1024,512,1,1,http://localhost:8080/api/test,45,0,12
1703123456989,150,HTTP Request,200,OK,Thread Group 1-1,text,true,,1024,512,1,1,http://localhost:8080/api/test,55,0,15'''
        
        with patch('builtins.open', mock_open(read_data=jtl_content)):
            result = self.executor.execute_test(
                self.jmx_path, self.iterations, self.output_dir, 
                self.test_name, self.thread_count
            )
        
        # 验证响应时间计算
        assert result.min_resp_time == 100.0
        assert result.max_resp_time == 200.0
        assert result.avg_resp_time == 150.0  # (100+200+150)/3


def mock_open(read_data=""):
    """模拟open函数"""
    mock_file = Mock()
    mock_file.read.return_value = read_data
    mock_file.__enter__.return_value = mock_file
    mock_file.__exit__.return_value = None
    return Mock(return_value=mock_file) 