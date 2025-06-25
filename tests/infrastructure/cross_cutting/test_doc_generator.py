import os
import tempfile
import shutil
import pytest
from src.infrastructure.cross_cutting.doc_generation.doc_generator import DocGenerator

class DummyBuilder:
    """
    用于测试的假Builder，记录调用情况。
    """
    def __init__(self):
        self.called = []
    def generate_api_doc(self, output_dir):
        self.called.append(('api', output_dir))
    def generate_design_doc(self, output_dir):
        self.called.append(('design', output_dir))
    def generate_changelog(self, output_dir):
        self.called.append(('changelog', output_dir))


def test_doc_generator_generate_all_and_each():
    """
    测试DocGenerator的generate_all和generate的所有分支。
    """
    api = DummyBuilder()
    design = DummyBuilder()
    changelog = DummyBuilder()
    gen = DocGenerator(api, design, changelog)
    temp_dir = tempfile.mkdtemp()
    # generate_all
    gen.generate_all(temp_dir)
    assert ('api', temp_dir) in api.called
    assert ('design', temp_dir) in design.called
    assert ('changelog', temp_dir) in changelog.called
    # generate各类型
    gen.generate('api', temp_dir)
    assert ('api', temp_dir) in api.called
    gen.generate('design', temp_dir)
    assert ('design', temp_dir) in design.called
    gen.generate('changelog', temp_dir)
    assert ('changelog', temp_dir) in changelog.called
    # 不支持类型
    with pytest.raises(ValueError):
        gen.generate('notype', temp_dir)
    shutil.rmtree(temp_dir)


def test_doc_generator_file_write_exceptions(monkeypatch):
    """
    测试各Builder文件写入异常分支。
    """
    # api_doc_extractor
    from src.infrastructure.cross_cutting.doc_generation.api_doc_extractor import ApiDocExtractor
    api = ApiDocExtractor()
    # 输出目录不存在
    temp_dir = tempfile.mkdtemp()
    shutil.rmtree(temp_dir)
    with pytest.raises(Exception):
        api.generate_api_doc(temp_dir)
    # design_doc_builder
    from src.infrastructure.cross_cutting.doc_generation.design_doc_builder import DesignDocBuilder
    design = DesignDocBuilder()
    with pytest.raises(Exception):
        design.generate_design_doc(temp_dir)
    # changelog_builder
    from src.infrastructure.cross_cutting.doc_generation.changelog_builder import ChangelogBuilder
    changelog = ChangelogBuilder()
    with pytest.raises(Exception):
        changelog.generate_changelog(temp_dir)


def test_get_doc_generator():
    """
    测试get_doc_generator的依赖注入路径。
    """
    from src.infrastructure.cross_cutting.doc_generation.doc_generator import get_doc_generator
    gen = get_doc_generator()
    assert hasattr(gen, 'generate_all') and hasattr(gen, 'generate') 