from abc import ABC, abstractmethod
import os
import ast

class IApiDocExtractor(ABC):
    """
    API文档提取器接口，定义API文档自动生成方法。
    """
    @abstractmethod
    def generate_api_doc(self, output_dir: str) -> None:
        pass

class ApiDocExtractor(IApiDocExtractor):
    """
    API文档提取器实现，自动扫描src目录下所有py文件，提取docstring生成API文档。
    """
    def generate_api_doc(self, output_dir: str) -> None:
        api_doc_path = os.path.join(output_dir, 'cross_cutting_API文档.md')
        with open(api_doc_path, 'w', encoding='utf-8') as f:
            f.write('# 横切关注点API文档\n\n')
            for root, _, files in os.walk('src/infrastructure/cross_cutting'):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as code_file:
                            tree = ast.parse(code_file.read(), filename=file)
                            for node in ast.iter_child_nodes(tree):
                                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                                    doc = ast.get_docstring(node)
                                    if doc:
                                        f.write(f'## {node.name}\n')
                                        f.write(f'{doc}\n\n') 