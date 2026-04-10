// ═══════════════════════════════════════════════════════════════
// 电力交易平台控制台 - 交互脚本（增强版）
// ═══════════════════════════════════════════════════════════════

/**
 * API 根地址。页面与后端不同源时必须指向 FastAPI（默认 :8000）。
 * 优先级：window.__POWER_TRADING_API_BASE__ > localStorage POWER_TRADING_API_BASE > 自动推断
 */
function getApiBase() {
  if (typeof window.__POWER_TRADING_API_BASE__ === "string" && window.__POWER_TRADING_API_BASE__.trim()) {
    return window.__POWER_TRADING_API_BASE__.trim().replace(/\/$/, "");
  }
  try {
    const stored = localStorage.getItem("POWER_TRADING_API_BASE");
    if (stored && stored.trim()) return stored.trim().replace(/\/$/, "");
  } catch (_) {
    /* ignore */
  }
  const { protocol, hostname, port } = window.location;
  if (protocol === "file:") {
    return "http://127.0.0.1:8000";
  }
  if (
    (hostname === "localhost" || hostname === "127.0.0.1") &&
    port &&
    port !== "8000"
  ) {
    return `http://${hostname}:8000`;
  }
  return "";
}

function apiUrl(path) {
  const p = path.startsWith("/") ? path : `/${path}`;
  const base = getApiBase();
  return base ? `${base}${p}` : p;
}

/** 网络失败时合并为一条提示，避免连续弹出多条相同 Toast */
let _lastNetworkErrorToastAt = 0;
const NETWORK_ERROR_TOAST_COOLDOWN_MS = 10000;

function notifyNetworkErrorOnce() {
  const now = Date.now();
  if (now - _lastNetworkErrorToastAt < NETWORK_ERROR_TOAST_COOLDOWN_MS) return;
  _lastNetworkErrorToastAt = now;
  const target = getApiBase() || `${window.location.origin}（同源）`;
  toast.error(
    `无法连接后端 API（${target}）。请先在本机启动服务：在 backend 目录执行 python -m uvicorn app.main:app --host 0.0.0.0 --port 8000，或使用项目根目录的 start-backend.ps1。然后浏览器打开 http://127.0.0.1:8000/console/ 使用控制台。`
  );
}

// ── Toast 通知系统 ───────────────────────────────────────────

const toast = {
  container: null,

  init() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      this.container.id = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'info', duration = 4000) {
    if (!this.container) this.init();

    const icons = {
      success: 'fa-check-circle',
      error: 'fa-times-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };

    const toastEl = document.createElement('div');
    toastEl.className = `toast ${type}`;
    toastEl.innerHTML = `
      <i class="fas ${icons[type]} toast-icon"></i>
      <span class="toast-message">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">
        <i class="fas fa-times"></i>
      </button>
    `;

    this.container.appendChild(toastEl);

    // 自动移除
    setTimeout(() => {
      toastEl.style.animation = 'toast-in 0.3s ease reverse';
      setTimeout(() => toastEl.remove(), 300);
    }, duration);
  },

  success(message) { this.show(message, 'success'); },
  error(message) { this.show(message, 'error'); },
  info(message) { this.show(message, 'info'); },
  warning(message) { this.show(message, 'warning'); }
};

// ── 数字动画 ─────────────────────────────────────────────────

function animateValue(element, start, end, duration = 1000, prefix = '', suffix = '') {
  if (!element) return;

  const startTime = performance.now();
  const isNumeric = typeof end === 'number';

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // 缓动函数
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);

    let current;
    if (isNumeric) {
      current = Math.floor(start + (end - start) * easeOutQuart);
    }

    element.textContent = prefix + current + suffix;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.classList.add('counting');
      setTimeout(() => element.classList.remove('counting'), 500);
    }
  }

  requestAnimationFrame(update);
}

// ── API 工具层 ──────────────────────────────────────────────

