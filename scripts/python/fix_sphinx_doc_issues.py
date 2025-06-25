#!/usr/bin/env python3
"""
Sphinx文档自动化修复脚本

- 自动补全src下所有包的__init__.py
- 自动美化docs/api/source下所有rst文件标题
- 自动整理index.rst的toctree，确保所有rst都被包含
- 所有操作前自动备份原文件，详细中文日志
"""
import os
from pathlib import Path
import shutil
import re

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SRC_DIR = PROJECT_ROOT / 'src'
DOCS_SOURCE = PROJECT_ROOT / 'docs' / 'api' / 'source'


def backup_file(file_path):
    """自动备份原文件，避免误操作。"""
    bak_path = file_path.with_suffix(file_path.suffix + '.bak')
    if file_path.exists() and not bak_path.exists():
        shutil.copy(file_path, bak_path)
        print(f"[备份] 已备份: {file_path} -> {bak_path}")


def fix_init_py():
    """
    自动递归补全src下所有包的__init__.py文件。
    """
    print("\n[步骤1] 检查并补全src下所有包的__init__.py...")
    for dirpath, dirnames, filenames in os.walk(SRC_DIR):
        dir_path = Path(dirpath)
        if any(f.suffix == '.py' for f in map(Path, filenames)) or dirnames:
            init_file = dir_path / '__init__.py'
            if not init_file.exists():
                init_file.touch()
                print(f"[修复] 新建__init__.py: {init_file}")
    print("[完成] __init__.py检查与补全。\n")


def fix_rst_titles():
    """
    自动美化docs/api/source下所有rst文件标题，消除下划线过短警告。
    """
    print("[步骤2] 美化rst标题下划线...")
    for rst_file in DOCS_SOURCE.glob('*.rst'):
        backup_file(rst_file)
        with open(rst_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # 检查标题（只处理一级/二级标题）
            if i+1 < len(lines) and re.match(r'^[=\-~`^\*\+#]+$', lines[i+1].strip()):
                title = line.rstrip('\n')
                underline = lines[i+1].strip()[0]
                fixed_underline = underline * max(len(title), len(lines[i+1].strip()))
                new_lines.append(title + '\n')
                new_lines.append(fixed_underline + '\n')
                i += 2
            else:
                new_lines.append(line)
                i += 1
        with open(rst_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"[美化] 已修正标题下划线: {rst_file}")
    print("[完成] rst标题美化。\n")


def fix_toctree():
    """
    自动整理index.rst的toctree，确保所有rst都被包含。
    """
    print("[步骤3] 整理index.rst的toctree...")
    index_rst = DOCS_SOURCE / 'index.rst'
    backup_file(index_rst)
    if not index_rst.exists():
        print(f"[警告] 未找到index.rst: {index_rst}")
        return
    # 收集所有应被包含的rst（排除index.rst本身）
    all_rst = sorted([f.stem for f in DOCS_SOURCE.glob('*.rst') if f.name != 'index.rst'])
    with open(index_rst, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 查找toctree块
    new_lines = []
    in_toctree = False
    for line in lines:
        if line.strip().startswith('.. toctree::'):
            in_toctree = True
            new_lines.append(line)
            # 跳过原有toctree内容，直接插入新内容
            new_lines.append('   :maxdepth: 2\n')
            new_lines.append('   :caption: 目录\n\n')
            for rst in all_rst:
                new_lines.append(f'   {rst}\n')
            # 跳过原有toctree内容
            while lines and (lines[0].startswith('   ') or lines[0].strip() == ''):
                lines.pop(0)
            in_toctree = False
        else:
            if not in_toctree:
                new_lines.append(line)
    with open(index_rst, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"[整理] 已更新toctree，包含所有rst: {index_rst}")
    print("[完成] toctree整理。\n")


def beautify_index_rst():
    """
    自动美化首页index.rst，补充中文项目简介和导航说明。
    """
    index_rst = DOCS_SOURCE / 'index.rst'
    backup_file(index_rst)
    intro = [
        "全项目自动化API文档\n",
        "====================\n",
        "本页面为项目自动生成的API文档首页，包含如下内容：\n",
        "- 项目简介与导航说明\n",
        "- 详细的模块API文档（见下方目录树）\n",
        "- 支持中英文搜索、交互式跳转\n",
        "\n",
        "如需定制首页内容，请编辑本文件。\n",
        "\n"
    ]
    # 保留原有toctree及后续内容
    with open(index_rst, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 查找toctree起始行
    for i, line in enumerate(lines):
        if line.strip().startswith('.. toctree::'):
            toctree_start = i
            break
    else:
        toctree_start = len(lines)
    # 只保留toctree及后续内容
    new_lines = intro + lines[toctree_start:]
    with open(index_rst, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"[美化] 首页index.rst已补充中文简介和导航: {index_rst}")


def main():
    print("\n========== Sphinx文档自动化修复与美化 ==========")
    fix_init_py()
    fix_rst_titles()
    fix_toctree()
    beautify_index_rst()
    print("[SUCCESS] 所有修复与美化已完成！请重新生成文档以验证效果。\n")

if __name__ == '__main__':
    main() 