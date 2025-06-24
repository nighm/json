from abc import ABC, abstractmethod
import os

class IDesignDocBuilder(ABC):
    """
    设计文档生成器接口，定义设计文档自动生成方法。
    """
    @abstractmethod
    def generate_design_doc(self, output_dir: str) -> None:
        pass

class DesignDocBuilder(IDesignDocBuilder):
    """
    设计文档生成器实现，自动生成横切关注点设计说明和Mermaid依赖关系图。
    """
    def generate_design_doc(self, output_dir: str) -> None:
        design_doc_path = os.path.join(output_dir, 'cross_cutting_设计说明.md')
        with open(design_doc_path, 'w', encoding='utf-8') as f:
            f.write('# 横切关注点设计说明\n\n')
            f.write('本模块实现了日志、配置、性能分析、异常处理等横切关注点，采用接口抽象与依赖倒置，便于扩展和复用。\n\n')
            f.write('## 依赖关系图（Mermaid）\n')
            f.write('```mermaid\n')
            f.write('graph TD\n')
            f.write('    DocGenerator --> ApiDocExtractor\n')
            f.write('    DocGenerator --> DesignDocBuilder\n')
            f.write('    DocGenerator --> ChangelogBuilder\n')
            f.write('    ApiDocExtractor --> cross_cutting_py_files\n')
            f.write('    DesignDocBuilder --> cross_cutting_py_files\n')
            f.write('    ChangelogBuilder --> cross_cutting_py_files\n')
            f.write('```\n') 