const api = {
  get: async (path) => {
    try {
      const resp = await fetch(apiUrl(path), { headers: authHeaders() });
      const data = await resp.json();
      if (!resp.ok && !data.success) {
        toast.error(`请求失败: ${resp.status} ${resp.statusText}`);
      }
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      notifyNetworkErrorOnce();
      return { success: false, message: msg, networkError: true };
    }
  },

  post: async (path, body) => {
    try {
      const resp = await fetch(apiUrl(path), {
        method: "POST",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await resp.json();
      if (!resp.ok && !data.success) {
        toast.error(`请求失败: ${resp.status}`);
      }
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      notifyNetworkErrorOnce();
      return { success: false, message: msg, networkError: true };
    }
  },

  patch: async (path, body) => {
    try {
      const resp = await fetch(apiUrl(path), {
        method: "PATCH",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await resp.json();
      if (!resp.ok && !data.success) {
        toast.error(`请求失败: ${resp.status}`);
      }
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      notifyNetworkErrorOnce();
      return { success: false, message: msg, networkError: true };
    }
  },
};

// ── DOM 工具函数 ─────────────────────────────────────────────

function write(id, value) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = JSON.stringify(value, null, 2);
  el.style.animation = "none";
  el.offsetHeight;
  el.style.animation = "fadeIn 0.3s ease";
}

/**
 * 将分页列表数据渲染为 HTML 表格。
 * @param {string} containerId - 表格容器元素 ID
 * @param {object} data - API 返回的列表数据 { total, items: [...] }
 * @param {Array}  columns - 列配置 [{key, label, render?}]
 *   render(val, row): 自定义单元格内容，返回 HTML 字符串
 * @param {string} emptyMsg - 无数据时显示的文字
 */
function renderTable(containerId, data, columns, emptyMsg) {
  const el = document.getElementById(containerId);
  if (!el) return;

  const items = data?.items;
  if (!items || items.length === 0) {
    el.innerHTML =
      '<div class="empty-state"><i class="fas fa-inbox"></i><p>' +
      (emptyMsg || "暂无数据") +
      "</p></div>";
    return;
  }

  const total = data?.total ?? items.length;
  let html =
    '<div class="table-info">共 <strong>' +
    total +
    '</strong> 条记录</div><div class="table-wrapper"><table class="data-table"><thead><tr>';

  for (const col of columns) {
    html += "<th>" + col.label + "</th>";
  }
  html += "</tr></thead><tbody>";

  for (const row of items) {
    html += "<tr>";
    for (const col of columns) {
      let val = col.key.split(".").reduce((o, k) => (o ? o[k] : undefined), row);
      const raw = val;
      val = col.render ? col.render(val, row) : _formatCell(val);
      html += '<td data-label="' + col.label + '">' + (val ?? "—") + "</td>";
    }
    html += "</tr>";
  }
  html += "</tbody></table></div>";
  el.innerHTML = html;
}

function _formatCell(val) {
  if (val === null || val === undefined) return null;
  if (typeof val === "boolean") return val ? "是" : "否";
  if (typeof val === "number") {
    if (Number.isInteger(val)) return val.toLocaleString();
    return val.toFixed(4).replace(/\.?0+$/, "");
  }
  if (typeof val === "string" && /^\d{4}-\d{2}-\d{2}T/.test(val)) {
    return val.slice(0, 19).replace("T", " ");
  }
  return String(val);
}

/** 渲染每日申报汇总表格 */
function renderDailySummaryTable(containerId, daily) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!daily || daily.length === 0) {
    el.innerHTML = '<div class="empty-state"><i class="fas fa-chart-bar"></i><p>暂无日汇总数据</p></div>';
    return;
  }
  const cols = [
    { key: "trade_date", label: "交易日期" },
    { key: "declarations", label: "申报次数" },
    {
      key: "volume_mwh",
      label: "总电量 (MWh)",
      render: (v) => (v !== null && v !== undefined ? Number(v).toFixed(2) : "—"),
    },
    {
      key: "avg_price",
      label: "均价 (元/MWh)",
      render: (v) => (v !== null && v !== undefined ? "¥" + Number(v).toFixed(2) : "—"),
    },
  ];
  let html = '<div class="table-wrapper"><table class="data-table"><thead><tr>';
  for (const c of cols) html += "<th>" + c.label + "</th>";
  html += "</tr></thead><tbody>";
  for (const row of daily) {
    html += "<tr>";
    for (const c of cols) {
      let v = c.key.split(".").reduce((o, k) => (o ? o[k] : undefined), row);
      html += '<td data-label="' + c.label + '">' + (c.render ? c.render(v, row) : _formatCell(v)) + "</td>";
    }
    html += "</tr>";
  }
  html += "</tbody></table></div>";
  el.innerHTML = html;
}

/** 渲染市场价格表格 */
function renderPriceTable(containerId, data) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const items = data?.items;
  if (!items || items.length === 0) {
    el.innerHTML = '<div class="empty-state"><i class="fas fa-chart-line"></i><p>暂无价格数据</p></div>';
    return;
  }
  const total = data?.total ?? items.length;
  let html =
    '<div class="table-info">共 <strong>' +
    total +
    '</strong> 条价格记录</div><div class="table-wrapper"><table class="data-table"><thead><tr>' +
    "<th>省份</th><th>日期</th><th>时段</th><th>价格 (元/MWh)</th><th>来源</th>" +
    "</tr></thead><tbody>";
  for (const row of items) {
    html +=
      "<tr><td data-label=\"省份\">" +
      _formatCell(row.province_code) +
      '</td><td data-label=\"日期\">' +
      _formatCell(row.market_date) +
      '</td><td data-label=\"时段\">' +
      _formatCell(row.timeslot) +
      '</td><td data-label=\"价格\" class="num">¥' +
      (row.price != null ? Number(row.price).toFixed(2) : "—") +
      '</td><td data-label=\"来源\">' +
      _formatCell(row.source) +
      "</td></tr>";
  }
  html += "</tbody></table></div>";
  el.innerHTML = html;
}

