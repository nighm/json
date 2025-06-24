import time
from src.domain.monitor.resource_snapshot import ResourceSnapshot
from src.domain.monitor.hardware_metrics import HardwareMetrics
from src.domain.monitor.test_summary import TestSummary
from src.domain.monitor.hardware_monitor_report import HardwareMonitorReport
from src.infrastructure.external.monitoring.remote_resource_collector import RemoteResourceCollector
import numpy as np
from typing import List

class ResourceMonitorService:
    """资源监控服务，负责协调监控和报告生成"""
    
    def __init__(self, host, username, password):
        self.collector = RemoteResourceCollector(host, username, password)
        # 移除connect调用，因为RemoteResourceCollector没有connect方法
        # self.collector.connect()

    def collect_snapshot(self):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        cpu = self.collector.get_cpu_usage()
        memory = self.collector.get_memory_usage()
        disk = self.collector.get_disk_usage()
        return ResourceSnapshot(timestamp, cpu=cpu, memory=memory, disk=disk)

    def collect_cpu_during_test(self, duration, interval=5):
        """
        定时采集CPU，统计各类指标
        Args:
            duration: 采集总时长（秒）
            interval: 采样间隔（秒）
        Returns:
            dict: 包含max, min, avg, p90, p95, records
        """
        records = self.collector.collect_cpu_usage_over_time(duration, interval)
        usages = [u for t, u in records]
        stats = {
            'max': max(usages) if usages else None,
            'min': min(usages) if usages else None,
            'avg': sum(usages)/len(usages) if usages else None,
            'p90': float(np.percentile(usages, 90)) if usages else None,
            'p95': float(np.percentile(usages, 95)) if usages else None,
            'records': records
        }
        return stats

    def collect_memory_during_test(self, duration, interval=5):
        """
        定时采集内存，统计各类指标
        Args:
            duration: 采集总时长（秒）
            interval: 采样间隔（秒）
        Returns:
            dict: 包含max, min, avg, p90, p95, records
        """
        records = self.collector.collect_memory_usage_over_time(duration, interval)
        usages = [m['usage_percent'] for t, m in records]
        stats = {
            'max': max(usages) if usages else None,
            'min': min(usages) if usages else None,
            'avg': sum(usages)/len(usages) if usages else None,
            'p90': float(np.percentile(usages, 90)) if usages else None,
            'p95': float(np.percentile(usages, 95)) if usages else None,
            'records': records
        }
        return stats

    def collect_disk_during_test(self, duration, interval=5):
        """
        定时采集磁盘，统计各类指标
        Args:
            duration: 采集总时长（秒）
            interval: 采样间隔（秒）
        Returns:
            dict: 包含max, min, avg, p90, p95, records
        """
        records = self.collector.collect_disk_usage_over_time(duration, interval)
        usages = [d['usage_percent'] for t, d in records]
        stats = {
            'max': max(usages) if usages else None,
            'min': min(usages) if usages else None,
            'avg': sum(usages)/len(usages) if usages else None,
            'p90': float(np.percentile(usages, 90)) if usages else None,
            'p95': float(np.percentile(usages, 95)) if usages else None,
            'records': records
        }
        return stats

    def collect_all_resources_during_test(self, duration, interval=5):
        """
        同时采集CPU、内存、磁盘，统计各类指标
        Args:
            duration: 采集总时长（秒）
            interval: 采样间隔（秒）
        Returns:
            dict: 包含cpu_stats, memory_stats, disk_stats
        """
        all_records = self.collector.collect_all_resources_over_time(duration, interval)
        
        # 分析CPU数据
        cpu_usages = [u for t, u in all_records['cpu_records']]
        cpu_stats = {
            'max': max(cpu_usages) if cpu_usages else None,
            'min': min(cpu_usages) if cpu_usages else None,
            'avg': sum(cpu_usages)/len(cpu_usages) if cpu_usages else None,
            'p90': float(np.percentile(cpu_usages, 90)) if cpu_usages else None,
            'p95': float(np.percentile(cpu_usages, 95)) if cpu_usages else None,
            'records': all_records['cpu_records']
        }
        
        # 分析内存数据
        memory_usages = [m['usage_percent'] for t, m in all_records['memory_records']]
        memory_stats = {
            'max': max(memory_usages) if memory_usages else None,
            'min': min(memory_usages) if memory_usages else None,
            'avg': sum(memory_usages)/len(memory_usages) if memory_usages else None,
            'p90': float(np.percentile(memory_usages, 90)) if memory_usages else None,
            'p95': float(np.percentile(memory_usages, 95)) if memory_usages else None,
            'records': all_records['memory_records']
        }
        
        # 分析磁盘数据
        disk_usages = [d['usage_percent'] for t, d in all_records['disk_records']]
        disk_stats = {
            'max': max(disk_usages) if disk_usages else None,
            'min': min(disk_usages) if disk_usages else None,
            'avg': sum(disk_usages)/len(disk_usages) if disk_usages else None,
            'p90': float(np.percentile(disk_usages, 90)) if disk_usages else None,
            'p95': float(np.percentile(disk_usages, 95)) if disk_usages else None,
            'records': all_records['disk_records']
        }
        
        return {
            'cpu_stats': cpu_stats,
            'memory_stats': memory_stats,
            'disk_stats': disk_stats
        }

    def generate_hardware_report(self, test_name: str, duration: int, interval: int, 
                               concurrent_users: int = None, notes: str = None) -> HardwareMonitorReport:
        """
        生成硬件监控报告
        Args:
            test_name: 测试名称
            duration: 采集时长（秒）
            interval: 采样间隔（秒）
            concurrent_users: 并发用户数
            notes: 备注信息
        Returns:
            HardwareMonitorReport: 硬件监控报告
        """
        # 采集数据
        stats = self.collect_cpu_during_test(duration, interval)
        
        # 计算CPU变化率
        cpu_change_rate = ((stats['max'] - stats['min']) / stats['min'] * 100) if stats['min'] is not None and stats['min'] > 0 else 0
        
        # 创建测试概览
        summary = TestSummary(
            test_name=test_name,
            concurrent_users=concurrent_users,
            sample_interval=interval,
            notes=notes
        )
        
        # 创建硬件指标
        metrics = HardwareMetrics(
            max_cpu=stats['max'],
            min_cpu=stats['min'],
            avg_cpu=stats['avg'],
            p90_cpu=stats['p90'],
            p95_cpu=stats['p95'],
            cpu_change_rate=cpu_change_rate,
            records=stats['records']
        )
        
        # 生成结论和建议
        conclusion = self._generate_conclusion(metrics)
        recommendations = self._generate_recommendations(metrics)
        
        return HardwareMonitorReport(
            summary=summary,
            metrics=metrics,
            conclusion=conclusion,
            recommendations=recommendations
        )
    
    def _generate_conclusion(self, metrics: HardwareMetrics) -> str:
        """生成测试结论"""
        if metrics.avg_cpu is None:
            return "无足够数据生成结论。"

        if metrics.avg_cpu >= 80:
            status = "系统资源已接近瓶颈，建议及时扩容"
        elif metrics.avg_cpu >= 60:
            status = "系统资源使用率较高，建议关注系统负载变化"
        else:
            status = "系统资源充足，运行状态良好"
            
        return f"本次测试期间，CPU使用率最高达到{metrics.max_cpu:.1f}%，平均使用率为{metrics.avg_cpu:.1f}%。{status}。"
    
    def _generate_recommendations(self, metrics: HardwareMetrics) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if metrics.avg_cpu is None:
            return recommendations

        if metrics.avg_cpu >= 80:
            recommendations.extend([
                "建议增加服务器CPU核心数或升级CPU型号",
                "建议优化接口性能，减少CPU密集型操作",
                "建议考虑使用负载均衡，分散系统压力"
            ])
        elif metrics.avg_cpu >= 60:
            recommendations.extend([
                "建议持续监控系统资源使用情况",
                "建议制定系统扩容预案",
                "建议优化数据库查询和缓存策略"
            ])
            
        if metrics.cpu_change_rate > 50:
            recommendations.extend([
                "CPU使用率波动较大，建议检查是否存在资源竞争问题",
                "建议检查是否有定时任务或批处理作业影响系统性能",
                "建议优化任务调度策略，避免资源使用峰值"
            ])
            
        return recommendations

    def close(self):
        """关闭连接"""
        # RemoteResourceCollector没有显式的close方法，这里可以留空
        pass 