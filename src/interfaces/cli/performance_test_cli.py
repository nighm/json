#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试CLI接口层
负责用户交互、参数处理和业务协调

遵循DDD架构原则：
- 只负责用户交互和参数验证
- 不包含业务逻辑，通过应用层服务处理
- 使用依赖注入实现松耦合
- 提供友好的用户界面和错误处理

主要功能：
1. 命令行参数解析和验证
2. 调用应用层服务执行测试
3. 协调报告生成和验证
4. 提供用户友好的反馈信息
"""

import argparse
from pathlib import Path
import sys
import os
from datetime import datetime
import traceback
from typing import Optional, Type

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from src.application.services.performance_test_service import PerformanceTestService
from src.domain.entities.test_config import TestConfig
from src.infrastructure.external.testing_tools.jmeter.jmeter_executor import JMeterExecutor
from src.config.config_manager import config_manager
from src.application.services.performance_tuning_service import PerformanceTuningService
from src.application.services.device_data_manager import DeviceDataManager
from src.application.services.device_query_service import DeviceQueryService
from src.application.services.register_verification_service import RegisterVerificationService
from src.infrastructure.external.file_system.report_generator import ReportGenerator


class PerformanceTestCLI:
    """
    性能测试CLI类 - 接口层
    
    职责：
    1. 提供命令行用户界面
    2. 解析和验证用户输入
    3. 协调应用层服务执行测试
    4. 处理用户反馈和错误信息
    
    设计原则：
    - 单一职责：只处理用户交互
    - 依赖倒置：通过依赖注入使用服务
    - 开闭原则：支持扩展新的测试类型
    """
    
    def __init__(
        self,
        performance_service_cls: Type[PerformanceTestService] = PerformanceTestService,
        device_data_manager_cls: Type[DeviceDataManager] = DeviceDataManager,
        register_verification_service_cls: Type[RegisterVerificationService] = RegisterVerificationService,
        performance_tuning_service_cls: Type[PerformanceTuningService] = PerformanceTuningService,
        jmeter_executor_cls: Type[JMeterExecutor] = JMeterExecutor,
        report_generator_cls: Type[ReportGenerator] = ReportGenerator,
        config_manager_instance = None
    ):
        """
        初始化CLI类
        
        Args:
            performance_service_cls: 性能测试服务类
            device_data_manager_cls: 设备数据管理器类
            register_verification_service_cls: 注册验证服务类
            performance_tuning_service_cls: 性能调优服务类
            jmeter_executor_cls: JMeter执行器类
            report_generator_cls: 报告生成器类
            config_manager_instance: 配置管理器实例
        """
        self.performance_service_cls = performance_service_cls
        self.device_data_manager_cls = device_data_manager_cls
        self.register_verification_service_cls = register_verification_service_cls
        self.performance_tuning_service_cls = performance_tuning_service_cls
        self.jmeter_executor_cls = jmeter_executor_cls
        self.report_generator_cls = report_generator_cls
        self.config_manager = config_manager_instance or config_manager
    
    def create_timestamped_output_dir(self, base_output_dir: str) -> str:
        """
        创建以时间戳命名的输出目录
        
        Args:
            base_output_dir: 基础输出目录
            
        Returns:
            str: 时间戳子目录路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_dir = Path(base_output_dir) / timestamp
        timestamped_dir.mkdir(parents=True, exist_ok=True)
        return str(timestamped_dir)
    
    def sync_actual_devices(self) -> bool:
        """
        同步数据库真实注册设备到actual_used_devices.json - 接口层协调
        
        Returns:
            bool: 同步是否成功
        """
        print("[CLI] 开始同步数据库真实注册设备到actual_used_devices.json ...")
        try:
            # 获取数据库配置
            mysql_config = self.config_manager.get_database_config()['mysql']
            db_config = {
                'host': mysql_config['host'],
                'port': mysql_config['port'],
                'user': mysql_config['username'],
                'password': mysql_config['password'],
                'database': mysql_config.get('database', 'yangguan')
            }
            
            # 通过应用层服务执行数据同步
            device_data_manager = self.device_data_manager_cls()
            success = device_data_manager.sync_actual_devices_from_database(db_config)
            
            if success:
                print("[CLI] actual_used_devices.json 同步完成！")
            else:
                print("[CLI] actual_used_devices.json 同步失败，请检查数据库配置和连接！")
                
            return success
            
        except Exception as e:
            print(f"[CLI] 同步失败: {e}")
            traceback.print_exc()
            return False
    
    def run(self, args: Optional[argparse.Namespace] = None) -> bool:
        """
        运行CLI主流程 - 接口层入口点
        
        职责：只负责参数解析、调用应用层协调方法、输出结果
        
        执行流程：
        1. 解析命令行参数（如果没有提供则自动解析）
        2. 处理特殊功能（如同步设备）
        3. 创建输出目录
        4. 处理参数类型转换
        5. 调用应用层服务执行测试
        6. 输出结果信息
        """
        try:
            print("[DEBUG] 启动性能测试CLI main() ...")
            
            # 步骤1: 解析命令行参数
            # 如果没有提供args参数，则自动解析命令行参数
            if args is None:
                parser = self._create_argument_parser()
                args = parser.parse_args()
            
            print(f"[DEBUG] 解析参数完成: {args}")
            
            # 步骤2: 处理同步设备功能（特殊功能）
            # 如果用户指定了--sync-actual-devices参数，则只执行同步功能并返回
            if args.sync_actual_devices:
                print("[DEBUG] 检测到同步设备参数，执行同步功能...")
                return self.sync_actual_devices()
            
            # 步骤3: 创建时间戳输出目录
            # 在指定的输出目录下创建以时间戳命名的子目录，避免结果覆盖
            timestamped_output_dir = self.create_timestamped_output_dir(args.output_dir)
            print(f"[DEBUG] 输出目录: {timestamped_output_dir}")
            
            # 步骤4: 处理参数类型转换
            # 将命令行参数转换为应用层需要的标准格式
            print("[DEBUG] 开始处理参数类型转换...")
            thread_counts = self._process_thread_counts(args.thread_counts)
            loop_counts = self._process_loop_counts(args.loop_counts)
            test_types = self._get_test_types(args.test_type)
            base_dir = self._get_jmx_base_dir(args.jmx)
            print(f"[DEBUG] 参数转换完成 - 线程数: {thread_counts}, 循环数: {loop_counts}, 测试类型: {test_types}, JMX目录: {base_dir}")
            
            # 步骤5: 通过应用层创建测试配置
            # 实例化性能测试服务，传入JMeter执行器和报告生成器
            print("[DEBUG] 开始创建应用层服务...")
            print(f"[DEBUG] JMeter路径: {args.jmeter_bin}")
            service = self.performance_service_cls(
                self.jmeter_executor_cls(args.jmeter_bin) if self.jmeter_executor_cls else None,
                self.report_generator_cls(timestamped_output_dir) if self.report_generator_cls else None
            )
            
            # 调用应用层服务创建测试配置
            print("[DEBUG] 开始创建测试配置...")
            test_configs = service.create_test_configs(
                test_types=test_types,
                thread_counts=thread_counts,
                loop_counts=loop_counts,
                test_name=args.test_name,
                jmeter_bin=args.jmeter_bin,
                output_dir=timestamped_output_dir,
                base_jmx_dir=base_dir
            )
            print(f"[DEBUG] 测试配置创建完成，共 {len(test_configs)} 个配置")
            
            # 步骤6: 统一执行测试、验证、报告生成
            # 调用应用层服务的综合测试套件，执行完整的测试流程
            print("[DEBUG] 开始执行综合测试套件...")
            result = service.execute_comprehensive_test_suite(
                test_configs=test_configs,
                test_name=args.test_name,
                output_dir=timestamped_output_dir,
                generate_excel=args.excel_report,
                enable_verification=('register' in test_types)  # 如果是注册测试则启用验证
            )
            
            # 步骤7: 结果输出
            # 向用户展示测试执行结果和相关信息
            print("\n=== 测试执行完成 ===")
            print(f"输出目录: {result['output_dir']}")
            print(f"报告文件: {result['report_paths']}")
            if result.get('verification_result'):
                print(f"注册验证: {result['verification_result']}")
            print("详细结果见报告文件。")
            return True
            
        except Exception as e:
            # 异常处理：捕获所有异常并输出详细信息
            print(f"[ERROR] 主流程异常: {e}")
            traceback.print_exc()
            return False
    
    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """
        创建命令行参数解析器 - 接口层用户界面
        
        职责：定义和配置命令行参数，提供用户友好的帮助信息
        
        参数分类说明：
        🔴 必须参数：没有默认值，必须由用户提供
        🟡 可选参数：有默认值，用户可以不提供
        🟢 功能开关：布尔类型，用于启用/禁用特定功能
        🔵 配置参数：用于调整测试行为的参数
        
        Returns:
            argparse.ArgumentParser: 配置好的参数解析器
        """
        parser = argparse.ArgumentParser(description='JMeter性能测试工具')
        
        # ==================== 🟡 核心测试参数（有默认值，可选） ====================
        
        # 🟡 线程数列表 - 控制并发用户数
        # default: 从配置文件读取，通常是 [10, 20]
        # nargs='+': 表示可以接受一个或多个值，如 --thread-counts 10 20 30
        # type=int: 确保输入的是整数
        # 作用：定义测试时的并发线程数，影响服务器压力
        parser.add_argument('--thread-counts', 
                          default=self.config_manager.get_jmeter_config()['test']['thread_counts'], 
                          nargs='+', 
                          type=int, 
                          help='线程数列表，默认读取配置文件，例如：--thread-counts 10 20 30')
        
        # 🟡 循环次数列表 - 控制每个线程的请求次数
        # default: 从配置文件读取，通常是 [1, 3]
        # nargs='+': 表示可以接受一个或多个值
        # 作用：定义每个线程执行多少次请求，影响总请求量
        parser.add_argument('--loop-counts', 
                          default=self.config_manager.get_jmeter_config()['test']['loop_counts'], 
                          nargs='+', 
                          type=int, 
                          help='循环次数列表，默认读取配置文件，例如：--loop-counts 1 3 5')
        
        # 🟡 JMX文件路径 - 指定JMeter测试计划文件
        # default: 从配置文件读取，通常是 'src/tools/jmeter/api_cases/heartbeat_test.jmx'
        # 作用：指定要执行的JMeter测试计划文件
        parser.add_argument('--jmx', 
                          default=self.config_manager.get_jmeter_config()['jmeter']['default_jmx'], 
                          help='JMX文件路径，默认读取配置文件')
        
        # 🟡 JMeter可执行文件路径 - 指定JMeter程序位置
        # default: 从配置文件读取，通常是 'D:/data/work/json/src/tools/jmeter/bin/jmeter.bat'
        # 作用：指定JMeter程序的安装路径
        parser.add_argument('--jmeter-bin', 
                          default=self.config_manager.get_jmeter_config()['jmeter']['jmeter_bin'], 
                          help='JMeter可执行文件路径，默认读取配置文件')
        
        # 🟡 输出目录 - 指定测试结果保存位置
        # default: 从配置文件读取，通常是 'src/tools/jmeter/results'
        # 作用：指定测试结果和报告的保存目录
        parser.add_argument('--output-dir', 
                          default=self.config_manager.get_jmeter_config()['output']['base_dir'], 
                          help='输出目录，默认读取配置文件')
        
        # 🟡 测试名称 - 指定测试的标识名称
        # default: 从配置文件读取，通常是 '接口性能测试'
        # 作用：用于标识测试，影响报告文件名和日志标识
        parser.add_argument('--test-name', 
                          default=self.config_manager.get_jmeter_config()['jmeter']['default_test_name'], 
                          help='测试名称，默认读取配置文件')
        
        # ==================== 🟢 功能开关参数（布尔类型，默认关闭） ====================
        
        # 🟢 自动调优功能 - 启用自动调优
        # action='store_true': 如果提供此参数，值为True；否则为False
        # 默认：False（不启用）
        # 作用：测试完成后自动分析报告并优化参数
        parser.add_argument('--auto-tune', 
                          action='store_true', 
                          help='启用自动调优，测试完成后自动分析报告并优化参数')
        
        # 🟢 禁用自动调优 - 明确禁用自动调优
        # action='store_true': 如果提供此参数，值为True；否则为False
        # 默认：False（不启用）
        # 作用：明确禁用自动调优功能
        parser.add_argument('--no-auto-tune', 
                          action='store_true', 
                          help='禁用自动调优功能，默认不执行')
        
        # 🟢 Excel报告生成 - 生成Excel格式报告
        # action='store_true': 如果提供此参数，值为True；否则为False
        # 默认：False（不生成Excel报告）
        # 作用：生成Excel多sheet格式的详细报告
        parser.add_argument('--excel-report', 
                          action='store_true', 
                          help='生成Excel多sheet报告')
        
        # 🟢 同步设备功能 - 同步数据库设备数据
        # action='store_true': 如果提供此参数，值为True；否则为False
        # 默认：False（不同步）
        # 作用：从数据库同步真实注册设备到actual_used_devices.json
        parser.add_argument('--sync-actual-devices', 
                          action='store_true', 
                          help='同步数据库真实注册设备到actual_used_devices.json')
        
        # ==================== 🔵 配置参数（有默认值，用于调整行为） ====================
        
        # 🔵 测试类型 - 指定要执行的测试类型
        # choices: 限制可选值，只能从指定列表中选择
        # default='register': 默认执行注册测试
        # 作用：指定要测试的接口类型
        parser.add_argument('--test-type', 
                          choices=['register', 'strategy', 'device_info', 'mode', 'brand', 'guard', 'logo', 'mqtt', 'heartbeat', 'all'], 
                          default='register', 
                          help='测试类型：register(终端注册), strategy(获取策略), device_info(获取设备信息), mode(获取模式设置), brand(获取品牌设置), guard(获取内卫设置), logo(获取logo设置), mqtt(获取MQTT地址), heartbeat(心跳), all(所有接口)')
        
        return parser
    
    def _process_thread_counts(self, thread_counts) -> list:
        """
        处理线程数参数 - 接口层参数验证
        
        职责：将用户输入的线程数参数转换为标准格式
        
        Args:
            thread_counts: 线程数参数（字符串、列表或单个值）
            
        Returns:
            list: 标准化的线程数列表
        """
        print(f"[DEBUG] 线程数: {thread_counts}")
        if isinstance(thread_counts, str):
            thread_counts = [int(x) for x in thread_counts.split(',') if x.strip()]
        elif not isinstance(thread_counts, list):
            thread_counts = [int(thread_counts)]
        return thread_counts
    
    def _process_loop_counts(self, loop_counts) -> list:
        """
        处理循环次数参数 - 接口层参数验证
        
        职责：将用户输入的循环次数参数转换为标准格式
        
        Args:
            loop_counts: 循环次数参数（字符串、列表或单个值）
            
        Returns:
            list: 标准化的循环次数列表
        """
        print(f"[DEBUG] 循环数: {loop_counts}")
        if isinstance(loop_counts, str):
            loop_counts = [int(x) for x in loop_counts.split(',') if x.strip()]
        elif not isinstance(loop_counts, list):
            loop_counts = [int(loop_counts)]
        return loop_counts
    
    def _get_test_types(self, test_type: str) -> list:
        """
        获取测试类型列表 - 接口层参数处理
        
        职责：根据用户输入的测试类型，解析出需要执行的具体测试列表
        
        Args:
            test_type: 测试类型字符串
            
        Returns:
            list: 具体的测试类型列表
        """
        if test_type == 'all':
            return ['register', 'strategy', 'device_info', 'mode', 'brand', 'guard', 'logo', 'mqtt', 'heartbeat']
        else:
            return [test_type]
    
    def _get_jmx_base_dir(self, jmx_path: str) -> str:
        """
        获取JMX文件基础目录 - 接口层路径处理
        
        职责：根据JMX文件路径，确定JMX文件的基础目录
        
        Args:
            jmx_path: JMX文件路径
            
        Returns:
            str: JMX文件基础目录
        """
        if 'api_cases' in jmx_path:
            return os.path.dirname(jmx_path)
        else:
            return 'src/tools/jmeter/api_cases'


# 创建默认CLI实例
_default_cli = PerformanceTestCLI()


def create_timestamped_output_dir(base_output_dir: str) -> str:
    """
    创建以时间戳命名的输出目录（保持向后兼容）
    
    职责：为现有代码提供向后兼容的接口
    
    Args:
        base_output_dir: 基础输出目录
        
    Returns:
        str: 时间戳子目录路径
    """
    return _default_cli.create_timestamped_output_dir(base_output_dir)


def main():
    """
    主函数（保持向后兼容）
    
    职责：为现有代码提供向后兼容的入口点
    
    Returns:
        bool: 执行是否成功
    """
    return _default_cli.run()


if __name__ == '__main__':
    main() 
