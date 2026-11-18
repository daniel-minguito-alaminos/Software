import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AccountView from '../views/AccountView.vue'
import AppView from '../views/AppView.vue'
import { loadSession } from '../auth/session'
import SetPasswordView from '../views/SetPasswordView.vue'
import CheckHistoryView from '../views/CheckHistoryView.vue'
import CheckDetailsView from '../views/CheckDetailsView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomeView },
    { path: '/login', component: AccountView, meta: { guestOnly: true } },
    { path: '/register', component: AccountView, props: { register: true } },
    { path: '/set-password', component: SetPasswordView },
    { path: '/app', component: AppView, meta: { requiresAuth: true } },
    { path: '/app/checks', name: 'check-history', component: CheckHistoryView, meta: { requiresAuth: true },},
    { path: '/app/checks/:id', name: 'check-details', component: CheckDetailsView, meta: { requiresAuth: true }, },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

// BIZ-32: protected pages need a session; logged-in users skip the login page.
router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    // Always ask the backend, so an expired session is noticed immediately.
    const user = await loadSession({ force: true })
    if (!user) return { path: '/login', query: { redirect: to.fullPath } }
  } else if (to.meta.guestOnly) {
    const user = await loadSession()
    if (user) return '/app'
  }
})

export default router
