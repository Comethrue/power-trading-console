# 电力交易AI平台 - 部署指南 (GitHub Pages + Render)

本文档说明如何将电力交易AI平台部署到互联网，采用 **GitHub Pages（前端）+ Render（后端）** 的免费方案。

---

## 部署架构

```
┌──────────────────────────────────────────────┐
│                   用户浏览器                   │
└──────────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                          ▼
┌─────────────────────┐   ┌──────────────────────────┐
│   GitHub Pages       │   │   Render Cloud            │
│  (前端 Vue 3)         │   │  (后端 FastAPI)           │
│                      │   │                           │
│ 静态托管，无限流量     │   │ 免费 750小时/月            │
│ https://xxx.github.io│   │ https://xxx.onrender.com  │
└─────────────────────┘   └──────────────────────────┘
          │                          ▲
          │    HTTPS API 请求         │
          └──────────────────────────┘
```

---

## 部署前准备

### 1.1 准备 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 **+** → **New repository**
3. 填写信息：
   - **Repository name**: `power-trading-console`
   - **Description**: 电力交易AI平台
   - **Private/Public**: 根据需要选择（公开仓库才能用 GitHub Pages 免费托管）
4. 点击 **Create repository**

### 1.2 生成 JWT 密钥

在后端部署时需要配置 JWT 密钥，先准备好：

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制生成的密钥备用（形如：`Xk9m2...`）

---

## 第一部分：后端部署到 Render

### 2.1 注册 Render 账号