function authHeaders() {
  const token = document.getElementById("auth-token")?.value?.trim();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

function updateUserBadge(username, orgId) {
  const badge = document.getElementById("user-badge-text");
  if (badge) {
    badge.textContent = username ? `${username} | org ${orgId}` : "未登录";
  }
}

// ── Tab 切换 ─────────────────────────────────────────────────

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));

    btn.classList.add("active");
    const panelId = `tab-${btn.dataset.tab}`;
    const panel = document.getElementById(panelId);
    if (panel) {
      panel.classList.add("active");
      // 触发动画
      panel.querySelectorAll('.animate-in').forEach((el, i) => {
        el.style.animationDelay = `${i * 0.1}s`;
        el.classList.add('animate-in');
      });
    }
  });
});

// ── 认证模块 ─────────────────────────────────────────────────

document.getElementById("btn-login").addEventListener("click", async () => {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();

  if (!username || !password) {
    toast.warning("请输入用户名和密码");
    return;
  }

  const btn = document.getElementById("btn-login");
  btn.innerHTML = '<span class="loading-spinner"></span> 登录中...';
  btn.disabled = true;

  const resp = await api.post("/api/v1/auth/login", { username, password });

  btn.innerHTML = '<i class="fas fa-key btn-icon"></i> 登录获取JWT';
  btn.disabled = false;

  if (resp?.success && resp?.data?.access_token) {
    document.getElementById("auth-token").value = resp.data.access_token;
    toast.success(`欢迎回来，${username}！`);
  }
  if (resp?.success && resp?.data?.refresh_token) {
    document.getElementById("refresh-token").value = resp.data.refresh_token;
  }
  if (resp?.success) {
    updateUserBadge(username, resp.data?.org_id ?? "—");
  } else if (!resp?.networkError) {
    toast.error(resp?.message || "登录失败");
  }

  write("auth-result", resp);
});

document.getElementById("btn-refresh-token").addEventListener("click", async () => {
  const refreshToken = document.getElementById("refresh-token").value.trim();
  if (!refreshToken) {
    toast.warning("请先输入 refresh token");
    return;
  }

  const btn = document.getElementById("btn-refresh-token");
  btn.innerHTML = '<span class="loading-spinner"></span>';
  btn.disabled = true;

  const resp = await api.post("/api/v1/auth/refresh", { refresh_token: refreshToken });

  btn.innerHTML = '<i class="fas fa-redo btn-icon"></i> 刷新 Token';
  btn.disabled = false;

  if (resp?.success && resp?.data?.access_token) {
    document.getElementById("auth-token").value = resp.data.access_token;
    toast.success("Token 刷新成功！");
  }
  if (resp?.success && resp?.data?.refresh_token) {
    document.getElementById("refresh-token").value = resp.data.refresh_token;
  }

  write("auth-result", resp);
});

document.getElementById("btn-logout").addEventListener("click", async () => {
  const refreshToken = document.getElementById("refresh-token").value.trim();
  if (!refreshToken) {
    toast.warning("请先登录");
    return;
  }

  const btn = document.getElementById("btn-logout");
  btn.innerHTML = '<span class="loading-spinner"></span>';
  btn.disabled = true;

  const resp = await api.post("/api/v1/auth/logout", { refresh_token: refreshToken });

  btn.innerHTML = '<i class="fas fa-sign-out-alt btn-icon"></i> 退出登录';
  btn.disabled = false;

  if (resp?.success) {
    document.getElementById("auth-token").value = "";
    document.getElementById("refresh-token").value = "";
    updateUserBadge("", "");
    toast.info("已退出登录");
  }

  write("auth-result", resp);
});

document.getElementById("btn-whoami").addEventListener("click", async () => {
  const resp = await api.get("/api/v1/auth/whoami");
  if (resp?.success) {
    updateUserBadge(resp.data?.username ?? "—", resp.data?.org_id ?? "—");
    toast.info(`当前用户: ${resp.data?.username || '未知'}`);
  } else if (!resp?.networkError) {
    toast.error("验证身份失败");
  }
  write("auth-result", resp);
});

async function loadSsoConfigHint() {
  const hint = document.getElementById("sso-hint");
  const pre = document.getElementById("sso-config-result");
  try {
    const r = await fetch(apiUrl("/api/v1/auth/sso/config"));
    const j = await r.json();
    if (j?.success && j?.data?.oidc_enabled) {
      hint.innerHTML =
        `<i class="fas fa-openid"></i> SSO 已启用：Issuer <code>${j.data.issuer || "—"}</code>，可将 IdP 签发的 Access Token 填入上方 Bearer 框。`;
    } else {
      hint.innerHTML =
        `<i class="fas fa-openid"></i> SSO：当前使用本地登录 JWT / 静态令牌；可在服务端设置 <code>APP_AUTH_OIDC_ENABLED</code> 等以接入 OIDC。`;
    }
    if (pre) write("sso-config-result", j);
  } catch (e) {
    if (hint) hint.innerHTML = `<i class="fas fa-openid"></i> SSO 配置加载失败`;
  }
}

