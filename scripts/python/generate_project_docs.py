#!/usr/bin/env python3
"""
全项目Sphinx开发文档一键自动生成脚本（兼容Sphinx 8.x，支持HTML/PDF/Markdown）

- 自动递归扫描src/目录，生成Sphinx API文档
- 自动初始化Sphinx配置（如首次运行）
- 自动调用sphinx-apidoc和sphinx-build
- 支持输出HTML、PDF、Markdown格式
- 输出目录为docs/api/build/
- 详细中文注释，便于维护
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
SRC_DIR = PROJECT_ROOT / 'src'
DOCS_DIR = PROJECT_ROOT / 'docs' / 'api'
SOURCE_DIR = DOCS_DIR / 'source'
BUILD_DIR = DOCS_DIR / 'build'


def check_sphinx_installed():
    """
    检查Sphinx及相关扩展是否已安装。
    """
    try:
        import sphinx
        import sphinx_rtd_theme
        print("[INFO] Sphinx 及主题已安装。")
        return True
    except ImportError:
        print("[ERROR] 未检测到Sphinx或主题，请先运行: pip install sphinx sphinx-autobuild sphinx_rtd_theme myst-parser")
        return False


def patch_conf_py():
    """
    修复conf.py，确保有extensions = []，并用+=方式追加扩展，避免NameError。
    """
    conf_py = SOURCE_DIR / 'conf.py'
    if not conf_py.exists():
        print(f"[ERROR] 未找到conf.py: {conf_py}")
        return
    with open(conf_py, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 检查是否有extensions定义
    has_ext = any(line.strip().startswith('extensions') for line in lines)
    new_lines = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        # 在第一个import后插入extensions = []
        if not has_ext and not inserted and line.strip().startswith('import'):
            new_lines.append('extensions = []\n')
            inserted = True
    if not has_ext and not inserted:
        # 没有import，直接加到开头
        new_lines = ['extensions = []\n'] + new_lines
    # 追加扩展（用+=，避免NameError）
    ext_patch = [
        "extensions += ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon', 'myst_parser']\n",
        "html_theme = 'sphinx_rtd_theme'\n",
        "language = 'zh_CN'\n",
        "import sys, os\nsys.path.insert(0, os.path.abspath('../../../../src'))\n"
    ]
    # 移除旧的相关扩展行，避免重复
    new_lines = [l for l in new_lines if not (
        'sphinx.ext.napoleon' in l or 'myst_parser' in l or 'sphinx.ext.autodoc' in l or 'sphinx.ext.viewcode' in l or 'html_theme' in l or 'language =' in l or 'sys.path.insert' in l)]
    new_lines += ext_patch
    with open(conf_py, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"[INFO] conf.py已修正: {conf_py}")


def init_sphinx_conf():
    """
    初始化Sphinx配置（仅首次运行时执行）。
    若发现docs/api/source/source/目录存在，则自动将其下所有文件移动到docs/api/source/，并删除多余的source子目录。
    """
    if not SOURCE_DIR.exists():
        print(f"[INFO] 初始化Sphinx配置目录: {SOURCE_DIR}")
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        # 调用 sphinx-quickstart 自动生成配置（去除不兼容参数）
        subprocess.run([
            sys.executable, '-m', 'sphinx.cmd.quickstart',
            str(SOURCE_DIR),
            '--quiet', '--project', 'ProjectDocs', '--author', 'AutoGen',
            '--sep', '--makefile', '--no-batchfile', '--ext-autodoc', '--ext-viewcode', '--language', 'zh_CN', '--release', '1.0'
        ])
    # 检查是否有多余的source/source嵌套
    nested_source = SOURCE_DIR / 'source'
    if nested_source.exists() and nested_source.is_dir():
        print(f"[INFO] 检测到多余的source嵌套目录，自动迁移文件...")
        for item in nested_source.iterdir():
            target = SOURCE_DIR / item.name
            if target.exists():
                print(f"[WARN] 目标文件已存在，跳过: {target}")
            else:
                item.rename(target)
                print(f"[迁移] {item} -> {target}")
        nested_source.rmdir()
        print(f"[INFO] 已删除多余的source目录: {nested_source}")
    patch_conf_py()


def ensure_init_py(target_dir):
    """
    递归补全指定目录下所有包的__init__.py，确保apidoc能识别并生成文档。
    """
    for dirpath, dirnames, filenames in os.walk(target_dir):
        dir_path = Path(dirpath)
        init_file = dir_path / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            print(f"[补全] 新建__init__.py: {init_file}")


def generate_apidoc():
    """
    自动调用sphinx-apidoc生成API文档源文件。
    修正：直接用Sphinx官方API调用，生成后检查modules.rst是否存在。

        新增：包含src、scripts、scripts/python所有内容，排除src/tools目录（直接将src/tools作为额外参数传入以排除）。
    """
    print(f"[INFO] 生成API文档源文件到: {SOURCE_DIR}")
    try:
        from sphinx.ext import apidoc
        # 先补全scripts及其所有子目录下的__init__.py，确保能被apidoc递归识别
        ensure_init_py(PROJECT_ROOT / 'scripts')
        ensure_init_py(PROJECT_ROOT / 'scripts' / 'python')
        # 生成API文档，--force覆盖，--separate每个模块单独文件，--no-toc不生成目录页
        # 同时包含src、scripts、scripts/python，排除src/tools（直接将src/tools作为额外参数传入）
        apidoc.main([
            '--force', '--separate', '--no-toc',
            '-o', str(SOURCE_DIR),
            str(SRC_DIR),
            str(PROJECT_ROOT / 'scripts'),
            str(PROJECT_ROOT / 'scripts' / 'python'),
            str(SRC_DIR / 'tools')  # 直接作为排除目录
        ])
        modules_rst = SOURCE_DIR / 'modules.rst'
        if not modules_rst.exists():
            print(f"[ERROR] 未生成modules.rst，API文档生成失败。请检查src/scripts目录结构和Sphinx版本兼容性。")
            print(f"[DIAGNOSE] 可能原因：1) 目录下无可识别的Python包；2) __init__.py缺失；3) Sphinx版本过高/低。建议手动运行sphinx-apidoc命令排查。")
        else:
            print(f"[INFO] modules.rst已生成: {modules_rst}")
    except Exception as e:
        print(f"[ERROR] sphinx-apidoc生成失败: {e}")
        import traceback
        traceback.print_exc()


def build_docs(formats):
    """
    根据formats参数生成HTML、PDF、Markdown等格式文档。
    所有子流程加异常捕获，详细输出报错。
    """
    for fmt in formats:
        try:
            if fmt == 'html':
                print("[INFO] 开始生成HTML文档...")
                subprocess.run([
                    sys.executable, '-m', 'sphinx',
                    '-b', 'html',
                    str(SOURCE_DIR),
                    str(BUILD_DIR / 'html')
                ], check=True)
                print(f"[INFO] HTML文档已生成: {BUILD_DIR / 'html'}")
            elif fmt == 'pdf':
                print("[INFO] 开始生成PDF文档...")
                latex_dir = BUILD_DIR / 'latex'
                subprocess.run([
                    sys.executable, '-m', 'sphinx',
                    '-b', 'latex',
                    str(SOURCE_DIR),
                    str(latex_dir)
                ], check=True)
                main_tex = next(latex_dir.glob('*.tex'), None)
                if main_tex:
                    # 优先用xelatex生成PDF，兼容中文
                    try:
                        subprocess.run(['xelatex', '-output-directory', str(latex_dir), str(main_tex)], check=True)
                        print(f"[INFO] PDF文档已生成: {latex_dir / (main_tex.stem + '.pdf')}")
                    except Exception as e:
                        print(f"[WARN] xelatex生成失败，尝试pdflatex: {e}")
                        subprocess.run(['pdflatex', '-output-directory', str(latex_dir), str(main_tex)], check=True)
                        print(f"[INFO] PDF文档已生成: {latex_dir / (main_tex.stem + '.pdf')}")
                else:
                    print("[WARN] 未找到tex主文件，PDF生成失败。请检查LaTeX环境。")
            elif fmt == 'md':
                print("[INFO] 开始生成Markdown文档...")
                md_dir = BUILD_DIR / 'markdown'
                subprocess.run([
                    sys.executable, '-m', 'sphinx',
                    '-b', 'markdown',
                    str(SOURCE_DIR),
                    str(md_dir)
                ], check=True)
                print(f"[INFO] Markdown文档已生成: {md_dir}")
            else:
                print(f"[WARN] 不支持的格式: {fmt}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Sphinx构建{fmt}文档失败: {e}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"[ERROR] 构建{fmt}文档时发生未知异常: {e}")
            import traceback
            traceback.print_exc()


def open_html():
    """
    自动用系统默认浏览器打开HTML文档首页。
    """
    index_html = BUILD_DIR / 'html' / 'index.html'
    if index_html.exists():
        print(f"[INFO] 正在打开: {index_html}")
        if sys.platform.startswith('win'):
            os.startfile(str(index_html))
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', str(index_html)])
        else:
            subprocess.run(['xdg-open', str(index_html)])
    else:
        print("[WARN] 未找到HTML首页，无法自动打开。")


def main():
    parser = argparse.ArgumentParser(description='全项目Sphinx文档自动生成脚本')
    parser.add_argument('--format', '-f', nargs='+', default=['html'], help='输出格式，可选: html pdf md，支持多选')
    args = parser.parse_args()

    print("\n========== 全项目Sphinx开发文档自动生成 ==========")
    if not check_sphinx_installed():
        return
    try:
        init_sphinx_conf()
        generate_apidoc()
        build_docs(args.format)
        open_html()
        print("[SUCCESS] 全项目开发文档已自动生成！\n")
        print(f"HTML文档路径: {BUILD_DIR / 'html' / 'index.html'}\n")
    except Exception as e:
        print(f"[FATAL] 文档自动生成流程发生致命错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 