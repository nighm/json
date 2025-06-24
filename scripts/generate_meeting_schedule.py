#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
会议日程表生成工具
生成日例会、周例会和编号的CSV文件
时间范围：5月到10月底
"""

import os
import sys
import pandas as pd
import csv
from pathlib import Path
from datetime import datetime, timedelta
from chinese_calendar import is_workday, is_holiday

def get_weekday_name(date):
    """
    获取中文星期名称
    
    Args:
        date (datetime): 日期对象
        
    Returns:
        str: 中文星期名称
    """
    weekday_names = ['一', '二', '三', '四', '五', '六', '日']
    return f"周{weekday_names[date.weekday()]}"

def is_working_day(date):
    """
    判断是否为工作日（考虑节假日）
    
    Args:
        date (datetime): 日期对象
        
    Returns:
        bool: 是否为工作日
    """
    return is_workday(date) and not is_holiday(date)

def get_last_working_day_of_week(date):
    """
    获取指定日期所在周的最后一个工作日
    
    Args:
        date (datetime): 日期对象
        
    Returns:
        datetime: 最后一个工作日
    """
    # 获取本周五
    friday = date + timedelta(days=(4 - date.weekday()))
    
    # 如果周五是工作日，返回周五
    if is_working_day(friday):
        return friday
    
    # 否则返回本周最后一个工作日
    current = friday
    while not is_working_day(current):
        current -= timedelta(days=1)
    return current

def generate_daily_meeting(start_date, end_date):
    """
    生成日例会数据
    
    Args:
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        
    Returns:
        DataFrame: 日例会数据
    """
    data = []
    seq_num = 1
    current_date = start_date
    
    while current_date <= end_date:
        if is_working_day(current_date):
            data.append({
                '序号': seq_num,
                '标题': f"{current_date.strftime('%y%m%d')} 测试1组 晨例会",
                '描述': "1）讨论昨日昆仑卫士主要工作内容。\n2）讨论今日主要工作内容。\n3）昨天工作遇到的问题讨论。"
            })
            seq_num += 1
        current_date += timedelta(days=1)
    
    return pd.DataFrame(data)

def generate_weekly_meeting(start_date, end_date):
    """
    生成周例会数据
    
    Args:
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        
    Returns:
        DataFrame: 周例会数据
    """
    data = []
    seq_num = 1
    current_date = start_date
    
    while current_date <= end_date:
        # 获取本周最后一个工作日
        last_working_day = get_last_working_day_of_week(current_date)
        
        if last_working_day <= end_date:
            data.append({
                '序号': seq_num,
                '标题': f"{last_working_day.strftime('%y%m%d')} 测试1组 周例会",
                '描述': "1、5月工作讨论&确认。责任人：胡明明；时长：5分钟。\n2、当前工作任务对齐（当前投入项目，进度，风险，求助等）。责任人：测试1组；时长：20分钟。\n3、昆仑卫士 云效本周工时登记 讲解。责任人：胡明明；时长：5分钟。\n4、昆仑卫士 央馆项目 性能测试流程 分享。责任人：胡明明"
            })
            seq_num += 1
        
        # 移动到下周
        current_date += timedelta(days=7)
    
    return pd.DataFrame(data)

def generate_numbering(start_date, end_date):
    """
    生成编号数据
    
    Args:
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        
    Returns:
        DataFrame: 编号数据
    """
    data = []
    seq_num = 1
    current_date = start_date
    
    while current_date <= end_date:
        if is_working_day(current_date):
            weekday_name = get_weekday_name(current_date)
            data.append({
                '序号': seq_num,
                '标题': f"{weekday_name}（{current_date.day}号）",
                '描述': ""
            })
            seq_num += 1
        current_date += timedelta(days=1)
    
    return pd.DataFrame(data)

def save_csv(df, file_path):
    """
    保存DataFrame为CSV文件
    
    Args:
        df (DataFrame): 要保存的数据
        file_path (Path): 文件路径
    """
    # 添加BOM头
    with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
        df.to_csv(f, index=False)

def generate_import_csv_july2025():
    # 字段顺序与原csv一致
    columns = [
        '任务名称','描述','任务ID','是否父任务','父任务','状态','负责人','产品','优先级','迭代','参与者','标签','计划开始时间','计划完成时间','预计工时','预计工时单位','实际工时单位'
    ]
    rows = []
    # 头部父任务
    rows.append(['7月','','AAMQ-374','Y','','待处理','胡明明','','中','','','','','','',''])
    # 生成编号、日例会、周例会
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 31)
    current_date = start_date
    seq = 1
    week_seq = 1
    parent_tasks = []
    # 先生成所有工作日的编号和日例会
    while current_date <= end_date:
        if is_working_day(current_date):
            # 编号父任务
            parent_name = f"编号{seq}组"
            rows.append([parent_name,'','', 'N','7月','待处理','胡明明','','中','','','','','','',''])
            parent_tasks.append((current_date, parent_name))
            # 日例会
            title = f"{current_date.strftime('%y%m%d')} 测试1组 晨例会"
            desc = "1）讨论昨日昆仑卫士主要工作内容。\n2）讨论今日主要工作内容。\n3）昨天工作遇到的问题讨论。"
            rows.append([title, desc, '', 'N', parent_name, '待处理', '胡明明', '', '中', '', '', '', '', '', '', '', ''])
            seq += 1
        current_date += timedelta(days=1)
    # 生成每周最后一个工作日的周例会
    current_date = start_date
    while current_date <= end_date:
        last_working = get_last_working_day_of_week(current_date)
        if last_working >= start_date and last_working <= end_date:
            # 找到对应父任务
            parent_name = None
            for d, p in parent_tasks:
                if d == last_working:
                    parent_name = p
                    break
            if parent_name:
                title = f"{last_working.strftime('%y%m%d')} 测试1组 周例会"
                desc = "1、7月工作讨论&确认。责任人：胡明明；时长：5分钟。\n2、当前工作任务对齐（当前投入项目，进度，风险，求助等）。责任人：测试1组；时长：20分钟。\n3、昆仑卫士 云效本周工时登记 讲解。责任人：胡明明；时长：5分钟。\n4、昆仑卫士 央馆项目 性能测试流程 分享。责任人：胡明明"
                rows.append([title, desc, '', 'N', parent_name, '待处理', '胡明明', '', '中', '', '', '', '', '', '', '', ''])
        current_date += timedelta(days=7)
    # 保存为csv
    output_dir = Path(__file__).parent.parent
    out_path = output_dir / '202507_导入.csv'
    with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print('202507_导入.csv 生成完成！')

def main():
    # 设置日期范围：5月1日到10月31日
    start_date = datetime(2025, 5, 1)
    end_date = datetime(2025, 10, 31)
    
    # 生成数据
    daily_df = generate_daily_meeting(start_date, end_date)
    weekly_df = generate_weekly_meeting(start_date, end_date)
    numbering_df = generate_numbering(start_date, end_date)
    
    # 保存为CSV文件
    output_dir = Path(__file__).parent.parent
    
    save_csv(daily_df, output_dir / "202506_日例会.csv")
    save_csv(weekly_df, output_dir / "202506_周例会.csv")
    save_csv(numbering_df, output_dir / "202506_编号.csv")
    
    print("文件生成完成！")
    print(f"日例会记录数: {len(daily_df)}")
    print(f"周例会记录数: {len(weekly_df)}")
    print(f"编号记录数: {len(numbering_df)}")

if __name__ == "__main__":
    generate_import_csv_july2025() 