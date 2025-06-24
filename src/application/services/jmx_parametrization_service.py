import os
from pathlib import Path
from typing import List, Dict, Any
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

class JMXParametrizationService:
    """JMX参数化服务，用于管理参数化JMX文件的生成和配置
    【警告】自动生成和保存JMX文件的功能已禁用，主流程和CLI禁止调用，仅允许底层特殊场景手动调用。
    """
    
    def __init__(self, api_cases_dir: str = "src/tools/jmeter/api_cases"):
        """
        初始化JMX参数化服务
        
        Args:
            api_cases_dir: API测试用例目录
        """
        self.api_cases_dir = Path(api_cases_dir)
        self.parametrized_dir = self.api_cases_dir / "parametrized"
        self.parametrized_dir.mkdir(exist_ok=True)
        
    def create_parametrized_jmx_for_interface(self, interface_name: str, csv_file_path: str,
                                            output_name: str = None, thread_count: int = 1,
                                            iterations: int = 1, ramp_time: int = 1,
                                            server_host: str = "192.168.24.45", server_port: str = "8080") -> str:
        """
        【警告】本方法仅供底层特殊场景手动调用，主流程和CLI禁止自动生成JMX文件！
        为指定接口创建参数化JMX文件
        
        Args:
            interface_name: 接口名称（如register, strategy_get, heartbeat等）
            csv_file_path: 设备信息CSV文件路径
            output_name: 输出文件名，如果为None则自动生成
            thread_count: 线程数
            iterations: 迭代次数
            ramp_time: 启动时间
            server_host: 服务器地址
            server_port: 服务器端口
            
        Returns:
            生成的JMX文件路径
        """
        # 接口映射
        interface_mapping = {
            "register": "register_test.jmx",
            "strategy_get": "strategy_get_test.jmx",
            "heartbeat": "heartbeat_test.jmx",
            "device_info_get": "device_info_get_test.jmx",
            "device_name_get": "device_name_get_test.jmx",
            "device_mode_get": "device_mode_get_test.jmx",
            "mode_get": "mode_get_test.jmx",
            "brand_get": "brand_get_test.jmx",
            "guard_get": "guard_get_test.jmx",
            "logo_get": "logo_get_test.jmx",
            "mqtt_addr_get": "mqtt_addr_get_test.jmx"
        }
        
        if interface_name not in interface_mapping:
            raise ValueError(f"不支持的接口名称: {interface_name}")
            
        template_name = interface_mapping[interface_name]
        template_path = self.api_cases_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"接口模板文件不存在: {template_path}")
            
        # 输出文件路径
        if output_name is None:
            timestamp = self._get_timestamp()
            output_name = f"{interface_name}_test_parametrized_{thread_count}_{iterations}_{timestamp}.jmx"
            
        output_path = self.parametrized_dir / output_name
        
        # 复制模板文件
        shutil.copy2(template_path, output_path)
        
        # 解析XML
        tree = ET.parse(output_path)
        root = tree.getroot()
        
        # 查找线程组
        thread_group = root.find(".//ThreadGroup")
        if thread_group is None:
            raise ValueError("未找到线程组配置")
        
        # 查找线程组的hashTree
        thread_group_hash_tree = None
        for elem in root.iter():
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
        
        # 根据接口类型设置不同的请求体模板
        body_templates = {
            "register": '''{"deviceId": "${device_id}", "password": "test_password_${device_serial_number}", "deviceName": "${device_name}", "ip": "${ip}", "mac": "${mac}", "brand": "${brand}", "model": "${model}", "processor": "${processor}", "operatingSystem": "${operating_system}", "hardDisk": "${hard_disk}", "memory": "${memory}", "mainBoard": "${main_board}"}''',
            "strategy_get": '''{"deviceId": "${device_id}", "deviceName": "${device_name}"}''',
            "heartbeat": '''{"deviceId": "${device_id}", "deviceName": "${device_name}", "ip": "${ip}", "mac": "${mac}"}''',
            "device_info_get": '''{"deviceId": "${device_id}"}''',
            "device_name_get": '''{"deviceId": "${device_id}"}''',
            "device_mode_get": '''{"deviceId": "${device_id}"}''',
            "mode_get": '''{"deviceId": "${device_id}"}''',
            "brand_get": '''{"deviceId": "${device_id}"}''',
            "guard_get": '''{"deviceId": "${device_id}"}''',
            "logo_get": '''{"deviceId": "${device_id}"}''',
            "mqtt_addr_get": '''{"deviceId": "${device_id}"}'''
        }
        
        # 更新HTTP请求体
        body_template = body_templates.get(interface_name, '''{"deviceId": "${device_id}"}''')
        http_sampler = root.find(".//HTTPSamplerProxy")
        if http_sampler is not None:
            arguments = http_sampler.find(".//elementProp[@name='HTTPsampler.Arguments']")
            if arguments is not None:
                collection = arguments.find("collectionProp[@name='Arguments.arguments']")
                if collection is not None:
                    arg_elem = collection.find("elementProp[@name='']")
                    if arg_elem is not None:
                        value_elem = arg_elem.find("stringProp[@name='Argument.value']")
                        if value_elem is not None:
                            value_elem.text = body_template
        
        # 更新线程组配置
        loop_controller = thread_group.find(".//LoopController")
        if loop_controller is not None:
            loops = loop_controller.find("stringProp[@name='LoopController.loops']")
            if loops is not None:
                loops.text = str(iterations)
        
        num_threads = thread_group.find("stringProp[@name='ThreadGroup.num_threads']")
        if num_threads is not None:
            num_threads.text = str(thread_count)
        
        ramp_time_elem = thread_group.find("stringProp[@name='ThreadGroup.ramp_time']")
        if ramp_time_elem is not None:
            ramp_time_elem.text = str(ramp_time)
        
        # 保存文件
        tree.write(output_path, encoding='UTF-8', xml_declaration=True)
        
        return str(output_path)
        
    def _get_timestamp(self) -> str:
        """获取时间戳字符串"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def list_parametrized_jmx_files(self) -> List[str]:
        """列出所有参数化JMX文件"""
        if not self.parametrized_dir.exists():
            return []
            
        return [f.name for f in self.parametrized_dir.glob("*.jmx")]
        
    def cleanup_parametrized_files(self):
        """清理参数化文件"""
        if self.parametrized_dir.exists():
            import shutil
            shutil.rmtree(self.parametrized_dir)
            self.parametrized_dir.mkdir(exist_ok=True) 