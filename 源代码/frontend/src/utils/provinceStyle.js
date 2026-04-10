import { TOP10_POWER_PROVINCES } from '@/constants/provinces'

// 琥珀/翡翠色系配色（不重复）
const PALETTE = [
  'bg-amber-500/10 text-amber-300',
  'bg-emerald-500/10 text-emerald-300',
  'bg-teal-500/10 text-teal-300',
  'bg-cyan-500/10 text-cyan-300',
  'bg-lime-500/10 text-lime-300',
  'bg-amber-600/10 text-amber-200',
  'bg-green-500/10 text-green-300',
  'bg-yellow-500/10 text-yellow-300',
  'bg-cyan-600/10 text-cyan-200',
  'bg-teal-600/10 text-teal-200',
]

/** 列表里省份标签配色 */
export function provinceBadgeClass(code) {
  const idx = TOP10_POWER_PROVINCES.findIndex((p) => p.code === code)
  if (idx < 0) return 'bg-gray-500/10 text-gray-400'
  return PALETTE[idx % PALETTE.length]
}