// ── 外部数据源（交易中心 / 计量）──────────────────────────────

document.getElementById("btn-external-status")?.addEventListener("click", async () => {
  const btn = document.getElementById("btn-external-status");
  btn.innerHTML = '<span class="loading-spinner"></span>';
  btn.disabled = true;
  const resp = await api.get("/api/v1/integrations/status");
  btn.innerHTML = '<i class="fas fa-info-circle btn-icon"></i> 连接状态';
  btn.disabled = false;
  write("external-result", resp);
  if (resp?.success) toast.info("已查询集成状态");
});

document.getElementById("btn-ext-tc-clearing")?.addEventListener("click", async () => {
  const d = document.getElementById("ext-tc-date")?.value?.trim();
  const q = d ? `?trade_date=${encodeURIComponent(d)}` : "";
  const resp = await api.get(`/api/v1/integrations/trading-center/clearing-snapshot${q}`);
  write("external-result", resp);
  if (resp?.success) toast.success("交易中心数据已返回");
  else toast.error(resp?.message || "请求失败");
});

document.getElementById("btn-ext-tc-prices")?.addEventListener("click", async () => {
  const province = document.getElementById("ext-tc-province")?.value?.trim();
  const md = document.getElementById("ext-tc-market-date")?.value?.trim();
  if (!province) {
    toast.warning("请填写省份代码");
    return;
  }
  const p = new URLSearchParams({ province_code: province });
  if (md) p.set("market_date", md);
  const resp = await api.get(`/api/v1/integrations/trading-center/market-prices?${p}`);
  write("external-result", resp);
  if (resp?.success) toast.success("外部电价已返回");
  else toast.error(resp?.message || "请求失败");
});

document.getElementById("btn-ext-metering")?.addEventListener("click", async () => {
  const mid = document.getElementById("ext-meter-id")?.value?.trim();
  const rd = document.getElementById("ext-meter-date")?.value?.trim();
  if (!mid) {
    toast.warning("请填写计量点 ID");
    return;
  }
  const p = new URLSearchParams({ meter_point_id: mid });
  if (rd) p.set("reading_date", rd);
  const resp = await api.get(`/api/v1/integrations/metering/readings?${p}`);
  write("external-result", resp);
  if (resp?.success) toast.success("计量数据已返回");
  else toast.error(resp?.message || "请求失败");
});

// ── 数据看板 ─────────────────────────────────────────────────

async function loadDashboard() {
  const btn = document.getElementById("btn-dashboard-refresh");
  btn.innerHTML = '<span class="loading-spinner"></span> 加载中...';
  btn.disabled = true;

  const resp = await api.get("/api/v1/dashboard/stats");

  btn.innerHTML = '<i class="fas fa-sync-alt btn-icon"></i> 刷新数据';
  btn.disabled = false;

  if (!resp?.success) {
    write("dashboard-raw", resp);
    document.getElementById("dashboard-raw").classList.remove("hidden");
    if (!resp?.networkError) {
      toast.error("看板数据加载失败");
    }
    return;
  }

  document.getElementById("dashboard-raw").classList.add("hidden");
  toast.success("数据已更新");

  const d = resp.data;

  // 数字动画
  animateValue(
    document.getElementById("stat-declarations-total"),
    0, d.declarations?.total || 0, 1000
  );
  document.getElementById("stat-declarations-today").innerHTML =
    `<i class="fas fa-calendar-day"></i> 今日: ${d.declarations?.submitted_today ?? '—'}`;

  animateValue(
    document.getElementById("stat-contracts-total"),
    0, d.contracts?.total || 0, 1000
  );
  document.getElementById("stat-contracts-active").innerHTML =
    `<i class="fas fa-check-circle"></i> 活跃: ${d.contracts?.active ?? '—'}`;

  animateValue(
    document.getElementById("stat-tasks-total"),
    0, d.reconcile_tasks?.total || 0, 1000
  );
  document.getElementById("stat-tasks-pending").innerHTML =
    `<i class="fas fa-clock"></i> 待处理: ${d.reconcile_tasks?.pending ?? '—'}`;

  const price = d.market?.latest_avg_price;
  document.getElementById("stat-market-price").textContent =
    price ? `¥${price}` : "暂无";
  document.getElementById("stat-market-date").innerHTML =
    `<i class="fas fa-calendar"></i> 日期: ${d.market?.latest_date ?? '—'}`;

  // 趋势图
  renderTrendChart(d.declaration_trend_7d || []);
}

function renderTrendChart(trend) {
  const chartEl = document.getElementById("trend-chart");
  chartEl.innerHTML = "";

  if (trend.length === 0) {
    chartEl.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:40px;">暂无近7日数据</div>';
    return;
  }

  const maxCount = Math.max(...trend.map((t) => t.count || 0), 1);

  trend.forEach((item, index) => {
    const col = document.createElement("div");
    col.className = "bar-col";
    const count = item.count || 0;
    const barHeight = Math.max(Math.round((count / maxCount) * 100), 8);

    col.innerHTML = `
      <div class="bar" style="height:${barHeight}px;animation-delay:${index * 0.1}s" title="${count}条申报"></div>
      <div class="bar-label">${item.date?.slice(5) || ''}</div>
    `;

    chartEl.appendChild(col);
  });
}

