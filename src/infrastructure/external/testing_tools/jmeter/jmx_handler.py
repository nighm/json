import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any

class JMXHandler:
    """JMX文件处理器"""
    
    def __init__(self, jmx_path: str):
        """
        初始化JMX处理器
        
        Args:
            jmx_path: JMX文件路径
        """
        self.jmx_path = Path(jmx_path)
        self.tree = ET.parse(jmx_path)
        self.root = self.tree.getroot()
        
    def update_thread_group(self, iterations: int, thread_count: int, ramp_time: int):
        """
        更新线程组配置
        
        Args:
            iterations: 迭代次数
            thread_count: 线程数
            ramp_time: 启动时间
        """
        # 查找线程组元素
        thread_group = self.root.find(".//ThreadGroup")
        if thread_group is None:
            raise ValueError("未找到线程组配置")
            
        # 更新循环次数
        loop_controller = thread_group.find(".//LoopController")
        if loop_controller is not None:
            loops = loop_controller.find("stringProp[@name='LoopController.loops']")
            if loops is not None:
                loops.text = str(iterations)
                
        # 更新线程数
        num_threads = thread_group.find("stringProp[@name='ThreadGroup.num_threads']")
        if num_threads is not None:
            num_threads.text = str(thread_count)
            
        # 更新启动时间
        ramp_time_elem = thread_group.find("stringProp[@name='ThreadGroup.ramp_time']")
        if ramp_time_elem is not None:
            ramp_time_elem.text = str(ramp_time)
            
    def update_http_request(self, params: Dict[str, Any]):
        """
        更新HTTP请求参数
        
        Args:
            params: 请求参数字典
        """
        # 查找HTTP请求元素
        http_sampler = self.root.find(".//HTTPSamplerProxy")
        if http_sampler is None:
            raise ValueError("未找到HTTP请求配置")
            
        # 更新请求参数
        for key, value in params.items():
            # 查找参数元素
            arg = http_sampler.find(f".//elementProp[@name='{key}']")
            if arg is not None:
                # 更新参数值
                value_elem = arg.find("stringProp[@name='Argument.value']")
                if value_elem is not None:
                    value_elem.text = str(value)
                    
    def save(self, output_path: str = None):
        """
        保存修改后的JMX文件
        
        Args:
            output_path: 输出文件路径，如果为None则覆盖原文件
        """
        if output_path is None:
            output_path = self.jmx_path
            
        # 保存文件
        self.tree.write(output_path, encoding='UTF-8', xml_declaration=True)
        
    @classmethod
    def create_from_template(cls, template_path: str, output_path: str, params: Dict[str, Any]):
        """
        从模板创建JMX文件
        
        Args:
            template_path: 模板文件路径
            output_path: 输出文件路径
            params: 参数配置
        """
        handler = cls(template_path)
        
        # 更新线程组配置
        if 'iterations' in params:
            handler.update_thread_group(
                iterations=params.get('iterations', 100),
                thread_count=params.get('thread_count', 10),
                ramp_time=params.get('ramp_time', 1)
            )
            
        # 更新HTTP请求参数
        if 'http_params' in params:
            handler.update_http_request(params['http_params'])
            
        # 保存文件
        handler.save(output_path)

    @staticmethod
    def create_jmx_template(jmx_path: str, thread_count: int = 1, iterations: int = 1, ramp_time: int = 1):
        """
        预留：自动生成JMX模板文件的静态方法
        Args:
            jmx_path: 生成的JMX文件路径
            thread_count: 线程数，默认1
            iterations: 循环次数，默认1
            ramp_time: 启动时间，默认1
        """
        # TODO: 实现自动生成JMX文件的逻辑
        pass 