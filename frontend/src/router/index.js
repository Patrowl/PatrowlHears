import Vue from 'vue'
import VueRouter from 'vue-router'

import AuthLayout from '@/components/layouts/AuthLayout.vue'
import AppPublicLayout from '@/components/layouts/AppPublicLayout.vue'
import UserRegistrationLayout from '@/components/layouts/UserRegistrationLayout.vue'
// import UserAuth from '@/components/pages/UserAuth'

import AppLayout from '@/components/layouts/AppLayout.vue'
import Homepage from '@/components/pages/Homepage'
import Alerts from '@/components/pages/Alerts'
import Ratings from '@/components/pages/Ratings'
import Settings from '@/components/pages/Settings'
import Search from '@/components/pages/Search'
import SearchPublic from '@/components/pages/SearchPublic'
import Vulns from '@/components/pages/Vulns'
import VulnsPublic from '@/components/pages/VulnsPublic'
import VulnDetails from '@/components/pages/VulnDetails'
import VulnDetailsPublic from '@/components/pages/VulnDetailsPublic'
import Exploits from '@/components/pages/Exploits'
import KBVendors from '@/components/pages/KB/Vendors'
import KBProducts from '@/components/pages/KB/Products'
import Monitoring from '@/components/pages/Monitoring'
import VendorsProducts from '@/components/pages/VendorsProducts'
import VendorDetails from '@/components/pages/VendorDetails'
import ProductDetails from '@/components/pages/ProductDetails'
import Packages from '@/components/pages/Packages'
import PackageDetails from '@/components/pages/PackageDetails'
// import KBProductVersions from '@/components/pages/KB/ProductVersions'
import KBCVE from '@/components/pages/KB/CVE'
import KBBulletins from '@/components/pages/KB/Bulletins'

import AdvancedSearch from '@/components/pages/AdvancedSearch.vue'

import FirstSteps from '@/components/pages/FirstSteps.vue'
import VulnAddEdit from '@/components/pages/VulnAddEdit.vue'
import UserEdit from '@/components/pages/UserEdit.vue'
import Help from '@/components/pages/Help.vue'
import NotFound from '@/components/general/NotFound.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/auth',
    name: 'AuthLayout',
    component: AuthLayout
  },
  {
    path: '/registration',
    name: 'UserRegistrationLayout',
    component: UserRegistrationLayout
  },
  {
    path: '/',
    component: AppLayout,
    redirect: '/homepage',
    children: [
      { path: 'homepage', name: 'Homepage', component: Homepage },
      { path: 'help', name: 'Help', component: Help },
      { path: 'alerts', name: 'Alerts', component: Alerts },
      { path: 'ratings', name: 'Ratings', component: Ratings },
      { path: 'monitoring', name: 'Monitoring', component: Monitoring },
      { path: 'settings', name: 'Settings', component: Settings },
      { path: 'search', name: 'Search', component: Search },
      { path: 'search/:appsearch', name: 'SearchData', component: Search, props: true },
      { path: '/products', name: 'KBProducts', component: KBProducts },
      { path: 'product', name: 'ProductDetails', component: ProductDetails },
      { path: 'product/:product_id', name: 'ProductDetailsData', component: ProductDetails },
      { path: '/vendors', name: 'VendorsProducts', component: VendorsProducts },
      { path: '/vendor/:vendor_id', name: 'VendorDetails', component: VendorDetails },
      { path: '/packages', name: 'Packages', component: Packages },
      { path: '/packages/:package_id', name: 'PackageDetails', component: PackageDetails },

      // { path: '/kb/vendors', name: 'KBVendors', component: KBVendors },
      // { path: '/kb/vendors/:vendor_name', name: 'KBProductVersions', component: KBProductVersions },
      { path: '/kb/cves', name: 'KBCVE', component: KBCVE },
      { path: '/kb/bulletins', name: 'KBBulletins', component: KBBulletins },
      { path: '/vulns', name: 'Vulns', component: Vulns },
      { path: '/vulns/:vuln_id', name: 'VulnDetails', component: VulnDetails },
      { path: '/exploits', name: 'Exploits', component: Exploits },

      { path: '/test-as', name: 'AdvancedSearch', component: AdvancedSearch },
    ]
  },
  {
    path: '/public',
    component: AppPublicLayout,
    redirect: '/public/vulns',
    children: [
      { path: '/public/search', name: 'SearchPublic', component: SearchPublic },
      { path: '/public/search/:appsearch', name: 'SearchDataPublic', component: SearchPublic, props: true },
      { path: '/public/vulns', name: 'VulnsPublic', component: VulnsPublic },
      { path: '/public/vulns/:vuln_id', name: 'VulnDetailsPublic', component: VulnDetailsPublic },
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
  if (localStorage.getItem('org_id') == null) {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    localStorage.removeItem('is_admin');
    localStorage.removeItem('is_org_admin');
    localStorage.removeItem('orgs');
    localStorage.removeItem('org_id');
    localStorage.removeItem('org_name');
  }

  if (localStorage.getItem('authToken') !== null
    || to.path === '/auth'
    || to.path === '/registration'
    || to.path === '/help'
    || to.path === '/public'
    || to.path.startsWith('/public/vulns')
    || to.path.startsWith('/public/search')
  ) {
    next();
  } else {
    next('/auth');
  }
})

export default router
