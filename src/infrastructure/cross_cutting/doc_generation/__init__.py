"""
横切关注点 - 文档生成模块

提供统一的文档生成服务，包括API文档、设计文档、变更日志等自动化生成能力。
遵循DDD架构的横切关注点设计原则，为整个应用提供文档生成基础设施。
"""

from .doc_generator import IDocGenerator, DocGenerator, get_doc_generator
from .api_doc_extractor import IApiDocExtractor, ApiDocExtractor
from .design_doc_builder import IDesignDocBuilder, DesignDocBuilder
from .changelog_builder import IChangelogBuilder, ChangelogBuilder
from .rst_beautifier import RstBeautifier

__all__ = [
    'IDocGenerator', 'DocGenerator', 'get_doc_generator',
    'IApiDocExtractor', 'ApiDocExtractor',
    'IDesignDocBuilder', 'DesignDocBuilder',
    'IChangelogBuilder', 'ChangelogBuilder',
    'RstBeautifier',
] 