import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/modules/auth';

// Main app components
import ResetPassword from '@/components/auth/ResetPassword.vue';
import Home from '@/views/HomePage.vue';
import MOQCampaigns from '@/views/MOQCampaigns.vue';
import Profile from '@/views/Profile.vue';
import Orders from '@/views/Orders.vue';
import About from '@/views/About.vue';
import Contact from '@/views/Contact.vue';
import Cart from '@/views/Cart.vue';
import CategoriesPage from '@/views/CategoryProducts.vue';
import ProductDetails from '@/views/ProductDetails.vue';
import CompletedOrders from '@/views/CompletedOrders.vue';
import SearchResults from '@/views/SearchResults.vue';
import Confirmation from '@/views/Confirmation.vue';
import Checkout from '@/views/Checkout.vue';
import PayandPick from '@/views/payandpick.vue'
import PrivacyPolicy from '@/pages/PrivacyPolicy.vue';
import CookiePolicy from '@/pages/CookiePolicy.vue';

import OrderDetails from '@/views/OrderDetails.vue';

// Admin components
import AdminDashboard from '@/components/admin/Dashboard.vue';
import Settings from '@/components/admin/Settings.vue';
import Products from '@/components/admin/Products.vue';
import AdminOrders from '@/components/admin/Orders.vue';

import Categories from '@/components/admin/Categories.vue';
import LoginAdmin from '@/components/admin/LoginAdmin.vue';
import RegistrationAdmin from '@/components/admin/RegisterAdmin.vue';

const routes = [
  // **Main App Routes**
  { path: '/', component: Home },
  { path: '/pay-and-pick', component: PayandPick },
  { path: '/moq-campaigns', component: MOQCampaigns },
  { path: '/SearchResults', component: SearchResults, name: 'search-results' },
  { path: '/profile', component: Profile },
  { path: '/reset-password/:token', name: 'ResetPassword', component: ResetPassword },
  { path: '/orders', component: Orders },
  { path: '/completed-orders', component: CompletedOrders },
  { path: '/about', component: About },
  { path: '/contact', component: Contact },
  { path: '/cart', component: Cart },
  {
    path: '/Checkout',
    name: 'Checkout',
    component: Checkout,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/orders/:orderId',
    name: 'OrderDetailsCustomer',
    component: OrderDetails,
    meta: { requiresAuth: true },
  },
  {
    path: '/checkout/confirmation',
    name: 'checkout-confirmation',
    component: Confirmation,
    meta: { requiresAuth: true },
  },
  { path: '/category/:categorySlug', component: MOQCampaigns, props: true },
  { path: '/category/:categorySlug/products', component: CategoriesPage, props: true },
  { path: '/product/:categorySlug/:productSlug', name: 'product-detail', component: ProductDetails, props: true },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy,
  },
  {
    path: '/cookie-policy',
    name: 'CookiePolicy',
    component: CookiePolicy,
  },

  // **Admin Routes**
  {
    path: '/admin-page/dashboard',
    name: 'admin_dashboard',
    component: AdminDashboard,
    meta: { requiresAdmin: true },
    beforeEnter: (to, from, next) => {
      const authStore = useAuthStore();
      if (authStore.isAdmin) {
        next();
      } else {
        next('/admin-page/login');
      }
    },
  },
  { path: '/admin-page/settings', component: Settings, meta: { requiresAdmin: true } },
  { path: '/admin-page/products', component: Products, meta: { requiresAdmin: true } },
  { path: '/admin-page/orders', component: AdminOrders, meta: { requiresAdmin: true } },
  { path: '/admin-page/categories', component: Categories, meta: { requiresAdmin: true } },
  { path: '/admin-page/login', component: LoginAdmin, meta: { requiresGuest: true } },
  { path: '/admin-page/register', component: RegistrationAdmin, meta: { requiresGuest: true } },
  { path: '/admin-page', redirect: '/admin-page/login' },
  {
    path: '/admin-page/orders/:orderId',
    name: 'OrderDetailsAdmin',
    component: OrderDetails,
    meta: { requiresAdmin: true },
  },
  // **Catch-All Route**
  { path: '/:catchAll(.*)', redirect: '/' },
];

export default function createMyRouter(pinia) {
  const router = createRouter({
    history: createWebHistory(),
    routes,
  });

  // Navigation Guard
  router.beforeEach(async (to, from, next) => {
    // Pass API and media requests to the backend
    if (to.path.startsWith('/api/') || to.path.startsWith('/media/')) {
      window.location.href = to.fullPath;
      return;
    }

    const authStore = useAuthStore(pinia);

    // Ensure user info is fetched if authenticated
    if (authStore.isAuthenticated && !authStore.user) {
      try {
        await authStore.fetchCurrentUserInfo();
      } catch (error) {
        console.error('Failed to fetch user info:', error);
        authStore.logout();
      }
    }

    // Admin Routes
    if (to.meta.requiresAdmin) {
      if (authStore.isAuthenticated && authStore.isAdmin) {
        next();
      } else {
        next('/admin-page/login');
      }
    }
    // Guest Routes
    else if (to.meta.requiresGuest) {
      if (authStore.isAuthenticated && authStore.isAdmin) {
        next('/admin-page/dashboard');
      } else {
        next();
      }
    }
    // Authenticated Routes
    else if (to.meta.requiresAuth) {
      if (authStore.isAuthenticated) {
        next();
      } else {
        next('/');
      }
    }
    // Public Routes
    else {
      next();
    }
  });

  return router;
}