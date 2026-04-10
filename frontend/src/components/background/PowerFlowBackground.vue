<template>
  <div class="fixed inset-0 z-0 pointer-events-none overflow-hidden bg-[#020308]">
    <!-- 深空：近黑 → 深蓝渐变 -->
    <div class="absolute inset-0 bg-gradient-to-b from-[#010205] via-[#050a14] to-[#0a1a32]"></div>
    <div
      class="absolute inset-0 opacity-[0.92] mix-blend-screen"
      style="
        background:
          radial-gradient(ellipse 120% 85% at 12% 18%, rgba(56, 189, 248, 0.14) 0%, transparent 50%),
          radial-gradient(ellipse 90% 70% at 88% 72%, rgba(59, 130, 246, 0.12) 0%, transparent 52%),
          radial-gradient(ellipse 70% 55% at 48% 100%, rgba(14, 165, 233, 0.16) 0%, transparent 48%),
          radial-gradient(ellipse 50% 40% at 70% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 45%);
      "
    ></div>

    <!-- 星空层（静态星点 + 微闪烁） -->
    <div class="absolute inset-0 stars-twinkle opacity-90"></div>

    <!-- 光波纹层（冷色电离层） -->
    <div class="absolute inset-0 opacity-45">
      <div class="ripple-layer ripple-space-a"></div>
      <div class="ripple-layer ripple-space-b"></div>
      <div class="ripple-layer ripple-space-c"></div>
    </div>

    <!-- Canvas：星尘微动 + 电弧 -->
    <canvas ref="canvasRef" class="absolute inset-0 h-full w-full opacity-[0.72]"></canvas>

    <!-- 电流网格 -->
    <div class="absolute inset-0 electric-grid opacity-80"></div>
    <div class="absolute inset-0 electric-diagonal opacity-45"></div>

    <!-- 远处星云光斑 -->
    <div class="absolute -top-40 left-1/4 h-96 w-96 rounded-full bg-sky-500/[0.06] blur-3xl"></div>
    <div class="absolute -bottom-32 right-1/3 h-80 w-80 rounded-full bg-blue-600/[0.05] blur-3xl"></div>
    <div class="absolute top-1/3 right-1/4 h-64 w-64 rounded-full bg-cyan-500/[0.045] blur-3xl"></div>

    <!-- 噪点层 -->
    <div
      class="absolute inset-0 opacity-[0.018]"
      style="
        background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23n)%22/%3E%3C/svg%3E');
      "
    ></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const canvasRef = ref(null)
