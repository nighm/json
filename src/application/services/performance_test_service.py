from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import csv
import xml.etree.ElementTree as ET
import re
import os
import logging

from src.config.config_manager import config_manager
from src.domain.entities.test_config import TestConfig
from src.domain.entities.test_result import TestResult
from src.infrastructure.cross_cutting.analysis.test_analyzer import TestAnalyzer
from src.infrastructure.external.testing_tools.jmeter.jmeter_executor import JMeterExecutor
from src.infrastructure.external.testing_tools.jmeter.jmx_handler import JMXHandler
from src.infrastructure.cross_cutting.logging.test_logger import TestLogger
from src.infrastructure.external.file_system.report_generator import ReportGenerator

# 创建logger实例
logger = logging.getLogger(__name__)

class PerformanceTestService:
    """性能测试服务"""
    
    def __init__(self, jmeter_executor: JMeterExecutor, report_generator: ReportGenerator):
        """
        初始化性能测试服务
        
        Args:
            jmeter_executor: JMeter执行器
            report_generator: 报告生成器
        """
        self.jmeter_executor = jmeter_executor
        self.report_generator = report_generator
        
    def run_tests(self, config: TestConfig) -> List[TestResult]:
        """
        运行性能测试
        
        Args:
            config: 测试配置
            
        Returns:
            List[TestResult]: 测试结果列表
        """
        # 创建日志记录器
        logger = TestLogger(config.test_name)
        logger.info(f"开始执行测试: {config.test_name}")
        logger.info(f"测试配置: 迭代次数={config.iterations}")
        
        # 获取所有线程数和循环次数组合
        thread_counts = config_manager.get_jmeter_config()['test']['thread_counts']
        loop_counts = config_manager.get_jmeter_config()['test']['loop_counts']
        results = []
        analysis_results = []
        # 双重循环遍历所有组合
        for thread_count in thread_counts:
            for loop_count in loop_counts:
                logger.info(f"开始执行 线程数={thread_count} 循环次数={loop_count} 的测试")
                try:
                    # 创建JMX处理器并更新配置（不保存临时文件）
                    jmx_handler = JMXHandler(config.jmx_path)
                    # 更新JMX文件配置
                    jmx_handler.update_thread_group(
                        iterations=loop_count,
                        thread_count=thread_count,
                        ramp_time=config_manager.get_jmeter_config()['test']['ramp_up_time']
                    )
                    # 保存到临时文件
                    temp_jmx_path = str(Path(config.output_dir) / f"temp_{config.test_name}_{thread_count}_{loop_count}.jmx")
                    jmx_handler.save(temp_jmx_path)
                    
                    # 使用临时JMX文件执行测试
                    result = self.jmeter_executor.execute_test(
                        jmx_path=temp_jmx_path,
                        iterations=loop_count,
                        output_dir=config.output_dir,
                        test_name=config.test_name,
                        thread_count=thread_count
                    )
                    results.append(result)
                    # 分析测试结果，传递线程数参数
                    analyzer = TestAnalyzer(config.output_dir)
                    analysis_result = analyzer.analyze_test_results(config.test_name, loop_count, thread_count)
                    analysis_results.append(analysis_result)
                    logger.info(f"完成 线程数={thread_count} 循环次数={loop_count} 的测试")
                    logger.info(f"执行时长: {result.duration:.2f}秒")
                    logger.info(f"报告路径: {result.report_path}")
                    logger.info(f"成功率: {analysis_result['success_rate']:.2f}%")
                    logger.info(f"平均响应时间: {analysis_result['avg_response_time']:.2f}ms")
                except Exception as e:
                    logger.error(f"执行 线程数={thread_count} 循环次数={loop_count} 的测试时发生错误: {str(e)}")
                    raise
        # 生成汇总报告
        try:
            report_path = self.report_generator.generate_summary_report(results)
            logger.info(f"生成汇总报告: {report_path}")
            # 生成分析报告
            analysis_report_path = str(Path(config.output_dir) / f"analysis_{config.test_name}.csv")
            analyzer = TestAnalyzer(config.output_dir)
            analyzer.generate_analysis_report(analysis_results, analysis_report_path)
            logger.info(f"生成分析报告: {analysis_report_path}")
            # 生成集成报告（测试名称+时间戳）
            timestamp = results[0].start_time.strftime("%Y%m%d_%H%M%S") if results else datetime.now().strftime("%Y%m%d_%H%M%S")
            integrated_report_path = self.report_generator.generate_integrated_report(
                analysis_csv_path=analysis_report_path,
                summary_csv_path=report_path,
                test_name=config.test_name,
                timestamp=timestamp
            )
            logger.info(f"生成集成报告: {integrated_report_path}")
        except Exception as e:
            logger.error(f"生成报告时发生错误: {str(e)}")
            raise
        logger.info("测试执行完成")
        return results 

    def process_register_test_jmx(self, jmx_path: str, thread_counts: list, loop_counts: list, 
                                test_name: str, output_dir: str, device_data_manager) -> str:
        """
        处理注册测试的JMX文件特殊逻辑 - 应用层业务逻辑
        
        Args:
            jmx_path: 原始JMX文件路径
            thread_counts: 线程数列表
            loop_counts: 循环次数列表
            test_name: 测试名称
            output_dir: 输出目录
            device_data_manager: 设备数据管理器
            
        Returns:
            str: 处理后的JMX文件路径
        """
        # 计算本次需要的设备数量（线程数*最大循环次数）
        total_devices_needed = sum(thread_counts) * max(loop_counts)
        
        # 获取可用设备数据
        device_csv_file = device_data_manager.get_available_devices(total_devices_needed)
        
        # === 添加调试输出：打印CSV文件中的参数值 ===
        print(f"\n🔍 [DEBUG] 本次测试将使用的设备参数 (CSV文件: {device_csv_file}):")
        print("=" * 80)
        try:
            with open(device_csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 1:  # 确保有数据行
                    print(f"📋 CSV文件头部: {lines[0].strip()}")
                    print("-" * 80)
                    print("📊 设备参数列表:")
                    for i, line in enumerate(lines[1:], 1):  # 跳过标题行
                        if i <= 10:  # 只显示前10行
                            parts = line.strip().split(',')
                            if len(parts) >= 2:
                                mac = parts[0]
                                serial_number = parts[1]
                                print(f"  设备{i:2d}: mac={mac:<20} | deviceSerialNumber={serial_number}")
                        elif i == 11:
                            print(f"  ... 还有 {len(lines)-11} 个设备")
                            break
                    print("-" * 80)
                    print(f"✅ 总共 {len(lines)-1} 个设备参数已准备就绪")
                else:
                    print("❌ CSV文件为空或格式错误")
        except Exception as e:
            print(f"❌ 读取CSV文件失败: {e}")
        print("=" * 80)
        
        # 设置环境变量供JMeter进程读取
        os.environ['device_csv_file'] = device_csv_file
        
        # === 返回传入的JMX文件路径，不再强制使用原始路径 ===
        print(f"🎯 [使用配置] JMeter将执行JMX文件: {jmx_path}")
        return jmx_path

    def update_test_configuration(self, thread_counts: list, loop_counts: list):
        """
        更新测试配置 - 应用层配置管理
        
        Args:
            thread_counts: 线程数列表
            loop_counts: 循环次数列表
        """
        jmeter_config = config_manager.get_jmeter_config()
        jmeter_config['test']['thread_counts'] = thread_counts
        jmeter_config['test']['loop_counts'] = loop_counts

    def generate_comprehensive_reports(self, results: List[TestResult], test_name: str, 
                                     output_dir: str, generate_excel: bool = False) -> Dict[str, str]:
        """
        生成综合报告 - 应用层报告协调
        
        Args:
            results: 测试结果列表
            test_name: 测试名称
            output_dir: 输出目录
            generate_excel: 是否生成Excel报告
            
        Returns:
            Dict[str, str]: 报告文件路径字典
        """
        from src.application.services.report_service import ReportService
        
        report_service = ReportService(output_dir)
        report_paths = {}
        
        # 生成Excel多sheet报告（如果启用）
        if generate_excel:
            excel_report_path = report_service.generate_multi_interface_excel_report(results)
            report_paths['excel'] = excel_report_path
        
        # 生成标准CSV报告
        external_report_csv = str(Path(output_dir) / f"{test_name}_对外整合版.csv")
        internal_report_csv = str(Path(output_dir) / f"{test_name}_内部分析版.csv")
        param_doc_csv = str(Path(output_dir) / f"{test_name}_参数说明表.csv")
        
        report_service.generate_external_report_from_results(results, external_report_csv)
        report_service.generate_internal_report_from_results(results, internal_report_csv, param_doc_csv)
        
        report_paths.update({
            'external': external_report_csv,
            'internal': internal_report_csv,
            'param_doc': param_doc_csv
        })
        
        return report_paths 

    def execute_comprehensive_test_suite(self, test_configs: list, test_name: str, 
                                       output_dir: str, generate_excel: bool = False,
                                       enable_verification: bool = True) -> dict:
        """
        执行完整的测试套件 - 应用层测试协调
        
        职责：协调整个测试流程，包括测试执行、注册验证、报告生成等
        
        Args:
            test_configs: 测试配置列表
            test_name: 测试名称
            output_dir: 输出目录
            generate_excel: 是否生成Excel报告
            enable_verification: 是否启用注册验证
            
        Returns:
            dict: 包含测试结果、验证结果、报告路径的完整结果
        """
        all_results = []
        
        # 执行所有测试
        for config in test_configs:
            results = self.run_tests(config)
            all_results.extend(results)
        
        # 处理注册验证
        verification_result = None
        if enable_verification and any('register' in config.test_name for config in test_configs):
            verification_result = self._handle_register_verification(all_results, output_dir)
        
        # 生成报告
        report_paths = self.generate_comprehensive_reports(all_results, test_name, output_dir, generate_excel)
        
        return {
            'test_results': all_results,
            'verification_result': verification_result,
            'report_paths': report_paths,
            'output_dir': output_dir
        }

    def _handle_register_verification(self, all_results: list, output_dir: str) -> dict:
        """
        处理注册验证 - 应用层验证协调
        
        Args:
            all_results: 所有测试结果
            output_dir: 输出目录
            
        Returns:
            dict: 验证结果
        """
        try:
            from src.application.services.register_verification_service import RegisterVerificationService
            from src.config.config_manager import config_manager
            
            database_config = config_manager.get_database_config()
            mysql_config = database_config.get('mysql', {})
            db_config = {
                'host': mysql_config.get('host', 'localhost'),
                'port': mysql_config.get('port', 3306),
                'user': mysql_config.get('username', 'root'),
                'password': mysql_config.get('password', ''),
                'database': mysql_config.get('database', '')
            }
            
            verification_service = RegisterVerificationService(db_config)
            verification_report = verification_service.verify_registration_results(
                all_results, os.path.basename(output_dir)
            )
            
            # 保存验证报告
            verification_service.save_verification_report(verification_report, output_dir)
            
            return {
                'success': True,
                'report': verification_report,
                'report_path': f"{output_dir}/verification_report_{os.path.basename(output_dir)}.json"
            }
            
        except Exception as e:
            logger.error(f"注册验证失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_test_configs(self, test_types: list, thread_counts: list, loop_counts: list,
                          test_name: str, jmeter_bin: str, output_dir: str, base_jmx_dir: str) -> list:
        """
        创建测试配置列表 - 应用层配置管理
        
        Args:
            test_types: 测试类型列表
            thread_counts: 线程数列表
            loop_counts: 循环次数列表
            test_name: 测试名称
            jmeter_bin: JMeter可执行文件路径
            output_dir: 输出目录
            base_jmx_dir: JMX文件基础目录
            
        Returns:
            list: 测试配置列表
        """
        configs = []
        
        for test_type in test_types:
            jmx_path = os.path.join(base_jmx_dir, f"{test_type}_test.jmx")
            
            # 处理register接口的特殊逻辑
            if test_type == 'register':
                from src.application.services.device_data_manager import DeviceDataManager
                device_data_manager = DeviceDataManager()
                processed_jmx_path = self.process_register_test_jmx(
                    jmx_path, thread_counts, loop_counts, test_name, 
                    output_dir, device_data_manager
                )
                jmx_path = processed_jmx_path
            
            config = TestConfig(
                test_name=f"{test_name}_{test_type}",
                iterations=loop_counts,
                jmx_path=jmx_path,
                jmeter_bin_path=jmeter_bin,
                output_dir=output_dir
            )
            configs.append(config)
        
        return configs 
