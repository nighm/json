import pymysql

class DBClient:
    """
    数据库连接基础类，支持MySQL，参数可配置。
    """
    def __init__(self, host, port, user, password, database=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None

    def connect(self):
        """连接数据库，支持不指定数据库名称"""
        if self.database:
            # 连接指定数据库
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
        else:
            # 连接MySQL服务器（不指定数据库）
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )

    def query(self, sql, params=None):
        if self.conn is None:
            self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()

    def execute(self, sql, params=None):
        """
        执行INSERT、UPDATE、DELETE等操作
        :param sql: SQL语句
        :param params: 参数
        :return: 影响的行数
        """
        if self.conn is None:
            self.connect()
        with self.conn.cursor() as cursor:
            affected_rows = cursor.execute(sql, params or ())
            self.conn.commit()
            return affected_rows

    def get_table_schema(self, table_name):
        """
        获取指定表的字段结构信息，包括字段名、类型、主键等。
        返回：字段信息列表，每项为dict，如：
        {"Field": "device_id", "Type": "varchar(64)", "Key": "PRI", ...}
        """
        if self.conn is None:
            self.connect()
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            schema = cursor.fetchall()
        return schema

    def get_databases(self):
        """
        获取服务器上的所有数据库名称。
        :return: 数据库名称列表
        """
        if self.conn is None:
            self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            # 过滤掉系统数据库
            system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
            return [db for db in databases if db not in system_dbs]

    def get_tables(self):
        """
        获取当前数据库中的所有表名称。
        :return: 表名称列表
        """
        if self.conn is None:
            self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            return tables

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None 