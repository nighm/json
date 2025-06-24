#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重构第二阶段：战场规划自动化分析
分析项目架构、依赖关系、确定重构优先级和风险点

作者：AI Assistant
创建时间：2025-01-27
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
import logging
from collections import defaultdict

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ArchitectureAnalyzer:
    """架构分析器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "docs" / "development"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # DDD分层定义
        self.ddd_layers = {
            'interfaces': ['cli', 'api', 'web', 'main'],
            'application': ['services', 'use_cases', 'application'],
            'domain': ['entities', 'value_objects', 'domain_services', 'repositories'],
            'infrastructure': ['persistence', 'external', 'cross_cutting']
        }

    def analyze_architecture_patterns(self) -> List[Dict]:
        """分析当前架构模式"""
        logger.info("开始分析架构模式...")
        
        patterns = []
        
        # 检查DDD分层结构
        ddd_compliance = self._check_ddd_compliance()
        patterns.append({
            'pattern': 'DDD分层架构',
            'compliance': ddd_compliance['compliance_rate'],
            'issues': ddd_compliance['issues'],
            'recommendations': ddd_compliance['recommendations']
        })
        
        # 检查模块化程度
        modularity = self._analyze_modularity()
        patterns.append({
            'pattern': '模块化设计',
            'compliance': modularity['modularity_score'],
            'issues': modularity['issues'],
            'recommendations': modularity['recommendations']
        })
        
        return patterns

    def _check_ddd_compliance(self) -> Dict:
        """检查DDD分层架构合规性"""
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return {
                'compliance_rate': 0.0,
                'issues': ['缺少src目录，未采用DDD分层架构'],
                'recommendations': ['创建src目录，按DDD分层组织代码']
            }
        
        layer_counts = {}
        issues = []
        recommendations = []
        
        # 统计各层文件数量
        for layer, subdirs in self.ddd_layers.items():
            layer_path = src_dir / layer
            if layer_path.exists():
                file_count = len(list(layer_path.rglob("*.py")))
                layer_counts[layer] = file_count
            else:
                layer_counts[layer] = 0
                issues.append(f"缺少{layer}层目录")
                recommendations.append(f"创建src/{layer}目录")
        
        # 计算合规率
        total_layers = len(self.ddd_layers)
        existing_layers = sum(1 for count in layer_counts.values() if count > 0)
        compliance_rate = existing_layers / total_layers
        
        return {
            'compliance_rate': compliance_rate,
            'layer_counts': layer_counts,
            'issues': issues,
            'recommendations': recommendations
        }

    def _analyze_modularity(self) -> Dict:
        """分析模块化程度"""
        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return {
                'modularity_score': 0.0,
                'issues': ['缺少模块化结构'],
                'recommendations': ['建立模块化目录结构']
            }
        
        # 统计模块数量
        modules = []
        for item in src_dir.iterdir():
            if item.is_dir():
                py_files = list(item.rglob("*.py"))
                modules.append({
                    'name': item.name,
                    'file_count': len(py_files),
                    'size': sum(f.stat().st_size for f in py_files if f.is_file())
                })
        
        # 计算模块化评分
        if not modules:
            return {
                'modularity_score': 0.0,
                'issues': ['src目录下无子模块'],
                'recommendations': ['创建功能模块目录']
            }
        
        modularity_score = min(1.0, len(modules) / 10)
        
        issues = []
        recommendations = []
        
        if modularity_score < 0.5:
            issues.append("模块化程度较低")
            recommendations.append("增加模块划分，平衡模块大小")
        
        return {
            'modularity_score': modularity_score,
            'modules': modules,
            'issues': issues,
            'recommendations': recommendations
        }

    def analyze_dependencies(self) -> Dict:
        """分析模块间依赖关系"""
        logger.info("开始分析依赖关系...")
        
        dependency_graph = defaultdict(set)
        
        # 扫描所有Python文件
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析导入语句
                imports = self._extract_imports(content)
                module_name = self._get_module_name(py_file)
                
                for imp in imports:
                    dependency_graph[module_name].add(imp)
                    
            except Exception as e:
                logger.warning(f"分析文件失败 {py_file}: {e}")
        
        # 计算依赖指标
        dependency_metrics = self._calculate_dependency_metrics(dependency_graph)
        
        return {
            'graph': dict(dependency_graph),
            'metrics': dependency_metrics
        }

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            '__pycache__', 'venv', '.git', 'node_modules',
            'site-packages', 'tests', 'test_'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _extract_imports(self, content: str) -> List[str]:
        """提取导入语句"""
        imports = []
        
        # 使用正则表达式提取导入
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*$',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    imports.append(match.group(1))
                    break
        
        return imports

    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名称"""
        relative_path = file_path.relative_to(self.project_root)
        return str(relative_path).replace('\\', '.').replace('/', '.').replace('.py', '')

    def _calculate_dependency_metrics(self, dependency_graph: Dict) -> Dict:
        """计算依赖指标"""
        metrics = {
            'total_modules': len(dependency_graph),
            'avg_dependencies': 0,
            'max_dependencies': 0,
            'high_coupling_modules': []
        }
        
        if dependency_graph:
            # 计算平均依赖数
            total_deps = sum(len(deps) for deps in dependency_graph.values())
            metrics['avg_dependencies'] = total_deps / len(dependency_graph)
            metrics['max_dependencies'] = max(len(deps) for deps in dependency_graph.values())
            
            # 识别高耦合模块
            threshold = metrics['avg_dependencies'] * 2
            for module, deps in dependency_graph.items():
                if len(deps) > threshold:
                    metrics['high_coupling_modules'].append({
                        'module': module,
                        'dependencies': len(deps)
                    })
        
        return metrics

    def determine_refactor_priorities(self, patterns: List[Dict], dependencies: Dict) -> List[Dict]:
        """确定重构优先级"""
        logger.info("开始确定重构优先级...")
        
        priorities = []
        
        # 基于架构问题确定优先级
        for pattern in patterns:
            if pattern['compliance'] < 0.5:
                priorities.append({
                    'module': 'architecture',
                    'priority': 'high',
                    'reason': f"{pattern['pattern']}合规性低 ({pattern['compliance']:.1%})",
                    'impact': 'high',
                    'effort': 'high'
                })
        
        # 基于依赖关系确定优先级
        if 'metrics' in dependencies:
            for module_info in dependencies['metrics']['high_coupling_modules']:
                priorities.append({
                    'module': module_info['module'],
                    'priority': 'high',
                    'reason': f"耦合度高 ({module_info['dependencies']} 个依赖)",
                    'impact': 'high',
                    'effort': 'high'
                })
        
        return priorities

    def identify_risk_points(self, patterns: List[Dict], dependencies: Dict) -> List[Dict]:
        """识别重构风险点"""
        logger.info("开始识别风险点...")
        
        risks = []
        
        # 基于依赖关系识别风险
        if 'metrics' in dependencies:
            if dependencies['metrics']['avg_dependencies'] > 5:
                risks.append({
                    'type': 'dependency_risk',
                    'description': '模块间依赖过多，重构可能影响范围大',
                    'severity': 'high',
                    'mitigation': '分阶段重构，先解耦核心模块'
                })
        
        # 基于架构问题识别风险
        for pattern in patterns:
            if pattern['compliance'] < 0.3:
                risks.append({
                    'type': 'architecture_risk',
                    'description': f'{pattern["pattern"]}严重不符合规范',
                    'severity': 'high',
                    'mitigation': '制定详细的重构计划，分步骤实施'
                })
        
        return risks

    def generate_planning_report(self) -> str:
        """生成规划报告"""
        logger.info("开始生成规划报告...")
        
        # 执行所有分析
        patterns = self.analyze_architecture_patterns()
        dependencies = self.analyze_dependencies()
        priorities = self.determine_refactor_priorities(patterns, dependencies)
        risks = self.identify_risk_points(patterns, dependencies)
        
        # 生成报告
        report_file = self.output_dir / "phase2_planning_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self._format_planning_report(patterns, dependencies, priorities, risks))
        
        logger.info(f"规划报告已生成: {report_file}")
        return str(report_file)

    def _format_planning_report(self, patterns: List[Dict], dependencies: Dict, priorities: List[Dict], risks: List[Dict]) -> str:
        """格式化规划报告"""
        report = f"""# 重构第二阶段：战场规划报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 架构设计分析

### 1.1 架构模式评估

"""
        
        for pattern in patterns:
            report += f"""#### {pattern['pattern']}
- **合规率**: {pattern['compliance']:.1%}
- **问题**: {', '.join(pattern['issues']) if pattern['issues'] else '无'}
- **建议**: {', '.join(pattern['recommendations']) if pattern['recommendations'] else '无'}

"""
        
        # 依赖关系分析
        if 'metrics' in dependencies:
            metrics = dependencies['metrics']
            report += f"""## 2. 依赖关系分析

### 2.1 依赖指标
- **总模块数**: {metrics['total_modules']}
- **平均依赖数**: {metrics['avg_dependencies']:.2f}
- **最大依赖数**: {metrics['max_dependencies']}

### 2.2 高耦合模块
"""
            for module in metrics['high_coupling_modules']:
                report += f"- {module['module']}: {module['dependencies']} 个依赖\n"
        
        # 重构优先级
        report += f"""
## 3. 重构优先级

### 3.1 高优先级模块
"""
        high_priority = [p for p in priorities if p['priority'] == 'high']
        for priority in high_priority[:5]:  # 显示前5个
            report += f"""- **{priority['module']}**
  - 原因: {priority['reason']}
  - 影响: {priority['impact']}
  - 工作量: {priority['effort']}

"""
        
        # 风险点
        report += f"""## 4. 风险点识别

"""
        for risk in risks:
            report += f"""### {risk['type']}
- **描述**: {risk['description']}
- **严重程度**: {risk['severity']}
- **缓解措施**: {risk['mitigation']}

"""
        
        # 建议
        report += f"""## 5. 重构建议

### 5.1 短期目标（1-2周）
1. 解决高优先级架构问题
2. 重构高复杂度模块
3. 建立基础DDD分层结构

### 5.2 中期目标（1个月）
1. 完善依赖注入机制
2. 优化模块间依赖关系
3. 建立代码规范

### 5.3 长期目标（2-3个月）
1. 实现完整的DDD架构
2. 建立自动化测试体系
3. 优化性能和可维护性

## 6. 下一步行动

1. 根据优先级制定详细的重构计划
2. 建立重构里程碑和检查点
3. 准备第三阶段：结构迁移
"""
        
        return report

    def print_summary(self, patterns: List[Dict], dependencies: Dict, priorities: List[Dict], risks: List[Dict]) -> None:
        """打印分析摘要"""
        print("\n" + "="*60)
        print("🎯 第二阶段：战场规划分析完成！")
        print("="*60)
        
        print("\n📊 分析结果摘要:")
        
        # 架构模式
        print(f"  • 架构模式分析: {len(patterns)} 个模式")
        for pattern in patterns:
            print(f"    - {pattern['pattern']}: {pattern['compliance']:.1%} 合规率")
        
        # 依赖关系
        if 'metrics' in dependencies:
            metrics = dependencies['metrics']
            print(f"  • 依赖关系: {metrics['total_modules']} 个模块，平均 {metrics['avg_dependencies']:.1f} 个依赖")
        
        # 重构优先级
        high_priority = [p for p in priorities if p['priority'] == 'high']
        print(f"  • 重构优先级: {len(high_priority)} 个高优先级模块")
        
        # 风险点
        high_risks = [r for r in risks if r['severity'] == 'high']
        print(f"  • 风险点: {len(high_risks)} 个高风险点")
        
        print(f"\n📄 详细报告: {self.output_dir}/phase2_planning_report.md")
        print("\n" + "="*60)


def main():
    """主函数"""
    try:
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent
        
        # 创建分析器实例
        analyzer = ArchitectureAnalyzer(project_root)
        
        # 生成规划报告
        report_file = analyzer.generate_planning_report()
        
        # 执行分析并打印摘要
        patterns = analyzer.analyze_architecture_patterns()
        dependencies = analyzer.analyze_dependencies()
        priorities = analyzer.determine_refactor_priorities(patterns, dependencies)
        risks = analyzer.identify_risk_points(patterns, dependencies)
        analyzer.print_summary(patterns, dependencies, priorities, risks)
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 