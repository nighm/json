#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用matplotlib+networkx画一个简单的树状脑图demo（纯Python，无需Graphviz可执行程序）
输出：docs/development/project_mindmap_demo.png
"""
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

# 定义脑图结构（嵌套字典）
mindmap = {
    '项目架构': {
        'src': {
            'domain': {},
            'application': {},
            'infrastructure': {},
            'interfaces': {},
            'config': {}
        },
        'scripts': {},
        'tools': {},
        'docs': {}
    }
}

# 递归将嵌套字典转为边列表
def add_edges(graph, parent, children):
    for child, subchildren in children.items():
        graph.add_edge(parent, child)
        if isinstance(subchildren, dict):
            add_edges(graph, child, subchildren)

G = nx.DiGraph()
add_edges(G, '项目架构', mindmap['项目架构'])

# 计算层级（用于纵向布局）
def get_levels(node, children, level=0, levels=None):
    if levels is None:
        levels = {}
    levels[node] = level
    for child, subchildren in children.get(node, {}).items():
        get_levels(child, children[node], level+1, levels)
    return levels

# 生成层级信息
def build_tree_dict(tree, parent=None, tree_dict=None):
    if tree_dict is None:
        tree_dict = {}
    for k, v in tree.items():
        tree_dict[k] = v
        if isinstance(v, dict):
            build_tree_dict(v, k, tree_dict)
    return tree_dict

tree_dict = build_tree_dict(mindmap['项目架构'])
levels = get_levels('项目架构', {'项目架构': tree_dict})

# 生成节点位置（竖向树状布局）
pos = {}
def layout(node, x=0, y=0, dx=1):
    children = list(G.successors(node))
    pos[node] = (x, -y)
    if children:
        width = dx * (len(children) - 1)
        for i, child in enumerate(children):
            layout(child, x - width/2 + i*dx, y+1, dx=dx/2)
layout('项目架构', x=0, y=0, dx=4)

# 绘图
plt.figure(figsize=(8, 6))
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="#e3f2fd", font_size=12, font_family='Microsoft YaHei', arrows=False)
plt.title("项目脑图Demo（matplotlib+networkx）", fontsize=16)
plt.tight_layout()

# 输出图片
out_path = Path('docs/development/project_mindmap_demo.png')
out_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_path, dpi=150)
plt.close()
print(f'✅ Demo脑图图片已生成：{out_path.resolve()}') 