#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本脚本用于批量修改 src/tools/jmeter/api_cases 目录下所有JMX文件的线程数和循环次数，
将 ThreadGroup.num_threads 和 LoopController.loops 的值都设置为1。
适用于JMeter接口压测模板的初始化。
"""
import os
import xml.etree.ElementTree as ET
from pathlib import Path

def update_jmx_file(jmx_path):
    """
    修改单个JMX文件的线程数和循环次数为1
    :param jmx_path: JMX文件路径
    """
    print(f"正在处理文件: {jmx_path}")
    # 解析XML结构
    tree = ET.parse(jmx_path)
    root = tree.getroot()
    # 遍历所有stringProp节点，查找并修改目标属性
    for elem in root.iter():
        if elem.tag == 'stringProp':
            if elem.get('name') == 'ThreadGroup.num_threads':
                elem.text = '1'
            elif elem.get('name') == 'LoopController.loops':
                elem.text = '1'
    # 保存修改后的XML到原文件
    tree.write(jmx_path, encoding='UTF-8', xml_declaration=True)
    print(f"文件 {jmx_path} 更新完成\n")

def main():
    # JMX文件所在目录
    jmx_dir = Path('src/tools/jmeter/api_cases')
    if not jmx_dir.exists():
        print(f"错误: 目录 {jmx_dir} 不存在")
        return
    # 查找所有JMX文件
    jmx_files = list(jmx_dir.glob('*.jmx'))
    if not jmx_files:
        print(f"错误: 在 {jmx_dir} 中没有找到JMX文件")
        return
    print(f"找到 {len(jmx_files)} 个JMX文件，开始批量处理...\n")
    # 批量处理
    for jmx_file in jmx_files:
        try:
            update_jmx_file(jmx_file)
        except Exception as e:
            print(f"处理文件 {jmx_file} 时出错: {str(e)}")
    print("所有JMX文件处理完成！")

if __name__ == '__main__':
    main() 