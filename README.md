# 电力交易AI平台（MVP）- 完善版

## 项目概述

面向市场主体（发电企业、售电公司、用户侧聚合商、储能运营方）的电力交易与风险管理平台，支持中长期与现货交易场景下的交易作业、风险管理、结算对账与合同台账管理。

---

## 🚀 快速启动

### 一键启动（前后端完整启动）

PowerShell 中执行：

```powershell
.\start-all.ps1
```

此脚本会依次：
1. 自动安装前端依赖（如果未安装）
2. 如需要会执行 `npm run build`（供后端托管 `/console`，避免只启动后端时出现 `GET /src/main.js` 404）
3. 导入示例市场价格数据（CSV）
4. 启动后端 FastAPI 服务（http://0.0.0.0:8000）
5. **自动插入演示数据**（合同、申报、结算任务、审计日志）
6. 启动前端 Vue 3 开发服务器（http://localhost:5173/console/）

> **同时按 Ctrl+C 可停止所有服务**

### 单独启动后端

```powershell
.\start-backend.ps1
```

- 后端地址：http://127.0.0.1:8000
- 控制台（构建产物，由后端托管）：http://127.0.0.1:8000/console/（首次可在 `frontend` 目录执行 `npm run build`，或直接使用 `backend\start.ps1` 会自动构建）
- API 文档：http://localhost:8000/docs

### 单独启动前端

```powershell
cd frontend
npm install        # 首次运行需安装依赖
npm run dev       # 启动后访问 http://localhost:5173/console/
```

---

## 📁 目录结构

```
.
├── backend/                      # 后端服务（FastAPI + SQLite）
│   ├── app/
│   │   ├── api/endpoints/        # API端点（10个模块）
│   │   ├── core/                 # 核心配置与中间件
│   │   ├── db/                   # 数据库连接与迁移
│   │   ├── schemas/              # Pydantic数据模型
│   │   └── services/             # 业务逻辑层
│   ├── db/migrations/            # SQL迁移脚本
│   ├── rules/provinces/          # 省份规则配置（Rule-as-Code）
│   ├── tests/                    # 测试用例
│   └── docs/                     # API文档
│
├── frontend/                     # 前端控制台（Vue 3 + Vite + Tailwind CSS）
│   ├── src/
│   │   ├── components/
│   │   │   ├── background/       # 电力特效背景（Canvas动画）
│   │   │   └── layout/           # 布局组件（侧边栏、顶部栏）
│   │   ├── views/                # 10个页面视图
│   │   ├── stores/               # Pinia 状态管理
│   │   ├── utils/                # API请求、数据格式化工具
│   │   ├── router/               # Vue Router 路由配置
│   │   ├── App.vue               # 根组件
│   │   ├── main.js               # 入口文件
│   │   └── style.css             # 全局样式（Tailwind + 自定义）
│   ├── index.html                # HTML模板
│   ├── package.json              # 依赖配置
│   ├── vite.config.js            # Vite 构建配置
│   ├── tailwind.config.js        # Tailwind 主题配置（电力主题）
│   └── start-frontend.ps1        # 前端启动脚本
│
├── start-all.ps1                 # 一键启动脚本（前后端）
├── start-backend.ps1             # 后端启动脚本
└── README.md                     # 本文档
```

---

## ✨ 技术亮点

### 前端技术亮点（全新 Vue 3 重构）

1. **电力特效背景**：`PowerFlowBackground.vue` - Canvas 电路流动画
   - 粒子节点系统（发光脉冲效果）
   - 节点间动态连接线
   - 随机脉冲波纹效果
   - 扫描线 + 光晕渐变效果

2. **科技感设计语言**
   - 配色方案：电光青 (`#00e5ff`)、霓虹黄、`#0f1e36` 深色背景
   - 玻璃态面板（毛玻璃 + 透明 + 边框发光）
   - 霓虹按钮（流光扫过动画）
   - 数字渐变文字（`bg-clip-text`）
   - 状态标签（绿/黄/红/灰四色语义）

