# 电力交易 AI 平台升级实施清单（文件级）

更新时间：2026-04-08  
适用仓库：`4. 大数据应用`（当前 FastAPI + SQLite + 原生前端）

## 1. 文档目的

本清单将你提出的 7 个升级方向拆到“可开发执行”的粒度：

1. 哪些现有文件要改。  
2. 哪些新文件要加。  
3. 每个模块的核心接口（含请求/响应示例，沿用当前 `success/code/message/data/request_id` 包装）。  
4. 数据迁移、测试、CI 的配套落地位置。

---

## 2. 当前仓库基线（用于对齐）

### 2.1 后端现有关键目录

- `backend/app/api/endpoints/*.py`
- `backend/app/services/*.py`
- `backend/app/schemas/*.py`
- `backend/app/core/{auth,errors,config,response}.py`
- `backend/app/db/{sqlite,migrate}.py`
- `backend/db/migrations/001~005_*.sql`
- `backend/tests/{conftest,test_api,test_new_features}.py`

### 2.2 前端现有关键目录

- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`

### 2.3 当前接口约定（必须保持）

- API 前缀：`/api/v1`
- 统一响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {},
  "request_id": "..."
}
```

---

## 3. 增量目录蓝图（建议）

```text
backend/
  app/
    api/endpoints/
      risk.py                  # 扩展双引擎/异常/回测接口
      settlement.py            # 改异步任务流接口
      rules.py                 # 增加 diff/灰度/回滚接口
      market.py                # 增加质量治理接口
      auth.py                  # 增加挑战确认接口
      dashboard.py             # 增加钻取/导出/告警接口
    core/
      permission.py            # 新增：细粒度 RBAC 校验
    services/
      risk_model_service.py
      risk_anomaly_service.py
      risk_backtest_service.py
      risk_feature_service.py
      settlement_queue_service.py
      settlement_worker_service.py
      rule_release_service.py
      market_quality_service.py
      rbac_service.py
      export_service.py
    workers/
      settlement_worker.py     # 队列消费者入口（Celery/RQ）
  db/migrations/
    006_risk_engine.sql
    007_settlement_async.sql
    008_rule_release.sql
    009_market_quality.sql
    010_rbac.sql
    011_postgres_prepare.sql
frontend/
  modules/
    api.js
    state.js
    dashboard.js
    risk.js
    settlement.js
    rules.js
    market.js
    auth.js
    export.js
```

---

## 4. 模块一：风控升级为“规则 + 模型”双引擎

### 4.1 后端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `backend/app/services/risk_service.py` | 修改 | 从单规则评分升级为融合评分（rule_score + model_score） |
| `backend/app/api/endpoints/risk.py` | 修改 | 新增 `/evaluate`、`/anomalies`、`/backtests` |
| `backend/app/schemas/risk.py` | 修改 | 增加 `RiskEvaluateRequest/Response`、`AnomalyItem`、`BacktestReport` |
| `backend/app/core/errors.py` | 修改 | 增加 `RISK_MODEL_NOT_READY`、`RISK_BACKTEST_NOT_FOUND` |
| `backend/app/services/risk_model_service.py` | 新增 | 模型加载、预测、版本管理 |
| `backend/app/services/risk_anomaly_service.py` | 新增 | 异常波动检测（EWMA/Z-Score/MAD） |
| `backend/app/services/risk_backtest_service.py` | 新增 | 历史回测计算与结果落库 |
| `backend/app/services/risk_feature_service.py` | 新增 | 特征快照构建 |
| `backend/db/migrations/006_risk_engine.sql` | 新增 | `risk_feature_snapshot/risk_score_record/risk_anomaly_event/risk_backtest_report` |
| `backend/tests/test_risk_engine.py` | 新增 | 双引擎、降级策略、异常检测、回测正确性测试 |

### 4.2 前端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `frontend/index.html` | 修改 | 风控 Tab 增加“异常列表”“模型版本”“回测结果”区域 |
| `frontend/app.js` | 修改 | 新增请求与渲染逻辑 |
| `frontend/styles.css` | 修改 | 异常级别高亮（high/medium/low） |
| `frontend/modules/risk.js` | 新增（可选） | 将风控逻辑从 `app.js` 拆分 |

