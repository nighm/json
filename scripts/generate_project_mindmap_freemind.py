#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成FreeMind(.mm)脑图文件：
- 简化版：主目录+2级子目录
- 详细版：递归所有代码相关目录和.py文件，自动排除第三方/依赖/缓存
输出：docs/development/project_mindmap_simple.mm、project_mindmap_full.mm
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

TOP_LEVEL_DIRS = ['src', 'scripts', 'tools', 'docs']
EXCLUDE_DIRS = {'venv', '__pycache__', '.git', 'node_modules', 'test_output', 'temp', 'data', 'backups', 'generated_devices', 'bin', 'lib', 'cache', 'dist', 'build', 'externals', 'java', 'jmeter', 'redis'}
EXCLUDE_FILES = {'.DS_Store', 'Thumbs.db'}
ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / 'docs' / 'development'

# FreeMind头部
def create_map():
    return ET.Element('map', version="1.0.1")

def add_node(parent, text):
    node = ET.SubElement(parent, 'node', TEXT=text)
    return node

def build_simple_tree():
    def get_children(path, level):
        if level > 2:
            return []
        children = []
        for sub in sorted(path.iterdir()):
            if sub.name.startswith('.') or sub.name in EXCLUDE_DIRS:
                continue
            children.append((sub.name, sub, level))
        return children
    data = []
    for d in TOP_LEVEL_DIRS:
        p = ROOT / d
        if p.exists():
            data.append((d, p, 1))
    return data, get_children

def build_full_tree():
    def get_children(path):
        children = []
        for sub in sorted(path.iterdir()):
            if sub.name in EXCLUDE_DIRS or sub.name.startswith('.') or sub.name in EXCLUDE_FILES:
                continue
            if sub.is_dir():
                sub_children = get_children(sub)
                if sub_children:
                    children.append((sub.name, sub, sub_children))
            elif sub.suffix == '.py':
                children.append((sub.name, sub, []))
        return children
    data = []
    for d in TOP_LEVEL_DIRS:
        p = ROOT / d
        if p.exists():
            children = get_children(p)
            if children:
                data.append((d, p, children))
    return data

def write_freemind_simple(filename):
    mm = create_map()
    root_node = add_node(mm, '项目架构')
    data, get_children = build_simple_tree()
    def add_children(parent, name, path, level):
        node = add_node(parent, name)
        if path.is_dir() and level < 2:
            for cname, cpath, clevel in get_children(path, level+1):
                add_children(node, cname, cpath, clevel)
    for name, path, level in data:
        add_children(root_node, name, path, level)
    xmlstr = minidom.parseString(ET.tostring(mm, encoding='utf-8')).toprettyxml(indent="  ", encoding='utf-8')
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / filename, 'wb') as f:
        f.write(xmlstr)
    print(f'✅ 简化版FreeMind脑图已生成：{(OUT_DIR/filename).resolve()}')

def write_freemind_full(filename):
    mm = create_map()
    root_node = add_node(mm, '项目架构')
    data = build_full_tree()
    def add_children(parent, name, path, children):
        node = add_node(parent, name)
        for cname, cpath, cchildren in children:
            add_children(node, cname, cpath, cchildren)
    for name, path, children in data:
        add_children(root_node, name, path, children)
    xmlstr = minidom.parseString(ET.tostring(mm, encoding='utf-8')).toprettyxml(indent="  ", encoding='utf-8')
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / filename, 'wb') as f:
        f.write(xmlstr)
    print(f'✅ 详细版FreeMind脑图已生成：{(OUT_DIR/filename).resolve()}')

if __name__ == "__main__":
    write_freemind_simple('project_mindmap_simple.mm')
    write_freemind_full('project_mindmap_full.mm') 