import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Estimator',
    component: () => import('../views/EstimatorView.vue'),
  },
  {
    path: '/share/:token',
    name: 'Share',
    component: () => import('../views/ShareView.vue'),
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/admin/Dashboard.vue'),
      },
      {
        path: 'price-params',
        name: 'AdminPriceParams',
        component: () => import('../views/admin/PriceParams.vue'),
      },
      {
        path: 'exhibit-items',
        name: 'AdminExhibitItems',
        component: () => import('../views/admin/ExhibitItems.vue'),
      },
      {
        path: 'suppliers',
        name: 'AdminSuppliers',
        component: () => import('../views/admin/Suppliers.vue'),
      },
      {
        path: 'products',
        name: 'AdminProducts',
        component: () => import('../views/admin/Products.vue'),
      },
      {
        path: 'quotes',
        name: 'AdminQuotes',
        component: () => import('../views/admin/Quotes.vue'),
      },
      {
        path: 'records',
        name: 'AdminRecords',
        component: () => import('../views/admin/Records.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