### 4.3 接口示例

#### 4.3.1 `POST /api/v1/risk/evaluate`

请求：
```json
{
  "org_id": 1001,
  "province_code": "GD",
  "trade_date": "2026-04-09",
  "rule_version": "2026.04",
  "model_version": "risk-gbdt-v1"
}
```

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "trade_date": "2026-04-09",
    "org_id": 1001,
    "province_code": "GD",
    "rule_version": "2026.04",
    "model_version": "risk-gbdt-v1",
    "rule_score": 0.42,
    "model_score": 0.57,
    "final_score": 0.51,
    "risk_level": "medium",
    "expected_deviation_cost": 18342.3,
    "explain": {
      "top_features": [
        {"name": "price_deviation_mean_30d", "value": 0.38},
        {"name": "declaration_count_7d", "value": 0.22}
      ]
    }
  },
  "request_id": "f1d5..."
}
```

#### 4.3.2 `GET /api/v1/risk/anomalies?org_id=1001&from=2026-04-01&to=2026-04-08`

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "total": 2,
    "items": [
      {
        "event_id": "RAE-001",
        "event_time": "2026-04-06T10:15:00Z",
        "anomaly_type": "price_spike",
        "severity": "high",
        "metric_value": 812.6,
        "threshold": 655.0
      }
    ]
  },
  "request_id": "d2b1..."
}
```

---

## 5. 模块二：结算对账异步任务流

### 5.1 后端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `backend/app/services/settlement_service.py` | 修改 | 从“直接处理”改为“入队 + 状态机” |
| `backend/app/api/endpoints/settlement.py` | 修改 | 增加 `/retry`、`/review`、`/events` |
| `backend/app/schemas/settlement.py` | 修改 | 增加 `retry_count/next_retry_at/review_status` 字段 |
| `backend/app/core/errors.py` | 修改 | 增加 `SETTLEMENT_TASK_TIMEOUT`、`SETTLEMENT_REVIEW_REQUIRED` |
| `backend/app/services/settlement_queue_service.py` | 新增 | 入队、出队、重试策略 |
| `backend/app/services/settlement_worker_service.py` | 新增 | 任务执行器（计算、对账、写回） |
| `backend/app/workers/settlement_worker.py` | 新增 | 队列 worker 入口 |
| `backend/db/migrations/007_settlement_async.sql` | 新增 | `settlement_jobs/settlement_job_attempts/settlement_review_queue` |
| `backend/tests/test_settlement_async.py` | 新增 | 重试、超时、人工复核流测试 |

### 5.2 前端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `frontend/index.html` | 修改 | 结算页新增“失败重试”“人工复核”操作区 |
| `frontend/app.js` | 修改 | 增加轮询任务状态和事件流展示 |
| `frontend/modules/settlement.js` | 新增（可选） | 结算异步逻辑拆分 |

### 5.3 接口示例

#### 5.3.1 `POST /api/v1/settlement/reconcile/tasks`

请求：
```json
{
  "org_id": 1001,
  "province_code": "GD",
  "cycle_start": "2026-04-01",
  "cycle_end": "2026-04-07"
}
```

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "queued",
  "data": {
    "task_id": "REC-A1B2C3D4",
    "status": "queued",
    "queue_name": "settlement-default",
    "retry_count": 0
  },
  "request_id": "1a2b..."
}
```

#### 5.3.2 `POST /api/v1/settlement/reconcile/tasks/REC-A1B2C3D4/retry`

请求：
```json
{
  "reason": "manual retry from console"
}
```

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "retry queued",
  "data": {
    "task_id": "REC-A1B2C3D4",
    "status": "queued",
    "retry_count": 2
  },
  "request_id": "3c4d..."
}
```

---

## 6. 模块三：规则引擎版本对比 + 灰度发布