let raf = 0
let ro = null

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d', { alpha: true })
  if (!ctx) return

  const ripples = []
  const particles = []
  const stars = []

  function rebuildStars() {
    stars.length = 0
    const w = window.innerWidth
    const h = window.innerHeight
    const count = Math.min(220, Math.floor((w * h) / 9000))
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 1.15 + 0.25,
        phase: Math.random() * Math.PI * 2,
        speed: 0.4 + Math.random() * 1.2,
      })
    }
  }

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    const w = window.innerWidth
    const h = window.innerHeight
    canvas.width = Math.floor(w * dpr)
    canvas.height = Math.floor(h * dpr)
    canvas.style.width = `${w}px`
    canvas.style.height = `${h}px`
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    rebuildStars()
  }

  function spawnRipple() {
    ripples.push({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      r: 0,
      maxR: 160 + Math.random() * 240,
      speed: 0.8 + Math.random() * 0.6,
      hue: Math.random() > 0.35 ? 198 : 215,
      born: performance.now(),
    })
  }

  function spawnArc() {
    // 电弧特效：随机起止点
    const x1 = Math.random() * window.innerWidth
    const y1 = Math.random() * window.innerHeight
    const x2 = x1 + (Math.random() - 0.5) * 300
    const y2 = y1 + (Math.random() - 0.5) * 200
    const segs = 8 + Math.floor(Math.random() * 8)
    const pts = [{ x: x1, y: y1 }]
    for (let i = 1; i < segs; i++) {
      const t = i / segs
      pts.push({
        x: x1 + (x2 - x1) * t + (Math.random() - 0.5) * 40,
        y: y1 + (y2 - y1) * t + (Math.random() - 0.5) * 30,
      })
    }
    pts.push({ x: x2, y: y2 })
    particles.push({
      type: 'arc',
      pts,
      life: 1,
      decay: 0.03 + Math.random() * 0.03,
      hue: 188 + Math.random() * 35,
    })
  }

  function ensureParticles(count) {
    while (particles.length < count) {
      particles.push({
        type: 'dot',
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: 1.0 + Math.random() * 2.0,
        phase: Math.random() * Math.PI * 2,
      })
    }
  }

  resize()
  ensureParticles(48)
  for (let i = 0; i < 5; i++) spawnRipple()

  ro = new ResizeObserver(() => resize())
  ro.observe(document.documentElement)

  let lastRipple = performance.now()
  let lastArc = performance.now()
  let last = performance.now()

  function tick(now) {
    const w = window.innerWidth
    const h = window.innerHeight
    const dt = Math.min(0.05, (now - last) / 1000)
    last = now

    ctx.clearRect(0, 0, w, h)

    // 星空微闪烁
    for (const s of stars) {
      s.phase += dt * s.speed
      const tw = 0.25 + 0.75 * (0.5 + 0.5 * Math.sin(s.phase))
      const a = 0.08 * tw
      ctx.fillStyle = `rgba(200, 230, 255, ${a})`
      ctx.beginPath()
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
      ctx.fill()
    }

    // 生成光波纹
    if (now - lastRipple > 2200 + Math.random() * 1800) {
      spawnRipple()
      lastRipple = now
    }

    // 生成电弧
    if (now - lastArc > 1500 + Math.random() * 2000) {
      spawnArc()
      lastArc = now
    }

    // 绘制光波纹
    for (let i = ripples.length - 1; i >= 0; i--) {
      const rp = ripples[i]
      rp.r += rp.speed * (60 * dt)
      const life = 1 - rp.r / rp.maxR
      if (life <= 0) { ripples.splice(i, 1); continue }
      // 外圈
      ctx.beginPath()
      ctx.strokeStyle = `hsla(${rp.hue}, 72%, 60%, ${0.12 * life})`
      ctx.lineWidth = 1.4
      ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2)
      ctx.stroke()
      // 内圈
      ctx.beginPath()
      ctx.strokeStyle = `hsla(${rp.hue + 12}, 85%, 75%, ${0.05 * life})`
      ctx.lineWidth = 0.7
      ctx.arc(rp.x, rp.y, rp.r * 0.9, 0, Math.PI * 2)
      ctx.stroke()
      // 光核
      const radGrad = ctx.createRadialGradient(rp.x, rp.y, 0, rp.x, rp.y, rp.r * 0.15)
      radGrad.addColorStop(0, `hsla(${rp.hue}, 80%, 80%, ${0.08 * life})`)
      radGrad.addColorStop(1, 'rgba(0,0,0,0)')
      ctx.fillStyle = radGrad
      ctx.beginPath()
      ctx.arc(rp.x, rp.y, rp.r * 0.15, 0, Math.PI * 2)
      ctx.fill()
    }

    // 绘制粒子
    for (const p of particles) {
      if (p.type === 'dot') {
        p.x += p.vx
        p.y += p.vy
        p.phase += dt * 1.0
        if (p.x < -20) p.x = w + 20
        if (p.x > w + 20) p.x = -20
        if (p.y < -20) p.y = h + 20
        if (p.y > h + 20) p.y = -20
        const pulse = 0.45 + 0.45 * Math.sin(p.phase)
        const hue = p.phase % (Math.PI * 2) < Math.PI ? 195 : 210
        const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 5)
        g.addColorStop(0, `hsla(${hue}, 80%, 72%, ${0.20 * pulse})`)
        g.addColorStop(0.4, `hsla(${hue}, 60%, 50%, ${0.07 * pulse})`)
        g.addColorStop(1, 'rgba(0,0,0,0)')
        ctx.fillStyle = g
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r * 5, 0, Math.PI * 2)
        ctx.fill()
      } else if (p.type === 'arc') {
        p.life -= p.decay
        if (p.life <= 0) {
          const idx = particles.indexOf(p)
          if (idx !== -1) particles.splice(idx, 1)
          continue
        }
        ctx.beginPath()
        ctx.moveTo(p.pts[0].x, p.pts[0].y)
        for (let i = 1; i < p.pts.length; i++) {
          ctx.lineTo(p.pts[i].x, p.pts[i].y)
        }
        ctx.strokeStyle = `hsla(${p.hue}, 85%, 75%, ${p.life * 0.35})`
        ctx.lineWidth = 1.5 * p.life
        ctx.stroke()
        // 电弧分支
        for (let i = 1; i < p.pts.length - 1; i += 2) {
          const br = p.pts[i]
          ctx.beginPath()
          ctx.moveTo(br.x, br.y)
          ctx.lineTo(br.x + (Math.random() - 0.5) * 30, br.y + (Math.random() - 0.5) * 20)
          ctx.strokeStyle = `hsla(${p.hue + 10}, 90%, 80%, ${p.life * 0.15})`
          ctx.lineWidth = 0.8 * p.life
          ctx.stroke()
        }
      }
    }

    raf = requestAnimationFrame(tick)
  }

  raf = requestAnimationFrame(tick)
})

