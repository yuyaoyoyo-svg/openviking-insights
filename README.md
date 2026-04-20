# OpenViking 项目洞察自动化系统

自动化采集 GitHub 开源项目数据，进行三层校准分析（自我基准、同类对标、分类阈值），并同步到飞书多维表格。

## 📊 今日数据（2026-04-15）

### OpenViking 核心指标
- ⭐ **Stars**: 22,321
- 🍴 **Forks**: 1,632
- 📋 **Open Issues**: 161
- 👁️ **Watchers**: 22,321
- 💪 **社区活力评分**: 100/100
- 🌍 **外部影响力评分**: 100/100

### 同类对标排名（12个项目）
| 排名 | 项目 | Stars | 状态 |
|------|------|-------|------|
| 🥇 1 | openclaw | 357,857 | 竞品 |
| 🥈 2 | hermes-agent | 88,014 | 竞品 |
| 🥉 3 | deer-flow | 61,699 | 竞品 |
| 4 | mem0 | 53,113 | 竞品 |
| **5** | **OpenViking** | **22,321** | **✓ 你的项目** |

### 关键洞察
- 🏆 **项目阶段**: 领军期（Stars > 5000）
- 📊 **百分位数**: 66.7%（超过66.7%的竞品）
- 📈 **排名**: 第 5 名 / 12 个项目
- 🎯 **评估**: 中等水平（Top 50%）

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- GitHub Token (Fine-grained)
- 飞书应用凭证

### 2. 运行采集
```bash
cd /Users/bytedance/openviking_insights
export GITHUB_TOKEN="your_token"
python3 main.py
```

### 3. 查看数据
- **飞书表格**: https://bytedance.larkoffice.com/base/KJknbcXDJaQfjjs8yAvcnNKKnsg
- **本地数据**: `data/insights_YYYY-MM-DD.json`

---

## 📁 项目结构

```
openviking_insights/
├── 📁 config/
│   └── projects.json              # 14个项目配置
├── 📁 data/                       # 数据存储
│   ├── insights_2026-04-15.json   # 今日采集数据
│   └── calibrated_2026-04-15.json # 校准分析结果
├── 📁 docs/                       # 文档
│   ├── GITHUB_TOKEN_GUIDE.md     # Token获取指南
│   └── QUICK_START.md            # 快速手册
├── 📁 src/                        # 核心模块
│   ├── github_collector.py       # GitHub数据采集
│   ├── calibration.py            # 三层校准计算
│   ├── lark_sync.py              # 飞书同步
│   └── sync_to_lark_api.py       # API同步
├── 📁 .github/workflows/          # 自动化部署
│   └── daily-insights.yml        # 每日定时任务
├── main.py                        # 主程序
├── run_local.sh                   # 运行脚本
└── README.md                      # 本文件
```

---

## 📊 三层校准说明

### 1. 自我基准（Self Benchmark）
- 对比：近7天 vs 前7天
- 输出：增长率 + 趋势分析
- 用途：了解项目自身成长速度

### 2. 同类对标（Peer Benchmark）
- 对比：与13个竞品项目
- 输出：分位数排名（0-100%）
- 用途：了解竞争地位

### 3. 分类阈值（Category Threshold）
- 评估：项目发展阶段
- 输出：种子期/成长期/成熟期/领军期
- 用途：了解项目成熟度

---

## 🔧 常用命令

```bash
# 运行完整采集
./run_local.sh ghp_your_token

# 手动运行
export GITHUB_TOKEN="your_token"
python3 main.py

# 仅同步到飞书
python3 src/sync_to_lark_api.py

# 检查飞书状态
lark-cli auth status

# 查看数据
ls -lh data/
```

---

## ⚠️ 注意事项

### GitHub Token
- **使用 Fine-grained Personal Access Token**
- 需要 `contents:read`, `issues:read`, `metadata:read` 权限
- 添加 `volcengine/OpenViking` 仓库访问权限

### 飞书配置
- Base Token: `KJknbcXDJaQfjjs8yAvcnNKKnsg`
- Table ID: `tbla5rlIN8S6miy5`
- 如需访问，联系管理员添加权限

---

## 📞 支持

如有问题：
1. 查看 `docs/QUICK_START.md` 故障排除
2. 检查日志输出
3. 联系项目维护者

---

**🎉 系统已完全就绪！开始享受自动化数据洞察吧！** 🚀

---

*最后更新: 2026-04-15*  
*版本: v1.0.0*