### 6.1 后端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `backend/app/services/rule_service.py` | 修改 | 增加版本差异比较、有效版本解析 |
| `backend/app/api/endpoints/rules.py` | 修改 | 新增 `/diff`、`/release`、`/rollback`、`/effective` |
| `backend/app/schemas/rules.py` | 修改 | 增加 `RuleDiffResponse/RuleReleasePolicy` |
| `backend/app/services/rule_release_service.py` | 新增 | 灰度策略（白名单/比例/时间窗） |
| `backend/db/migrations/008_rule_release.sql` | 新增 | `rule_release_policies/rule_release_logs/rule_diff_snapshot` |
| `backend/tests/test_rule_release.py` | 新增 | 灰度命中、回滚、版本差异正确性测试 |

### 6.2 前端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `frontend/index.html` | 修改 | 规则页新增“版本对比视图”和“灰度发布表单” |
| `frontend/app.js` | 修改 | 增加 diff 渲染、发布/回滚交互 |
| `frontend/modules/rules.js` | 新增（可选） | 规则模块拆分 |

### 6.3 接口示例

#### 6.3.1 `GET /api/v1/rules/diff?province_code=GD&from_version=2026.04&to_version=2026.05`

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "province_code": "GD",
    "from_version": "2026.04",
    "to_version": "2026.05",
    "changes": [
      {"path": "risk.high_threshold", "old": 0.70, "new": 0.75},
      {"path": "trade.price_max", "old": 1500, "new": 1600}
    ]
  },
  "request_id": "7e8f..."
}
```

#### 6.3.2 `POST /api/v1/rules/release`

请求：
```json
{
  "province_code": "GD",
  "target_version": "2026.05",
  "strategy": "org_whitelist",
  "org_ids": [1001, 1002],
  "operator_note": "pilot rollout"
}
```

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "release policy created",
  "data": {
    "policy_id": "RLP-20260408-001",
    "status": "active"
  },
  "request_id": "0a1b..."
}
```

---

## 7. 模块四：市场数据质量治理

### 7.1 后端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `backend/scripts/import_market_data.py` | 修改 | 导入前校验 + 质量报告输出 |
| `backend/app/services/market_service.py` | 修改 | 数据读取仅走 `validated`/`curated` 数据 |
| `backend/app/api/endpoints/market.py` | 修改 | 增加质量查询接口 |
| `backend/app/schemas/market.py` | 修改 | 增加质量报告模型 |
| `backend/app/services/market_quality_service.py` | 新增 | 缺失/重复/越界/峰值检测 |
| `backend/db/migrations/009_market_quality.sql` | 新增 | `market_price_raw/market_quality_issue/market_quality_daily_score` |
| `backend/tests/test_market_quality.py` | 新增 | 导入校验与质量评分测试 |

### 7.2 前端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `frontend/index.html` | 修改 | 市场页新增“质量评分卡”和“问题列表” |
| `frontend/app.js` | 修改 | 导入质量结果渲染 |
| `frontend/modules/market.js` | 新增（可选） | 市场数据模块拆分 |

### 7.3 接口示例

#### 7.3.1 `POST /api/v1/market/import/validate`

请求：
```json
{
  "source": "sample",
  "rows": [
    {"province_code": "GD", "market_date": "2026-04-08", "timeslot": "09:00-09:15", "price": 420.2}
  ]
}
```

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "validated",
  "data": {
    "accepted_rows": 96,
    "rejected_rows": 4,
    "quality_score": 92.5,
    "issues": [
      {"type": "DUPLICATE", "count": 2},
      {"type": "OUTLIER", "count": 2}
    ]
  },
  "request_id": "9a7c..."
}
```

---

## 8. 模块五：权限体系细化（RBAC + 数据权限 + 二次确认）

### 8.1 后端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `backend/app/core/auth.py` | 修改 | 支持角色 + 权限点 + 数据范围解析 |
| `backend/app/core/errors.py` | 修改 | 增加 `PERMISSION_DENIED`、`CONFIRMATION_REQUIRED` |
| `backend/app/api/endpoints/auth.py` | 修改 | 增加挑战与确认接口 |
| `backend/app/api/endpoints/{rules,settlement,contracts}.py` | 修改 | 敏感操作加确认校验 |
| `backend/app/core/permission.py` | 新增 | `require_permission("resource:action")` 装饰器 |
| `backend/app/services/rbac_service.py` | 新增 | 角色权限和数据范围服务 |
| `backend/db/migrations/010_rbac.sql` | 新增 | `permissions/roles/user_roles/data_scope_policies/auth_challenges` |
| `backend/tests/test_rbac.py` | 新增 | 权限校验、越权拦截、确认流程测试 |

### 8.2 前端文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `frontend/index.html` | 修改 | 关键操作增加确认弹层 |
| `frontend/app.js` | 修改 | 自动处理 `CONFIRMATION_REQUIRED` 并调用确认 API |
| `frontend/modules/auth.js` | 新增（可选） | 登录、权限、确认流统一管理 |

### 8.3 接口示例

#### 8.3.1 `POST /api/v1/auth/challenges`

请求：
```json
{
  "action": "rules:release",
  "resource_id": "GD:2026.05",
  "reason": "publish new rule version"
}
```

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "challenge issued",
  "data": {
    "challenge_id": "CHL-20260408-001",
    "expires_in": 300
  },
  "request_id": "4f6d..."
}
```

