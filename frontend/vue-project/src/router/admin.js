
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/components/admin/Dashboard.vue'; // Updated path to match your directory structure
import Settings from '@/components/admin/Settings.vue';
import Products from '@/components/admin/Products.vue';
import Orders from '@/components/admin/Orders.vue';
import Categories from '@/components/admin/Categories.vue';
import LoginAdmin from '@/components/admin/LoginAdmin.vue';
import RegistrationAdmin from '@/components/admin/RegisterAdmin.vue'; // Corrected component name to match file
import { useEcommerceStore } from '@/stores/ecommerce';

const routes = [
  { path: '/admin-page/dashboard', component: Dashboard, meta: { requiresAdmin: true } },
  { path: '/admin-page/settings', component: Settings, meta: { requiresAdmin: true } },
  { path: '/admin-page/products', component: Products, meta: { requiresAdmin: true } },
  { path: '/admin-page/orders', component: Orders, meta: { requiresAdmin: true } },
  { path: '/admin-page/categories', component: Categories, meta: { requiresAdmin: true } },
  { path: '/admin-page/login', component: LoginAdmin, meta: { requiresGuest: true } },
  { path: '/admin-page/register', component: RegistrationAdmin, meta: { requiresGuest: true } },
  { path: '/admin-page', redirect: '/admin-page/login' },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/admin-page/login',
  },
];

const createAdminRouter = () => {
  const router = createRouter({
    history: createWebHistory(),
    routes,
  });

  router.beforeEach((to, from, next) => {
    const store = useEcommerceStore();

    const isAuthenticated = store.isAuthenticated;
    const isAdmin = store.isAdmin();

    if (to.meta.requiresAdmin) {
      if (!isAuthenticated) {
        next('/admin-page/dashboard');
      } else if (!isAdmin) {
        next('/');
      } else {
        next();
      }
    } else if (to.meta.requiresGuest) {
      if (isAuthenticated && isAdmin) {
        next('/admin-page/dashboard');
      } else {
        next();
      }
    } else {
      next();
    }
  });

  return router;
};

export default createAdminRouter;

