/**
 * 组织与演示账号的展示文案（不改变后端 org_id / 登录用户名）
 */
const ORG_META = {
  0: { code: 'SYS-ROOT', name: '体系运营管理中心' },
  1001: { code: 'ORG-SPS-2026-001', name: '华南电力交易单元' },
  1002: { code: 'ORG-EPS-2026-002', name: '华东电力交易单元' },
}

export function formatOrgLine(orgId) {
  const n = Number(orgId)
  const m = ORG_META[n]
  if (m) return `${m.name} · ${m.code}`
  if (orgId === null || orgId === undefined || orgId === '') return '—'
  return `交易单元 · ORG-${n}`
}

export function formatOrgCodeOnly(orgId) {
  const n = Number(orgId)
  return ORG_META[n]?.code ?? `ORG-${n}`
}
