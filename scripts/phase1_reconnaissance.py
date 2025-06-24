#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一阶段：战场侦察自动化工具
功能：代码统计、模块关系分析、重复代码检测、思维导图生成
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter
import re
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class CodeAnalyzer:
    """代码分析器 - 统计项目规模和复杂度"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.exclude_dirs = {
            'venv', '__pycache__', '.git', 'node_modules', 
            'tools/java', 'tools/jmeter', 'tools/redis',
            'data/generated_devices', 'test_output', 'temp'
        }
        self.python_extensions = {'.py', '.pyx', '.pyi'}
        
    def count_files_and_lines(self) -> Dict[str, Any]:
        """统计文件数量和代码行数"""
        stats = {
            'total_files': 0,
            'python_files': 0,
            'total_lines': 0,
            'code_lines': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'by_directory': defaultdict(lambda: {'files': 0, 'lines': 0}),
            'by_extension': Counter()
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # 排除不需要分析的目录
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_root)
                
                # 统计所有文件
                stats['total_files'] += 1
                stats['by_extension'][file_path.suffix] += 1
                
                # 统计Python文件
                if file_path.suffix in self.python_extensions:
                    stats['python_files'] += 1
                    dir_name = rel_path.parts[0] if rel_path.parts else 'root'
                    stats['by_directory'][dir_name]['files'] += 1
                    
                    # 分析Python文件内容
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            stats['total_lines'] += len(lines)
                            stats['by_directory'][dir_name]['lines'] += len(lines)
                            
                            for line in lines:
                                stripped = line.strip()
                                if not stripped:
                                    stats['blank_lines'] += 1
                                elif stripped.startswith('#'):
                                    stats['comment_lines'] += 1
                                else:
                                    stats['code_lines'] += 1
                    except Exception as e:
                        print(f"警告：无法读取文件 {file_path}: {e}")
        
        return stats
    
    def analyze_module_dependencies(self) -> Dict[str, List[str]]:
        """分析模块依赖关系"""
        dependencies = defaultdict(set)
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 提取import语句
                        import_patterns = [
                            r'^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*$',
                            r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
                            r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import\s+\*'
                        ]
                        
                        for pattern in import_patterns:
                            matches = re.findall(pattern, content, re.MULTILINE)
                            for match in matches:
                                module_name = match.split('.')[0]  # 取主模块名
                                if module_name not in ['os', 'sys', 'json', 're', 'datetime', 'pathlib', 'typing', 'collections']:
                                    dependencies[str(file_path.relative_to(self.project_root))].add(module_name)
                                    
                    except Exception as e:
                        print(f"警告：无法分析文件 {file_path}: {e}")
        
        return {k: list(v) for k, v in dependencies.items()}
    
    def detect_duplicate_code(self) -> List[Dict[str, Any]]:
        """检测重复代码片段"""
        duplicates = []
        
        # 简单的重复代码检测（基于函数和类定义）
        code_patterns = [
            (r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):', '函数定义'),
            (r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]', '类定义'),
            (r'if\s+__name__\s*==\s*[\'"]__main__[\'"]:', '主程序入口')
        ]
        
        pattern_counts = defaultdict(list)
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern, pattern_type in code_patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                pattern_counts[f"{pattern_type}:{match}"].append(str(file_path.relative_to(self.project_root)))
                                    
                    except Exception as e:
                        print(f"警告：无法分析文件 {file_path}: {e}")
        
        # 找出重复的模式
        for pattern, files in pattern_counts.items():
            if len(files) > 1:
                duplicates.append({
                    'pattern': pattern,
                    'files': files,
                    'count': len(files)
                })
        
        return sorted(duplicates, key=lambda x: x['count'], reverse=True)

class MindMapGenerator:
    """思维导图生成器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def generate_mermaid_mindmap(self, dependencies: Dict[str, List[str]]) -> str:
        """生成Mermaid格式的思维导图"""
        mermaid_code = """graph TD
    A[项目架构] --> B[src目录]
    A --> C[scripts目录]
    A --> D[tools目录]
    A --> E[docs目录]
    A --> F[其他文件]
    
    B --> B1[domain层]
    B --> B2[application层]
    B --> B3[infrastructure层]
    B --> B4[interfaces层]
    B --> B5[config层]
    
    B1 --> B1A[entities实体]
    B1 --> B1B[services领域服务]
    B1 --> B1C[value_objects值对象]
    B1 --> B1D[strategy策略]
    
    B2 --> B2A[services应用服务]
    B2 --> B2B[jmeter测试服务]
    B2 --> B2C[monitor监控服务]
    
    B3 --> B3A[repositories仓储]
    B3 --> B3B[jmeter执行器]
    B3 --> B3C[report报告生成]
    B3 --> B3D[analysis分析工具]
    
    B4 --> B4A[cli命令行接口]
    B4 --> B4B[main主程序]
    
    B5 --> B5A[api配置]
    B5 --> B5B[core核心配置]
    B5 --> B5C[test测试配置]
    
    C --> C1[Python脚本]
    C --> C2[其他脚本]
    
    D --> D1[jmeter工具]
    D --> D2[redis工具]
    D --> D3[其他工具]
    
    E --> E1[api文档]
    E --> E2[design设计文档]
    E --> E3[development开发文档]
    E --> E4[requirements需求文档]
"""
        return mermaid_code
    
    def generate_dependency_graph(self, dependencies: Dict[str, List[str]]) -> str:
        """生成依赖关系图"""
        mermaid_code = """graph LR
"""
        
        # 按目录分组
        dir_modules = defaultdict(set)
        for file_path, deps in dependencies.items():
            dir_name = file_path.split('/')[0] if '/' in file_path else 'root'
            dir_modules[dir_name].update(deps)
        
        # 生成节点
        for dir_name, modules in dir_modules.items():
            mermaid_code += f"    {dir_name.replace('-', '_')}[{dir_name}]\n"
        
        # 生成连接
        connections = set()
        for file_path, deps in dependencies.items():
            source_dir = file_path.split('/')[0] if '/' in file_path else 'root'
            for dep in deps:
                target_dir = dep.split('.')[0] if '.' in dep else dep
                if target_dir in dir_modules:
                    connection = f"{source_dir.replace('-', '_')} --> {target_dir.replace('-', '_')}"
                    if connection not in connections:
                        connections.add(connection)
                        mermaid_code += f"    {connection}\n"
        
        return mermaid_code

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_html_report(self, stats: Dict[str, Any], dependencies: Dict[str, List[str]], 
                           duplicates: List[Dict[str, Any]], mindmap_code: str) -> str:
        """生成HTML格式的分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"phase1_report_{timestamp}.html"
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>第一阶段重构分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .highlight {{ background-color: #f0f8ff; padding: 10px; border-radius: 3px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .warning {{ color: #ff6b6b; }}
        .success {{ color: #51cf66; }}
    </style>
</head>
<body>
    <h1>第一阶段重构分析报告</h1>
    <p>生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <div class="section">
        <h2>📊 项目统计概览</h2>
        <div class="highlight">
            <p><strong>总文件数：</strong>{stats['total_files']}</p>
            <p><strong>Python文件数：</strong>{stats['python_files']}</p>
            <p><strong>总代码行数：</strong>{stats['total_lines']}</p>
            <p><strong>有效代码行数：</strong>{stats['code_lines']}</p>
            <p><strong>注释行数：</strong>{stats['comment_lines']}</p>
            <p><strong>空行数：</strong>{stats['blank_lines']}</p>
        </div>
    </div>
    
    <div class="section">
        <h2>📁 按目录统计</h2>
        <table>
            <tr><th>目录</th><th>文件数</th><th>代码行数</th></tr>
"""
        
        for dir_name, dir_stats in sorted(stats['by_directory'].items()):
            html_content += f"            <tr><td>{dir_name}</td><td>{dir_stats['files']}</td><td>{dir_stats['lines']}</td></tr>\n"
        
        html_content += """        </table>
    </div>
    
    <div class="section">
        <h2>🔗 项目架构思维导图</h2>
        <div class="mermaid">
"""
        html_content += mindmap_code
        html_content += """        </div>
    </div>
    
    <div class="section">
        <h2>⚠️ 重复代码检测</h2>
"""
        
        if duplicates:
            html_content += """        <table>
            <tr><th>重复模式</th><th>出现次数</th><th>文件列表</th></tr>
"""
            for dup in duplicates[:10]:  # 只显示前10个
                files_str = ', '.join(dup['files'][:3])  # 只显示前3个文件
                if len(dup['files']) > 3:
                    files_str += f" ... (共{len(dup['files'])}个文件)"
                html_content += f"            <tr><td>{dup['pattern']}</td><td>{dup['count']}</td><td>{files_str}</td></tr>\n"
            html_content += "        </table>"
        else:
            html_content += "        <p class='success'>未发现明显的重复代码模式</p>"
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>🎯 重构建议</h2>
        <ul>
            <li><strong>高优先级：</strong>关注代码行数最多的目录，优先重构</li>
            <li><strong>中优先级：</strong>处理重复代码模式，提取公共逻辑</li>
            <li><strong>低优先级：</strong>优化注释和空行比例</li>
        </ul>
    </div>
