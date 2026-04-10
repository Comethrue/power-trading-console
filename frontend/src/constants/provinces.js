/**
 * 全国电力市场常用「十大重点省份」演示数据（代码 + 中文名）
 * 用于界面展示与种子数据对齐
 */
export const TOP10_POWER_PROVINCES = [
  { code: 'GD', name: '广东' },
  { code: 'JS', name: '江苏' },
  { code: 'ZJ', name: '浙江' },
  { code: 'SD', name: '山东' },
  { code: 'NM', name: '内蒙古' },
  { code: 'HE', name: '河北' },
  { code: 'SC', name: '四川' },
  { code: 'HA', name: '河南' },
  { code: 'HB', name: '湖北' },
  { code: 'AH', name: '安徽' },
]

export function provinceLabel(code) {
  const f = TOP10_POWER_PROVINCES.find((p) => p.code === code)
  return f ? `${f.name} ${code}` : code || '—'
}