#### 8.3.2 `POST /api/v1/auth/challenges/confirm`

请求：
```json
{
  "challenge_id": "CHL-20260408-001",
  "confirm_code": "834129"
}
```

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "confirmed",
  "data": {
    "confirm_token": "cfm_eyJ...",
    "expires_in": 300
  },
  "request_id": "5e3a..."
}
```

---

## 9. 模块六：前端看板交互增强（联动、钻取、导出、告警）

### 9.1 前端文件改造（重点）

| 文件 | 动作 | 说明 |
|---|---|---|
| `frontend/index.html` | 修改 | 全局筛选栏（日期/省份/组织）+ 告警区 + 导出按钮 |
| `frontend/app.js` | 修改 | 先保留兼容，再逐步迁移到 `modules/` |
| `frontend/styles.css` | 修改 | 告警色板、钻取面板、移动端布局 |
| `frontend/modules/state.js` | 新增 | 全局筛选状态（单一数据源） |
| `frontend/modules/dashboard.js` | 新增 | 卡片联动、趋势图、钻取渲染 |
| `frontend/modules/export.js` | 新增 | CSV/Excel 导出请求与下载 |
| `frontend/modules/api.js` | 新增 | 统一请求拦截与错误处理 |

### 9.2 后端配套文件

| 文件 | 动作 | 说明 |
|---|---|---|
| `backend/app/api/endpoints/dashboard.py` | 修改 | 新增钻取和导出接口 |
| `backend/app/services/export_service.py` | 新增 | 生成导出数据 |
| `backend/tests/test_dashboard_interactions.py` | 新增 | 筛选联动与导出接口测试 |

### 9.3 接口示例

#### 9.3.1 `GET /api/v1/dashboard/drilldown?metric=declarations&from=2026-04-01&to=2026-04-08&province_code=GD`

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "metric": "declarations",
    "rows": [
      {"trade_date": "2026-04-08", "org_id": 1001, "count": 6}
    ]
  },
  "request_id": "8b9c..."
}
```

#### 9.3.2 `POST /api/v1/dashboard/export`

请求：
```json
{
  "dataset": "reconcile_tasks",
  "filters": {
    "from": "2026-04-01",
    "to": "2026-04-08",
    "province_code": "GD"
  },
  "format": "csv"
}
```

响应：
```json
{
  "success": true,
  "code": "OK",
  "message": "export generated",
  "data": {
    "file_name": "reconcile_tasks_20260408.csv",
    "download_url": "/api/v1/dashboard/export/files/reconcile_tasks_20260408.csv"
  },
  "request_id": "2d11..."
}
```

---

## 10. 模块七：工程化与上线能力（PostgreSQL/Redis/监控/Docker）

### 10.1 后端与部署文件改造

