# 获取 GitHub Token 指南

## 为什么需要 GitHub Token?

GitHub API 有速率限制:
- 未认证: 每小时 60 次请求
- 已认证: 每小时 5,000 次请求

本项目需要采集多个项目的数据，必须使用认证 Token。

## 如何创建 GitHub Token

### 步骤 1: 登录 GitHub

访问 https://github.com 并登录你的账号

### 步骤 2: 进入设置

点击右上角头像 → Settings

### 步骤 3: 进入 Developer Settings

在左侧菜单底部点击 "Developer settings"

### 步骤 4: 创建 Personal Access Token

1. 点击 "Personal access tokens" → "Tokens (classic)"
2. 点击 "Generate new token (classic)"
3. 输入 Token 描述，例如 "OpenViking Insights"
4. 选择过期时间（建议选择 "No expiration" 或较长的时间）
5. 勾选权限:
   - ✅ `public_repo` (访问公开仓库)
   - ✅ `read:org` (读取组织信息，可选)
6. 点击 "Generate token"

### 步骤 5: 保存 Token

⚠️ **重要**: 页面只会显示一次 Token，务必立即复制并保存！

## 在项目中使用 Token

### 方法 1: 环境变量（推荐）

```bash
# 临时设置（当前终端会话）
export GITHUB_TOKEN="ghp_xxxxxx"

# 验证是否设置成功
echo $GITHUB_TOKEN

# 运行采集
python main.py
```

### 方法 2: 写入 .env 文件

在项目根目录创建 `.env` 文件:

```
GITHUB_TOKEN=ghp_xxxxxx
```

然后安装 python-dotenv:

```bash
pip install python-dotenv
```

### 方法 3: GitHub Actions Secrets

如果是 GitHub Actions 自动化运行:

1. 进入 GitHub 仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. Name: `GITHUB_TOKEN`
4. Value: 你的 Token
5. 点击 "Add secret"

## 验证 Token 是否有效

### 方法 1: 使用 curl

```bash
curl -H "Authorization: Bearer ghp_xxxxxx" \
  https://api.github.com/user
```

如果返回你的用户信息，说明 Token 有效。

### 方法 2: 使用 Python

```python
import requests

token = "ghp_xxxxxx"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "https://api.github.com/repos/volcengine/OpenViking",
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Stars: {data['stargazers_count']}")
else:
    print(f"Error: {response.text}")
```

## 常见问题

### Q: Token 过期了怎么办？

A: 重新按照上述步骤创建新的 Token，然后更新到环境变量或 Secrets 中。

### Q: 提示 "Bad credentials" 怎么办？

A: 说明 Token 无效或已过期，请重新创建 Token。

### Q: 如何撤销 Token？

A: 进入 GitHub Settings → Developer settings → Personal access tokens，找到对应的 Token，点击 "Delete"。

### Q: Token 可以共享吗？

A: 不建议共享 Token。每个用户应该创建自己的 Token，这样可以追踪使用情况并在必要时单独撤销。

## 安全提示

⚠️ **切勿将 Token 提交到 Git 仓库！**

如果你不小心提交了 Token:

1. 立即在 GitHub 上撤销该 Token
2. 创建新的 Token
3. 如果 Token 已推送到公开仓库，建议监控是否有异常使用

建议使用 `.gitignore` 忽略包含 Token 的文件:

```gitignore
.env
*.token
config/local*
```

---

**现在你已经知道如何获取和使用 GitHub Token 了，开始采集数据吧！** 🚀
