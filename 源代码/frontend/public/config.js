/**
 * 前端运行时配置文件
 *
 * 说明：
 * - 构建时：GitHub Actions 会通过注入脚本将实际 API 地址写入此文件
 * - 兜底逻辑：如果构建时未注入，则使用下方的默认值
 *
 * API 地址列表：
 *   线上后端：https://power-trading-console.onrender.com
 *   本地后端：http://localhost:8000
 */
window.APP_CONFIG = {
  // API 基础地址（GitHub Actions 构建时会替换此行）
  API_BASE: 'https://power-trading-console.onrender.com',
  // 备用 API 地址（如果主地址不可用时使用）
  API_BASE_FALLBACK: '',
};
