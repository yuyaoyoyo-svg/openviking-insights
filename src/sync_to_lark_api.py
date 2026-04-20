#!/usr/bin/env python3
"""
飞书表格数据同步脚本 - 修复版
"""

import json
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 飞书配置
LARK_APP_ID = "cli_a93916aeff3adcc4"
LARK_APP_SECRET = "x9KbzqiiNNqRfsPeX18G4gHtfyUR1YSR"
BASE_TOKEN = "KJknbcXDJaQfjjs8yAvcnNKKnsg"
TABLE_ID = "tbla5rlIN8S6miy5"


def get_tenant_access_token():
    """获取租户访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": LARK_APP_ID, "app_secret": LARK_APP_SECRET}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                return result.get("tenant_access_token")
            else:
                logger.error(f"获取token失败: {result}")
                return None
        else:
            logger.error(f"请求失败: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"获取token异常: {e}")
        return None


def sync_to_lark_bitable(records):
    """同步数据到飞书多维表格"""
    token = get_tenant_access_token()
    if not token:
        logger.error("无法获取访问令牌")
        return False

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/records/batch_create"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 准备批量创建的数据
    batch_records = []
    for record in records:
        batch_records.append({"fields": record["fields"]})

    data = {"records": batch_records}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                logger.info(f"✓ 成功写入 {len(records)} 条记录")
                return True
            else:
                logger.error(f"写入失败: {result}")
                return False
        else:
            logger.error(f"请求失败: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        logger.error(f"同步异常: {e}")
        return False


def main():
    # 读取采集的数据
    with open("data/insights_2026-04-15.json", "r") as f:
        data = json.load(f)

    logger.info(f"准备同步 {len(data['projects'])} 个项目到飞书...")

    # 准备记录
    records = []
    for project in data["projects"]:
        record = {
            "fields": {
                "项目名称": project.get("name", ""),
                "项目标识": f"{project.get('owner', '')}/{project.get('repo', '')}",
                "数据日期": datetime.now().strftime("%Y-%m-%d"),
                "项目分类": "自我" if project.get("type") == "self" else "同类对标",
                "Stars": project.get("stars", 0),
                "Forks": project.get("forks", 0),
                "Open Issues": project.get("open_issues", 0),
                "Watchers": project.get("watchers", 0),
                "社区活力评分": project.get("vitality_score", 0),
                "外部影响力评分": project.get("influence_score", 0),
            }
        }
        records.append(record)

    # 批量写入
    success = sync_to_lark_bitable(records)

    if success:
        logger.info("✓ 飞书同步完成！")
        logger.info(f"📊 查看数据: https://bytedance.larkoffice.com/base/{BASE_TOKEN}")
    else:
        logger.error("✗ 飞书同步失败")

    return success


if __name__ == "__main__":
    main()