</body>
<script>
    mermaid.initialize({{ startOnLoad: true }});
</script>
</html>"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_file)
    
    def generate_markdown_report(self, stats: Dict[str, Any], dependencies: Dict[str, List[str]], 
                               duplicates: List[Dict[str, Any]]) -> str:
        """生成Markdown格式的分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"phase1_report_{timestamp}.md"
        
        markdown_content = f"""# 第一阶段重构分析报告

**生成时间：** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 项目统计概览

- **总文件数：** {stats['total_files']}
- **Python文件数：** {stats['python_files']}
- **总代码行数：** {stats['total_lines']}
- **有效代码行数：** {stats['code_lines']}
- **注释行数：** {stats['comment_lines']}
- **空行数：** {stats['blank_lines']}

## 📁 按目录统计

| 目录 | 文件数 | 代码行数 |
|------|--------|----------|
"""
        
        for dir_name, dir_stats in sorted(stats['by_directory'].items()):
            markdown_content += f"| {dir_name} | {dir_stats['files']} | {dir_stats['lines']} |\n"
        
        markdown_content += f"""
## 🔗 模块依赖关系

共发现 {len(dependencies)} 个文件存在模块依赖关系。

### 主要依赖模式：
"""
        
        # 统计依赖频率
        dep_counter = Counter()
        for deps in dependencies.values():
            dep_counter.update(deps)
        
        for dep, count in dep_counter.most_common(10):
            markdown_content += f"- {dep}: 被 {count} 个文件引用\n"
        
        markdown_content += f"""
