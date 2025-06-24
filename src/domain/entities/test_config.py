from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class TestConfig:
    """测试配置实体类"""
    test_name: str  # 测试名称
    iterations: List[int]  # 测试迭代次数列表
    jmx_path: str  # JMX文件路径
    jmeter_bin_path: str  # JMeter可执行文件路径
    output_dir: str  # 输出目录
    timestamp: datetime = None  # 测试时间戳

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now() 