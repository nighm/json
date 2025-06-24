#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合授权管理工具
合并了授权分析、深度分析和问题修复功能
"""
import pymysql
import json
import argparse
from datetime import datetime, timedelta

class AuthorizationManager:
    def __init__(self, host='192.168.24.45', port=3307, user='root', 
                 password='At6mj*1ygb2', database='yangguan'):
        """初始化授权管理器"""
        self.db_config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4'
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def analyze_authorization_limits(self):
        """分析授权限制信息"""
        print("=== 授权限制分析报告 ===\n")
        
        if not self.connect():
            return
        
        try:
            # 1. 查看当前设备统计
            print("1. 当前设备统计")
            print("-" * 50)
            self.cursor.execute("""
                SELECT 
                    device_group_id,
                    COUNT(*) as device_count,
                    COUNT(DISTINCT brand) as brand_count,
                    GROUP_CONCAT(DISTINCT brand) as brands
                FROM biz_device 
                WHERE del_flag = 0 
                GROUP BY device_group_id
            """)
            device_stats = self.cursor.fetchall()
            
            for stat in device_stats:
                print(f"设备组ID: {stat[0]}")
                print(f"设备数量: {stat[1]}")
                print(f"品牌数量: {stat[2]}")
                print(f"品牌列表: {stat[3]}")
                print()
            
            # 2. 查看授权订阅信息
            print("2. 授权订阅信息")
            print("-" * 50)
            self.cursor.execute("""
                SELECT 
                    id, dept_id, service_item, duration, 
                    authorized_device_num, server_ip, server_id, create_time
                FROM sys_authorization_subscribe 
                WHERE del_flag = 0
            """)
            subscribe_data = self.cursor.fetchall()
            
            for row in subscribe_data:
                print(f"订阅ID: {row[0]}")
                print(f"部门ID: {row[1]}")
                print(f"服务项: {row[2]}")
                print(f"时长(月): {row[3]}")
                print(f"授权设备数: {row[4]}")
                print(f"服务器IP: {row[5]}")
                print(f"服务器ID: {row[6]}")
                print(f"创建时间: {row[7]}")
                print()
            
            # 3. 查看授权分配信息
            print("3. 授权分配信息")
            print("-" * 50)
            self.cursor.execute("""
                SELECT 
                    id, dept_id, service_item, device_num, 
                    customer_code, create_time, expiry_time
                FROM sys_authorization_assign 
                WHERE del_flag = 0
            """)
            assign_data = self.cursor.fetchall()
            
            for row in assign_data:
                print(f"分配ID: {row[0]}")
                print(f"部门ID: {row[1]}")
                print(f"服务项: {row[2]}")
                print(f"设备数: {row[3]}")
                print(f"客户代码: {row[4]}")
                print(f"创建时间: {row[5]}")
                print(f"过期时间: {row[6]}")
                print()
            
            # 4. 分析授权限制原因
            print("4. 授权限制分析")
            print("-" * 50)
            
            current_group_id = device_stats[0][0] if device_stats else None
            
            if current_group_id:
                self.cursor.execute("""
                    SELECT service_item, device_num, dept_id
                    FROM sys_authorization_assign 
                    WHERE del_flag = 0 AND dept_id = %s
                """, (current_group_id,))
                group_assignments = self.cursor.fetchall()
                
                if group_assignments:
                    print(f"当前设备组ID: {current_group_id}")
                    print("对应的授权分配:")
                    for assignment in group_assignments:
                        print(f"  服务项: {assignment[0]}, 授权设备数: {assignment[1]}, 部门ID: {assignment[2]}")
                    
                    total_authorized = sum(assignment[1] for assignment in group_assignments)
                    current_devices = device_stats[0][1] if device_stats else 0
                    
                    print(f"\n授权限制分析:")
                    print(f"  当前设备数: {current_devices}")
                    print(f"  总授权设备数: {total_authorized}")
                    print(f"  剩余可用设备数: {total_authorized - current_devices}")
                    
                    if current_devices >= total_authorized:
                        print(f"  ❌ 已达到授权限制！")
                        print(f"  💡 建议: 增加授权设备数或删除部分设备")
                    else:
                        print(f"  ✅ 未达到授权限制")
                else:
                    print(f"⚠️  未找到设备组 {current_group_id} 的授权分配信息")
            else:
                print("⚠️  无法确定当前设备组ID")
                
        except Exception as e:
            print(f"❌ 分析过程中出现错误: {e}")

    def deep_authorization_analysis(self):
        """深度授权分析"""
        print("=== 深度授权限制分析 ===\n")
        
        if not self.connect():
            return
        
        try:
            # 1. 检查所有可能的授权相关表
            print("1. 检查所有授权相关表")
            print("-" * 50)
            
            auth_tables = [
                'sys_authorization_subscribe',
                'sys_authorization_assign', 
                'sys_authorization_service_assign',
                'sys_config'
            ]
            
            for table in auth_tables:
                try:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = self.cursor.fetchone()[0]
                    print(f"{table}: {count} 条记录")
                except Exception as e:
                    print(f"{table}: 查询失败 - {e}")
            
            # 2. 检查系统配置
            print("\n2. 系统配置检查")
            print("-" * 50)
            
            self.cursor.execute("""
                SELECT config_key, config_value, config_type
                FROM sys_config 
                WHERE config_key LIKE '%device%' OR config_key LIKE '%auth%' OR config_key LIKE '%limit%'
            """)
            device_configs = self.cursor.fetchall()
            
            if device_configs:
                print("设备相关配置:")
                for config in device_configs:
                    print(f"  {config[0]}: {config[1]} ({config[2]})")
            else:
                print("未找到设备相关配置")
            
            # 3. 检查设备注册历史
            print("\n3. 设备注册历史检查")
            print("-" * 50)
            
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_devices,
                    COUNT(DISTINCT device_serial_number) as unique_sn,
                    COUNT(DISTINCT mac) as unique_mac,
                    MIN(create_time) as first_register,
                    MAX(create_time) as last_register
                FROM biz_device 
                WHERE del_flag = 0 OR del_flag = 1
            """)
            device_history = self.cursor.fetchone()
            
            print(f"设备注册历史统计:")
            print(f"  总设备记录数: {device_history[0]}")
            print(f"  唯一序列号数: {device_history[1]}")
            print(f"  唯一MAC地址数: {device_history[2]}")
            print(f"  首次注册时间: {device_history[3]}")
            print(f"  最后注册时间: {device_history[4]}")
            
            # 4. 检查软删除的设备
            self.cursor.execute("SELECT COUNT(*) FROM biz_device WHERE del_flag = 1")
            soft_deleted = self.cursor.fetchone()[0]
            print(f"  软删除设备数: {soft_deleted}")
            
            # 5. 检查设备清理表
            print("\n4. 设备清理表检查")
            print("-" * 50)
            
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_cleared,
                    COUNT(DISTINCT device_serial_number) as unique_cleared_sn,
                    MIN(create_time) as first_clear,
                    MAX(create_time) as last_clear
                FROM biz_device_clear
            """)
            clear_history = self.cursor.fetchone()
            
            print(f"设备清理历史:")
            print(f"  总清理记录数: {clear_history[0]}")
            print(f"  唯一清理序列号数: {clear_history[1]}")
            print(f"  首次清理时间: {clear_history[2]}")
            print(f"  最后清理时间: {clear_history[3]}")
            
        except Exception as e:
            print(f"❌ 深度分析过程中出现错误: {e}")

    def fix_authorization_issue(self):
        """修复授权分配问题"""
        print("=== 修复授权分配问题 ===\n")
        
        if not self.connect():
            return
        
        try:
            # 1. 获取当前设备组信息
            self.cursor.execute("""
                SELECT device_group_id, COUNT(*) as device_count
                FROM biz_device 
                WHERE del_flag = 0 
                GROUP BY device_group_id
            """)
            device_group = self.cursor.fetchone()
            
            if not device_group:
                print("❌ 未找到设备组信息")
                return
            
            current_group_id = device_group[0]
            current_device_count = device_group[1]
            
            print(f"当前设备组ID: {current_group_id}")
            print(f"当前设备数量: {current_device_count}")
            
            # 2. 检查是否已有授权分配
            self.cursor.execute("""
                SELECT id, service_item, device_num
                FROM sys_authorization_assign 
                WHERE dept_id = %s AND del_flag = 0
            """, (current_group_id,))
            existing_assignments = self.cursor.fetchall()
            
            if existing_assignments:
                print(f"\n✅ 已存在授权分配:")
                for assignment in existing_assignments:
                    print(f"  ID: {assignment[0]}, 服务项: {assignment[1]}, 设备数: {assignment[2]}")
            else:
                print(f"\n❌ 未找到设备组 {current_group_id} 的授权分配")
                
                # 3. 创建授权分配
                print(f"\n🔧 正在创建授权分配...")
                
                # 获取可用的服务项
                self.cursor.execute("""
                    SELECT DISTINCT service_item, authorized_device_num
                    FROM sys_authorization_subscribe 
                    WHERE del_flag = 0
                """)
                available_services = self.cursor.fetchall()
                
                if not available_services:
                    print("❌ 未找到可用的服务项")
                    return
                
                # 为每个服务项创建授权分配
                for service in available_services:
                    service_item = service[0]
                    authorized_num = service[1]
                    
                    # 设置过期时间为1年后
                    expiry_time = datetime.now() + timedelta(days=365)
                    
                    self.cursor.execute("""
                        INSERT INTO sys_authorization_assign 
                        (server_ip, server_id, dept_id, device_num, service_item, 
                         create_time, create_by, update_time, update_by, del_flag, 
                         batch_no, duration, issue_time, expiry_time, order_time, 
                         sync_time, customer_code)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        '',  # server_ip
                        'klsec-server',  # server_id
                        current_group_id,  # dept_id
                        authorized_num,  # device_num
                        service_item,  # service_item
                        datetime.now(),  # create_time
                        'system',  # create_by
                        datetime.now(),  # update_time
                        'system',  # update_by
                        '0',  # del_flag
                        f'BATCH_{datetime.now().strftime("%Y%m%d%H%M%S")}',  # batch_no
                        12,  # duration
                        datetime.now(),  # issue_time
                        expiry_time,  # expiry_time
                        datetime.now(),  # order_time
                        datetime.now(),  # sync_time
                        '101'  # customer_code
                    ))
                    
                    print(f"  ✅ 创建服务项 {service_item} 的授权分配，设备数: {authorized_num}")
                
                # 提交事务
                self.conn.commit()
                print(f"\n✅ 授权分配创建完成！")
            
            # 4. 验证修复结果
            print(f"\n🔍 验证修复结果:")
            self.cursor.execute("""
                SELECT service_item, device_num, expiry_time
                FROM sys_authorization_assign 
                WHERE dept_id = %s AND del_flag = 0
            """, (current_group_id,))
            new_assignments = self.cursor.fetchall()
            
            total_authorized = sum(assignment[1] for assignment in new_assignments)
            remaining = total_authorized - current_device_count
            
            print(f"  总授权设备数: {total_authorized}")
            print(f"  当前设备数: {current_device_count}")
            print(f"  剩余可用设备数: {remaining}")
            
            if remaining > 0:
                print(f"  ✅ 现在可以注册 {remaining} 台设备了！")
            else:
                print(f"  ⚠️  仍然达到授权限制")
                
        except Exception as e:
            print(f"❌ 修复过程中出现错误: {e}")
            self.conn.rollback()

def main():
    parser = argparse.ArgumentParser(description='综合授权管理工具')
    parser.add_argument('--host', default='192.168.24.45', help='数据库主机地址')
    parser.add_argument('--port', type=int, default=3307, help='数据库端口')
    parser.add_argument('--user', default='root', help='数据库用户名')
    parser.add_argument('--password', default='At6mj*1ygb2', help='数据库密码')
    parser.add_argument('--database', default='yangguan', help='数据库名称')
    parser.add_argument('--action', choices=['analyze', 'deep-analyze', 'fix', 'all'], 
                       default='all', help='执行的操作：analyze(基础分析), deep-analyze(深度分析), fix(修复), all(全部)')
    
    args = parser.parse_args()
    
    manager = AuthorizationManager(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    try:
        if args.action == 'analyze' or args.action == 'all':
            manager.analyze_authorization_limits()
        
        if args.action == 'deep-analyze' or args.action == 'all':
            manager.deep_authorization_analysis()
        
        if args.action == 'fix' or args.action == 'all':
            manager.fix_authorization_issue()
            
    finally:
        manager.close()

if __name__ == "__main__":
    main() 