document.getElementById("btn-dashboard-refresh").addEventListener("click", loadDashboard);

// ── 规则配置 ─────────────────────────────────────────────────

document.getElementById("btn-rule").addEventListener("click", async () => {
  const province = document.getElementById("rule-province").value.trim();
  if (!province) {
    toast.warning("请输入省份代码");
    return;
  }

  const btn = document.getElementById("btn-rule");
  btn.innerHTML = '<span class="loading-spinner"></span>';
  btn.disabled = true;

  const date = document.getElementById("rule-date").value.trim();
  const params = new URLSearchParams({ province_code: province });
  if (date) params.set("trade_date", date);

  const resp = await api.get(`/api/v1/rules?${params.toString()}`);

  btn.innerHTML = '<i class="fas fa-search btn-icon"></i> 查询规则';
  btn.disabled = false;

  if (resp?.success) {
    toast.success("规则查询成功");
  } else {
    toast.error("规则查询失败");
  }

  write("rule-result", resp);
});

document.getElementById("btn-rule-versions").addEventListener("click", async () => {
  const province = document.getElementById("rule-versions-province").value.trim();
  if (!province) {
    toast.warning("请输入省份代码");
    return;
  }

  const btn = document.getElementById("btn-rule-versions");
  btn.innerHTML = '<span class="loading-spinner"></span>';
  btn.disabled = true;

  const resp = await api.get(`/api/v1/rules/versions?province_code=${province}`);

  btn.innerHTML = '<i class="fas fa-list-ul btn-icon"></i> 查询版本列表';
  btn.disabled = false;

  if (resp?.success) {
    toast.success("版本列表查询成功");
  } else {
    toast.error("版本列表查询失败");
  }

  write("rule-versions-result", resp);
});

// ── 合同台账 ─────────────────────────────────────────────────

document.getElementById("btn-contract-create").addEventListener("click", async () => {
  const payload = {
    org_id: Number(document.getElementById("ctr-org-id").value.trim()),
    province_code: document.getElementById("ctr-province").value.trim(),
    contract_type: document.getElementById("ctr-type").value,
    counterpart: document.getElementById("ctr-counterpart").value.trim() || undefined,
    volume_mwh: Number(document.getElementById("ctr-volume").value.trim()),
    price: Number(document.getElementById("ctr-price").value.trim()),
    start_date: document.getElementById("ctr-start").value.trim(),
    end_date: document.getElementById("ctr-end").value.trim(),
    remark: document.getElementById("ctr-remark").value.trim() || undefined,
  };

  if (!payload.org_id || !payload.province_code) {
    toast.warning("请填写必填字段");
    return;
  }

  const btn = document.getElementById("btn-contract-create");
  btn.innerHTML = '<span class="loading-spinner"></span> 创建中...';
  btn.disabled = true;

  const resp = await api.post("/api/v1/contracts/contracts", payload);

  btn.innerHTML = '<i class="fas fa-save btn-icon"></i> 创建合同';
  btn.disabled = false;

  if (resp?.success) {
    toast.success("合同创建成功！");
  } else {
    toast.error(resp?.message || "合同创建失败");
  }

  write("contract-create-result", resp);
});

async function loadContracts() {
  const btn = document.getElementById("btn-contract-list");
  btn.innerHTML = '<span class="loading-spinner"></span> 查询中...';
  btn.disabled = true;

  const status = document.getElementById("ctr-filter-status").value;
  const type = document.getElementById("ctr-filter-type").value;
  const params = new URLSearchParams({ page_no: 1, page_size: 20 });
  if (status) params.set("status", status);
  if (type) params.set("contract_type", type);

  const resp = await api.get(`/api/v1/contracts/contracts?${params.toString()}`);

  btn.innerHTML = '<i class="fas fa-search btn-icon"></i> 查询合同列表';
  btn.disabled = false;

  if (resp?.success) {
    toast.info(`找到 ${resp.data?.total || 0} 条合同记录`);
    const columns = [
      { key: "contract_id", label: "合同ID" },
      { key: "org_id", label: "组织ID" },
      { key: "province_code", label: "省份" },
      {
        key: "contract_type",
        label: "类型",
        render: (v) =>
          '<span class="tag tag-blue">' + _formatCell(v) + "</span>",
      },
      { key: "counterpart", label: "对手方" },
      {
        key: "volume_mwh",
        label: "电量 (MWh)",
        render: (v) => _formatCell(v),
      },
      {
        key: "price",
        label: "价格 (元/MWh)",
        render: (v) => (v != null ? "¥" + Number(v).toFixed(2) : "—"),
      },
      { key: "start_date", label: "开始日期" },
      { key: "end_date", label: "结束日期" },
      {
        key: "status",
        label: "状态",
        render: (v) => {
          const m = { active: "tag-green", expired: "tag-gray", cancelled: "tag-red" };
          return '<span class="tag ' + (m[v] || "") + '">' + _formatCell(v) + "</span>";
        },
      },
      { key: "created_at", label: "创建时间" },
    ];
    renderTable("contract-list-result", resp.data, columns, "暂无合同记录");
    write("contract-create-result", resp);
  } else if (!resp?.networkError) {
    toast.error("查询失败: " + (resp?.message || "未知错误"));
  }
}

