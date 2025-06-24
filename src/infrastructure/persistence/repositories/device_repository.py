from .db_client import DBClient
from src.domain.entities.device_info import DeviceInfo

class DeviceRepository:
    """
    设备信息查询仓储，支持批量查询设备信息。
    """
    def __init__(self, db_client: DBClient):
        self.db_client = db_client

    def get_all_devices(self, table_name='biz_device', limit=100, fields=None, filter_condition=None):
        """
        查询设备信息，支持指定表名、字段、筛选条件和数量限制。
        :param table_name: 查询的表名
        :param limit: 查询数量
        :param fields: 查询字段（逗号分隔字符串或列表）
        :param filter_condition: 筛选条件（如 'brand=\'HIKVISION\''）
        :return: DeviceInfo对象列表
        """
        # 处理字段
        if fields:
            if isinstance(fields, str):
                field_list = [f.strip() for f in fields.split(',')]
            else:
                field_list = fields
        else:
            # 默认字段（与DeviceInfo实体匹配）
            field_list = [
                'id', 'device_id', 'device_serial_number', 'device_name', 
                'ip', 'mac', 'macs', 'outside_ip', 'type', 'model', 'brand', 
                'supplier', 'processor', 'operating_system', 'hard_disk', 
                'memory', 'main_board', 'resolution', 'online', 'status', 
                'last_heartbeat_time', 'last_login_time', 'offline_time',
                'device_group_id', 'device_user_group_id', 'user_id', 
                'login_user_id', 'login_status', 'image_id', 'image_snapshot_id',
                'local_image_status', 'image_backup_time', 'purchase_batch',
                'remark', 'create_time', 'create_by', 'update_time', 'update_by',
                'del_flag'
            ]
        field_str = ', '.join(field_list)

        # 处理筛选条件
        sql = f"SELECT {field_str} FROM {table_name}"
        params = []
        if filter_condition:
            sql += f" WHERE {filter_condition}"
        sql += " LIMIT %s"
        params.append(limit)

        rows = self.db_client.query(sql, params)
        
        # 动态构造DeviceInfo对象
        result = []
        for row in rows:
            if isinstance(row, (list, tuple)):
                # 根据字段顺序构造DeviceInfo
                device_dict = {}
                for i, field in enumerate(field_list):
                    if i < len(row):
                        device_dict[field] = row[i]
                result.append(DeviceInfo(**device_dict))
            elif isinstance(row, dict):
                # 直接使用字典构造
                result.append(DeviceInfo(**row))
            else:
                # 兜底
                result.append(row)
        return result

    def get_table_schema(self, table_name):
        """
        获取指定表的字段结构信息，返回字段名、类型、主键信息等。
        """
        return self.db_client.get_table_schema(table_name)

    def delete_devices(self, table_name='biz_device', filter_condition=None, limit=None):
        """
        删除设备信息，支持筛选条件和数量限制。
        :param table_name: 表名
        :param filter_condition: 筛选条件（如 'brand=\'robot\'')
        :param limit: 删除数量限制
        :return: 删除的记录数
        """
        # 构建DELETE语句
        sql = f"DELETE FROM {table_name}"
        params = []
        
        if filter_condition:
            sql += f" WHERE {filter_condition}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        # 执行删除操作
        affected_rows = self.db_client.execute(sql, params)
        return affected_rows

    def get_device_count(self, table_name='biz_device', filter_condition=None):
        """
        获取设备数量。
        :param table_name: 表名
        :param filter_condition: 筛选条件
        :return: 设备数量
        """
        sql = f"SELECT COUNT(*) FROM {table_name}"
        params = []
        
        if filter_condition:
            sql += f" WHERE {filter_condition}"
        
        result = self.db_client.query(sql, params)
        if result and len(result) > 0:
            return result[0][0] if isinstance(result[0], (list, tuple)) else result[0]
        return 0

    def get_all_device_sn(self, table_name='biz_device'):
        """获取指定表中的所有设备序列号(device_serial_number)"""
        query = f"SELECT device_serial_number FROM {table_name} WHERE device_serial_number IS NOT NULL AND device_serial_number != ''"
        results = self.db_client.query(query, [])
        # 将结果从元组列表转换为字符串集合
        return {row[0] for row in results}

    # 可扩展更多查询方法，如按条件筛选、导出为CSV等 