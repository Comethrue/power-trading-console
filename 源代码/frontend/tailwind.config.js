/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          50: '#030508',
          100: '#060d18',
          200: '#0a1528',
          300: '#0e1e38',
          400: '#122648',
          500: '#163058',
          600: '#1a3a68',
          700: '#1e4478',
          800: '#224e88',
          900: '#0a1220',
        },
        // 琥珀/金色主色调
        amber: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        // 翡翠绿
        emerald: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        // 珊瑚橙（用于风险警示）
        coral: {
          400: '#fb7185',
          500: '#f43f5e',
        },
        neon: {
          cyan: '#00e5ff',
          blue: '#2979ff',
          green: '#00e676',
          yellow: '#ffea00',
          orange: '#ff6d00',
          red: '#ff1744',
          // 新增：琥珀/翡翠主题
          amber: '#fbbf24',
          emerald: '#34d399',
          gold: '#f59e0b',
        },
        glow: {
          amber: 'rgba(245, 158, 11, 0.35)',
          emerald: 'rgba(16, 185, 129, 0.35)',
          gold: 'rgba(245, 158, 11, 0.4)',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'PingFang SC', 'Microsoft YaHei', 'sans-serif'],
      },
      boxShadow: {
        'glow-amber': '0 0 18px rgba(245, 158, 11, 0.3), 0 0 36px rgba(245, 158, 11, 0.1)',
        'glow-emerald': '0 0 18px rgba(16, 185, 129, 0.3), 0 0 36px rgba(16, 185, 129, 0.1)',
        'glow-gold': '0 0 22px rgba(245, 158, 11, 0.4), 0 0 44px rgba(245, 158, 11, 0.15)',
        'amber-glow': '0 4px 20px rgba(245, 158, 11, 0.25), 0 0 0 1px rgba(0,0,0,0.15) inset',
        'glow-card': '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05)',
        'inner-glow': 'inset 0 0 30px rgba(245, 158, 11, 0.04)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'grid-pattern': 'linear-gradient(rgba(245,158,11,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(245,158,11,0.025) 1px, transparent 1px)',
        'gold-gradient': 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 50%, #f59e0b 100%)',
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
        'flicker': 'flicker 0.15s infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
        'count-up': 'countUp 1.5s ease-out',
        'border-glow': 'borderGlow 3s ease-in-out infinite',
        'text-shimmer': 'textShimmer 3s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(245,158,11,0.5), 0 0 10px rgba(245,158,11,0.25)' },
          '50%': { boxShadow: '0 0 18px rgba(245,158,11,0.8), 0 0 36px rgba(245,158,11,0.4)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        flicker: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        countUp: {
          '0%': { opacity: '0', transform: 'scale(0.5)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        borderGlow: {
          '0%, 100%': { borderColor: 'rgba(245,158,11,0.25)' },
          '50%': { borderColor: 'rgba(245,158,11,0.7)' },
        },
        textShimmer: {
          '0%': { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' },
        },
      },
    },
  },
  /* 省份标签 provinceBadgeClass() 动态类名，需保留编译 */
  safelist: [
    'bg-emerald-500/10',
    'text-emerald-300',
    'bg-amber-500/10',
    'text-amber-300',
    'bg-rose-500/10',
    'text-rose-300',
    'bg-gray-500/10',
    'text-gray-400',
    'bg-cyan-500/10',
    'text-cyan-300',
    'bg-teal-500/10',
    'text-teal-300',
    'bg-amber-600/10',
    'text-amber-200',
    'bg-lime-500/10',
    'text-lime-300',
  ],
  plugins: [],
}