document.getElementById("btn-contract-list").addEventListener("click", loadContracts);
document.getElementById("ctr-filter-status").addEventListener("change", loadContracts);
document.getElementById("ctr-filter-type").addEventListener("change", loadContracts);

// ── 交易申报 ─────────────────────────────────────────────────

document.getElementById("btn-trade-submit").addEventListener("click", async () => {
  const payload = {
    province_code: document.getElementById("trade-province").value.trim(),
    trade_date: document.getElementById("trade-date").value.trim(),
    market_type: document.getElementById("trade-market-type").value.trim(),
    idempotency_key: document.getElementById("trade-idempotency").value.trim(),
    timeslots: [{ slot: "09:00-09:15", volume_mwh: 12.5, price: 420 }],
  };

  if (!payload.province_code || !payload.trade_date) {
    toast.warning("请填写必填字段");
    return;
  }

  const btn = document.getElementById("btn-trade-submit");
  btn.innerHTML = '<span class="loading-spinner"></span> 提交中...';
  btn.disabled = true;

  const resp = await api.post("/api/v1/trades/declarations", payload);

  btn.innerHTML = '<i class="fas fa-paper-plane btn-icon"></i> 提交申报';
  btn.disabled = false;

  if (resp?.success) {
    toast.success("申报提交成功！");
    // 生成新的幂等键
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    document.getElementById("trade-idempotency").value = `dec-${date}-ui-${Date.now().toString().slice(-6)}`;
  } else {
    toast.error(resp?.message || "申报提交失败");
  }

  write("trade-result", resp);
});

async function loadTrades() {
  const btn = document.getElementById("btn-trade-list");
  btn.innerHTML = '<span class="loading-spinner"></span> 查询中...';
  btn.disabled = true;

  const resp = await api.get("/api/v1/trades/declarations?page_no=1&page_size=20");

  btn.innerHTML = '<i class="fas fa-list btn-icon"></i> 查询申报列表';
  btn.disabled = false;

  if (resp?.success) {
    toast.info(`找到 ${resp.data?.total || 0} 条申报记录`);
    const columns = [
      { key: "declaration_id", label: "申报ID" },
      { key: "org_id", label: "组织ID" },
      { key: "province_code", label: "省份" },
      { key: "rule_version", label: "规则版本" },
      { key: "trade_date", label: "交易日期" },
      { key: "market_type", label: "市场类型" },
      {
        key: "status",
        label: "状态",
        render: (v) => {
          const m = { submitted: "tag-blue", confirmed: "tag-green", rejected: "tag-red" };
          return '<span class="tag ' + (m[v] || "") + '">' + _formatCell(v) + "</span>";
        },
      },
      { key: "created_at", label: "创建时间" },
    ];
    renderTable("trade-list-result", resp.data, columns, "暂无申报记录");
  } else if (!resp?.networkError) {
    toast.error("查询失败: " + (resp?.message || "未知错误"));
  }
}

document.getElementById("btn-trade-list").addEventListener("click", loadTrades);

// ── 风险管理 ─────────────────────────────────────────────────

document.getElementById("btn-risk").addEventListener("click", async () => {
  const province = document.getElementById("risk-province").value.trim();
  const tradeDate = document.getElementById("risk-date").value.trim();
  const orgId = document.getElementById("risk-org-id").value.trim();

  if (!province || !tradeDate) {
    toast.warning("请填写省份和日期");
    return;
  }

  const btn = document.getElementById("btn-risk");
  btn.innerHTML = '<span class="loading-spinner"></span> 查询中...';
  btn.disabled = true;

  const params = new URLSearchParams({
    province_code: province,
    trade_date: tradeDate,
    org_id: orgId
  });
  const resp = await api.get(`/api/v1/risk/deviation?${params.toString()}`);

  btn.innerHTML = '<i class="fas fa-search btn-icon"></i> 查询风险';
  btn.disabled = false;

  write("risk-result", resp);

  if (resp?.success && resp?.data) {
    const card = document.getElementById("risk-result-card");
    const badge = document.getElementById("risk-level-badge");
    const level = resp.data.deviation_risk_level;
    const levelLabels = { low: "低风险", medium: "中等风险", high: "高风险" };
    const levelIcons = { low: "fa-check-circle", medium: "fa-exclamation-circle", high: "fa-exclamation-triangle" };

    badge.innerHTML = `<i class="fas ${levelIcons[level] || 'fa-info-circle'}"></i> ${levelLabels[level] || level}`;
    badge.className = `risk-level-badge ${level}`;
    card.classList.remove("hidden");

    document.getElementById("risk-ratio").textContent = `${(resp.data.deviation_ratio * 100).toFixed(2)}%`;
    document.getElementById("risk-cost").textContent = `¥${resp.data.expected_deviation_cost?.toFixed(2) || '—'}`;
    document.getElementById("risk-rule-version").textContent = resp.data.rule_version || "—";

    // 根据风险等级显示通知
    if (level === 'high') {
      toast.warning("检测到高风险，请关注！");
    } else if (level === 'medium') {
      toast.info("当前风险等级为中等");
    } else {
      toast.success("风险状态正常");
    }
  } else {
    toast.error("风险查询失败");
    document.getElementById("risk-result-card").classList.add("hidden");
  }
});

