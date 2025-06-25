class RstDocument:
    """
    领域实体：表示一份RST文档的结构和内容。
    只负责内容的结构化表达，不涉及文件IO。
    """
    def __init__(self, content: str):
        """
        初始化RST文档实体。
        :param content: RST文档的原始内容字符串
        """
        self.content = content

    def get_lines(self):
        """
        获取文档的所有行（用于后续处理）。
        :return: 行列表
        """
        return self.content.splitlines(keepends=True)

    def update_content(self, new_content: str):
        """
        更新文档内容。
        :param new_content: 新的内容字符串
        """
        self.content = new_content 