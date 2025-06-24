import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from src.domain.entities.test_result import TestResult

class ReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, output_dir: str):
        """
        初始化报告生成器
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _generate_standard_report_name(self, test_name: str, interface_names: List[str] = None, 
                                     thread_counts: List[int] = None, iterations: List[int] = None) -> str:
        """
        生成标准报告文件名：性能接口测试_对外整合版_XXX_YYY.CSV
        
        Args:
            test_name: 测试名称
            interface_names: 接口名称列表
            thread_counts: 线程数列表
            iterations: 循环次数列表
            
        Returns:
            str: 标准报告文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 构建XXX部分（接口名/参数组合）
        if interface_names and len(interface_names) > 0:
            if len(interface_names) == 1:
                # 单个接口
                interface_part = interface_names[0]
                if thread_counts and iterations:
                    interface_part += f"_{thread_counts[0]}_{iterations[0]}"
            else:
                # 多个接口，用&连接
                interface_part = "&".join(interface_names)
                if thread_counts and iterations:
                    # 添加参数组合信息
                    param_parts = []
                    for i, (tc, it) in enumerate(zip(thread_counts, iterations)):
                        if i < len(interface_names):
                            param_parts.append(f"{interface_names[i]}_{tc}_{it}")
                    interface_part = "&".join(param_parts)
        else:
            # 无接口信息，使用测试名称
            interface_part = test_name
            
        # 如果接口名过长，简化为all
        if len(interface_part) > 50:
            interface_part = "all"
            
        return f"性能接口测试_对外整合版_{interface_part}_{timestamp}.csv"
        
    def generate_summary_report(self, results: List[TestResult]) -> str:
        """
        生成测试汇总报告
        
        Args:
            results: 测试结果列表
            
        Returns:
            str: 报告文件路径
        """
        # 提取接口名称和参数信息
        interface_names = list(set([result.test_name for result in results]))
        thread_counts = list(set([result.thread_count for result in results]))
        iterations = list(set([result.iterations for result in results]))
        
        # 生成标准报告名
        report_name = self._generate_standard_report_name(
            test_name="汇总报告",
            interface_names=interface_names,
            thread_counts=thread_counts,
            iterations=iterations
        )
        report_path = self.output_dir / report_name
        
        # 写入CSV报告
        with open(report_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow([
                '测试名称',
                '迭代次数',
                '开始时间',
                '结束时间',
                '执行时长(秒)',
                '报告路径',
                '是否成功'
            ])
            
            # 写入测试结果
            for result in results:
                writer.writerow([
                    result.test_name,
                    result.iterations,
                    result.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    result.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    f"{result.duration:.2f}",
                    result.report_path,
                    '成功' if result.success else '失败'
                ])
                
        return str(report_path)

    def generate_integrated_report(self, analysis_csv_path: str, summary_csv_path: str, test_name: str, timestamp: str) -> str:
        """
        合并分析报告和汇总报告，生成集成报告（含服务端CPU使用率，默认'-'）
        Args:
            analysis_csv_path: 分析报告CSV路径
            summary_csv_path: 汇总报告CSV路径
            test_name: 测试名称
            timestamp: 时间戳字符串
        Returns:
            str: 集成报告文件路径
        """
        # 读取分析报告
        with open(analysis_csv_path, 'r', encoding='utf-8') as f:
            analysis_rows = list(csv.DictReader(f))
        # 读取汇总报告
        with open(summary_csv_path, 'r', encoding='utf-8') as f:
            summary_rows = list(csv.DictReader(f))
        # 构建主键索引（线程数+循环次数）
        summary_index = {}
        for row in summary_rows:
            key = (str(row.get('线程数', row.get('迭代次数', row.get('循环次数', '')))), str(row.get('循环次数', row.get('迭代次数', ''))))
            summary_index[key] = row
        # 合并字段顺序
        fieldnames = [
            '测试名称', '线程数', '循环次数', '总请求数', '成功数', '失败数', '成功率(%)',
            '最小响应时间(ms)', '最大响应时间(ms)', '平均响应时间(ms)', 'TP90响应时间(ms)', 'TP99响应时间(ms)',
            '开始时间', '结束时间', '执行时长(秒)', '报告路径', '是否成功', '服务端CPU使用率'
        ]
        merged_rows = []
        for arow in analysis_rows:
            key = (str(arow.get('线程数', arow.get('迭代次数', arow.get('循环次数', '')))), str(arow.get('循环次数', arow.get('迭代次数', ''))))
            srow = summary_index.get(key, {})
            merged = {
                '测试名称': test_name,
                '线程数': arow.get('线程数', ''),
                '循环次数': arow.get('循环次数', arow.get('迭代次数', '')),
                '总请求数': arow.get('总请求数', arow.get('总样本数', '')),
                '成功数': arow.get('成功数', ''),
                '失败数': arow.get('失败数', ''),
                '成功率(%)': arow.get('成功率(%)', ''),
                '最小响应时间(ms)': arow.get('最小响应时间(ms)', ''),
                '最大响应时间(ms)': arow.get('最大响应时间(ms)', ''),
                '平均响应时间(ms)': arow.get('平均响应时间(ms)', ''),
                'TP90响应时间(ms)': arow.get('TP90响应时间(ms)', ''),
                'TP99响应时间(ms)': arow.get('TP99响应时间(ms)', ''),
                '开始时间': srow.get('开始时间', ''),
                '结束时间': srow.get('结束时间', ''),
                '执行时长(秒)': srow.get('执行时长(秒)', ''),
                '报告路径': srow.get('报告路径', ''),
                '是否成功': srow.get('是否成功', ''),
                '服务端CPU使用率': '-',
            }
            merged_rows.append(merged)
        # 输出新CSV，使用标准命名
        report_name = self._generate_standard_report_name(test_name)
        output_path = self.output_dir / report_name
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(merged_rows)
        return str(output_path)

    def generate_multi_interface_excel_report(self, results: List[TestResult], output_name: str = None) -> str:
        """
        生成多接口Excel报告，每个接口一个sheet
        
        Args:
            results: 测试结果列表
            output_name: 输出文件名，如果为None则自动生成
            
        Returns:
            str: Excel报告文件路径
        """
        if not results:
            raise ValueError("测试结果列表不能为空")
            
        # 生成标准报告名
        interface_names = list(set([result.test_name for result in results]))
        thread_counts = list(set([result.thread_count for result in results]))
        iterations = list(set([result.iterations for result in results]))
        
        if output_name is None:
            report_name = self._generate_standard_report_name(
                test_name="多接口测试",
                interface_names=interface_names,
                thread_counts=thread_counts,
                iterations=iterations
            )
            # 将.csv改为.xlsx
            report_name = report_name.replace('.csv', '.xlsx')
        else:
            report_name = output_name if output_name.endswith('.xlsx') else f"{output_name}.xlsx"
            
        output_path = self.output_dir / report_name
        
        # 创建Excel写入器
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 按接口分组
            interface_groups = {}
            for result in results:
                if result.test_name not in interface_groups:
                    interface_groups[result.test_name] = []
                interface_groups[result.test_name].append(result)
                
            # 为每个接口创建sheet
            for interface_name, interface_results in interface_groups.items():
                # 转换为DataFrame
                data = []
                for result in interface_results:
                    data.append({
                        '测试名称': result.test_name,
                        '线程数': result.thread_count,
                        '循环次数': result.iterations,
                        '总请求数': result.total_requests,
                        '成功数': result.success_count,
                        '失败数': result.fail_count,
                        '成功率(%)': f"{result.success_rate:.2f}",
                        '最小响应时间(ms)': f"{result.min_resp_time:.2f}",
                        '最大响应时间(ms)': f"{result.max_resp_time:.2f}",
                        '平均响应时间(ms)': f"{result.avg_resp_time:.2f}",
                        'TP90响应时间(ms)': f"{result.tp90_resp_time:.2f}",
                        'TP99响应时间(ms)': f"{result.tp99_resp_time:.2f}",
                        '开始时间': result.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        '结束时间': result.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        '执行时长(秒)': f"{result.duration:.2f}",
                        '报告路径': result.report_path,
                        '是否成功': '成功' if result.success else '失败',
                        '服务端CPU使用率': result.server_cpu or '-',
                    })
                    
                df = pd.DataFrame(data)
                
                # 写入Excel sheet，sheet名限制为31字符
                sheet_name = interface_name[:31] if len(interface_name) > 31 else interface_name
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
            # 创建汇总sheet
            summary_data = []
            for result in results:
                summary_data.append({
                    '接口名称': result.test_name,
                    '线程数': result.thread_count,
                    '循环次数': result.iterations,
                    '总请求数': result.total_requests,
                    '成功率(%)': f"{result.success_rate:.2f}",
                    '平均响应时间(ms)': f"{result.avg_resp_time:.2f}",
                    'TP99响应时间(ms)': f"{result.tp99_resp_time:.2f}",
                    '执行时长(秒)': f"{result.duration:.2f}",
                    '是否成功': '成功' if result.success else '失败',
                })
                
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='汇总', index=False)
            
        return str(output_path)

    def generate_external_report(self, main_csv: str, summary_csv: str, analysis_csv: str, output_csv: str) -> str:
        """
        生成对外标准报告：严格用三元组主键补全所有字段，所有字段都必须有值，找不到时统一填'-'，并自动推断"是否成功"等字段。
        """
        # 读取主报告、汇总报告、分析报告
        with open(main_csv, encoding='utf-8') as f:
            main_data = list(csv.DictReader(f))
        with open(summary_csv, encoding='utf-8') as f:
            summary_data = list(csv.DictReader(f))
        with open(analysis_csv, encoding='utf-8') as f:
            analysis_data = list(csv.DictReader(f))
        # 构建查找索引（严格三元组主键）
        summary_map = {(row['测试名称'], str(row.get('线程数', '')).strip(), str(row.get('循环次数', '')).strip()): row for row in summary_data}
        analysis_map = {(row['测试名称'], str(row.get('线程数', '')).strip(), str(row.get('循环次数', '')).strip()): row for row in analysis_data}
        # 需要补全的字段
        fieldnames = [
            '测试名称', '线程数', '循环次数', '总请求数', '成功数', '失败数', '成功率(%)',
            '最小响应时间(ms)', '最大响应时间(ms)', '平均响应时间(ms)', 'TP90响应时间(ms)', 'TP99响应时间(ms)',
            '开始时间', '结束时间', '执行时长(秒)', '报告路径', '是否成功', '服务端CPU使用率'
        ]
        new_rows = []
        for row in main_data:
            test_name = row.get('测试名称', '-').strip()
            thread_count = str(row.get('线程数', '-')).strip()
            loop_count = str(row.get('循环次数', '-')).strip()
            key = (test_name, thread_count, loop_count)
            # 以主报告为基础，先补全自身字段
            merged = {k: (row.get(k, '-') or '-') for k in fieldnames}
            # summary补全
            srow = summary_map.get(key, {})
            for f in ['开始时间', '结束时间', '执行时长(秒)', '报告路径']:
                merged[f] = srow.get(f, merged[f]) or '-'
            # analysis补全
            arow = analysis_map.get(key, {})
            for f in ['总请求数', '成功数', '失败数', '成功率(%)', '最小响应时间(ms)', '最大响应时间(ms)', '平均响应时间(ms)', 'TP90响应时间(ms)', 'TP99响应时间(ms)']:
                merged[f] = arow.get(f, merged[f]) or '-'
            # 自动推断"是否成功"
            if merged['是否成功'] == '-' or not merged['是否成功']:
                try:
                    merged['是否成功'] = '成功' if float(merged['失败数']) == 0 else '失败'
                except Exception:
                    merged['是否成功'] = '-'
            # 服务端CPU使用率
            if not merged.get('服务端CPU使用率'):
                merged['服务端CPU使用率'] = '-'
            # 任何字段为空都补'-'
            for k in fieldnames:
                if not merged.get(k):
                    merged[k] = '-'
            new_rows.append(merged)
        # 写入新CSV，使用标准命名
        test_name = main_data[0].get('测试名称', '对外报告') if main_data else '对外报告'
        report_name = self._generate_standard_report_name(test_name)
        output_path = self.output_dir / report_name
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(new_rows)
        return str(output_path)

    def generate_internal_analysis_report(self, main_csv: str, summary_csv: str, analysis_csv: str, output_csv: str, param_doc_csv: str) -> str:
        """
        生成内部详细分析报告和参数说明表，严格用三元组主键补全所有字段，所有字段都必须有值。
        """
        # 参数说明表内容
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
        # 写入参数说明表
        with open(param_doc_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(PARAM_DOC)
        # 详细数据表复用对外报告生成逻辑
        self.generate_external_report(main_csv, summary_csv, analysis_csv, output_csv)
        return output_csv

    def generate_external_report_from_results(self, results, output_csv):
        """
        直接用TestResult列表生成对外标准报告，不依赖中间csv。
        """
        import csv
        fieldnames = [
            '测试名称', '线程数', '循环次数', '总请求数', '成功数', '失败数', '成功率(%)',
            '最小响应时间(ms)', '最大响应时间(ms)', '平均响应时间(ms)', 'TP90响应时间(ms)', 'TP99响应时间(ms)',
            '开始时间', '结束时间', '执行时长(秒)', '报告路径', '是否成功', '服务端CPU使用率'
        ]
        rows = []
        for r in results:
            rows.append({
                '测试名称': r.test_name,
                '线程数': r.thread_count,
                '循环次数': r.iterations,
                '总请求数': r.total_requests,
                '成功数': r.success_count,
                '失败数': r.fail_count,
                '成功率(%)': f"{r.success_rate:.2f}",
                '最小响应时间(ms)': f"{r.min_resp_time:.2f}",
                '最大响应时间(ms)': f"{r.max_resp_time:.2f}",
                '平均响应时间(ms)': f"{r.avg_resp_time:.2f}",
                'TP90响应时间(ms)': f"{r.tp90_resp_time:.2f}",
                'TP99响应时间(ms)': f"{r.tp99_resp_time:.2f}",
                '开始时间': r.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                '结束时间': r.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                '执行时长(秒)': f"{r.duration:.2f}",
                '报告路径': r.report_path,
                '是否成功': '成功' if r.success else '失败',
                '服务端CPU使用率': r.server_cpu or '-',
            })
        # 使用标准命名
        test_name = results[0].test_name if results else '对外报告'
        report_name = self._generate_standard_report_name(test_name)
        output_path = self.output_dir / report_name
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return str(output_path)

    def generate_internal_report_from_results(self, results, output_csv, param_doc_csv):
        """
        直接用TestResult列表生成内部详细分析报告和参数说明表。
        """
        import csv
        # 参数说明表内容
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
        with open(param_doc_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(PARAM_DOC)
        # 内部分析报告内容与对外版一致，但可扩展更多字段
        self.generate_external_report_from_results(results, output_csv)
        return output_csv 