// ── 结算对账 ─────────────────────────────────────────────────

document.getElementById("btn-settle-create").addEventListener("click", async () => {
  const payload = {
    org_id: Number(document.getElementById("settle-org-id").value.trim()),
    province_code: document.getElementById("settle-province").value.trim(),
    cycle_start: document.getElementById("settle-start").value.trim(),
    cycle_end: document.getElementById("settle-end").value.trim(),
  };

  if (!payload.org_id || !payload.province_code) {
    toast.warning("请填写必填字段");
    return;
  }

  const btn = document.getElementById("btn-settle-create");
  btn.innerHTML = '<span class="loading-spinner"></span> 创建中...';
  btn.disabled = true;

  const resp = await api.post("/api/v1/settlement/reconcile/tasks", payload);

  btn.innerHTML = '<i class="fas fa-play btn-icon"></i> 创建结算任务';
  btn.disabled = false;

  if (resp?.success) {
    toast.success("结算任务创建成功！");
    // 自动填充汇总报告 task_id
    if (resp?.data?.task_id) {
      document.getElementById("settle-summary-task-id").value = resp.data.task_id;
    }
  } else {
    toast.error(resp?.message || "结算任务创建失败");
  }

  write("settle-result", resp);
});

document.getElementById("btn-settle-list").addEventListener("click", async () => {
  const btn = document.getElementById("btn-settle-list");
  btn.innerHTML = '<span class="loading-spinner"></span> 查询中...';
  btn.disabled = true;

  const resp = await api.get("/api/v1/settlement/reconcile/tasks?page_no=1&page_size=20");

  btn.innerHTML = '<i class="fas fa-list btn-icon"></i> 查询任务列表';
  btn.disabled = false;

  if (resp?.success) {
    toast.info(`找到 ${resp.data?.total || 0} 条结算任务`);
    const columns = [
      { key: "task_id", label: "任务ID" },
      { key: "org_id", label: "组织ID" },
      { key: "province_code", label: "省份" },
      { key: "rule_version", label: "规则版本" },
      { key: "cycle_start", label: "周期开始" },
      { key: "cycle_end", label: "周期结束" },
      {
        key: "status",
        label: "状态",
        render: (v) => {
          const m = { queued: "tag-yellow", running: "tag-blue", completed: "tag-green", failed: "tag-red" };
          return '<span class="tag ' + (m[v] || "") + '">' + _formatCell(v) + "</span>";
        },
      },
      { key: "message", label: "备注" },
      { key: "created_at", label: "创建时间" },
    ];
    renderTable("settle-result", resp.data, columns, "暂无结算任务");
  } else if (!resp?.networkError) {
    toast.error("查询失败: " + (resp?.message || "未知错误"));
  }
});

document.getElementById("btn-settle-summary").addEventListener("click", async () => {
  const taskId = document.getElementById("settle-summary-task-id").value.trim();
  if (!taskId) {
    toast.warning("请输入任务ID（可从上方任务列表中复制）");
    return;
  }

  const btn = document.getElementById("btn-settle-summary");
  btn.innerHTML = '<span class="loading-spinner"></span> 查询中...';
  btn.disabled = true;

  const resp = await api.get(`/api/v1/settlement/reconcile/tasks/${taskId}/summary`);

  btn.innerHTML = '<i class="fas fa-chart-pie btn-icon"></i> 查询汇总报告';
  btn.disabled = false;

  write("settle-summary-result", resp);

  if (resp?.success && resp?.data) {
    const d = resp.data;
    document.getElementById("summary-declarations").textContent = d.total_declarations ?? "—";
    document.getElementById("summary-volume").textContent =
      d.total_volume_mwh != null ? Number(d.total_volume_mwh).toFixed(2) + " MWh" : "—";
    document.getElementById("summary-avg-price").textContent =
      d.avg_price != null ? "¥" + Number(d.avg_price).toFixed(4) : "—";
    document.getElementById("summary-contract-vol").textContent =
      d.contract_volume_mwh != null ? Number(d.contract_volume_mwh).toFixed(2) + " MWh" : "—";

    const dev = d.deviation_mwh;
    const devText =
      dev === null || dev === undefined
        ? "—"
        : dev === 0
        ? "无偏差"
        : (dev > 0 ? "+" : "") + Number(dev).toFixed(2) + " MWh";
    const devEl = document.getElementById("summary-deviation");
    devEl.textContent = devText;
    if (dev > 0) devEl.className = "risk-high";
    else if (dev < 0) devEl.className = "risk-medium";
    else devEl.className = "";

    // 渲染日汇总表格
    renderDailySummaryTable("summary-daily-table", d.daily_summary || []);

    document.getElementById("settle-summary-card").classList.remove("hidden");
    document.getElementById("settle-summary-card").style.animation = "fadeIn 0.3s ease";
    toast.success("汇总报告已生成");
  } else if (!resp?.networkError) {
    toast.error("汇总报告查询失败: " + (resp?.message || "未知错误"));
    document.getElementById("settle-summary-card").classList.add("hidden");
  }
});

