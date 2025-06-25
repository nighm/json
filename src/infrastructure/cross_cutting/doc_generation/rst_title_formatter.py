from pathlib import Path
from src.domain.entities.rst_document import RstDocument
from src.domain.value_objects.rst_title_rule import RstTitleRule
from src.domain.services.rst_beautify_service import RstBeautifyService
from .rst_file_handler import RstFileHandler

class RstTitleFormatter:
    """
    技术适配器：负责调用领域服务实现RST标题美化。
    """
    @staticmethod
    def format_titles(path: Path, rule: RstTitleRule):
        """
        对指定RST文件进行标题美化。
        :param path: RST文件路径
        :param rule: RstTitleRule实例
        """
        # 读取原始内容
        content = RstFileHandler.read_rst(path)
        doc = RstDocument(content)
        # 调用领域服务美化标题
        new_doc = RstBeautifyService.beautify_titles(doc, rule)
        # 写回文件
        RstFileHandler.write_rst(path, new_doc.content) 