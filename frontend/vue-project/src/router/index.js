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
import SearchResults from '../views/SearchResults.vue';
import Confirmation from '@/views/Confirmation.vue';
import Checkout from '@/views/Checkout.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/moq-campaigns', component: MOQCampaigns },
  { path: '/SearchResults', component: SearchResults, name:'search-results' },
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
    meta: { requiresAuth: true }
  },
  {
    path: '/checkout/confirmation',
    name: 'checkout-confirmation',
    component: Confirmation,
    meta: { requiresAuth: true }
  },
  { path: '/category/:categorySlug', component: CategoryPage, props: true },
  { path: '/category/:categorySlug/products', component: CategoriesPage, props: true },
  { path: '/product/:categorySlug/:productSlug',name: 'product-detail', component: ProductDetails, props: true },
  { path: '/:catchAll(.*)', redirect: '/' },
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Add navigation guard to exclude /api/* and /media/* from client-side routing
router.beforeEach((to, from, next) => {
  if (to.path.startsWith('/api/') || to.path.startsWith('/media/')) {
    // Let the browser handle the request (i.e., pass it to the backend)
    window.location.href = to.fullPath;
    return;
  }
  next();
});

export default router;