| 文件 | 动作 | 说明 |
|---|---|---|
| `backend/requirements.txt` | 修改 | 增加 `psycopg[binary]`、`redis`、`rq/celery`、`prometheus-client` |
| `backend/requirements-dev.txt` | 修改 | 增加集成测试、lint、类型检查依赖 |
| `backend/app/core/config.py` | 修改 | 增加 `APP_DATABASE_URL/APP_REDIS_URL/APP_QUEUE_BACKEND` |
| `backend/app/db/sqlite.py` | 修改 | 抽象为 `db/session.py`，兼容 SQLite 与 PostgreSQL |
| `backend/app/db/migrate.py` | 修改 | 支持跨数据库迁移管理 |
| `backend/db/migrations/011_postgres_prepare.sql` | 新增 | PostgreSQL 兼容字段与索引 |
| `backend/app/api/endpoints/health.py` | 修改 | 新增 `ready/live` 探针（检查 DB/Redis） |
| `backend/Dockerfile` | 新增 | 后端镜像 |
| `backend/docker-compose.yml` | 新增 | `api + worker + redis + postgres` 本地一键启动 |
| `.github/workflows/backend-ci.yml` | 修改 | 增加 lint、迁移检查、PostgreSQL 集成测试 |
| `.github/workflows/backend-cd.yml` | 新增（可选） | 自动构建镜像并部署 |

### 10.2 CI 建议修改点（`backend-ci.yml`）

1. `python-version` 固定为 `3.11/3.12` 矩阵。  
2. 新增 `services: postgres, redis`。  
3. 增加步骤：`migration dry-run`、`pytest -m "integration"`。  
4. 失败时上传测试报告与日志。

---

## 11. 接口汇总（新增）

| 模块 | 方法 | 路径 | 鉴权 |
|---|---|---|---|
| 风控双引擎 | `POST` | `/api/v1/risk/evaluate` | `trader/admin` |
| 风控异常 | `GET` | `/api/v1/risk/anomalies` | `trader/admin` |
| 风控回测 | `POST` | `/api/v1/risk/backtests` | `admin` |
| 结算重试 | `POST` | `/api/v1/settlement/reconcile/tasks/{task_id}/retry` | `trader/admin` |
| 结算复核 | `POST` | `/api/v1/settlement/reconcile/tasks/{task_id}/review` | `admin` |
| 规则 diff | `GET` | `/api/v1/rules/diff` | `admin` |
| 规则发布 | `POST` | `/api/v1/rules/release` | `admin + confirm` |
| 规则回滚 | `POST` | `/api/v1/rules/rollback` | `admin + confirm` |
| 市场质量报告 | `GET` | `/api/v1/market/quality/daily` | `trader/admin` |
| 权限挑战 | `POST` | `/api/v1/auth/challenges` | `trader/admin` |
| 权限确认 | `POST` | `/api/v1/auth/challenges/confirm` | `trader/admin` |
| 看板钻取 | `GET` | `/api/v1/dashboard/drilldown` | `trader/admin` |
| 看板导出 | `POST` | `/api/v1/dashboard/export` | `trader/admin` |

---

## 12. 分阶段排期（建议 4 个迭代）

### 迭代 1（基础设施周）

1. `006~007` 迁移。  
2. 异步队列骨架。  
3. RBAC 框架与确认机制基础。  

### 迭代 2（核心业务周）

1. 风控双引擎 + 异常检测。  
2. 结算异步执行 + 自动重试。  
3. 规则 diff 与灰度发布。  

### 迭代 3（体验与治理周）

1. 市场数据质量治理。  
2. 前端全局筛选联动 + 钻取 + 导出。  
3. 告警高亮与复核工作台。  

### 迭代 4（工程化上线周）

1. PostgreSQL 切换演练。  
2. Docker Compose 一键环境。  
3. CI 完整化（lint + unit + integration + migration）。  

---

## 13. 最小可交付（MVP++）验收口径

1. 结算任务提交在高并发下不阻塞 API（异步入队成功率 > 99.9%）。  
2. 风控接口输出包含 `rule_score/model_score/final_score`，并支持无模型降级。  
3. 规则版本可 diff、可灰度、可回滚，且审计日志可追踪。  
4. 市场导入会输出质量分，低质量数据默认不进入下游计算。  
5. 敏感操作必须二次确认。  
6. 看板支持筛选联动、钻取、导出，关键告警可视化。  
7. CI 包含数据库迁移和集成测试，部署可回滚。

