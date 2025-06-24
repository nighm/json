#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具包
提供各种通用工具功能
"""

from .file_utils import (
    ensure_directory,
    copy_file,
    move_file,
    delete_file,
    get_files,
    read_file,
    write_file,
    create_backup,
)

from .template_utils import (
    TemplateManager,
    replace_placeholders,
    extract_placeholders,
    validate_placeholders,
    process_template_file,
)

from .config_utils import (
    ConfigManager,
    load_json_config,
    save_json_config,
    load_yaml_config,
    save_yaml_config,
)

from .logging_utils import (
    Logger,
    setup_logger,
    get_logger,
    set_log_level,
    disable_logging,
    enable_logging,
)

__all__ = [
    # 文件操作工具
    "ensure_directory",
    "copy_file",
    "move_file",
    "delete_file",
    "get_files",
    "read_file",
    "write_file",
    "create_backup",
    # 模板处理工具
    "TemplateManager",
    "replace_placeholders",
    "extract_placeholders",
    "validate_placeholders",
    "process_template_file",
    # 配置管理工具
    "ConfigManager",
    "load_json_config",
    "save_json_config",
    "load_yaml_config",
    "save_yaml_config",
    # 日志工具
    "Logger",
    "setup_logger",
    "get_logger",
    "set_log_level",
    "disable_logging",
    "enable_logging",
] 