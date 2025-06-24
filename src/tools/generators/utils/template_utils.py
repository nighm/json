from src.utils.parallel.decorators import parallel
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模板处理工具模块
提供模板渲染和处理的通用功能
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Optional, Union
from jinja2 import Environment, FileSystemLoader, Template

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("template_utils.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class TemplateManager:
    """模板管理器类"""

    def __init__(self, template_dir: Union[str, Path]):
        """
        初始化模板管理器

        Args:
            template_dir: 模板目录路径
        """
        self.template_dir = Path(template_dir)
        if not self.template_dir.exists():
            raise ValueError(f"模板目录不存在: {template_dir}")

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_template(self, template_name: str, context: Dict) -> Optional[str]:
        """
        渲染模板

        Args:
            template_name: 模板文件名
            context: 模板上下文数据

        Returns:
            Optional[str]: 渲染后的内容
        """
        try:
            template = self.env.get_template(template_name)
            content = template.render(**context)
            logger.info(f"渲染模板: {template_name}")
            return content
        except Exception as e:
            logger.error(f"渲染模板失败: {e}")
            return None

    def render_string(self, template_string: str, context: Dict) -> Optional[str]:
        """
        渲染模板字符串

        Args:
            template_string: 模板字符串
            context: 模板上下文数据

        Returns:
            Optional[str]: 渲染后的内容
        """
        try:
            template = Template(template_string)
            content = template.render(**context)
            logger.info("渲染模板字符串")
            return content
        except Exception as e:
            logger.error(f"渲染模板字符串失败: {e}")
            return None

    def get_template_names(self) -> list[str]:
        """
        获取所有模板文件名

        Returns:
            list[str]: 模板文件名列表
        """
        return self.env.list_templates()

    def validate_template(self, template_name: str) -> bool:
        """
        验证模板是否有效

        Args:
            template_name: 模板文件名

        Returns:
            bool: 模板是否有效
        """
        try:
            self.env.get_template(template_name)
            return True
        except Exception as e:
            logger.error(f"模板验证失败: {e}")
            return False


def replace_placeholders(content: str, replacements: Dict[str, str]) -> str:
    """
    替换内容中的占位符

    Args:
        content: 原始内容
        replacements: 替换映射

    Returns:
        str: 替换后的内容
    """
    for key, value in replacements.items():
        placeholder = f"{{{{ {key} }}}}"
        content = content.replace(placeholder, str(value))
    return content


def extract_placeholders(content: str) -> list[str]:
    """
    提取内容中的占位符

    Args:
        content: 原始内容

    Returns:
        list[str]: 占位符列表
    """
    pattern = r"{{([^}]+)}}"
    matches = re.findall(pattern, content)
    return [match.strip() for match in matches]


def validate_placeholders(content: str, required_placeholders: list[str]) -> bool:
    """
    验证内容中的占位符是否完整

    Args:
        content: 原始内容
        required_placeholders: 必需的占位符列表

    Returns:
        bool: 占位符是否完整
    """
    found_placeholders = extract_placeholders(content)
    return all(placeholder in found_placeholders for placeholder in required_placeholders)


def process_template_file(
    template_path: Union[str, Path],
    output_path: Union[str, Path],
    context: Dict[str, str],
    encoding: str = "utf-8",
) -> bool:
    """
    处理模板文件并生成输出文件

    Args:
        template_path: 模板文件路径
        output_path: 输出文件路径
        context: 模板上下文数据
        encoding: 文件编码

    Returns:
        bool: 是否处理成功
    """
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        logger.error(f"模板文件不存在: {template_path}")
        return False

    try:
        # 读取模板内容
        content = template_path.read_text(encoding=encoding)
        
        # 验证必需的占位符
        required_placeholders = list(context.keys())
        if not validate_placeholders(content, required_placeholders):
            missing = [p for p in required_placeholders if p not in extract_placeholders(content)]
            logger.error(f"模板缺少必需的占位符: {missing}")
            return False

        # 替换占位符
        processed_content = replace_placeholders(content, context)

        # 写入输出文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(processed_content, encoding=encoding)
        
        logger.info(f"处理模板文件: {template_path} -> {output_path}")
        return True
    except Exception as e:
        logger.error(f"处理模板文件失败: {e}")
        return False 