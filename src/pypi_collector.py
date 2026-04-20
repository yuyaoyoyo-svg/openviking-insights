"""
PyPI 数据采集模块
负责采集包的下载量、引用次数等指标
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PyPICollector:
    """PyPI 数据采集器"""

    BASE_URL = "https://pypi.org/pypi"
    STATS_URL = "https://pypistats.org/api"
    LIBRARIES_IO_URL = "https://libraries.io/api"

    def __init__(self, libraries_io_api_key: Optional[str] = None):
        self.libraries_io_key = libraries_io_api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": "OpenViking-Insights/1.0"}
        )

    def get_package_info(self, package_name: str) -> Dict:
        """获取 PyPI 包基本信息"""
        url = f"{self.BASE_URL}/{package_name}/json"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get package info for {package_name}: {e}")
            return {}

    def get_download_stats(self, package_name: str, period: str = "month") -> Dict:
        """获取下载统计数据"""
        stats = {"recent": 0, "last_month": 0, "last_week": 0, "last_day": 0}

        try:
            import pypistats

            # 获取近30天数据
            recent = pypistats.overall(package_name, total=True, format="json")
            if recent and len(recent) > 0:
                stats["recent"] = recent[0].get("downloads", 0)

            # 获取最近30天详细数据
            last_month = pypistats.overall(
                package_name, period="month", total=True, format="json"
            )
            if last_month:
                stats["last_month"] = sum(
                    item.get("downloads", 0) for item in last_month
                )

            # 获取最近7天数据
            last_week = pypistats.overall(
                package_name, period="week", total=True, format="json"
            )
            if last_week:
                stats["last_week"] = sum(item.get("downloads", 0) for item in last_week)

            # 获取最近1天数据
            last_day = pypistats.overall(
                package_name, period="day", total=True, format="json"
            )
            if last_day:
                stats["last_day"] = sum(item.get("downloads", 0) for item in last_day)

        except ImportError:
            logger.warning("pypistats package not installed, using alternative method")
            stats = self._get_downloads_from_libraries_io(package_name)

        return stats

    def _get_downloads_from_libraries_io(self, package_name: str) -> Dict:
        """从 libraries.io 获取下载数据"""
        if not self.libraries_io_key:
            logger.warning("Libraries.io API key not provided")
            return {}

        url = f"{self.LIBRARIES_IO_URL}/pypi/{package_name}"
        params = {"api_key": self.libraries_io_key}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                "total_downloads": data.get("dependents_repositories_count", 0),
                "dependent_repos": data.get("dependents_repositories_count", 0),
                "dependent_packages": data.get("dependents_count", 0),
                "stars": data.get("stars", 0),
                "forks": data.get("forks", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get data from libraries.io: {e}")
            return {}

    def get_package_dependencies(self, package_name: str) -> Dict:
        """获取包依赖关系"""
        info = self.get_package_info(package_name)

        if not info:
            return {}

        requires_dist = info.get("info", {}).get("requires_dist", [])

        # 解析依赖
        dependencies = []
        if requires_dist:
            for dep in requires_dist:
                if dep:
                    # 简单解析依赖名称
                    dep_name = dep.split("[")[0].split(";")[0].strip()
                    if dep_name:
                        dependencies.append(dep_name)

        return {
            "total_dependencies": len(dependencies),
            "dependencies": dependencies[:50],  # 限制数量
        }

    def get_reverse_dependencies(self, package_name: str) -> Dict:
        """获取反向依赖（哪些包依赖了这个包）"""
        if not self.libraries_io_key:
            logger.warning("Libraries.io API key required for reverse dependencies")
            return {}

        url = f"{self.LIBRARIES_IO_URL}/pypi/{package_name}/dependents"
        params = {"api_key": self.libraries_io_key}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                "dependent_packages": data.get("dependents", []),
                "dependent_repositories": data.get("dependent_repos", []),
                "total_dependent_packages": len(data.get("dependents", [])),
                "total_dependent_repos": len(data.get("dependent_repos", [])),
            }
        except Exception as e:
            logger.error(f"Failed to get reverse dependencies: {e}")
            return {}

    def collect_all_metrics(self, package_name: str) -> Dict:
        """采集所有 PyPI 指标"""
        logger.info(f"Collecting PyPI metrics for {package_name}")

        info = self.get_package_info(package_name)
        downloads = self.get_download_stats(package_name)
        deps = self.get_package_dependencies(package_name)

        # 尝试获取反向依赖
        try:
            reverse_deps = self.get_reverse_dependencies(package_name)
        except:
            reverse_deps = {}

        return {
            "package_name": package_name,
            "collected_at": datetime.now().isoformat(),
            "version": info.get("info", {}).get("version", ""),
            "downloads": downloads,
            "dependencies": deps,
            "reverse_dependencies": reverse_deps,
            "project_urls": info.get("info", {}).get("project_urls", {}),
            "classifiers": info.get("info", {}).get("classifiers", []),
            "requires_python": info.get("info", {}).get("requires_python", ""),
        }


def get_github_repo_from_pypi(package_name: str) -> Optional[str]:
    """从 PyPI 信息中提取 GitHub 仓库地址"""
    collector = PyPICollector()
    info = collector.get_package_info(package_name)

    urls = info.get("info", {}).get("project_urls", {})

    # 常见 URL 字段
    github_urls = []
    for key in ["Source", "Source Code", "Homepage", "Repository", "Code"]:
        if key in urls:
            url = urls[key]
            if "github.com" in url:
                github_urls.append(url)

    # 解析 GitHub URL
    for url in github_urls:
        if "github.com" in url:
            # 提取 owner/repo
            parts = url.split("github.com/")[-1].split("/")
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1].replace(".git", "").split("/")[0]
                return f"{owner}/{repo}"

    return None


if __name__ == "__main__":
    import os

    logging.basicConfig(level=logging.INFO)

    # 测试
    collector = PyPICollector(libraries_io_api_key=os.getenv("LIBRARIES_IO_API_KEY"))

    # 尝试获取 openviking 的信息（如果有的话）
    metrics = collector.collect_all_metrics("openviking")
    import json

    print(json.dumps(metrics, indent=2, ensure_ascii=False))
