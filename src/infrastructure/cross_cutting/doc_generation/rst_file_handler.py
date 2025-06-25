from pathlib import Path
import shutil

class RstFileHandler:
    """
    文件操作工具：负责RST文件的读取、写入和备份。
    """
    @staticmethod
    def read_rst(path: Path) -> str:
        """
        读取指定路径的RST文件内容。
        :param path: RST文件路径
        :return: 文件内容字符串
        """
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def write_rst(path: Path, content: str):
        """
        将内容写入指定路径的RST文件。
        :param path: RST文件路径
        :param content: 要写入的内容
        """
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def backup_rst(path: Path):
        """
        备份指定路径的RST文件，避免误操作。
        :param path: RST文件路径
        """
        bak_path = path.with_suffix(path.suffix + '.bak')
        if path.exists() and not bak_path.exists():
            shutil.copy(path, bak_path) 