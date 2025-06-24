# -*- coding: utf-8 -*-
"""
性能批量注册/登录主控服务（DDD架构）
- 负责参数批量组合、流程调度、结果整合
- 底层功能全部通过依赖注入的DDD已有模块调用
- 便于任何py文件import调用
"""
from typing import List, Dict, Any
from src.domain.entities.test_result import TestResult

class PerformanceBatchService:
    """
    性能批量注册/登录主控服务
    负责参数批量组合、流程调度、结果整合，底层功能全部调用DDD已有模块
    """
    def __init__(self, jmeter_executor, resource_monitor, report_generator, device_query_service):
        """
        依赖注入底层服务
        :param jmeter_executor: JMeterExecutor实例
        :param resource_monitor: ResourceMonitorService实例
        :param report_generator: ReportGenerator实例
        :param device_query_service: DeviceQueryService实例
        """
        self.jmeter_executor = jmeter_executor
        self.resource_monitor = resource_monitor
        self.report_generator = report_generator
        self.device_query_service = device_query_service

    def run_batch_test(self, thread_configs: List[Dict[str, int]], test_type: str = "register", iterations: int = 1) -> List[TestResult]:
        """
        批量注册/登录主控流程
        :param thread_configs: [{'threads': 100, 'loops': 1}, ...]
        :param test_type: "register" or "login"
        :param iterations: 迭代次数
        :return: 测试结果列表
        """
        results = []
        count_before = self.device_query_service.get_device_count('biz_device')
        for i, config in enumerate(thread_configs):
            thread_count = config['threads']
            loops = config.get('loops', 1)
            test_name = f"{test_type}_{thread_count}_{loops}_iter{i+1}"
            # 启动资源监控（假设监控时长与测试时长一致，实际可根据需要调整）
            # 这里可根据实际情况先采集一次快照，或异步监控
            # 采集前快照
            # self.resource_monitor.collect_snapshot()
            # 执行JMeter测试
            result = self.jmeter_executor.execute_test(
                jmx_path=None,  # 由JMeterExecutor内部决定JMX
                iterations=loops,
                output_dir="src/tools/jmeter/results",
                test_name=test_name,
                thread_count=thread_count
            )
            # 采集资源监控数据（假设测试时长为result.duration，实际可根据需要调整）
            cpu_stats = self.resource_monitor.collect_cpu_during_test(duration=int(result.duration), interval=2)
            memory_stats = self.resource_monitor.collect_memory_during_test(duration=int(result.duration), interval=2)
            disk_stats = self.resource_monitor.collect_disk_during_test(duration=int(result.duration), interval=2)
            # 获取注册后设备数
            count_after = self.device_query_service.get_device_count('biz_device')
            # 写入监控数据和注册数量
            result.registered_count = count_after - count_before
            result.cpu_stats = cpu_stats
            result.memory_stats = memory_stats
            result.disk_stats = disk_stats
            count_before = count_after
            results.append(result)
        # 汇总报告
        self.report_generator.generate_summary_report(results)
        return results 