export function formatDate(val) {
  if (!val) return '—'
  return String(val).slice(0, 19).replace('T', ' ')
}

export function formatPrice(val) {
  if (val == null) return '—'
  return '¥' + Number(val).toFixed(2)
}

export function formatNumber(val, decimals = 2) {
  if (val == null) return '—'
  return Number(val).toFixed(decimals).replace(/\.?0+$/, '')
}

export function formatPercent(val) {
  if (val == null) return '—'
  return (Number(val) * 100).toFixed(2) + '%'
}

export function statusClass(status) {
  const map = {
    active: 'tag-active',
    completed: 'tag-active',
    submitted: 'tag-info',
    confirmed: 'tag-active',
    queued: 'tag-pending',
    running: 'tag-pending',
    expired: 'tag-expired',
    cancelled: 'tag-expired',
    failed: 'tag-error',
    rejected: 'tag-error',
    pending: 'tag-pending',
    medium: 'tag-pending',
    high: 'tag-error',
    low: 'tag-active',
  }
  return map[status] || 'tag-info'
}

export function statusLabel(status) {
  const map = {
    active: '生效中',
    completed: '已完成',
    submitted: '已提交',
    confirmed: '已确认',
    queued: '排队中',
    running: '进行中',
    expired: '已到期',
    cancelled: '已取消',
    failed: '失败',
    rejected: '已拒绝',
    pending: '待处理',
  }
  return map[status] || status || '—'
}
