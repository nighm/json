from typing import List, Dict, Any

class ReportField:
    """
    报告字段实体，描述每个字段的名称、含义、来源、采集/计算方法、代码位置等
    """
    def __init__(self, name: str, description: str, method: str, code_location: str):
        self.name = name  # 字段名
        self.description = description  # 字段含义/来源说明
        self.method = method  # 采集/计算方法说明
        self.code_location = code_location  # 代码位置/来源文件

class Report:
    """
    报告实体，包含报告的所有数据行和字段定义
    """
    def __init__(self, title: str, fields: List[ReportField], rows: List[Dict[str, Any]]):
        self.title = title  # 报告标题
        self.fields = fields  # 字段定义列表
        self.rows = rows  # 数据行，每行为字典 