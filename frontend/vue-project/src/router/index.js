import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/HomePage.vue';
import MOQCampaigns from '@/views/MOQCampaigns.vue';
import Profile from '@/views/Profile.vue';
import Orders from '@/views/Orders.vue';
import About from '@/views/About.vue';
import Contact from '@/views/Contact.vue';
import Cart from '@/views/Cart.vue';
import CategoryPage from '@/views/AllCategories.vue';
import CategoriesPage from '@/views/CategoryProducts.vue';
import ProductDetails from '@/views/ProductDetails.vue';
import CompletedOrders from '@/views/CompletedOrders.vue';
import SearchResultsPage from '@/views/SearchResultsPage.vue';
import { useEcommerceStore } from '@/stores/ecommerce';

const routes = [
  { path: '/', component: Home },
  { path: '/moq-campaigns', component: MOQCampaigns },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/orders', component: Orders, meta: { requiresAuth: true } },
  { path: '/completed-orders', component: CompletedOrders, meta: { requiresAuth: true } },
  { path: '/about', component: About },
  { path: '/contact', component: Contact },
  { path: '/cart', component: Cart, meta: { requiresAuth: true } },
  {
    path: '/search-results',
    name: 'SearchResults',
    component: SearchResultsPage,
  },
  { path: '/category/:categorySlug', component: CategoryPage, props: true },
  { path: '/category/:categorySlug/products', component: CategoriesPage, props: true },
  { path: '/products/:categorySlug/:productSlug', component: ProductDetails, props: true },
  { path: '/:catchAll(.*)', redirect: '/' }, // Catch-all redirect for unmatched routes
];

const createMyRouter = () => {
  const router = createRouter({
    history: createWebHistory(),
    routes,
  });

  router.beforeEach((to, from, next) => {
    const store = useEcommerceStore();
    if (to.meta.requiresAuth && !store.isAuthenticated) {
      // Redirect to login if not authenticated (removed /auth)
      window.location.href = '/login';
    } else {
      next();
    }
  });

  return router;
};

export default createMyRouter;
