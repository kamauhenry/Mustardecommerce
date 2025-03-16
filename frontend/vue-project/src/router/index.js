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

const routes = [
  { path: '/', component: Home },
  { path: '/moq-campaigns', component: MOQCampaigns },
  { path: '/profile', component: Profile },
  { path: '/orders', component: Orders },
  { path: '/completed-orders', component: CompletedOrders },
  { path: '/about', component: About },
  { path: '/contact', component: Contact },
  { path: '/cart', component: Cart },
  { path: '/category/:categorySlug', component: CategoryPage, props: true },
  { path: '/category/:categorySlug/products', component: CategoriesPage, props: true },
  { path: '/products/:categorySlug/:productSlug', component: ProductDetails, props: true },
  { path: '/:catchAll(.*)', redirect: '/' },
];

// Lazy initialization of router
const createMyRouter = () => {
  return createRouter({
    history: createWebHistory(),
    routes,
  });
};

export default createMyRouter;
