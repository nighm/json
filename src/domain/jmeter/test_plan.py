#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JMeter测试计划领域模型
- 处理JMX文件的读取和修改
- 管理测试计划的并发配置
"""
import os
import xml.etree.ElementTree as ET
from datetime import datetime

class TestPlan:
    """测试计划领域模型"""
    
    def __init__(self, jmx_dir: str):
        """
        初始化测试计划
        
        Args:
            jmx_dir: JMX文件目录
        """
        self.jmx_dir = jmx_dir
    
    def get_latest_filtered_jmx(self) -> str:
        """
        获取最新的filtered JMX文件
        
        Returns:
            str: JMX文件路径
            
        Raises:
            FileNotFoundError: 未找到任何filtered JMX文件
        """
        jmx_files = [f for f in os.listdir(self.jmx_dir) if f.startswith('filtered_') and f.endswith('.jmx')]
        if not jmx_files:
            raise FileNotFoundError('未找到任何filtered JMX文件！')
        jmx_files.sort(reverse=True)  # 按文件名倒序排序
        return os.path.join(self.jmx_dir, jmx_files[0])
    
    def modify_concurrent_level(self, jmx_path: str, concurrent_level: int, output_path: str) -> None:
        """
        修改JMX文件中的并发数
        
        Args:
            jmx_path: 源JMX文件路径
            concurrent_level: 目标并发数
            output_path: 输出JMX文件路径
        """
        tree = ET.parse(jmx_path)
        root = tree.getroot()
        
        # 查找并修改线程组配置
        for tg in root.iter('ThreadGroup'):
            # 修改线程数
            for elem in tg.iter('stringProp'):
                if elem.get('name') == 'ThreadGroup.num_threads':
                    elem.text = str(concurrent_level)
            # 修改循环次数
            for elem in tg.iter('stringProp'):
                if elem.get('name') == 'LoopController.loops':
                    elem.text = '1'  # 每个线程只执行一次
        
        # 保存修改后的JMX文件
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    def generate_jmx_filename(self, concurrent_level: int) -> str:
        """
        生成JMX文件名
        
        Args:
            concurrent_level: 并发数
            
        Returns:
            str: 生成的JMX文件名
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'jmeter_{concurrent_level}_{timestamp}.jmx' 