#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【警告】本脚本仅供底层特殊场景手动调用，主流程和CLI禁止自动生成JMX文件！
"""

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

def create_parametrized_register_jmx(csv_file_path: str, output_path: str, 
                                   thread_count: int = 1, iterations: int = 1):
    """创建参数化的注册接口JMX文件"""
    
    # 模板文件路径
    template_path = "src/tools/jmeter/api_cases/register_test.jmx"
    
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
        ("variableNames", "id,device_id,device_serial_number,device_name,ip,mac,macs,outside_ip,type,model,brand,supplier,processor,operating_system,hard_disk,memory,main_board,resolution,online,status,last_heartbeat_time,last_login_time,offline_time,device_group_id,device_user_group_id,user_id,login_user_id,login_status,image_id,image_snapshot_id,local_image_status,image_backup_time,purchase_batch,remark,create_time,create_by,update_time,update_by,del_flag")
    ]
    
    for name, value in properties:
        prop = ET.SubElement(csv_dataset, "stringProp")
        prop.set("name", name)
        prop.text = str(value)
    
    # 将CSV DataSet插入到hashTree的开始位置
    thread_group_hash_tree.insert(0, csv_dataset)
    
    # 添加CSV DataSet对应的hashTree
    csv_hash_tree = ET.SubElement(thread_group_hash_tree, "hashTree")
    
    # 更新HTTP请求体
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
                        value_elem.text = '{"deviceId": "${device_id}", "password": "test_password_${device_serial_number}", "deviceName": "${device_name}", "ip": "${ip}", "mac": "${mac}", "brand": "${brand}", "model": "${model}", "processor": "${processor}", "operatingSystem": "${operating_system}", "hardDisk": "${hard_disk}", "memory": "${memory}", "mainBoard": "${main_board}"}'
    
    # 更新线程组配置
    loop_controller = thread_group.find(".//LoopController")
    if loop_controller is not None:
        loops = loop_controller.find("stringProp[@name='LoopController.loops']")
        if loops is not None:
            loops.text = str(iterations)
    
    num_threads = thread_group.find("stringProp[@name='ThreadGroup.num_threads']")
    if num_threads is not None:
        num_threads.text = str(thread_count)
    
    # 保存文件
    tree.write(output_path, encoding='UTF-8', xml_declaration=True)
    
    print(f"参数化JMX文件创建成功: {output_path}")

def main():
    """主函数"""
    # 生成设备信息
    csv_file = "data/generated_devices/generated_devices_20250618_172306.csv"
    
    # 创建输出目录
    output_dir = Path("src/tools/jmeter/api_cases/parametrized")
    output_dir.mkdir(exist_ok=True)
    
    # 创建参数化JMX文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"register_test_parametrized_3_2_{timestamp}.jmx"
    
    create_parametrized_register_jmx(
        csv_file_path=csv_file,
        output_path=str(output_path),
        thread_count=3,
        iterations=2
    )

if __name__ == "__main__":
    main() 