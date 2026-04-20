"""
三层校准计算模块
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class ThreeLayerCalibration:
    """三层校准计算器"""

    def __init__(self, all_metrics: List[Dict]):
        self.all_metrics = all_metrics
        self.self_project = None
        self.peer_projects = []

        # 分离自我项目和同类对标项目
        for metric in all_metrics:
            if metric.get("type") == "self":
                self.self_project = metric
            else:
                self.peer_projects.append(metric)

    def calculate_self_benchmark(self) -> Dict:
        """计算自我基准校准（近7天 vs 前7天）"""
        if not self.self_project:
            return {"error": "No self project data found"}

        # 这里简化处理，实际应该读取历史数据对比
        current = {
            "stars": self.self_project.get("stars", 0),
            "forks": self.self_project.get("forks", 0),
            "open_issues": self.self_project.get("open_issues", 0),
        }

        return {
            "type": "自我基准",
            "current_values": current,
            "note": "需历史数据计算周环比",
        }

    def calculate_peer_benchmark(self) -> Dict:
        """计算同类对标校准（分位数/排名）"""
        if not self.peer_projects or not self.self_project:
            return {"error": "Insufficient data for peer benchmark"}

        # 按 stars 排序计算排名
        all_stars = [(p.get("name", ""), p.get("stars", 0)) for p in self.peer_projects]
        all_stars.append(
            (self.self_project.get("name", ""), self.self_project.get("stars", 0))
        )
        all_stars.sort(key=lambda x: x[1], reverse=True)

        # 找到 OpenViking 的排名
        ov_rank = next(
            i for i, (name, _) in enumerate(all_stars, 1) if "OpenViking" in name
        )
        ov_stars = self.self_project.get("stars", 0)

        # 计算百分位
        percentile = (1 - (ov_rank - 1) / len(all_stars)) * 100

        return {
            "type": "同类对标",
            "total_projects": len(all_stars),
            "openviking_rank": ov_rank,
            "openviking_stars": ov_stars,
            "percentile": round(percentile, 1),
            "top_projects": all_stars[:5],
            "assessment": self._get_percentile_assessment(percentile),
        }

    def _get_percentile_assessment(self, percentile: float) -> str:
        """根据百分位给出评估"""
        if percentile >= 90:
            return "优秀（Top 10%）"
        elif percentile >= 75:
            return "良好（Top 25%）"
        elif percentile >= 50:
            return "中等（Top 50%）"
        elif percentile >= 25:
            return "落后（Bottom 50%）"
        else:
            return "需改进（Bottom 25%）"

    def calculate_threshold_calibration(self) -> Dict:
        """计算分类阈值校准（按项目阶段）"""
        if not self.self_project:
            return {"error": "No self project data found"}

        stars = self.self_project.get("stars", 0)
        forks = self.self_project.get("forks", 0)

        # 定义阶段阈值
        if stars < 50:
            stage = "种子期"
            description = "初创阶段，关注核心功能验证"
        elif stars < 500:
            stage = "成长期"
            description = "快速发展，关注用户增长和社区建设"
        elif stars < 5000:
            stage = "成熟期"
            description = "稳定发展，关注生态建设和商业化"
        else:
            stage = "领军期"
            description = "行业领军，关注技术引领和生态治理"

        return {
            "type": "分类阈值",
            "current_stage": stage,
            "stage_description": description,
            "metrics": {"stars": stars, "forks": forks},
            "next_stage_requirements": self._get_next_stage_requirements(stars),
        }

    def _get_next_stage_requirements(self, current_stars: int) -> Dict:
        """获取下一阶段的要求"""
        if current_stars < 50:
            return {
                "next_stage": "成长期",
                "required_stars": 50,
                "current_stars": current_stars,
                "gap": 50 - current_stars,
            }
        elif current_stars < 500:
            return {
                "next_stage": "成熟期",
                "required_stars": 500,
                "current_stars": current_stars,
                "gap": 500 - current_stars,
            }
        elif current_stars < 5000:
            return {
                "next_stage": "领军期",
                "required_stars": 5000,
                "current_stars": current_stars,
                "gap": 5000 - current_stars,
            }
        else:
            return {
                "next_stage": "保持领军地位",
                "current_stars": current_stars,
                "note": "已达到最高阶段，需继续保持领先",
            }

    def calculate_all_calibrations(self) -> Dict:
        """计算所有三层校准"""
        return {
            "calculated_at": datetime.now().isoformat(),
            "projects_analyzed": len(self.all_metrics),
            "self_project": self.self_project.get("name", "")
            if self.self_project
            else None,
            "peer_projects_count": len(self.peer_projects),
            "calibrations": {
                "self_benchmark": self.calculate_self_benchmark(),
                "peer_benchmark": self.calculate_peer_benchmark(),
                "threshold_calibration": self.calculate_threshold_calibration(),
            },
        }


if __name__ == "__main__":
    # 测试代码
    import logging

    logging.basicConfig(level=logging.INFO)

    # 模拟测试数据
    test_metrics = [
        {
            "name": "OpenViking",
            "type": "self",
            "stars": 22321,
            "forks": 1632,
            "open_issues": 161,
        },
        {
            "name": "mem0",
            "type": "peer",
            "stars": 53113,
            "forks": 5000,
            "open_issues": 200,
        },
        {
            "name": "lancedb",
            "type": "peer",
            "stars": 9947,
            "forks": 800,
            "open_issues": 150,
        },
    ]

    # 创建校准器并计算
    calibrator = ThreeLayerCalibration(test_metrics)
    results = calibrator.calculate_all_calibrations()

    print("\\n✓ 校准计算完成！")
    print(f"  - 分析项目: {results['projects_analyzed']} 个")
    print(f"  - 自我项目: {results['self_project']}")
    print(f"  - 对标项目: {results['peer_projects_count']} 个")

    # 显示关键结果
    peer = results["calibrations"]["peer_benchmark"]
    if "percentile" in peer:
        print(f"\\n  📊 OpenViking 排名: 第 {peer['openviking_rank']} 名")
        print(f"  📈 百分位数: {peer['percentile']}%")
        print(f"  🏆 评估: {peer['assessment']}")
