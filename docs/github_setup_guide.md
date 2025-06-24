# GitHub仓库设置指南

## 概述

本指南将帮助您将昆仑卫士性能测试与设备管理平台项目上传到GitHub。项目已经配置了合适的`.gitignore`文件，确保只上传必要的代码文件，排除敏感数据和大文件。

## 前置条件

1. **安装Git**
   - Windows: 下载并安装 [Git for Windows](https://git-scm.com/download/win)
   - 验证安装: `git --version`

2. **GitHub账户**
   - 在 [GitHub](https://github.com) 创建账户
   - 创建新的仓库（Repository）

3. **项目准备**
   - 确保项目根目录包含以下文件：
     - `README.md` - 项目说明文档
     - `requirements.txt` - Python依赖
     - `LICENSE` - 许可证文件
     - `.gitignore` - Git忽略文件

## 快速设置

### 方法一：使用自动化脚本（推荐）

1. **激活虚拟环境**
   ```bash
   venv\Scripts\activate
   ```

2. **运行设置脚本**
   ```bash
   # 设置仓库（替换为您的GitHub仓库URL）
   python scripts/python/setup_github.py --remote-url https://github.com/your-username/your-repo.git
   
   # 推送代码到GitHub
   python scripts/python/setup_github.py --push
   ```

3. **查看状态**
   ```bash
   python scripts/python/setup_github.py --status
   ```

### 方法二：手动设置

1. **初始化Git仓库**
   ```bash
   git init
   ```

2. **添加远程仓库**
   ```bash
   git remote add origin https://github.com/your-username/your-repo.git
   ```

3. **添加文件**
   ```bash
   git add .
   ```

4. **提交文件**
   ```bash
   git commit -m "Initial commit: 昆仑卫士性能测试与设备管理平台"
   ```

5. **推送到GitHub**
   ```bash
   git branch -M main
   git push -u origin main
   ```

## 项目文件说明

### 会上传的文件
- `src/` - 源代码目录（DDD架构）
- `config/` - 配置文件
- `docs/` - 文档目录
- `scripts/` - 脚本文件
- `tests/` - 测试文件
- `README.md` - 项目说明
- `requirements.txt` - 依赖列表
- `LICENSE` - 许可证

### 不会上传的文件（已配置在.gitignore中）
- `venv/` - 虚拟环境
- `tools/` - 第三方工具（JMeter、Redis等）
- `data/` - 敏感数据文件
- `charts/` - 生成的图表
- `test_output/` - 测试输出
- `temp/` - 临时文件
- `*.log` - 日志文件
- `*.db` - 数据库文件
- `*.csv` - 数据文件
- `*.zip` - 压缩文件

## 常见问题

### Q: 为什么某些文件没有被上传？
A: 这些文件可能被`.gitignore`文件排除，或者包含敏感信息。检查`.gitignore`文件确认。

### Q: 如何添加被忽略的文件？
A: 如果确实需要上传某个被忽略的文件，可以使用：
```bash
git add -f filename
```

### Q: 如何更新远程仓库？
A: 修改代码后，使用以下命令：
```bash
git add .
git commit -m "更新说明"
git push
```

### Q: 如何查看哪些文件会被上传？
A: 使用以下命令：
```bash
git status
```

## 安全注意事项

1. **敏感信息**
   - 确保不包含密码、API密钥等敏感信息
   - 使用环境变量或配置文件管理敏感数据

2. **大文件**
   - 避免上传大型二进制文件
   - 使用Git LFS处理大文件（如需要）

3. **许可证**
   - 确保项目有合适的许可证
   - 检查第三方依赖的许可证兼容性

## 后续维护

### 日常开发流程
1. 创建功能分支
2. 开发功能
3. 提交代码
4. 创建Pull Request
5. 代码审查
6. 合并到主分支

### 版本管理
- 使用语义化版本号
- 创建Release标签
- 维护更新日志

## 联系支持

如果在设置过程中遇到问题，请：
1. 检查错误信息
2. 查看GitHub文档
3. 联系项目维护者

---

**注意**: 首次上传可能需要输入GitHub用户名和密码（或个人访问令牌）。 