import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AccountView from '../views/AccountView.vue'

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomeView },
    { path: '/login', component: AccountView },
    { path: '/register', component: AccountView, props: { register: true } },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
