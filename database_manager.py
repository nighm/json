#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合数据库管理工具
合并了设备历史清理和设备删除功能
"""
import pymysql
import argparse
from datetime import datetime

class DatabaseManager:
    def __init__(self, host='192.168.24.45', port=3307, user='root', 
                 password='At6mj*1ygb2', database='yangguan'):
        """初始化数据库管理器"""
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

    def clear_all_device_history(self):
        """全库查找并彻底清理所有设备注册相关历史"""
        print("=== 全库设备注册历史清理工具 ===\n")
        
        if not self.connect():
            return
        
        try:
            # 1. 查找所有设备相关表
            self.cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in self.cursor.fetchall()]
            device_tables = [t for t in all_tables if 'device' in t or 'register' in t or 'clear' in t or 'history' in t]
            print(f"发现设备相关表：{device_tables}\n")
            
            # 2. 统计并清空每个表
            for table in device_tables:
                try:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = self.cursor.fetchone()[0]
                    print(f"表 {table} 现有记录数: {count}")
                    if count > 0:
                        self.cursor.execute(f"DELETE FROM {table}")
                        print(f"  已清空 {table}！")
                except Exception as e:
                    print(f"  跳过 {table}，原因: {e}")
            
            self.conn.commit()
            print("\n✅ 所有设备相关表已清理完毕！")
            
            # 3. 再次统计确认
            for table in device_tables:
                try:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = self.cursor.fetchone()[0]
                    print(f"表 {table} 剩余记录数: {count}")
                except Exception as e:
                    print(f"  跳过 {table}，原因: {e}")
                    
        except Exception as e:
            print(f"❌ 清理过程中出现错误: {e}")
            self.conn.rollback()

    def delete_devices(self, table='biz_device', filter_condition=None, limit=None):
        """删除设备"""
        print("=== 设备删除工具 ===\n")
        
        if not self.connect():
            return 0
        
        try:
            # 先查询要删除的设备数量
            count_sql = f"SELECT COUNT(*) FROM {table}"
            if filter_condition:
                count_sql += f" WHERE {filter_condition}"
            
            self.cursor.execute(count_sql)
            total_count = self.cursor.fetchone()[0]
            print(f"符合条件的设备总数: {total_count}")
            
            if total_count == 0:
                print("没有找到符合条件的设备")
                return 0
            
            # 构建删除SQL
            delete_sql = f"DELETE FROM {table}"
            if filter_condition:
                delete_sql += f" WHERE {filter_condition}"
            if limit:
                delete_sql += f" LIMIT {limit}"
            
            print(f"执行删除SQL: {delete_sql}")
            
            # 执行删除
            affected_rows = self.cursor.execute(delete_sql)
            self.conn.commit()
            
            print(f"成功删除 {affected_rows} 台设备")
            return affected_rows
            
        except Exception as e:
            print(f"删除失败: {e}")
            self.conn.rollback()
            return 0

    def analyze_device_tables(self):
        """分析设备相关表"""
        print("=== 设备相关表分析 ===\n")
        
        if not self.connect():
            return
        
        try:
            # 查找所有设备相关表
            self.cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in self.cursor.fetchall()]
            device_tables = [t for t in all_tables if 'device' in t or 'register' in t or 'clear' in t or 'history' in t]
            
            print(f"发现设备相关表：{len(device_tables)} 个")
            print("-" * 50)
            
            for table in device_tables:
                try:
                    # 统计记录数
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    total_count = self.cursor.fetchone()[0]
                    
                    # 统计软删除记录数
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE del_flag = 1")
                    deleted_count = self.cursor.fetchone()[0]
                    
                    # 统计有效记录数
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE del_flag = 0")
                    valid_count = self.cursor.fetchone()[0]
                    
                    print(f"表名: {table}")
                    print(f"  总记录数: {total_count}")
                    print(f"  有效记录数: {valid_count}")
                    print(f"  软删除记录数: {deleted_count}")
                    
                    # 显示表结构
                    self.cursor.execute(f"SHOW COLUMNS FROM {table}")
                    columns = self.cursor.fetchall()
                    print(f"  字段数: {len(columns)}")
                    
                    # 显示前几条记录
                    if total_count > 0:
                        self.cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        sample_records = self.cursor.fetchall()
                        print(f"  示例记录数: {len(sample_records)}")
                    
                    print()
                    
                except Exception as e:
                    print(f"  分析表 {table} 失败: {e}")
                    print()
                    
        except Exception as e:
            print(f"❌ 分析过程中出现错误: {e}")

    def backup_device_data(self, backup_table_suffix="_backup"):
        """备份设备数据"""
        print("=== 设备数据备份 ===\n")
        
        if not self.connect():
            return
        
        try:
            # 查找所有设备相关表
            self.cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in self.cursor.fetchall()]
            device_tables = [t for t in all_tables if 'device' in t or 'register' in t or 'clear' in t or 'history' in t]
            
            backup_tables = []
            
            for table in device_tables:
                backup_table = f"{table}{backup_table_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                try:
                    # 创建备份表
                    self.cursor.execute(f"CREATE TABLE {backup_table} LIKE {table}")
                    self.cursor.execute(f"INSERT INTO {backup_table} SELECT * FROM {table}")
                    
                    # 统计备份记录数
                    self.cursor.execute(f"SELECT COUNT(*) FROM {backup_table}")
                    backup_count = self.cursor.fetchone()[0]
                    
                    backup_tables.append((backup_table, backup_count))
                    print(f"✅ 表 {table} 已备份到 {backup_table}，记录数: {backup_count}")
                    
                except Exception as e:
                    print(f"❌ 备份表 {table} 失败: {e}")
            
            self.conn.commit()
            print(f"\n✅ 备份完成，共备份 {len(backup_tables)} 个表")
            
            return backup_tables
            
        except Exception as e:
            print(f"❌ 备份过程中出现错误: {e}")
            self.conn.rollback()
            return []

def main():
    parser = argparse.ArgumentParser(description='综合数据库管理工具')
    parser.add_argument('--host', default='192.168.24.45', help='数据库主机地址')
    parser.add_argument('--port', type=int, default=3307, help='数据库端口')
    parser.add_argument('--user', default='root', help='数据库用户名')
    parser.add_argument('--password', default='At6mj*1ygb2', help='数据库密码')
    parser.add_argument('--database', default='yangguan', help='数据库名称')
    parser.add_argument('--action', choices=['clear-history', 'delete-devices', 'analyze', 'backup', 'all'], 
                       default='analyze', help='执行的操作：clear-history(清理历史), delete-devices(删除设备), analyze(分析), backup(备份), all(全部)')
    parser.add_argument('--table', default='biz_device', help='操作的表名')
    parser.add_argument('--filter', help='筛选条件，如：brand=\'robot\'')
    parser.add_argument('--limit', type=int, help='删除数量限制')
    parser.add_argument('--confirm', action='store_true', help='确认删除操作')
    parser.add_argument('--backup-suffix', default='_backup', help='备份表后缀')
    
    args = parser.parse_args()
    
    manager = DatabaseManager(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    try:
        if args.action == 'analyze' or args.action == 'all':
            manager.analyze_device_tables()
        
        if args.action == 'backup' or args.action == 'all':
            manager.backup_device_data(args.backup_suffix)
        
        if args.action == 'clear-history' or args.action == 'all':
            if args.confirm:
                manager.clear_all_device_history()
            else:
                print("⚠️  清理历史操作需要 --confirm 参数确认")
        
        if args.action == 'delete-devices' or args.action == 'all':
            if args.confirm:
                manager.delete_devices(
                    table=args.table,
                    filter_condition=args.filter,
                    limit=args.limit
                )
            else:
                print("⚠️  删除设备操作需要 --confirm 参数确认")
                
    finally:
        manager.close()

if __name__ == "__main__":
    main() 