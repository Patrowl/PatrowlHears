import Vue from 'vue'
import VueRouter from 'vue-router'

import AuthLayout from '@/components/layouts/AuthLayout.vue'
import UserAuth from '@/components/pages/UserAuth'

import AppLayout from '@/components/layouts/AppLayout.vue'
import Homepage from '@/components/pages/Homepage'
import Alerts from '@/components/pages/Alerts'
import Ratings from '@/components/pages/Ratings'
import Settings from '@/components/pages/Settings'
import Search from '@/components/pages/Search'
import Vulns from '@/components/pages/Vulns'
import VulnDetails from '@/components/pages/VulnDetails'
import Exploits from '@/components/pages/Exploits'
import KBVendors from '@/components/pages/KB/Vendors'
import KBProducts from '@/components/pages/KB/Products'
import KBProductVersions from '@/components/pages/KB/ProductVersions'
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
    redirect: '/homepage',
    children: [
      { path: 'homepage', name: 'Homepage', component: Homepage },
      { path: 'alerts', name: 'Alerts', component: Alerts },
      { path: 'ratings', name: 'Ratings', component: Ratings },
      { path: 'settings', name: 'Settings', component: Settings },
      { path: 'search', name: 'Search', component: Search },
      { path: 'search/:appsearch', name: 'SearchData', component: Search, props: true },
      { path: '/kb/products', name: 'KBProducts', component: KBProducts },
      { path: '/kb/vendors', name: 'KBVendors', component: KBVendors },
      { path: '/kb/vendors/:vendor_name', name: 'KBProductVersions', component: KBProductVersions },
      { path: '/kb/cves', name: 'KBCVE', component: KBCVE },
      { path: '/kb/bulletins', name: 'KBBulletins', component: KBBulletins },
      { path: '/vulns', name: 'Vulns', component: Vulns },
      { path: '/vulns/:vuln_id', name: 'VulnDetails', component: VulnDetails },
      { path: '/exploits', name: 'Exploits', component: Exploits },
    ]
  },
  {
    path: '*',
    component: NotFound
  }
]

const router = new VueRouter({
  // mode: 'history',
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
