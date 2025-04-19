import { createRouter, createWebHistory } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';

// Main app components
import Home from '@/views/HomePage.vue';
import MOQCampaigns from '@/views/MOQCampaigns.vue';
import Profile from '@/views/Profile.vue';
import Orders from '@/views/Orders.vue';
import OrderDetails from '@/views/OrderDetails.vue';
import About from '@/views/About.vue';
import Contact from '@/views/Contact.vue';
import Cart from '@/views/Cart.vue';
import CategoryPage from '@/views/AllCategories.vue';
import CategoriesPage from '@/views/CategoryProducts.vue';
import ProductDetails from '@/views/ProductDetails.vue';
import CompletedOrders from '@/views/CompletedOrders.vue';
import SearchResults from '@/views/SearchResults.vue';
import Confirmation from '@/views/Confirmation.vue';
import Checkout from '@/views/Checkout.vue';
import PrivacyPolicy from '@/pages/PrivacyPolicy.vue';
import CookiePolicy from '@/pages/CookiePolicy.vue';

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
  { path: '/moq-campaigns', component: MOQCampaigns },
  { path: '/SearchResults', component: SearchResults, name: 'search-results' },
  { path: '/profile', component: Profile },
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
    path: '/checkout/confirmation',
    name: 'checkout-confirmation',
    component: Confirmation,
    meta: { requiresAuth: true },
  },
  {
    path: '/orders/:orderId',
    name: 'OrderDetails',
    component: OrderDetails,
  },
  { path: '/category/:categorySlug', component: CategoryPage, props: true },
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
      const store = useEcommerceStore(); // This will now work after Pinia is initialized
      if (store.isAdmin) {
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

  // **Catch-All Route**
  { path: '/:catchAll(.*)', redirect: '/' },
];

export default function createMyRouter(pinia) {
  const router = createRouter({
    history: createWebHistory(),
    routes,
  });

  // **Navigation Guard**
  router.beforeEach((to, from, next) => {
    // Handle API and media requests by passing them to the backend
    if (to.path.startsWith('/api/') || to.path.startsWith('/media/')) {
      window.location.href = to.fullPath;
      return;
    }

    // Access the store to check authentication status
    const store = useEcommerceStore(pinia); // Use the pinia instance passed from main.js
    const isAuthenticated = store.isAuthenticated;
    const isAdmin = store.isAdmin;

    // **Admin Routes**: Require admin privileges
    if (to.meta.requiresAdmin) {
      if (!isAuthenticated || !isAdmin) {
        next('/admin-page/login');
      } else {
        next();
      }
    }
    // **Guest Routes**: Redirect authenticated admins to dashboard
    else if (to.meta.requiresGuest) {
      if (isAuthenticated && isAdmin) {
        next('/admin-page/dashboard');
      } else {
        next();
      }
    }
    // **Authenticated Routes**: Require user authentication
    else if (to.meta.requiresAuth) {
      if (!isAuthenticated) {
        next('/');
      } else {
        next();
      }
    }
    // **Public Routes**: Allow access
    else {
      next();
    }
  });

  return router;
}
