#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将Mermaid思维导图源码自动转换为PNG图片（使用mermaid.ink在线API）
输入：docs/development/project_mindmap.mmd
输出：docs/development/project_mindmap.png
"""
import sys
from pathlib import Path

print("=== Mermaid PNG 导出脚本开始 ===")

# 检查requests库
try:
    import requests
except ImportError:
    print("❌ 未安装requests库，请先运行：pip install requests")
    sys.exit(1)
import base64

mmd_path = Path('docs/development/project_mindmap.mmd')
png_path = Path('docs/development/project_mindmap.png')

if not mmd_path.exists():
    print(f"❌ Mermaid源码文件不存在: {mmd_path}")
    sys.exit(1)

try:
    with open(mmd_path, 'r', encoding='utf-8') as f:
        mermaid_code = f.read()
except Exception as e:
    print(f"❌ 读取Mermaid源码失败: {e}")
    sys.exit(1)

try:
    mermaid_b64 = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
    api_url = f'https://mermaid.ink/img/{mermaid_b64}'
    print(f'API URL: {api_url}')
    print('正在请求mermaid.ink API生成PNG图片...')
    response = requests.get(api_url, timeout=20)
    print(f'响应Content-Type: {response.headers.get("Content-Type")}, 状态码: {response.status_code}')
    if response.status_code == 200 and response.headers['Content-Type'].startswith('image/png'):
        with open(png_path, 'wb') as f:
            f.write(response.content)
        print(f'✅ 图片已保存到: {png_path.resolve()}')
    else:
        print(f'❌ 图片生成失败，状态码: {response.status_code}')
        print('响应内容前100字节：', response.content[:100])
        if response.headers.get('Content-Type', '').startswith('text'):
            print('响应文本内容：', response.text[:500])
except Exception as e:
    print(f"❌ 网络请求或图片保存失败: {e}")
    sys.exit(1)

print("=== Mermaid PNG 导出脚本结束 ===") 