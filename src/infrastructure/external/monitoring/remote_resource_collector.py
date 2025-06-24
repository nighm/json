import paramiko
import time
import re

class RemoteResourceCollector:
    def __init__(self, host, username, password=None, key_filename=None):
        self.host = host
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self._ssh = None  # 持久SSH连接

    def _connect_ssh(self):
        """建立SSH持久连接"""
        if not self._ssh:
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(self.host, username=self.username, password=self.password, key_filename=self.key_filename)
        return self._ssh

    def _ssh_exec(self, command):
        """使用持久连接执行SSH命令"""
        try:
            ssh = self._connect_ssh()
            stdin, stdout, stderr = ssh.exec_command(command)
            result = stdout.read().decode().strip()
            return result
        except Exception as e:
            print(f"⚠️ SSH命令执行失败: {e}")
            # 连接可能断开，重置连接
            self._ssh = None
            return "0"

    def __del__(self):
        """析构时关闭SSH连接"""
        if self._ssh:
            try:
                self._ssh.close()
            except:
                pass

    def get_process_info(self):
        """
        获取进程数、线程数和上下文切换数
        Returns:
            dict: 包含process_count, thread_count, context_switches信息
        """
        try:
            # 获取进程数
            cmd_proc = "ps -e | wc -l"
            process_count = int(self._ssh_exec(cmd_proc))
            
            # 获取线程数
            cmd_thread = "ps -eLf | wc -l"
            thread_count = int(self._ssh_exec(cmd_thread))
            
            # 获取上下文切换数
            cmd_cs = "cat /proc/stat | grep ctxt"
            cs_output = self._ssh_exec(cmd_cs)
            context_switches = int(cs_output.split()[1]) if cs_output else 0
            
            return {
                'process_count': process_count,
                'thread_count': thread_count,
                'context_switches': context_switches
            }
        except Exception as e:
            print(f"❌ 获取进程信息失败: {e}")
            return {
                'process_count': 0,
                'thread_count': 0,
                'context_switches': 0
            }

    def get_cpu_usage(self):
        """
        采集全核平均CPU使用率，解析/proc/stat，保证与top/htop一致
        """
        cmd = "cat /proc/stat | grep '^cpu '"
        stat1 = self._ssh_exec(cmd)
        time.sleep(1)
        stat2 = self._ssh_exec(cmd)
        def parse_cpu_line(line):
            parts = [float(x) for x in line.strip().split()[1:]]
            idle = parts[3]
            total = sum(parts)
            return idle, total
        idle1, total1 = parse_cpu_line(stat1)
        idle2, total2 = parse_cpu_line(stat2)
        usage = 100 * (1 - (idle2 - idle1) / (total2 - total1))
        return usage

    def get_memory_usage(self):
        """
        采集内存使用率，解析/proc/meminfo，返回详细的内存信息
        Returns:
            dict: 包含total, used, free, available, usage_percent等信息
        """
        try:
            # 读取/proc/meminfo获取内存信息
            cmd = "cat /proc/meminfo"
            meminfo = self._ssh_exec(cmd)
            
            # 解析内存信息
            mem_data = {}
            for line in meminfo.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    mem_data[key.strip()] = int(value.strip().split()[0]) * 1024  # 转换为字节
            
            # 计算内存使用情况
            total = mem_data.get('MemTotal', 0)
            free = mem_data.get('MemFree', 0)
            available = mem_data.get('MemAvailable', 0)
            cached = mem_data.get('Cached', 0)
            buffers = mem_data.get('Buffers', 0)
            
            # 计算实际使用的内存（不包括缓存和缓冲区）
            used = total - available if available > 0 else (total - free - cached - buffers)
            
            # 计算使用率
            usage_percent = (used / total * 100) if total > 0 else 0
            
            return {
                'total': total,
                'used': used,
                'free': free,
                'available': available,
                'cached': cached,
                'buffers': buffers,
                'usage_percent': usage_percent
            }
        except Exception as e:
            print(f"❌ 获取内存信息失败: {e}")
            return {
                'total': 0,
                'used': 0,
                'free': 0,
                'available': 0,
                'cached': 0,
                'buffers': 0,
                'usage_percent': 0
            }

    def get_disk_usage(self):
        """
        采集磁盘使用率，使用df命令获取磁盘信息
        Returns:
            dict: 包含total, used, free, usage_percent等信息
        """
        try:
            # 使用df命令获取根目录磁盘使用情况
            cmd = "df -h / | tail -1"
            df_output = self._ssh_exec(cmd)
            
            # 解析df输出
            # 格式: Filesystem Size Used Avail Use% Mounted on
            parts = df_output.split()
            if len(parts) >= 5:
                filesystem = parts[0]
                total_str = parts[1]
                used_str = parts[2]
                free_str = parts[3]
                usage_percent_str = parts[4].replace('%', '')
                
                # 转换大小字符串为字节数
                def parse_size(size_str):
                    """将大小字符串转换为字节数"""
                    size_str = size_str.upper()
                    if 'G' in size_str:
                        return int(float(size_str.replace('G', '')) * 1024 * 1024 * 1024)
                    elif 'M' in size_str:
                        return int(float(size_str.replace('M', '')) * 1024 * 1024)
                    elif 'K' in size_str:
                        return int(float(size_str.replace('K', '')) * 1024)
                    else:
                        return int(float(size_str))
                
                total = parse_size(total_str)
                used = parse_size(used_str)
                free = parse_size(free_str)
                usage_percent = float(usage_percent_str)
                
                return {
                    'filesystem': filesystem,
                    'total': total,
                    'used': used,
                    'free': free,
                    'usage_percent': usage_percent
                }
            else:
                raise ValueError("无法解析df命令输出")
                
        except Exception as e:
            print(f"❌ 获取磁盘信息失败: {e}")
            return {
                'filesystem': '/',
                'total': 0,
                'used': 0,
                'free': 0,
                'usage_percent': 0
            }

    def collect_cpu_usage_over_time(self, duration, interval=2):
        """
        定时采集CPU使用率，返回[(timestamp, usage), ...]
        Args:
            duration: 采集总时长（秒）
            interval: 采样间隔（秒）
        """
        records = []
        start = time.time()
        while time.time() - start < duration:
            usage = self.get_cpu_usage()
            records.append((time.strftime('%Y-%m-%d %H:%M:%S'), usage))
            time.sleep(interval)
        return records

    def collect_memory_usage_over_time(self, duration, interval=2):
        """
        定时采集内存使用率，返回[(timestamp, memory_info), ...]
        Args:
            duration: 采集总时长（秒）
            interval: 采样间隔（秒）
        """
        records = []
        start = time.time()
        while time.time() - start < duration:
            memory_info = self.get_memory_usage()
            records.append((time.strftime('%Y-%m-%d %H:%M:%S'), memory_info))
            time.sleep(interval)
        return records

    def collect_disk_usage_over_time(self, duration, interval=2):
        """
        定时采集磁盘使用率，返回[(timestamp, disk_info), ...]
        Args:
            duration: 采集总时长（秒）
            interval: 采样间隔（秒）
        """
        records = []
        start = time.time()
        while time.time() - start < duration:
            disk_info = self.get_disk_usage()
            records.append((time.strftime('%Y-%m-%d %H:%M:%S'), disk_info))
            time.sleep(interval)
        return records

    def collect_all_resources_over_time(self, duration, interval=2):
        """
        同时采集CPU、内存、磁盘使用率
        Args:
            duration: 采集总时长（秒）
            interval: 采样间隔（秒）
        Returns:
            dict: 包含cpu_records, memory_records, disk_records
        """
        cpu_records = []
        memory_records = []
        disk_records = []
        
        start = time.time()
        while time.time() - start < duration:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 并行采集各项指标
            try:
                cpu_usage = self.get_cpu_usage()
                cpu_records.append((timestamp, cpu_usage))
            except Exception as e:
                print(f"⚠️  CPU采集异常: {e}")
            
            try:
                memory_info = self.get_memory_usage()
                memory_records.append((timestamp, memory_info))
            except Exception as e:
                print(f"⚠️  内存采集异常: {e}")
            
            try:
                disk_info = self.get_disk_usage()
                disk_records.append((timestamp, disk_info))
            except Exception as e:
                print(f"⚠️  磁盘采集异常: {e}")
            
            time.sleep(interval)
        
        return {
            'cpu_records': cpu_records,
            'memory_records': memory_records,
            'disk_records': disk_records
        }

    def start_cpu_stress(self, seconds=30, cores=2):
        """
        用yes命令模拟多核高负载，无需第三方工具
        Args:
            seconds: 加压持续时间
            cores: 加压核数（即启动多少个yes进程）
        """
        for _ in range(cores):
            self._ssh_exec("nohup bash -c 'yes > /dev/null &' > /dev/null 2>&1 &")
        # 定时kill所有yes进程，避免影响业务
        self._ssh_exec(f"(sleep {seconds}; pkill yes) > /dev/null 2>&1 &") 