from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IDocGenerator(ABC):
    """
    文档生成器接口，定义所有文档自动化的核心方法。
    """
    @abstractmethod
    def generate_all(self, output_dir: str) -> None:
        """
        自动生成所有支持的文档类型。
        :param output_dir: 文档输出目录
        """
        pass

    @abstractmethod
    def generate(self, doc_type: str, output_dir: str) -> None:
        """
        按类型生成指定文档。
        :param doc_type: 文档类型，如api、design、changelog等
        :param output_dir: 文档输出目录
        """
        pass

class DocGenerator(IDocGenerator):
    """
    文档生成器实现，聚合各类文档构建器。
    """
    def __init__(self, api_extractor, design_builder, changelog_builder):
        self.api_extractor = api_extractor
        self.design_builder = design_builder
        self.changelog_builder = changelog_builder

    def generate_all(self, output_dir: str) -> None:
        self.api_extractor.generate_api_doc(output_dir)
        self.design_builder.generate_design_doc(output_dir)
        self.changelog_builder.generate_changelog(output_dir)

    def generate(self, doc_type: str, output_dir: str) -> None:
        if doc_type == 'api':
            self.api_extractor.generate_api_doc(output_dir)
        elif doc_type == 'design':
            self.design_builder.generate_design_doc(output_dir)
        elif doc_type == 'changelog':
            self.changelog_builder.generate_changelog(output_dir)
        else:
            raise ValueError(f'不支持的文档类型: {doc_type}')

def get_doc_generator():
    from .api_doc_extractor import ApiDocExtractor
    from .design_doc_builder import DesignDocBuilder
    from .changelog_builder import ChangelogBuilder
    return DocGenerator(ApiDocExtractor(), DesignDocBuilder(), ChangelogBuilder()) 