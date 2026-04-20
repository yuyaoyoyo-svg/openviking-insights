#!/usr/bin/env python3
"""
OpenViking 项目洞察 - 主程序
整合数据采集、校准计算和飞书同步
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def load_projects():
    """加载项目配置"""
    config_path = Path(__file__).parent / "config" / "projects.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_github_data(github_token):
    """采集 GitHub 数据"""
    from github_collector import GitHubCollector

    config = load_projects()
    collector = GitHubCollector(github_token)

    all_metrics = []

    for project in config["projects"]:
        try:
            logger.info(f"正在采集: {project['owner']}/{project['repo']}")
            metrics = collector.collect_basic_metrics(project["owner"], project["repo"])
            if metrics:
                metrics["type"] = project["type"]
                all_metrics.append(metrics)
                logger.info(f"  ✓ Stars: {metrics.get('stars', 0)}")
        except Exception as e:
            logger.error(f"  ✗ 采集失败: {e}")

    return all_metrics


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("OpenViking 项目洞察 - 数据采集与校准系统")
    logger.info("=" * 60)

    # 获取 GitHub Token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.error("错误: 未设置 GITHUB_TOKEN 环境变量")
        logger.info("请设置: export GITHUB_TOKEN='your_token'")
        return 1

    try:
        # 采集 GitHub 数据
        logger.info("\\n[步骤 1/2] 采集 GitHub 数据...")
        metrics = collect_github_data(github_token)
        logger.info(f"✓ 成功采集 {len(metrics)} 个项目的数据")

        # 保存数据
        logger.info("\\n[步骤 2/2] 保存数据...")
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        insights_file = data_dir / f"insights_{date_str}.json"

        with open(insights_file, "w", encoding="utf-8") as f:
            json.dump(
                {"collected_at": datetime.now().isoformat(), "projects": metrics},
                f,
                ensure_ascii=False,
                indent=2,
            )

        logger.info(f"✓ 数据已保存: {insights_file}")

        # 完成
        logger.info("\\n" + "=" * 60)
        logger.info("✓ 所有任务完成！")
        logger.info("=" * 60)
        logger.info(f"📊 采集项目: {len(metrics)} 个")
        logger.info(f"📁 数据文件: {insights_file}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"\\n✗ 运行出错: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
