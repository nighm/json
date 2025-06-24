from src.utils.parallel.decorators import parallel
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DDD重构迁移脚本
用于自动化代码迁移过程，确保迁移过程可追踪和回滚
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("migration.log"), logging.StreamHandler()],
)


class DDDMigrator:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.src_dir = self.root_dir / "src"
        self.backup_dir = (
            self.root_dir / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        )

    def create_backup(self):
        """创建备份"""
        logging.info("创建备份...")
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        shutil.copytree(self.src_dir, self.backup_dir / "src")
        logging.info(f"备份已创建: {self.backup_dir}")

    def migrate_core_to_domains(self):
        """迁移core目录到domains"""
        logging.info("开始迁移core目录到domains...")
        core_dir = self.src_dir / "core"
        domains_dir = self.src_dir / "domains" / "watchdog"

        # 迁移runner
        if (core_dir / "runner").exists():
            target_dir = domains_dir / "services"
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(
                str(core_dir / "runner" / "api_runner.py"),
                str(target_dir / "api_runner.py"),
            )

        # 迁移manager
        if (core_dir / "manager").exists():
            target_dir = domains_dir / "aggregates"
            target_dir.mkdir(parents=True, exist_ok=True)
            for file in (core_dir / "manager").glob("*.py"):
                shutil.move(str(file), str(target_dir / file.name))

        # 迁移executor
        if (core_dir / "executor").exists():
            target_dir = domains_dir / "services"
            target_dir.mkdir(parents=True, exist_ok=True)
            for file in (core_dir / "executor").glob("*.py"):
                shutil.move(str(file), str(target_dir / file.name))

    def migrate_watchdog_to_domains(self):
        """迁移watchdog目录到domains"""
        logging.info("开始迁移watchdog目录到domains...")
        watchdog_dir = self.src_dir / "watchdog"
        domains_dir = self.src_dir / "domains" / "watchdog"

        # 迁移monitor
        if (watchdog_dir / "monitor").exists():
            target_dir = domains_dir / "entities"
            target_dir.mkdir(parents=True, exist_ok=True)
            for file in (watchdog_dir / "monitor").glob("*.py"):
                shutil.move(str(file), str(target_dir / file.name))

        # 迁移alert
        if (watchdog_dir / "alert").exists():
            target_dir = domains_dir / "entities"
            target_dir.mkdir(parents=True, exist_ok=True)
            for file in (watchdog_dir / "alert").glob("*.py"):
                shutil.move(str(file), str(target_dir / file.name))

        # 迁移report
        if (watchdog_dir / "report").exists():
            target_dir = domains_dir / "value_objects"
            target_dir.mkdir(parents=True, exist_ok=True)
            for file in (watchdog_dir / "report").glob("*.py"):
                shutil.move(str(file), str(target_dir / file.name))

    def cleanup(self):
        """清理空目录"""
        logging.info("清理空目录...")
        for dir_path in [self.src_dir / "core", self.src_dir / "watchdog"]:
            if dir_path.exists():
                shutil.rmtree(dir_path)

    def run(self):
        """执行迁移"""
        try:
            self.create_backup()
            self.migrate_core_to_domains()
            self.migrate_watchdog_to_domains()
            self.cleanup()
            logging.info("迁移完成！")
        except Exception as e:
            logging.error(f"迁移过程中出现错误: {str(e)}")
            logging.info("正在回滚...")
            if self.backup_dir.exists():
                shutil.rmtree(self.src_dir)
                shutil.copytree(self.backup_dir / "src", self.src_dir)
            raise


if __name__ == "__main__":
    migrator = DDDMigrator()
    migrator.run()
