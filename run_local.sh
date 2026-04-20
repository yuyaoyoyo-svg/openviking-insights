#!/bin/bash

# OpenViking 项目洞察 - 本地运行脚本
# 使用方法: ./run_local.sh <你的GitHub Token>

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  OpenViking 项目洞察 - 本地运行脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3，请先安装 Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"

# 检查参数
if [ -z "$1" ]; then
    echo -e "${YELLOW}警告: 未提供 GitHub Token${NC}"
    echo ""
    echo "使用方法:"
    echo "  ./run_local.sh <你的GitHub Token>"
    echo ""
    echo "如何获取 GitHub Token:"
    echo "  1. 访问 https://github.com/settings/tokens"
    echo "  2. 点击 'Generate new token (classic)'"
    echo "  3. 勾选 'public_repo' 权限"
    echo "  4. 生成后复制 token"
    echo ""
    echo "详细指南: docs/GITHUB_TOKEN_GUIDE.md"
    echo ""
    exit 1
fi

GITHUB_TOKEN=$1

# 验证 Token 格式
if [[ ! $GITHUB_TOKEN =~ ^ghp_[a-zA-Z0-9]{36}$ ]]; then
    echo -e "${YELLOW}警告: Token 格式看起来不正确${NC}"
    echo "正常的 GitHub Token 格式: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    echo ""
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 设置工作目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${GREEN}✓ 工作目录: $SCRIPT_DIR${NC}"

# 安装依赖
echo ""
echo -e "${YELLOW}正在检查依赖...${NC}"

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}错误: 未找到 requirements.txt${NC}"
    exit 1
fi

pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${RED}✗ 依赖安装失败${NC}"
    exit 1
fi

# 验证 Token
echo ""
echo -e "${YELLOW}正在验证 GitHub Token...${NC}"

python3 -c "
import requests
import sys

token = '$GITHUB_TOKEN'
headers = {'Authorization': f'Bearer {token}'}

try:
    response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f'✓ Token 验证成功')
        print(f'  用户: {data.get(\"login\")}')
        print(f'  剩余请求: {response.headers.get(\"X-RateLimit-Remaining\", \"N/A\")}')
        sys.exit(0)
    elif response.status_code == 401:
        print('✗ Token 无效或已过期')
        sys.exit(1)
    else:
        print(f'✗ 验证失败: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'✗ 验证出错: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}Token 验证失败，请检查:${NC}"
    echo "  1. Token 是否正确复制"
    echo "  2. Token 是否已过期"
    echo "  3. Token 是否被撤销"
    echo ""
    echo "请重新获取 Token: https://github.com/settings/tokens"
    exit 1
fi

# 运行主程序
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  开始运行数据采集与分析${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

export GITHUB_TOKEN

python3 main.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ✓ 运行成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "数据已保存到:"
    echo "  - data/insights_$(date +%Y-%m-%d).json"
    echo "  - data/calibrated_$(date +%Y-%m-%d).json"
    echo ""
    echo "飞书多维表格:"
    echo "  https://bytedance.larkoffice.com/base/KJknbcXDJaQfjjs8yAvcnNKKnsg"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  ✗ 运行失败${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "请检查错误信息并修复问题"
    echo ""
fi

exit $EXIT_CODE