3. **10个功能页面**
   - 数据看板：统计卡片 + 柱状趋势图 + 市场行情
   - 认证管理：登录/刷新/退出/Token管理
   - 合同台账：表格化展示 + 新建抽屉表单
   - 交易申报：时段编辑 + 提交动画
   - 结算对账：任务列表 + 汇总报告面板
   - 风险管理：偏差等级大卡片 + 仪表盘
   - 市场价格：迷你柱状走势图 + 极值统计
   - 外部数据：系统连接状态检测
   - 规则配置：规则详情三栏卡片布局
   - 审计日志：操作类型过滤 + 分页

4. **Tailwind CSS 深度定制**
   - `dark-*` 系列（深色背景层次）
   - `electric-*` 系列（电光青色系）
   - `neon-*` 系列（霓虹色：cyan/blue/purple/green/yellow/orange/red/pink）
   - `glow-*` 阴影效果（发光边框）
   - `glass-panel` 玻璃态组件

### 后端技术栈

- **框架**：FastAPI 0.115+
- **数据库**：SQLite（支持迁移版本化）
- **认证**：JWT（HS256）+ Refresh Token
- **规则引擎**：YAML + Pydantic 校验
- **测试**：pytest + TestClient

---

## 🧪 测试账号

| 用户名 | 密码 | 组织ID | 角色 | 说明 |
|--------|------|--------|------|------|
| admin | admin123 | 0 | admin | 管理员（可跨组织查询�� |
| user1001 | pass1001 | 1001 | trader | 交易员A |
| user1002 | pass1002 | 1002 | trader | 交易员B |

---

## 🔌 API 端点清单

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `POST /api/v1/auth/login` | 登录（返回 access_token + refresh_token） |
| 认证 | `POST /api/v1/auth/refresh` | 刷新 Token |
| 认证 | `POST /api/v1/auth/logout` | 退出登录 |
| 认证 | `GET /api/v1/auth/whoami` | 验证当前用户身份 |
| 合同 | `POST /api/v1/contracts/contracts` | 创建合同 |
| 合同 | `GET /api/v1/contracts/contracts` | 查询合同列表 |
| 申报 | `POST /api/v1/trades/declarations` | 提交交易申报（幂等） |
| 申报 | `GET /api/v1/trades/declarations` | 查询申报列表 |
| 风险 | `GET /api/v1/risk/deviation` | 偏差风险查询 |
| 结算 | `POST /api/v1/settlement/reconcile/tasks` | 创建结算任务 |
| 结算 | `GET /api/v1/settlement/reconcile/tasks` | 查询任务列表 |
| 结算 | `GET /api/v1/settlement/reconcile/tasks/{id}/summary` | 结算汇总报告 |
| 规则 | `GET /api/v1/rules` | 查询省份规则 |
| 规则 | `GET /api/v1/rules/versions` | 规则版本列表 |
| 市场 | `GET /api/v1/market/prices` | 查询市场价格 |
| 看板 | `GET /api/v1/dashboard/stats` | 看板统计数据 |
| 审计 | `GET /api/v1/audit/logs` | 查询审计日志 |
| 外部 | `GET /api/v1/integrations/status` | 系统连接状态 |
| 健康 | `GET /api/v1/health` | 健康检查 |

---

## 🎨 演示数据说明

启动时自动插入的演示数据：

- **10 条合同记录**：GD/ZJ 两省，中长期+现货类型，active/expired 状态
- **30 条交易申报**：2026-04-01 ~ 2026-04-08 期间，含96时段数据
- **5 条结算任务**：queued/running/completed 状态，含汇总报告
- **60 条审计日志**：trade_declaration_create、contract_create、reconcile_task_create 等操作
- **1100+ 条市场价格**：GD/ZJ 两省 8 天 × 96 时段/天

---

## 📦 部署建议

### 开发环境
- SQLite 本地数据库
- 单机部署
- 日志输出到控制台

### 生产环境
- 迁移至 PostgreSQL/MySQL
- Docker 容器化部署
- Nginx 反向代理
- 日志收集（ELK/Loki）
- 监控告警（Prometheus + Grafana）
- 备份策略（数据库定时备份）

---

## 📄 其他文档

- 项目开发文档：`./电力交易AI平台开发文档.md`
- 行业研究：`./deep-research-report.md`
- 迭代计划：`./开发迭代计划.md`