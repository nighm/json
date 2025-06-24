#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用pyecharts生成美观的项目脑图（Tree），输出HTML和PNG（需安装snapshot-selenium和Chrome）
输出：docs/development/project_mindmap_pyecharts.html 和 project_mindmap_pyecharts.png
"""
from pyecharts import options as opts
from pyecharts.charts import Tree
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot
from pathlib import Path

# 定义脑图结构（可根据实际项目结构自动生成，这里用简化版）
data = [
    {
        "name": "项目架构",
        "children": [
            {"name": "src", "children": [
                {"name": "domain"}, {"name": "application"}, {"name": "infrastructure"},
                {"name": "interfaces"}, {"name": "config"}
            ]},
            {"name": "scripts"},
            {"name": "tools"},
            {"name": "docs"}
        ]
    }
]

# 构建pyecharts树图
c = (
    Tree()
    .add(
        "",
        data,
        orient="LR",
        symbol_size=18,
        label_opts=opts.LabelOpts(position="left", font_size=14, font_family='Microsoft YaHei')
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="项目脑图（pyecharts）"))
)

# 输出HTML
out_html = Path('docs/development/project_mindmap_pyecharts.html')
out_html.parent.mkdir(parents=True, exist_ok=True)
c.render(str(out_html))
print(f'✅ 脑图HTML已生成：{out_html.resolve()}')

# 输出PNG（需安装snapshot-selenium和Chrome）
out_png = Path('docs/development/project_mindmap_pyecharts.png')
try:
    make_snapshot(snapshot, c.render(), str(out_png))
    print(f'✅ 脑图PNG已生成：{out_png.resolve()}')
except Exception as e:
    print(f'⚠️ PNG导出失败（如未安装Chrome或snapshot-selenium）：{e}')
    print('你可以直接用浏览器打开HTML文件查看脑图效果。') 