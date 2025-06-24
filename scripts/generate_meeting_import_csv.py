import csv
from pathlib import Path
from datetime import datetime, timedelta
from chinese_calendar import is_workday, is_holiday

def get_chinese_weekday(num):
    # 0=一，1=二，2=三，3=四，4=五，5=六，6=日
    mapping = ['一', '二', '三', '四', '五', '六', '日']
    return mapping[num]

def is_working_day(date):
    return is_workday(date) and not is_holiday(date)

def get_last_working_day_of_week(date):
    # 获取本周最后一个工作日（周五或往前推）
    friday = date + timedelta(days=(4 - date.weekday()))
    if is_working_day(friday):
        return friday
    current = friday
    while not is_working_day(current):
        current -= timedelta(days=1)
    return current

def generate_july_import_csv():
    # 字段顺序严格按截图
    columns = [
        '标题','描述','父项ID','父项是否存在','父项标题','状态','负责人','产品','优先级','迭代','参与者','抄送','标签','计划开始时间','计划完成时间','预计工时','预计工时汇总','实际工时汇总'
    ]
    rows = []
    # 1. 顶层父任务"7月"
    rows.append(['7月','', 'AAMQ-374', 'Y', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    # 2. 生成所有工作日的编号任务和日例会
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2025, 7, 31)
    current_date = start_date
    week_map = {}
    seq = 1
    # 先生成所有工作日的编号任务和日例会
    while current_date <= end_date:
        if is_working_day(current_date):
            weekday_cn = get_chinese_weekday(current_date.weekday())
            day_num = current_date.day
            parent_title = f'周{weekday_cn}（{day_num}号）'
            # 编号任务
            rows.append([
                parent_title, '', '', 'N', '7月', '待处理', '胡明明', '', '中', '', '', '', '', '', '', '', '', ''
            ])
            # 日例会
            title = f'{current_date.strftime("%y%m%d")} 测试1组 晨例会'
            desc = '1）讨论昨日昆仑卫士主要工作内容。\n2）讨论今日主要工作内容。\n3）昨天工作遇到的问题讨论。'
            rows.append([
                title, desc, '', 'N', parent_title, '待处理', '胡明明', '', '中', '', '', '', '', '', '', '', '', ''
            ])
            week_map.setdefault(current_date.isocalendar()[1], []).append((current_date, parent_title))
        current_date += timedelta(days=1)
    # 3. 生成每周最后一个工作日的周例会
    for week, days in week_map.items():
        last_day, parent_title = days[-1]
        title = f'{last_day.strftime("%y%m%d")} 测试1组 周例会'
        desc = '1）讨论昨日昆仑卫士主要工作内容。\n2）讨论今日主要工作内容。\n3）昨天工作遇到的问题讨论。'
        rows.append([
            title, desc, '', 'N', parent_title, '待处理', '胡明明', '', '中', '', '', '', '', '', '', '', '', ''
        ])
    # 保存为csv
    output_dir = Path(__file__).parent.parent
    out_path = output_dir / '202507_导入.csv'
    with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print('202507_导入.csv 生成完成！')

def generate_month_import_csv(year, month, parent_id='AAMQ-374'):
    # 字段顺序严格按截图
    columns = [
        '标题','描述','父项ID','父项是否存在','父项标题','状态','负责人','产品','优先级','迭代','参与者','抄送','标签','计划开始时间','计划完成时间','预计工时','预计工时汇总','实际工时汇总'
    ]
    rows = []
    # 顶层父任务"X月"
    month_title = f'{month}月'
    rows.append([month_title,'', parent_id, 'Y', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    # 生成所有工作日的编号任务和日例会
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year, 12, 31)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    current_date = start_date
    week_map = {}
    while current_date <= end_date:
        if is_working_day(current_date):
            weekday_cn = get_chinese_weekday(current_date.weekday())
            day_num = current_date.day
            parent_title = f'周{weekday_cn}（{day_num}号）'
            # 编号任务
            rows.append([
                parent_title, '', '', 'N', month_title, '待处理', '胡明明', '', '中', '', '', '', '', '', '', '', '', ''
            ])
            # 日例会
            title = f'{current_date.strftime("%y%m%d")} 测试1组 晨例会'
            desc = '1）讨论昨日昆仑卫士主要工作内容。\n2）讨论今日主要工作内容。\n3）昨天工作遇到的问题讨论。'
            rows.append([
                title, desc, '', 'N', parent_title, '待处理', '胡明明', '', '中', '', '', '', '', '', '', '', '', ''
            ])
            week_map.setdefault(current_date.isocalendar()[1], []).append((current_date, parent_title))
        current_date += timedelta(days=1)
    # 生成每周最后一个工作日的周例会
    for week, days in week_map.items():
        last_day, parent_title = days[-1]
        title = f'{last_day.strftime("%y%m%d")} 测试1组 周例会'
        desc = '1）讨论昨日昆仑卫士主要工作内容。\n2）讨论今日主要工作内容。\n3）昨天工作遇到的问题讨论。'
        rows.append([
            title, desc, '', 'N', parent_title, '待处理', '胡明明', '', '中', '', '', '', '', '', '', '', '', ''
        ])
    # 保存为csv
    output_dir = Path(__file__).parent.parent
    out_path = output_dir / f'{year}{month:02d}_导入.csv'
    with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f'{year}{month:02d}_导入.csv 生成完成！')

def generate_year_import_csv(year=2025):
    for month in range(1, 13):
        generate_month_import_csv(year, month)

if __name__ == "__main__":
    generate_year_import_csv(2025) 