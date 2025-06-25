from src.domain.entities.rst_document import RstDocument
from src.domain.value_objects.rst_title_rule import RstTitleRule
import re

class RstBeautifyService:
    """
    领域服务：实现RST内容的美化算法（如标题下划线修正）。
    只处理字符串和结构，不涉及文件IO。
    """
    @staticmethod
    def beautify_titles(document: RstDocument, rule: RstTitleRule) -> RstDocument:
        """
        美化RST文档中的所有标题下划线。
        :param document: RstDocument实例
        :param rule: RstTitleRule实例
        :return: 新的RstDocument实例（内容已美化）
        """
        lines = document.get_lines()
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # 检查下方是否为标题下划线
            if i+1 < len(lines) and re.match(r'^[=\-~`^\*\+#]+$', lines[i+1].strip()):
                title = line.rstrip('\n')
                underline = rule.get_underline(title)
                new_lines.append(title + '\n')
                new_lines.append(underline + '\n')
                i += 2
            else:
                new_lines.append(line)
                i += 1
        return RstDocument(''.join(new_lines)) 