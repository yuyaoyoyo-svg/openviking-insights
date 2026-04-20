"""
飞书多维表格同步模块
"""

import json
import logging
from datetime import datetime
from typing import Dict, List
import subprocess

logger = logging.getLogger(__name__)


class LarkSync:
    """飞书数据同步器"""

    def __init__(self, base_token: str = None, table_id: str = None):
        self.base_token = base_token or "KJknbcXDJaQfjjs8yAvcnNKKnsg"
        self.table_id = table_id or "tbla5rlIN8S6miy5"

    def sync_project_data(self, metrics: Dict) -> bool:
        """同步单个项目数据到飞书"""
        try:
            # 构建字段映射
            fields = {
                "项目名称": metrics.get("name", ""),
                "项目标识": f"{metrics.get('owner', '')}/{metrics.get('repo', '')}",
                "数据日期": datetime.now().strftime("%Y-%m-%d"),
                "项目分类": "自我" if metrics.get("type") == "self" else "同类对标",
                "Stars": metrics.get("stars", 0),
                "Forks": metrics.get("forks", 0),
                "Open Issues": metrics.get("open_issues", 0),
                "Closed Issues": 0,  # 简化版
                "Open PRs": 0,  # 简化版
                "Closed PRs": 0,  # 简化版
                "Contributors": 0,  # 简化版
                "Watchers": metrics.get("watchers", 0),
                "Size (KB)": metrics.get("size_kb", 0),
                "Recent Commits": 0,  # 简化版
                "社区活力评分": metrics.get("vitality_score", 0),
                "外部影响力评分": metrics.get("influence_score", 0),
                "自我基准对比": "-",  # 简化版
                "同类对标分位数": 0,  # 简化版
                "项目阶段阈值": "-",  # 简化版
                "数据来源": "GitHub API",
            }

            # 构建记录数据
            record = {"fields": fields}

            # 使用 lark-cli 命令行工具插入数据
            cmd = [
                "lark-cli",
                "base",
                "+record-batch-create",
                "--base-token",
                self.base_token,
                "--table-id",
                self.table_id,
                "--records",
                json.dumps({"records": [record]}, ensure_ascii=False),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"  ✓ 已同步: {metrics.get('name')}")
                return True
            else:
                logger.error(f"  ✗ 同步失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"  ✗ 同步异常: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    import os

    logging.basicConfig(level=logging.INFO)

    # 创建测试数据
    test_metrics = {
        "name": "TestProject",
        "owner": "testowner",
        "repo": "testrepo",
        "type": "self",
        "stars": 100,
        "forks": 50,
        "open_issues": 10,
        "watchers": 100,
        "size_kb": 1024,
        "vitality_score": 75.5,
        "influence_score": 80.0,
    }

    # 测试同步
    sync = LarkSync()
    result = sync.sync_project_data(test_metrics)

    if result:
        print("✓ 测试同步成功")
    else:
        print("✗ 测试同步失败")