// ── 市场价格 ─────────────────────────────────────────────────

document.getElementById("btn-market").addEventListener("click", async () => {
  const province = document.getElementById("market-province").value.trim();
  if (!province) {
    toast.warning("请输入省份代码");
    return;
  }

  const btn = document.getElementById("btn-market");
  btn.innerHTML = '<span class="loading-spinner"></span> 查询中...';
  btn.disabled = true;

  const marketDate = document.getElementById("market-date").value.trim();
  const params = new URLSearchParams({ province_code: province });
  if (marketDate) params.set("market_date", marketDate);

  const resp = await api.get(`/api/v1/market/prices?${params.toString()}`);

  btn.innerHTML = '<i class="fas fa-search btn-icon"></i> 查询市场价格';
  btn.disabled = false;

  if (resp?.success) {
    toast.success("市场价格查询成功");
    renderPriceTable("market-result", resp.data);
  } else if (!resp?.networkError) {
    toast.error("市场价格查询失败: " + (resp?.message || "未知错误"));
  }
});

// ── 审计日志 ─────────────────────────────────────────────────

async function loadAuditLogs() {
  const btn = document.getElementById("btn-audit-refresh");
  btn.innerHTML = '<span class="loading-spinner"></span>';
  btn.disabled = true;

  const action = document.getElementById("audit-action-filter").value;
  const params = new URLSearchParams({ page_no: 1, page_size: 30 });
  if (action) params.set("action", action);

  const resp = await api.get(`/api/v1/audit/logs?${params.toString()}`);

  btn.innerHTML = '<i class="fas fa-sync-alt btn-icon"></i> 刷新日志';
  btn.disabled = false;

  if (resp?.success) {
    toast.info(`加载了 ${resp.data?.total || 0} 条日志`);
    const actionLabels = {
      trade_declaration_create: "交易申报",
      reconcile_task_create: "创建结算任务",
      reconcile_task_status_update: "更新结算状态",
      contract_create: "创建合同",
      contract_status_update: "更新合同状态",
    };
    const columns = [
      { key: "id", label: "ID" },
      { key: "org_id", label: "组织" },
      {
        key: "action",
        label: "操作类型",
        render: (v) =>
          '<span class="tag tag-blue">' + (actionLabels[v] || _formatCell(v)) + "</span>",
      },
      { key: "resource_type", label: "资源类型" },
      { key: "resource_id", label: "资源ID" },
      {
        key: "details_json",
        label: "操作详情",
        render: (v) => {
          try {
            const obj = JSON.parse(v);
            return JSON.stringify(obj);
          } catch {
            return _formatCell(v);
          }
        },
      },
      { key: "created_at", label: "时间" },
    ];
    renderTable("audit-result", resp.data, columns, "暂无审计日志");
  } else if (!resp?.networkError) {
    toast.error("审计日志加载失败: " + (resp?.message || "未知错误"));
  }
}

document.getElementById("btn-audit-refresh").addEventListener("click", loadAuditLogs);
document.getElementById("audit-action-filter").addEventListener("change", loadAuditLogs);

// ── 初始化 ─────────────────────────────────────────────────

// 初始化 Toast 系统
toast.init();

async function checkBackendAndBanner() {
  if (location.protocol === "file:") return;
  const el = document.getElementById("api-env-banner");
  if (!el) return;
  try {
    const r = await fetch(apiUrl("/api/v1/health"), { method: "GET" });
    if (!r.ok) throw new Error("health not ok");
    el.classList.add("hidden");
    el.innerHTML = "";
  } catch {
    el.classList.remove("hidden");
    el.innerHTML =
      "<strong>后端未响应（连接被拒绝）。</strong> 请先在 <code>backend</code> 目录启动 API，或运行项目里的 <code>start-backend.ps1</code>，然后在浏览器打开 <a href=\"http://127.0.0.1:8000/console/\">http://127.0.0.1:8000/console/</a>。";
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  console.log("电力交易平台控制台已加载", { apiBase: getApiBase() || "(同源)" });
  await checkBackendAndBanner();
  loadSsoConfigHint();
  loadDashboard();
});
