#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成项目脑图（pyecharts Tree）：
- 简化版：只展示主目录及2级子目录
- 详细版：递归所有子目录，仅展示代码相关目录和.py文件，自动排除第三方/依赖/缓存
输出：docs/development/project_mindmap_simple.html、project_mindmap_full.html
"""
from pyecharts import options as opts
from pyecharts.charts import Tree
from pathlib import Path

# 需要纳入脑图的主目录
TOP_LEVEL_DIRS = ['src', 'scripts', 'tools', 'docs']
# 详细版排除目录/文件
EXCLUDE_DIRS = {'venv', '__pycache__', '.git', 'node_modules', 'test_output', 'temp', 'data', 'backups', 'generated_devices', 'bin', 'lib', 'cache', 'dist', 'build', 'externals', 'java', 'jmeter', 'redis'}
EXCLUDE_FILES = {'.DS_Store', 'Thumbs.db'}

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / 'docs' / 'development'

# 简化版：只递归2级目录
def build_simple_tree():
    def get_children(path, level):
        if level > 2:
            return []
        children = []
        for sub in sorted(path.iterdir()):
            if sub.name.startswith('.') or sub.name in EXCLUDE_DIRS:
                continue
            node = {"name": sub.name}
            if sub.is_dir() and level < 2:
                node["children"] = get_children(sub, level+1)
            children.append(node)
        return children
    data = []
    for d in TOP_LEVEL_DIRS:
        p = ROOT / d
        if p.exists():
            data.append({"name": d, "children": get_children(p, 1)})
    return [{"name": "项目架构", "children": data}]

# 详细版：递归所有子目录，只展示代码相关目录和.py文件
def build_full_tree():
    def is_code_dir(path):
        # 只要不是排除目录就算代码相关
        return path.is_dir() and path.name not in EXCLUDE_DIRS and not path.name.startswith('.')
    def get_children(path):
        children = []
        for sub in sorted(path.iterdir()):
            if sub.name in EXCLUDE_DIRS or sub.name.startswith('.') or sub.name in EXCLUDE_FILES:
                continue
            if sub.is_dir():
                sub_children = get_children(sub)
                if sub_children:
                    children.append({"name": sub.name, "children": sub_children})
            elif sub.suffix == '.py':
                children.append({"name": sub.name})
        return children
    data = []
    for d in TOP_LEVEL_DIRS:
        p = ROOT / d
        if p.exists():
            children = get_children(p)
            if children:
                data.append({"name": d, "children": children})
    return [{"name": "项目架构", "children": data}]

# 生成脑图HTML
def render_tree(data, out_html, title):
    c = (
        Tree()
        .add(
            "",
            data,
            orient="LR",
            symbol_size=16,
            label_opts=opts.LabelOpts(position="left", font_size=13, font_family='Microsoft YaHei')
        )
        .set_global_opts(title_opts=opts.TitleOpts(title=title))
    )
    out_html.parent.mkdir(parents=True, exist_ok=True)
    c.render(str(out_html))
    print(f'✅ 脑图已生成：{out_html.resolve()}')

if __name__ == "__main__":
    # 简化版
    simple_data = build_simple_tree()
    render_tree(simple_data, OUT_DIR / 'project_mindmap_simple.html', '项目脑图（简化版，仅2级目录）')
    # 详细版
    full_data = build_full_tree()
    render_tree(full_data, OUT_DIR / 'project_mindmap_full.html', '项目脑图（详细版，仅代码相关）') 