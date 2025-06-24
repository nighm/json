import csv
import os

# 参数说明表，字段名-说明-采集/计算方法-代码位置
PARAM_DOC = [
    ['字段名', '含义/来源说明', '采集/计算方法说明', '代码位置/来源文件'],
    ['测试名称', '本次性能测试的名称，来自配置或命令行参数', '由测试脚本传递', 'src/interfaces/cli/performance_test_cli.py'],
    ['线程数', '并发线程数，来自配置或命令行参数', '由performance_test_cli.py解析参数后传递到TestConfig', 'src/interfaces/cli/performance_test_cli.py'],
    ['循环次数', '每线程请求次数，来自配置或命令行参数', '同上', '同上'],
    ['总请求数', '线程数×循环次数', '由测试脚本自动计算', 'src/domain/entities/test_config.py'],
    ['成功数/失败数', 'JMeter执行后统计的成功/失败请求数', '由JMeter结果文件统计', 'src/infrastructure/jmeter/jmeter_executor.py'],
    ['成功率(%)', '成功数/总请求数×100%', '由报告生成器自动计算', 'src/infrastructure/report/report_generator.py'],
    ['最小/最大/平均响应时间(ms)', 'JMeter原始结果统计', '由JMeter结果文件统计', '同上'],
    ['TP90/TP99响应时间(ms)', '90%、99%分位响应时间，JMeter原始结果统计', '由JMeter结果文件统计', '同上'],
    ['开始/结束时间', '每组测试的实际启动和结束时间', '由测试脚本记录', 'src/interfaces/cli/performance_test_cli.py'],
    ['执行时长(秒)', '本组测试实际耗时', '结束时间-开始时间', '同上'],
    ['报告路径', '本组测试详细原始报告存放路径', '由测试脚本生成', '同上'],
    ['服务端CPU使用率', '采集自服务端监控（如有），否则为"-"', '需集成服务端监控采集脚本', '预留字段'],
]

# 详细数据表，直接复用主报告并补全
main_report = r'src/tools/jmeter/results/心跳接口测试_20250614_110100.csv'
summary_report = r'src/tools/jmeter/results/test_summary_20250614_110718.csv'
analysis_report = r'src/tools/jmeter/results/analysis_心跳接口测试.csv'
output_report = r'src/tools/jmeter/results/心跳接口测试_20250614_110100_内部分析版.csv'
param_doc_report = r'src/tools/jmeter/results/心跳接口测试_20250614_110100_参数说明表.csv'

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

def write_param_doc(filepath, doc):
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(doc)

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
    test_name = row['测试名称']
    thread_count = row['线程数']
    loop_count = row['循环次数']
    # 查找summary补全
    summary_row = summary_map.get((test_name, loop_count))
    if summary_row:
        for f in extra_fields:
            row[f] = summary_row.get(f, row.get(f, '-'))
    # 查找analysis补全
    analysis_row = analysis_map.get((test_name, thread_count, loop_count))
    if analysis_row:
        for k, v in analysis_row.items():
            if k not in row or not row[k]:
                row[k] = v
    if not row.get('服务端CPU使用率'):
        row['服务端CPU使用率'] = '-'
    new_rows.append(row)

# 统一字段顺序
fieldnames = list(main_data[0].keys())
for f in extra_fields:
    if f not in fieldnames:
        fieldnames.append(f)

write_csv_dict(output_report, fieldnames, new_rows)
write_param_doc(param_doc_report, PARAM_DOC)
print(f'内部详细分析报告已生成: {output_report}')
print(f'参数说明表已生成: {param_doc_report}') 