from src.infrastructure.db_query.device_repository import DeviceRepository
from src.infrastructure.db_query.db_client import DBClient

class DeviceQueryService:
    """
    设备查询服务，封装仓储调用，便于上层接口和CLI使用。
    """
    def __init__(self, db_config):
        self.db_client = DBClient(**db_config)
        self.repository = DeviceRepository(self.db_client)

    def get_devices(self, table_name='device_register', limit=100, fields=None, filter_condition=None):
        """
        查询设备信息，支持表名、字段、筛选条件、数量等参数。
        :param table_name: 表名
        :param limit: 数量
        :param fields: 字段
        :param filter_condition: 筛选条件
        :return: 设备信息对象列表
        """
        return self.repository.get_all_devices(
            table_name=table_name,
            limit=limit,
            fields=fields,
            filter_condition=filter_condition
        )

    def analyze_table_schema(self, table_name):
        """
        获取指定表的字段结构信息。
        :param table_name: 表名
        :return: 字段结构信息列表
        """
        return self.repository.get_table_schema(table_name)

    def discover_databases(self):
        """
        自动发现服务器上的所有数据库。
        :return: 数据库名称列表
        """
        return self.db_client.get_databases()

    def discover_tables(self):
        """
        自动发现当前数据库中的所有表。
        :return: 表名称列表
        """
        return self.db_client.get_tables()

    def delete_devices(self, table_name='biz_device', filter_condition=None, limit=None):
        """
        删除设备信息，支持筛选条件和数量限制。
        :param table_name: 表名
        :param filter_condition: 筛选条件（如 'brand=\'robot\'')
        :param limit: 删除数量限制
        :return: 删除的记录数
        """
        return self.repository.delete_devices(
            table_name=table_name,
            filter_condition=filter_condition,
            limit=limit
        )

    def get_device_count(self, table_name='biz_device', filter_condition=None):
        """
        获取设备数量。
        :param table_name: 表名
        :param filter_condition: 筛选条件
        :return: 设备数量
        """
        return self.repository.get_device_count(
            table_name=table_name,
            filter_condition=filter_condition
        )

    def get_all_device_sn(self, table_name='biz_device'):
        """获取指定表中的所有设备序列号"""
        return self.repository.get_all_device_sn(table_name)

    def close(self):
        self.db_client.close() 