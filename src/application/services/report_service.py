from typing import List, Dict
from src.domain.entities.report import Report, ReportField
from src.domain.entities.test_result import TestResult
from src.infrastructure.report.report_generator import ReportGenerator

class ReportService:
    """
    报告整合与分析服务，负责生成对外标准报告、内部详细分析报告和参数说明表
    """
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.generator = ReportGenerator(output_dir)

    def generate_external_report(self, main_csv: str, summary_csv: str, analysis_csv: str, output_csv: str) -> str:
        """
        生成对外标准报告，自动补全所有字段，集成有价值参数
        """
        return self.generator.generate_external_report(main_csv, summary_csv, analysis_csv, output_csv)

    def generate_internal_analysis_report(self, main_csv: str, summary_csv: str, analysis_csv: str, output_csv: str, param_doc_csv: str) -> str:
        """
        生成内部详细分析报告和参数说明表
        """
        return self.generator.generate_internal_analysis_report(main_csv, summary_csv, analysis_csv, output_csv, param_doc_csv)

    def generate_external_report_from_results(self, results: List[TestResult], output_csv: str) -> str:
        """
        直接用TestResult列表生成对外标准报告
        """
        return self.generator.generate_external_report_from_results(results, output_csv)

    def generate_internal_report_from_results(self, results: List[TestResult], output_csv: str, param_doc_csv: str) -> str:
        """
        直接用TestResult列表生成内部详细分析报告和参数说明表
        """
        return self.generator.generate_internal_report_from_results(results, output_csv, param_doc_csv)
        
    def generate_multi_interface_excel_report(self, results: List[TestResult], output_name: str = None) -> str:
        """
        生成多接口Excel报告，每个接口一个sheet
        
        Args:
            results: 测试结果列表
            output_name: 输出文件名，如果为None则自动生成
            
        Returns:
            str: Excel报告文件路径
        """
        return self.generator.generate_multi_interface_excel_report(results, output_name) 