import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/components/admin/Dashboard.vue';
import Settings from '@/components/admin/Settings.vue';
import Products from '@/components/admin/Products.vue';
import Orders from '@/components/admin/Orders.vue';
import Categories from '@/components/admin/Categories.vue';
import LoginAdmin from '@/components/admin/LoginAdmin.vue';
import RegistrationAdmin from '@/components/admin/RegisterAdmin.vue';
import { useAuthStore } from '@/stores/modules/auth';

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
    const authStore = useAuthStore();
    const isAuthenticated = authStore.isAuthenticated;
    const isAdmin = authStore.isAdmin();

    if (to.meta.requiresAdmin) {
      if (!isAuthenticated || !isAdmin) {
        next('/admin-page/login');
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