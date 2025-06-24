#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本功能：一键自动同步本地所有未被.gitignore忽略的变更（新增、修改、删除）到GitHub远程仓库。
使用方法：直接运行，无需参数。
作者：AI自动生成
"""
import subprocess
import sys
import datetime


def run_cmd(cmd, check=True):
    """
    执行shell命令并返回输出，异常时可选择抛出或仅打印。
    :param cmd: 命令字符串或列表
    :param check: 是否遇到错误时抛出异常
    :return: 命令输出字符串
    """
    try:
        result = subprocess.run(cmd, shell=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {cmd}\n错误信息: {e.stderr}")
        if check:
            sys.exit(1)
        return None


def has_changes():
    """
    检查当前git仓库是否有未提交的变更（不含.gitignore忽略内容）。
    :return: True有变更，False无变更
    """
    status = run_cmd('git status --porcelain', check=False)
    return bool(status.strip())


def main():
    print("\n========== Git 一键同步脚本 ==========")
    # 1. 检查是否有变更
    if not has_changes():
        print("没有检测到任何本地变更，无需同步。\n")
        return

    # 2. 添加所有变更（已跟踪和新文件，自动忽略.gitignore内容）
    print("添加所有变更文件到暂存区...")
    run_cmd('git add -u')
    run_cmd('git add .')

    # 3. 生成带时间戳的中文提交说明
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_msg = f"自动同步：{now}"
    print(f"提交说明：{commit_msg}")

    # 4. 提交
    run_cmd(f'git commit -m "{commit_msg}"', check=False)

    # 5. 推送到远程
    print("推送到GitHub远程仓库...")
    run_cmd('git push', check=False)
    print("同步完成！\n")


if __name__ == '__main__':
    main() 