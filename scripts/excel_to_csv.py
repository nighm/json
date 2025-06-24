#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel转CSV工具
将Excel文件中的每个工作表转换为单独的CSV文件
输出文件格式：原文件名_工作表名.csv
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

def is_weekend(date):
    """
    判断是否为周末
    
    Args:
        date (datetime): 日期对象
        
    Returns:
        bool: 是否为周末
    """
    return date.weekday() >= 5

def expand_daily_meeting(df, start_date_str, days=30):
    """
    扩充日例会数据
    
    Args:
        df (DataFrame): 原始数据
        start_date_str (str): 起始日期，格式为'YYMMDD'
        days (int): 要生成的天数
        
    Returns:
        DataFrame: 扩充后的数据
    """
    # 解析起始日期
    start_date = datetime.strptime(start_date_str, '%y%m%d')
    
    # 创建新的数据列表
    new_data = []
    
    # 获取原始数据的第一行
    first_row = df.iloc[0]
    base_title = first_row['标题'].split(' ', 1)[1]  # 获取"测试1组 晨例会"部分
    
    # 生成新的数据
    current_date = start_date
    seq_num = 1
    
    for _ in range(days):
        if not is_weekend(current_date):
            new_row = {
                '序号': seq_num,
                '标题': f"{current_date.strftime('%y%m%d')} {base_title}",
                '描述': first_row['描述']
            }
            new_data.append(new_row)
            seq_num += 1
        current_date += timedelta(days=1)
    
    return pd.DataFrame(new_data)

def excel_to_csv(excel_file_path):
    """
    将Excel文件转换为CSV文件
    
    Args:
        excel_file_path (str): Excel文件的路径
        
    Returns:
        list: 成功转换的CSV文件路径列表
    """
    try:
        # 获取Excel文件名（不含扩展名）
        excel_name = Path(excel_file_path).stem
        
        # 读取所有工作表
        excel_file = pd.ExcelFile(excel_file_path)
        sheet_names = excel_file.sheet_names
        
        # 存储成功转换的文件路径
        converted_files = []
        
        # 处理每个工作表
        for sheet_name in sheet_names:
            # 读取工作表数据
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            
            # 跳过空工作表
            if df.empty:
                print(f"工作表 '{sheet_name}' 为空，已跳过")
                continue
            
            # 如果是日例会工作表，进行数据扩充
            if sheet_name == '日例会':
                # 从第一行数据中提取日期
                first_row = df.iloc[0]
                start_date = first_row['标题'].split(' ')[0]  # 获取"250513"部分
                df = expand_daily_meeting(df, start_date)
                print(f"已扩充日例会数据，生成 {len(df)} 条记录")
            
            # 生成CSV文件名
            csv_filename = f"{excel_name}_{sheet_name}.csv"
            csv_path = Path(excel_file_path).parent / csv_filename
            
            # 保存为CSV文件，使用GBK编码
            df.to_csv(csv_path, index=False, encoding='gbk')
            converted_files.append(str(csv_path))
            print(f"已转换工作表 '{sheet_name}' 到文件: {csv_filename}")
        
        return converted_files
    
    except Exception as e:
        print(f"转换过程中发生错误: {str(e)}")
        return []

def main():
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    excel_file = project_root / "202506.xlsx"
    
    if not excel_file.exists():
        print(f"错误: 文件 {excel_file} 不存在")
        sys.exit(1)
    
    print(f"开始转换文件: {excel_file}")
    converted_files = excel_to_csv(str(excel_file))
    
    if converted_files:
        print("\n转换完成！生成的文件:")
        for file_path in converted_files:
            print(f"- {file_path}")
    else:
        print("\n没有成功转换任何文件")

if __name__ == "__main__":
    main() 