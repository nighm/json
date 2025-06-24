import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List
import shutil

class ParametrizedJMXHandler:
    """参数化JMX文件处理器，支持CSV DataSet和动态参数配置
    【警告】自动生成和保存JMX文件仅供底层特殊场景手动调用，主流程和CLI禁止自动生成。
    """
    
    def __init__(self, jmx_path: str):
        """
        初始化参数化JMX处理器
        
        Args:
            jmx_path: JMX文件路径
        """
        self.jmx_path = Path(jmx_path)
        self.tree = ET.parse(jmx_path)
        self.root = self.tree.getroot()
        
    def add_csv_dataset(self, csv_file_path: str, variable_names: List[str], delimiter: str = ","):
        """
        添加CSV DataSet配置
        
        Args:
            csv_file_path: CSV文件路径
            variable_names: 变量名列表
            delimiter: 分隔符
        """
        # 查找线程组
        thread_group = self.root.find(".//ThreadGroup")
        if thread_group is None:
            raise ValueError("未找到线程组配置")
            
        # 查找线程组的hashTree
        thread_group_hash_tree = None
        for elem in self.root.iter():
            if elem.tag == "hashTree":
                # 检查这个hashTree是否包含ThreadGroup
                if elem.find("ThreadGroup") is not None:
                    thread_group_hash_tree = elem
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
            ("delimiter", delimiter),
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
            
        # 将CSV DataSet插入到线程组hashTree的开始位置
        thread_group_hash_tree.insert(0, csv_dataset)
        
        # 添加CSV DataSet对应的hashTree
        csv_hash_tree = ET.SubElement(thread_group_hash_tree, "hashTree")
        
    def update_http_request_body(self, body_template: str):
        """
        更新HTTP请求体，支持变量替换
        
        Args:
            body_template: 请求体模板，支持${variable_name}格式的变量
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
            # 查找或创建参数元素
            arg_elem = collection.find("elementProp[@name='']")
            if arg_elem is None:
                arg_elem = ET.SubElement(collection, "elementProp")
                arg_elem.set("name", "")
                arg_elem.set("elementType", "HTTPArgument")
                
            # 更新参数值
            value_elem = arg_elem.find("stringProp[@name='Argument.value']")
            if value_elem is None:
                value_elem = ET.SubElement(arg_elem, "stringProp")
                value_elem.set("name", "Argument.value")
                
            value_elem.text = body_template
            
            # 确保metadata存在
            metadata_elem = arg_elem.find("stringProp[@name='Argument.metadata']")
            if metadata_elem is None:
                metadata_elem = ET.SubElement(arg_elem, "stringProp")
                metadata_elem.set("name", "Argument.metadata")
                metadata_elem.text = "="
                
    def add_user_defined_variables(self, variables: Dict[str, str]):
        """
        添加用户定义的变量
        
        Args:
            variables: 变量字典
        """
        # 查找TestPlan
        test_plan = self.root.find(".//TestPlan")
        if test_plan is None:
            raise ValueError("未找到测试计划配置")
            
        # 查找或创建用户定义变量
        user_vars = test_plan.find(".//elementProp[@name='TestPlan.user_defined_variables']")
        if user_vars is None:
            user_vars = ET.SubElement(test_plan, "elementProp")
            user_vars.set("name", "TestPlan.user_defined_variables")
            user_vars.set("elementType", "Arguments")
            user_vars.set("guiclass", "ArgumentsPanel")
            user_vars.set("testclass", "Arguments")
            user_vars.set("testname", "用户定义的变量")
            user_vars.set("enabled", "true")
            
        # 查找或创建参数集合
        collection = user_vars.find("collectionProp[@name='Arguments.arguments']")
        if collection is None:
            collection = ET.SubElement(user_vars, "collectionProp")
            collection.set("name", "Arguments.arguments")
            
        # 添加变量
        for name, value in variables.items():
            arg_elem = ET.SubElement(collection, "elementProp")
            arg_elem.set("name", name)
            arg_elem.set("elementType", "Argument")
            
            name_elem = ET.SubElement(arg_elem, "stringProp")
            name_elem.set("name", "Argument.name")
            name_elem.text = name
            
            value_elem = ET.SubElement(arg_elem, "stringProp")
            value_elem.set("name", "Argument.value")
            value_elem.text = value
            
            metadata_elem = ET.SubElement(arg_elem, "stringProp")
            metadata_elem.set("name", "Argument.metadata")
            metadata_elem.text = "="
            
    def add_response_assertions(self):
        """添加响应断言"""
        # 查找HTTP请求元素
        http_sampler = self.root.find(".//HTTPSamplerProxy")
        if http_sampler is None:
            raise ValueError("未找到HTTP请求配置")
            
        # 查找线程组
        thread_group = self.root.find(".//ThreadGroup")
        if thread_group is None:
            raise ValueError("未找到线程组配置")
            
        hash_tree = thread_group.find("hashTree")
        if hash_tree is None:
            return
            
        # 添加响应码断言
        response_assertion = ET.SubElement(hash_tree, "ResponseAssertion")
        response_assertion.set("guiclass", "AssertionGui")
        response_assertion.set("testclass", "ResponseAssertion")
        response_assertion.set("testname", "响应断言")
        response_assertion.set("enabled", "true")
        
        # 断言配置
        collection = ET.SubElement(response_assertion, "collectionProp")
        collection.set("name", "Asserion.test_strings")
        
        test_string = ET.SubElement(collection, "stringProp")
        test_string.set("name", "49586")
        test_string.text = "200"
        
        custom_message = ET.SubElement(response_assertion, "stringProp")
        custom_message.set("name", "Assertion.custom_message")
        custom_message.text = "注册失败，响应码不是200"
        
        test_field = ET.SubElement(response_assertion, "stringProp")
        test_field.set("name", "Assertion.test_field")
        test_field.text = "Assertion.response_code"
        
        assume_success = ET.SubElement(response_assertion, "boolProp")
        assume_success.set("name", "Assertion.assume_success")
        assume_success.text = "false"
        
        test_type = ET.SubElement(response_assertion, "intProp")
        test_type.set("name", "Assertion.test_type")
        test_type.text = "8"
        
        # 添加对应的hashTree
        assertion_hash_tree = ET.SubElement(hash_tree, "hashTree")
        assertion_hash_tree.insert(0, response_assertion)
        
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
                               server_host: str = "192.168.24.45", server_port: str = "8080"):
        """
        【警告】本方法仅供底层特殊场景手动调用，主流程和CLI禁止自动生成JMX文件！
        从模板创建参数化JMX文件
        
        Args:
            template_path: 模板文件路径
            output_path: 输出文件路径
            csv_file_path: CSV文件路径
            thread_count: 线程数
            iterations: 迭代次数
            ramp_time: 启动时间
            server_host: 服务器地址
            server_port: 服务器端口
        """
        # 复制模板文件
        shutil.copy2(template_path, output_path)
        
        # 创建参数化处理器
        handler = cls(output_path)
        
        # 定义CSV变量名（与设备信息生成器的字段对应）
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
        handler.add_csv_dataset(csv_file_path, variable_names)
        
        # 添加用户定义变量
        user_variables = {
            "device_csv_file": csv_file_path,
            "server_host": server_host,
            "server_port": server_port
        }
        handler.add_user_defined_variables(user_variables)
        
        # 更新HTTP请求体（注册接口的JSON模板）
        body_template = '''{"deviceId": "${device_id}", "password": "test_password_${device_serial_number}", "deviceName": "${device_name}", "ip": "${ip}", "mac": "${mac}", "brand": "${brand}", "model": "${model}", "processor": "${processor}", "operatingSystem": "${operating_system}", "hardDisk": "${hard_disk}", "memory": "${memory}", "mainBoard": "${main_board}"}'''
        handler.update_http_request_body(body_template)
        
        # 添加响应断言
        handler.add_response_assertions()
        
        # 更新线程组配置
        handler.update_thread_group(iterations, thread_count, ramp_time)
        
        # 保存文件
        handler.save()
        
        return handler 