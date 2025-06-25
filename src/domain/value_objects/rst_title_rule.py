class RstTitleRule:
    """
    值对象：定义RST标题美化规则（如下划线符号、长度策略等）。
    """
    def __init__(self, underline_char: str = '=', min_length: int = 1):
        """
        初始化标题美化规则。
        :param underline_char: 标题下划线符号（如'='、'-'等）
        :param min_length: 下划线最小长度
        """
        self.underline_char = underline_char
        self.min_length = min_length

    def get_underline(self, title: str) -> str:
        """
        根据标题文本生成合适长度的下划线。
        :param title: 标题文本
        :return: 下划线字符串
        """
        return self.underline_char * max(len(title), self.min_length) 