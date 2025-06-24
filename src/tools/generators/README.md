# 项目生成工具集
# Project Generation Tools

本目录包含用于生成项目结构和模板的各种工具和脚本。
This directory contains various tools and scripts for generating project structures and templates.

## 目录结构
## Directory Structure

```
tools/
├── generators/           # 项目生成工具
│   # Project Generation Tools
│   ├── templates/       # 模板文件
│   │   # Template Files
│   ├── utils/          # 工具类
│   │   # Utility Classes
│   ├── project_template.py # 项目模板生成器
│   │   # Project Template Generator
│   ├── migrate_ddd.py  # DDD架构迁移工具
│   │   # DDD Architecture Migration Tool
│   └── create_game_templates.ps1 # 游戏模板生成脚本
│       # Game Template Generation Script
```

## 工具说明
## Tool Description

1. 项目模板生成器
   Project Template Generator
   - `project_template.py`: 生成标准项目结构
   - `init_project.ps1`: 初始化新项目

2. 游戏相关生成器
   Game-related Generators
   - `create_game_templates.ps1`: 生成游戏相关模板
   - `create_game_module.ps1`: 生成游戏模块结构

3. 架构迁移工具
   Architecture Migration Tool
   - `migrate_ddd.py`: 将现有项目迁移到DDD架构

## 使用方法
## Usage

1. 生成新项目：
   Generate New Project:
```powershell
python tools/generators/project_template.py --name my_project
```

2. 初始化项目：
   Initialize Project:
```powershell
.\tools\generators\init_project.ps1
```

3. 生成游戏模板：
   Generate Game Templates:
```powershell
.\tools\generators\create_game_templates.ps1
```

4. 生成游戏模块：
   Generate Game Module:
```powershell
.\tools\generators\create_game_module.ps1 --name my_game
```

5. 迁移到DDD架构：
   Migrate to DDD Architecture:
```powershell
python tools/generators/migrate_ddd.py --project path/to/project
```

## 模板说明
## Template Description

模板文件位于 `templates/` 目录下，包括：
Template files are located in the `templates/` directory, including:
- 项目基础结构模板
  Project Basic Structure Template
- 游戏模块模板
  Game Module Template
- DDD架构模板
  DDD Architecture Template
- 配置文件模板
  Configuration File Template

## 注意事项
## Notes

1. 生成项目前请确保目标目录为空
   Ensure the target directory is empty before generating the project

2. 使用模板时注意检查配置参数
   Check configuration parameters when using templates

3. 迁移项目前请备份重要数据
   Backup important data before migrating the project

4. 生成的代码需要根据实际需求调整
   Generated code needs to be adjusted according to actual requirements

5. 保持模板文件的更新和维护
   Keep template files updated and maintained
