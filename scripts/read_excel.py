#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel文件读取工具
用于读取和显示Excel文件的内容
"""

import os
import sys
import pandas as pd
from pathlib import Path

def read_excel_file(file_path):
    """
    读取Excel文件并返回其内容
    
    Args:
        file_path (str): Excel文件的路径
        
    Returns:
        dict: 包含所有工作表数据的字典
    """
    try:
        # 读取所有工作表
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        # 存储所有工作表的数据
        all_sheets_data = {}
        
        # 读取每个工作表
        for sheet_name in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            all_sheets_data[sheet_name] = df
            
        return all_sheets_data
    
    except Exception as e:
        print(f"读取Excel文件时发生错误: {str(e)}")
        return None

def display_excel_content(data_dict):
    """
    显示Excel文件的内容
    
    Args:
        data_dict (dict): 包含所有工作表数据的字典
    """
    if not data_dict:
        print("没有数据可显示")
        return
        
    for sheet_name, df in data_dict.items():
        print(f"\n{'='*50}")
        print(f"工作表: {sheet_name}")
        print(f"{'='*50}")
        
        if df.empty:
            print("\n这是一个空的工作表")
            continue
            
        print(f"\n数据形状: {df.shape}")
        print("\n列名:")
        print(df.columns.tolist())
        print("\n前5行数据:")
        print(df.head())
        print("\n数据类型:")
        print(df.dtypes)
        
        # 只对数值型列进行统计描述
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if not numeric_cols.empty:
            print("\n数值列的基本统计信息:")
            print(df[numeric_cols].describe())

def main():
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    excel_file = project_root / "202506.xlsx"
    
    if not excel_file.exists():
        print(f"错误: 文件 {excel_file} 不存在")
        sys.exit(1)
        
    print(f"正在读取文件: {excel_file}")
    data = read_excel_file(str(excel_file))
    
    if data:
        display_excel_content(data)

if __name__ == "__main__":
    main() 