onUnmounted(() => {
  cancelAnimationFrame(raf)
  ro?.disconnect()
})
</script>

<style scoped>
/* 远景星点（CSS 层，与 Canvas 叠加） */
.stars-twinkle {
  background-image:
    radial-gradient(1px 1px at 8% 12%, rgba(220, 240, 255, 0.85), transparent),
    radial-gradient(1px 1px at 18% 44%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1px 1px at 31% 8%, rgba(186, 230, 253, 0.7), transparent),
    radial-gradient(1px 1px at 42% 63%, rgba(255, 255, 255, 0.35), transparent),
    radial-gradient(1px 1px at 55% 22%, rgba(224, 242, 254, 0.75), transparent),
    radial-gradient(1px 1px at 67% 78%, rgba(255, 255, 255, 0.4), transparent),
    radial-gradient(1px 1px at 78% 35%, rgba(165, 243, 252, 0.65), transparent),
    radial-gradient(1px 1px at 88% 56%, rgba(255, 255, 255, 0.45), transparent),
    radial-gradient(1px 1px at 12% 88%, rgba(224, 242, 254, 0.55), transparent),
    radial-gradient(1px 1px at 92% 12%, rgba(255, 255, 255, 0.5), transparent),
    radial-gradient(1.2px 1.2px at 25% 30%, rgba(255, 255, 255, 0.25), transparent),
    radial-gradient(1.2px 1.2px at 73% 48%, rgba(186, 230, 253, 0.3), transparent),
    radial-gradient(1.2px 1.2px at 48% 91%, rgba(255, 255, 255, 0.22), transparent);
  background-size: 100% 100%;
  animation: star-shimmer 14s ease-in-out infinite;
}

@keyframes star-shimmer {
  0%,
  100% {
    opacity: 0.82;
  }
  50% {
    opacity: 1;
  }
}

/* 电离光波纹 */
.ripple-layer {
  position: absolute;
  inset: -30%;
  border-radius: 50%;
  filter: blur(80px);
  animation: space-ripple 28s ease-in-out infinite;
}

.ripple-space-a {
  background: radial-gradient(
    circle at 28% 38%,
    rgba(56, 189, 248, 0.13) 0%,
    rgba(15, 40, 80, 0.05) 45%,
    transparent 58%
  );
}

.ripple-space-b {
  background: radial-gradient(
    circle at 72% 48%,
    rgba(99, 102, 241, 0.1) 0%,
    transparent 52%
  );
  animation-delay: -9s;
  animation-duration: 34s;
}

.ripple-space-c {
  background: radial-gradient(
    circle at 50% 82%,
    rgba(14, 165, 233, 0.11) 0%,
    transparent 48%
  );
  animation-delay: -16s;
  animation-duration: 31s;
}

@keyframes space-ripple {
  0%,
  100% {
    transform: scale(1) translate(0, 0);
    opacity: 0.72;
  }
  50% {
    transform: scale(1.08) translate(1.5%, -1.2%);
    opacity: 1;
  }
}

/* 电流网格 */
.electric-grid {
  background-image:
    linear-gradient(rgba(56, 189, 248, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.055) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: radial-gradient(ellipse 85% 72% at 50% 42%, black 18%, transparent 100%);
}

.electric-diagonal {
  background: repeating-linear-gradient(
    -28deg,
    transparent,
    transparent 20px,
    rgba(34, 211, 238, 0.045) 20px,
    rgba(34, 211, 238, 0.045) 21px
  );
}
</style>
