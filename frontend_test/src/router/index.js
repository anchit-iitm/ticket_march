import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import test_page from '@/views/test_page.vue'
// import something from '@/assests/something'
import login from '@/views/login.vue'
import dashboard from '@/views/dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/test_page',
    name: 'test',
    component: test_page
  },
  {
    path: '/login',
    name: 'login',
    component: login
  },
  {
    path: '/register',
    name: 'register',
    component: () => import(/* webpackChunkName: "register" */ '../views/register.vue')
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: dashboard,
    // component: () =>
      // import(/* webpackChunkName: "Dashboard" */ "../views/Dashboard.vue"),
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
