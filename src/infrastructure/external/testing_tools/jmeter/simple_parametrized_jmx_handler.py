import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List
import shutil

class SimpleParametrizedJMXHandler:
    """简化的参数化JMX文件处理器"""
    
    def __init__(self, jmx_path: str):
        """
        初始化参数化JMX处理器
        
        Args:
            jmx_path: JMX文件路径
        """
        self.jmx_path = Path(jmx_path)
        self.tree = ET.parse(jmx_path)
        self.root = self.tree.getroot()
        
    def add_csv_dataset_config(self, csv_file_path: str, variable_names: List[str]):
        """
        添加CSV DataSet配置到JMX文件
        
        Args:
            csv_file_path: CSV文件路径
            variable_names: 变量名列表
        """
        # 查找线程组
        thread_group = self.root.find(".//ThreadGroup")
        if thread_group is None:
            raise ValueError("未找到线程组配置")
            
        # 查找线程组后面的hashTree
        thread_group_hash_tree = None
        for i, elem in enumerate(self.root.iter()):
            if elem.tag == "ThreadGroup":
                # 找到ThreadGroup后的hashTree
                for j in range(i + 1, len(list(self.root.iter()))):
                    next_elem = list(self.root.iter())[j]
                    if next_elem.tag == "hashTree":
                        thread_group_hash_tree = next_elem
                        break
                break
                
        if thread_group_hash_tree is None:
            raise ValueError("未找到线程组的hashTree")
            
        # 创建CSV DataSet元素
        csv_dataset = ET.Element("CSVDataSet")
        csv_dataset.set("guiclass", "TestBeanGUI")
        csv_dataset.set("testclass", "CSVDataSet")
        csv_dataset.set("testname", "设备信息数据集")
        csv_dataset.set("enabled", "true")
        
        # 添加CSV DataSet属性
        properties = [
            ("delimiter", ","),
            ("fileEncoding", "UTF-8"),
            ("filename", csv_file_path),
            ("ignoreFirstLine", "true"),
            ("quotedData", "false"),
            ("recycle", "true"),
            ("shareMode", "shareMode.all"),
            ("stopThread", "false"),
            ("variableNames", ",".join(variable_names))
        ]
        
        for name, value in properties:
            prop = ET.SubElement(csv_dataset, "stringProp")
            prop.set("name", name)
            prop.text = str(value)
            
        # 将CSV DataSet插入到hashTree的开始位置
        thread_group_hash_tree.insert(0, csv_dataset)
        
        # 添加CSV DataSet对应的hashTree
        csv_hash_tree = ET.SubElement(thread_group_hash_tree, "hashTree")
        
    def update_http_request_body(self, body_template: str):
        """
        更新HTTP请求体
        
        Args:
            body_template: 请求体模板
        """
        # 查找HTTP请求元素
        http_sampler = self.root.find(".//HTTPSamplerProxy")
        if http_sampler is None:
            raise ValueError("未找到HTTP请求配置")
            
        # 查找请求体参数
        arguments = http_sampler.find(".//elementProp[@name='HTTPsampler.Arguments']")
        if arguments is None:
            raise ValueError("未找到HTTP请求参数配置")
            
        # 更新请求体
        collection = arguments.find("collectionProp[@name='Arguments.arguments']")
        if collection is not None:
            # 查找参数元素
            arg_elem = collection.find("elementProp[@name='']")
            if arg_elem is not None:
                # 更新参数值
                value_elem = arg_elem.find("stringProp[@name='Argument.value']")
                if value_elem is not None:
                    value_elem.text = body_template
                    
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
    def create_parametrized_jmx(cls, template_path: str, output_path: str, csv_file_path: str,
                               thread_count: int = 1, iterations: int = 1, ramp_time: int = 1,
                               body_template: str = None):
        """
        从模板创建参数化JMX文件
        
        Args:
            template_path: 模板文件路径
            output_path: 输出文件路径
            csv_file_path: CSV文件路径
            thread_count: 线程数
            iterations: 迭代次数
            ramp_time: 启动时间
            body_template: 请求体模板
        """
        # 复制模板文件
        shutil.copy2(template_path, output_path)
        
        # 创建参数化处理器
        handler = cls(output_path)
        
        # 定义CSV变量名
        variable_names = [
            "id", "device_id", "device_serial_number", "device_name", "ip", "mac", "macs",
            "outside_ip", "type", "model", "brand", "supplier", "processor", "operating_system",
            "hard_disk", "memory", "main_board", "resolution", "online", "status",
            "last_heartbeat_time", "last_login_time", "offline_time", "device_group_id",
            "device_user_group_id", "user_id", "login_user_id", "login_status", "image_id",
            "image_snapshot_id", "local_image_status", "image_backup_time", "purchase_batch",
            "remark", "create_time", "create_by", "update_time", "update_by", "del_flag"
        ]
        
        # 添加CSV DataSet
        handler.add_csv_dataset_config(csv_file_path, variable_names)
        
        # 更新HTTP请求体
        if body_template:
            handler.update_http_request_body(body_template)
        
        # 更新线程组配置
        handler.update_thread_group(iterations, thread_count, ramp_time)
        
        # 保存文件
        handler.save()
        
        return handler 