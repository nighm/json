import csv
import os

# 定义输入文件路径
main_report = r'src/tools/jmeter/results/心跳接口测试_20250614_110100.csv'
summary_report = r'src/tools/jmeter/results/test_summary_20250614_110718.csv'
analysis_report = r'src/tools/jmeter/results/analysis_心跳接口测试.csv'
output_report = r'src/tools/jmeter/results/心跳接口测试_20250614_110100_对外整合版.csv'

# 读取csv为字典列表
def read_csv_dict(filepath):
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv_dict(filepath, fieldnames, rows):
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# 读取所有报告
main_data = read_csv_dict(main_report)
summary_data = read_csv_dict(summary_report)
analysis_data = read_csv_dict(analysis_report)

# 用于快速查找summary和analysis中的数据
summary_map = {(row['测试名称'], row['迭代次数']): row for row in summary_data}
analysis_map = {(row['测试名称'], row['线程数'], row['循环次数']): row for row in analysis_data}

# 需要补全的字段
extra_fields = ['开始时间', '结束时间', '执行时长(秒)', '报告路径']

# 生成新数据
new_rows = []
for row in main_data:
    # 以主报告为基础
    test_name = row['测试名称']
    thread_count = row['线程数']
    loop_count = row['循环次数']
    # 查找summary补全
    summary_row = summary_map.get((test_name, loop_count))
    if summary_row:
        for f in extra_fields:
            row[f] = summary_row.get(f, row.get(f, '-'))
    # 查找analysis补全（如有新统计项可补充）
    analysis_row = analysis_map.get((test_name, thread_count, loop_count))
    if analysis_row:
        for k, v in analysis_row.items():
            if k not in row or not row[k]:
                row[k] = v
    # 处理服务端CPU使用率
    if not row.get('服务端CPU使用率'):
        row['服务端CPU使用率'] = '-'
    new_rows.append(row)

# 统一字段顺序
fieldnames = list(main_data[0].keys())
for f in extra_fields:
    if f not in fieldnames:
        fieldnames.append(f)

write_csv_dict(output_report, fieldnames, new_rows)
print(f'对外整合报告已生成: {output_report}') 