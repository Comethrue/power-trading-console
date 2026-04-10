import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'auth', name: 'Auth', component: () => import('@/views/AuthView.vue') },
      { path: 'contracts', name: 'Contracts', component: () => import('@/views/ContractsView.vue') },
      { path: 'trades', name: 'Trades', component: () => import('@/views/TradesView.vue') },
      { path: 'risk', name: 'Risk', component: () => import('@/views/RiskView.vue') },
      { path: 'settlement', name: 'Settlement', component: () => import('@/views/SettlementView.vue') },
      { path: 'market', name: 'Market', component: () => import('@/views/MarketView.vue') },
      { path: 'external', name: 'External', component: () => import('@/views/ExternalView.vue') },
      { path: 'rules', name: 'Rules', component: () => import('@/views/RulesView.vue') },
      { path: 'audit', name: 'Audit', component: () => import('@/views/AuditView.vue') },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router