## ⚠️ 重复代码检测

发现 {len(duplicates)} 个重复代码模式：

"""
        
        for i, dup in enumerate(duplicates[:10], 1):
            files_str = ', '.join(dup['files'][:3])
            if len(dup['files']) > 3:
                files_str += f" ... (共{len(dup['files'])}个文件)"
            markdown_content += f"{i}. **{dup['pattern']}** - 出现 {dup['count']} 次\n   - 文件：{files_str}\n\n"
        
        markdown_content += """
## 🎯 重构建议

### 高优先级
- 关注代码行数最多的目录，优先重构
- 处理重复代码模式，提取公共逻辑

### 中优先级
- 优化模块依赖关系，减少循环依赖
- 统一代码风格和注释规范

### 低优先级
- 优化注释和空行比例
- 完善文档和测试覆盖

## 📋 下一步行动

1. 根据统计结果确定重构优先级
2. 制定详细的模块迁移计划
3. 开始第二阶段的手术规划
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(report_file)

def main():
    """主函数"""
    print("🚀 开始第一阶段：战场侦察")
    print("=" * 50)
    
    # 初始化分析器
    analyzer = CodeAnalyzer(project_root)
    mindmap_gen = MindMapGenerator(project_root)
    
    # 创建输出目录
    output_dir = project_root / "docs" / "development" / "phase1_reports"
    report_gen = ReportGenerator(output_dir)
    
    # 1. 统计代码
    print("📊 正在统计代码...")
    stats = analyzer.count_files_and_lines()
    
    # 2. 分析依赖关系
    print("🔗 正在分析模块依赖关系...")
    dependencies = analyzer.analyze_module_dependencies()
    
    # 3. 检测重复代码
    print("⚠️ 正在检测重复代码...")
    duplicates = analyzer.detect_duplicate_code()
    
    # 4. 生成思维导图
    print("🗺️ 正在生成思维导图...")
    mindmap_code = mindmap_gen.generate_mermaid_mindmap(dependencies)
    
    # 5. 生成报告
    print("📝 正在生成分析报告...")
    html_report = report_gen.generate_html_report(stats, dependencies, duplicates, mindmap_code)
    md_report = report_gen.generate_markdown_report(stats, dependencies, duplicates)
    
    # 6. 输出结果
    print("\n✅ 分析完成！")
    print(f"📄 HTML报告：{html_report}")
    print(f"📄 Markdown报告：{md_report}")
    
    # 7. 输出关键发现
    print("\n🔍 关键发现：")
    print(f"- 项目共有 {stats['total_files']} 个文件，其中 {stats['python_files']} 个Python文件")
    print(f"- 总代码行数：{stats['total_lines']}，有效代码行数：{stats['code_lines']}")
    print(f"- 发现 {len(duplicates)} 个重复代码模式")
    print(f"- 模块依赖关系涉及 {len(dependencies)} 个文件")
    
    # 8. 识别最大目录
    if stats['by_directory']:
        largest_dir = max(stats['by_directory'].items(), key=lambda x: x[1]['lines'])
        print(f"- 代码量最大的目录：{largest_dir[0]} ({largest_dir[1]['lines']} 行)")
    
    print("\n💡 建议：")
    print("1. 查看生成的报告了解详细分析结果")
    print("2. 根据重复代码模式制定重构计划")
    print("3. 重点关注代码量最大的目录")
    print("4. 进入第二阶段：手术规划")

if __name__ == "__main__":
    main()