#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动扫描项目目录结构，生成结构化脑图图片（Graphviz实现，输出PNG）
输出路径：docs/development/project_mindmap_graphviz.png
"""
import os
from pathlib import Path
from graphviz import Digraph

# 项目根目录
ROOT = Path(__file__).parent.parent

# 需要纳入脑图的一级目录
TOP_LEVEL_DIRS = ['src', 'scripts', 'tools', 'docs']

# 脑图输出路径
OUTPUT_PATH = ROOT / 'docs' / 'development' / 'project_mindmap_graphviz'

# 初始化Graphviz有向图
mindmap = Digraph('项目脑图', format='png')
mindmap.attr(rankdir='LR', fontsize='16', fontname='Microsoft YaHei', bgcolor='white')

# 添加根节点
mindmap.node('A', '项目架构', shape='ellipse', style='filled', fillcolor='#e3f2fd')

# 遍历一级目录
for idx, top_dir in enumerate(TOP_LEVEL_DIRS, start=1):
    top_path = ROOT / top_dir
    if not top_path.exists():
        continue
    node_id = chr(ord('B') + idx - 1)
    mindmap.node(node_id, f'{top_dir}目录', shape='box', style='filled', fillcolor='#bbdefb')
    mindmap.edge('A', node_id)
    # 只递归src、docs、tools、scripts下的2级子目录/文件
    for sub in sorted(top_path.iterdir()):
        if sub.name.startswith('.') or sub.name == '__pycache__':
            continue
        sub_id = f'{node_id}_{sub.name}'
        label = sub.name
        if sub.is_dir():
            mindmap.node(sub_id, label, shape='folder', style='filled', fillcolor='#e1bee7')
            mindmap.edge(node_id, sub_id)
            # 只递归到2级
            for sub2 in sorted(sub.iterdir()):
                if sub2.name.startswith('.') or sub2.name == '__pycache__':
                    continue
                sub2_id = f'{sub_id}_{sub2.name}'
                mindmap.node(sub2_id, sub2.name, shape='note', style='filled', fillcolor='#fff9c4')
                mindmap.edge(sub_id, sub2_id)
        else:
            mindmap.node(sub_id, label, shape='note', style='filled', fillcolor='#fff9c4')
            mindmap.edge(node_id, sub_id)

# 输出PNG图片
mindmap.render(str(OUTPUT_PATH), view=False)
print(f'✅ 脑图图片已生成：{OUTPUT_PATH.with_suffix(".png")}') 