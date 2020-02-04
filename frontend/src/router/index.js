import Vue from 'vue'
import VueRouter from 'vue-router'
// import Home from '../views/Home.vue'

import AuthLayout from '@/components/layouts/AuthLayout.vue'
import UserAuth from '@/components/pages/UserAuth'

import AppLayout from '@/components/layouts/AppLayout.vue'
import Homepage from '@/components/pages/Homepage'
import Vulns from '@/components/pages/Vulns'
import KBVendors from '@/components/pages/KB/Vendors'
import KBCVE from '@/components/pages/KB/CVE'
import KBBulletins from '@/components/pages/KB/Bulletins'

import NotFound from '@/components/general/NotFound.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/auth',
    name: 'AuthLayout',
    component: AuthLayout
  },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: 'homepage', name: 'Homepage', component: Homepage },
      { path: '/kb/vendors', name: 'KBVendors', component: KBVendors },
      { path: '/kb/cves', name: 'KBCVE', component: KBCVE },
      { path: '/kb/bulletins', name: 'KBBulletins', component: KBBulletins },
      { path: '/vulns', name: 'Vulns', component: Vulns },
      // { path: '/scans', name: 'Scans', component: Scans },
      // { path: '/reports', name: 'Reports', component: Reports },
    ]
  },
  {
    path: '*',
    component: NotFound
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  if (localStorage.getItem('authToken') !== null || to.path === '/auth') {
    next()
  } else {
    next('/auth')
  }
})

export default router
