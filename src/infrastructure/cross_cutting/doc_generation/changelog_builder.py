from abc import ABC, abstractmethod
import os
import datetime

class IChangelogBuilder(ABC):
    """
    变更记录生成器接口，定义变更记录文档自动生成方法。
    """
    @abstractmethod
    def generate_changelog(self, output_dir: str) -> None:
        pass

class ChangelogBuilder(IChangelogBuilder):
    """
    变更记录生成器实现，自动生成横切关注点变更记录文档。
    """
    def generate_changelog(self, output_dir: str) -> None:
        changelog_path = os.path.join(output_dir, 'cross_cutting_变更记录.md')
        with open(changelog_path, 'a', encoding='utf-8') as f:
            f.write(f'\n## {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('- 自动生成横切关注点变更记录。\n') 