1. 访问 [https://render.com](https://render.com)
2. 点击 **Sign Up** → 使用 **GitHub 账号登录**（推荐）
3. 完成邮箱验证

### 2.2 创建 Web Service

1. 登录后，点击 **Dashboard** → **New +** → **Web Service**

2. 连接到 GitHub 仓库：
   
   - 选择 **Connect a GitHub repository**
   - 授权 GitHub 访问
   - 选择仓库 `power-trading-console`

3. 配置 Web Service：

| 配置项                | 值                                                  | 说明                 |
| ------------------ | -------------------------------------------------- | ------------------ |
| **Name**           | `power-trading-api`                                | 服务名称               |
| **Region**         | Singapore                                          | 离中国较近              |
| **Language**       | Python                                             |                    |
| **Branch**         | `main`                                             |                    |
| **Root Directory** | `backend`                                          | 后端代码目录             |
| **Build Command**  | `pip install -r requirements.txt`                  |                    |
| **Start Command**  | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | 使用 Render 提供的 PORT |
| **Plan**           | `Free`                                             | 免费计划               |

4. 点击 **Create Web Service** 开始部署

### 2.3 配置环境变量

在 Render Dashboard 中，切换到 **Environment** 标签页，添加以下变量：

| 变量名                       | 值            | 说明                   |
| ------------------------- | ------------ | -------------------- |
| `APP_ENV`                 | `production` | 生产环境                 |
| `APP_HOST`                | `0.0.0.0`    | 监听所有接口               |
| `APP_PORT`                | `10000`      | 由 Render 自动提供        |
| `APP_AUTH_JWT_SECRET`     | `你刚才生成的密钥`   | **重要！JWT 签名密钥**      |
| `APP_AUTH_ENABLED`        | `true`       | 启用认证                 |
| `APP_MOUNT_FRONTEND_DIST` | `false`      | **前后端分离，必须设为 false** |

### 2.4 等待部署完成

1. 查看 **Logs** 标签页的部署日志
2. 状态变为 **Live** 后，服务部署成功
3. 记录后端 URL，例如：`https://power-trading-api.onrender.com`

### 2.5 测试后端 API

访问以下地址确认后端正常运行：

- API 文档：`https://power-trading-api.onrender.com/docs`
- 健康检查：`https://power-trading-api.onrender.com/api/v1/health`

---

## 第二部分：前端部署到 GitHub Pages

### 3.1 推送代码到 GitHub

在后端部署完成后，进行前端部署。首先初始化 Git 并推送代码：

```powershell
# 进入项目目录
cd "C:\Users\a\Desktop\program\My Program"

# 初始化 Git 仓库
git init

# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/power-trading-console.git

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: 电力交易AI平台"

# 推送代码到 GitHub
git branch -M main
git push -u origin main
```

### 3.2 配置仓库变量

> **重要**：GitHub Pages 部署需要先推送代码触发 Actions 运行，才能看到 GitHub Pages 设置选项。

1. 进入 GitHub 仓库 → **Settings** → **Vars and secrets** → **Actions**

2. 添加以下仓库变量（点击 **Variables** → **New repository variable**）：

| 变量名                 | 值                                        | 说明                   |
| ------------------- | ---------------------------------------- | -------------------- |
| `FRONTEND_BASE_URL` | `/power-trading-console/`                | 仓库路径（带前后斜杠）          |
| `API_BASE_URL`      | `https://power-trading-api.onrender.com` | **你实际的 Render 后端地址** |

### 3.3 启用 GitHub Pages

1. 进入仓库 → **Settings** → **Pages**
2. 配置：
   - **Source**: Deploy from a branch
   - **Branch**: 选择 `gh-pages`（如果没有，先推送代码触发 Actions 后再回来）
   - **Folder**: / (root)
3. 点击 **Save**

### 3.4 等待前端部署

1. 进入仓库 → **Actions** 查看部署状态
2. 看到绿色勾选表示部署成功
3. 前端地址：`https://YOUR_USERNAME.github.io/power-trading-console/`

---

## 第三部分：配置前后端连接

### 4.1 修改后端 CORS 配置

Render 后端默认需要允许 GitHub Pages 域名访问。进入 Render Dashboard：

1. 点击你的 Web Service → **Environment**
2. 添加环境变量：

| 变量名                | 值                                 |
| ------------------ | --------------------------------- |
| `APP_CORS_ORIGINS` | `https://YOUR_USERNAME.github.io` |

> 如果你有自定义域名，添加你的域名；如果本地开发测试，添加 `http://localhost:5173`

### 4.2 验证连接

1. 打开前端页面：`https://YOUR_USERNAME.github.io/power-trading-console/`
2. 尝试登录（使用测试账号）
3. 如果登录成功并能获取数据，说明前后端连接正常

---

## 第四部分：测试账号

部署完成后可使用以下测试账号登录：

| 用户名      | 密码       | 角色  |
| -------- | -------- | --- |
| admin    | admin123 | 管理员 |
| user1001 | pass1001 | 交易员 |
| user1002 | pass1002 | 交易员 |

---

## 常见问题排查

### 问题：登录后显示"无法连接后端"

**解决方法**：

1. 检查浏览器 F12 开发者工具 → Network 标签
2. 确认前端请求的后端地址是否正确
3. 检查 GitHub 仓库中的 `API_BASE_URL` 变量是否设置为你实际的 Render 地址
4. 确认后端服务状态是 **Live**（非休眠状态）

### 问题：登录后 CORS 错误

**解决方法**：

1. 确认后端环境变量 `APP_CORS_ORIGINS` 包含你的 GitHub Pages 域名
2. 在 Render Dashboard 重启后端服务

### 问题：GitHub Pages 页面 404

**解决方法**：

1. 确认 `FRONTEND_BASE_URL` 与仓库名完全一致（带前后斜杠）
2. 确认 GitHub Pages 已正确启用（Settings → Pages → Source 设为 GitHub Actions）
3. 进入 Actions 页面查看是否有失败的部署任务

### 问题：后端响应慢

**这是正常的**：Render 免费版有冷启动延迟（30秒左右），首次访问后服务会保持活跃一段时间。

---

## 更新部署

### 更新前端

只需推送到 GitHub，Actions 会自动构建部署：

```powershell
git add .
git commit -m "更新说明"
git push
```

### 更新后端

1. 方法一：Render 会自动检测 GitHub 推送并重新部署
2. 方法二：在 Render Dashboard 手动点击 **Manual Deploy** → **Deploy latest commit**

---

## 成本总结

| 项目     | 平台           | 费用     | 备注      |
| ------ | ------------ | ------ | ------- |
| 前端托管   | GitHub Pages | 免费     | 无限流量    |
| 后端服务   | Render       | 免费     | 750小时/月 |
| **合计** |              | **免费** |         |

---

## 下一步：自定义域名（可选）

### GitHub Pages 自定义域名

1. 购买域名（阿里云、腾讯云等）
2. 在 GitHub 仓库 **Settings** → **Pages** 中：
   - 填入你的域名
   - 添加 DNS 记录：
     - CNAME：`YOUR_USERNAME.github.io`

### 后端自定义域名

Render 免费版不支持自定义域名，需要升级到 Pro 计划。

---

技术支持：如果部署遇到问题，请检查 GitHub Actions 日志、Render 部署日志、浏览器开发者工具控制台。
