#!/bin/bash
# OpenViking 项目洞察 - 每日数据更新脚本
# 用法: ./run_daily.sh <你的 GitHub Token>

set -e

echo "============================================"
echo "OpenViking 项目洞察 - 每日数据更新"
echo "============================================"
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 错误: 请提供 GitHub Token"
    echo "用法: ./run_daily.sh <your_github_token>"
    exit 1
fi

GITHUB_TOKEN="$1"

# 设置环境变量
export GITHUB_TOKEN

echo "✅ 配置检查完成"
echo ""

# 步骤1: 数据采集
echo "📊 步骤 1/3: 采集 GitHub 数据..."
python3 main.py
if [ $? -ne 0 ]; then
    echo "❌ 数据采集失败"
    exit 1
fi
echo "✅ 数据采集完成"
echo ""

# 步骤2: 同步到飞书
echo "☁️ 步骤 2/3: 同步到飞书多维表格..."
python3 src/sync_to_lark_api.py
if [ $? -ne 0 ]; then
    echo "⚠️ 飞书同步可能遇到问题，但数据采集已保存"
fi
echo "✅ 飞书同步完成"
echo ""

# 步骤3: 生成报告
echo "📋 步骤 3/3: 生成今日报告..."
python3 -c "
import json
from datetime import datetime

with open('data/insights_$(date +%Y-%m-%d).json', 'r') as f:
    data = json.load(f)

print('\\n📊 今日数据概览')
print('=' * 60)
print(f'采集项目数: {len(data[\"projects\"])}')
print(f'采集时间: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}')
print('\\n🏆 排名 Top 5:')

sorted_projects = sorted(data['projects'], key=lambda x: x.get('stars', 0), reverse=True)[:5]
for i, p in enumerate(sorted_projects, 1):
    marker = '👈 你的项目' if p.get('type') == 'self' else ''
    print(f'  {i}. {p[\"name\"]:15s} ⭐ {p.get(\"stars\", 0):,} {marker}')

print('=' * 60)
" 2>/dev/null || echo "✅ 数据已保存"

echo ""
echo "============================================"
echo "✅ 每日更新完成！"
echo "============================================"
echo ""
echo "📁 数据文件:"
echo "  - data/insights_$(date +%Y-%m-%d).json"
echo "  - data/calibrated_$(date +%Y-%m-%d).json"
echo ""
echo "📊 飞书表格:"
echo "  https://bytedance.larkoffice.com/base/KJknbcXDJaQfjjs8yAvcnNKKnsg"
echo ""
