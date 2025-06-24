"""
测试配置实体测试模块
测试TestConfig实体的功能
"""
import pytest
from pathlib import Path

from src.domain.entities.test_config import TestConfig


class TestTestConfig:
    """测试TestConfig实体"""
    
    def test_init_with_valid_parameters(self):
        """测试使用有效参数初始化"""
        config = TestConfig(
            test_name="test_performance",
            iterations=[1, 2, 3],
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        assert config.test_name == "test_performance"
        assert config.iterations == [1, 2, 3]
        assert config.jmx_path == "test.jmx"
        assert config.jmeter_bin_path == "jmeter.bin"
        assert config.output_dir == "output"
    
    def test_init_with_single_iteration(self):
        """测试使用单个迭代次数初始化"""
        config = TestConfig(
            test_name="test_performance",
            iterations=5,
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        assert config.iterations == [5]
    
    def test_init_with_empty_iterations(self):
        """测试使用空迭代次数初始化"""
        config = TestConfig(
            test_name="test_performance",
            iterations=[],
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        assert config.iterations == []
    
    def test_str_representation(self):
        """测试字符串表示"""
        config = TestConfig(
            test_name="test_performance",
            iterations=[1, 2],
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        str_repr = str(config)
        assert "test_performance" in str_repr
        assert "test.jmx" in str_repr
        assert "output" in str_repr
    
    def test_repr_representation(self):
        """测试repr表示"""
        config = TestConfig(
            test_name="test_performance",
            iterations=[1, 2],
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        repr_str = repr(config)
        assert "TestConfig" in repr_str
        assert "test_performance" in repr_str
    
    def test_equality(self):
        """测试相等性比较"""
        config1 = TestConfig(
            test_name="test1",
            iterations=[1, 2],
            jmx_path="test1.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output1"
        )
        
        config2 = TestConfig(
            test_name="test1",
            iterations=[1, 2],
            jmx_path="test1.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output1"
        )
        
        config3 = TestConfig(
            test_name="test2",
            iterations=[1, 2],
            jmx_path="test2.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output2"
        )
        
        assert config1 == config2
        assert config1 != config3
    
    def test_hash(self):
        """测试哈希值"""
        config1 = TestConfig(
            test_name="test1",
            iterations=[1, 2],
            jmx_path="test1.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output1"
        )
        
        config2 = TestConfig(
            test_name="test1",
            iterations=[1, 2],
            jmx_path="test1.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output1"
        )
        
        assert hash(config1) == hash(config2)
    
    def test_validation_with_invalid_test_name(self):
        """测试无效测试名称的验证"""
        with pytest.raises(ValueError):
            TestConfig(
                test_name="",  # 空名称
                iterations=[1, 2],
                jmx_path="test.jmx",
                jmeter_bin_path="jmeter.bin",
                output_dir="output"
            )
    
    def test_validation_with_invalid_jmx_path(self):
        """测试无效JMX路径的验证"""
        with pytest.raises(ValueError):
            TestConfig(
                test_name="test_performance",
                iterations=[1, 2],
                jmx_path="",  # 空路径
                jmeter_bin_path="jmeter.bin",
                output_dir="output"
            )
    
    def test_validation_with_invalid_jmeter_bin_path(self):
        """测试无效JMeter路径的验证"""
        with pytest.raises(ValueError):
            TestConfig(
                test_name="test_performance",
                iterations=[1, 2],
                jmx_path="test.jmx",
                jmeter_bin_path="",  # 空路径
                output_dir="output"
            )
    
    def test_validation_with_invalid_output_dir(self):
        """测试无效输出目录的验证"""
        with pytest.raises(ValueError):
            TestConfig(
                test_name="test_performance",
                iterations=[1, 2],
                jmx_path="test.jmx",
                jmeter_bin_path="jmeter.bin",
                output_dir=""  # 空目录
            )
    
    def test_validation_with_negative_iterations(self):
        """测试负迭代次数的验证"""
        with pytest.raises(ValueError):
            TestConfig(
                test_name="test_performance",
                iterations=[-1, 2],  # 负迭代次数
                jmx_path="test.jmx",
                jmeter_bin_path="jmeter.bin",
                output_dir="output"
            )
    
    def test_validation_with_zero_iterations(self):
        """测试零迭代次数的验证"""
        with pytest.raises(ValueError):
            TestConfig(
                test_name="test_performance",
                iterations=[0, 2],  # 零迭代次数
                jmx_path="test.jmx",
                jmeter_bin_path="jmeter.bin",
                output_dir="output"
            )
    
    def test_path_properties(self):
        """测试路径属性"""
        config = TestConfig(
            test_name="test_performance",
            iterations=[1, 2],
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        # 验证路径是Path对象
        assert isinstance(config.jmx_path, str)
        assert isinstance(config.jmeter_bin_path, str)
        assert isinstance(config.output_dir, str)
    
    def test_iterations_property(self):
        """测试迭代次数属性"""
        config = TestConfig(
            test_name="test_performance",
            iterations=[1, 2, 3],
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        # 验证迭代次数是列表
        assert isinstance(config.iterations, list)
        assert len(config.iterations) == 3
        assert all(isinstance(i, int) for i in config.iterations)
    
    def test_max_iterations_property(self):
        """测试最大迭代次数属性"""
        config = TestConfig(
            test_name="test_performance",
            iterations=[1, 5, 3],
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        # 验证最大迭代次数
        assert max(config.iterations) == 5
    
    def test_total_iterations_property(self):
        """测试总迭代次数属性"""
        config = TestConfig(
            test_name="test_performance",
            iterations=[1, 2, 3],
            jmx_path="test.jmx",
            jmeter_bin_path="jmeter.bin",
            output_dir="output"
        )
        
        # 验证总迭代次数
        assert sum(config.iterations) == 6 