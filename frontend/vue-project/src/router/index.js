import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/HomePage.vue';
import MOQCampaigns from '@/views/MOQCampaigns.vue';
import Profile from '@/views/Profile.vue';
import Orders from '@/views/Orders.vue';
import About from '@/views/About.vue';
import Contact from '@/views/Contact.vue';
import Cart from '@/views/Cart.vue';
import CategoryPage from '@/views/CategoryPage.vue';
import ProductDetails from '@/components/home/categories/ProductDetails.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/moq-campaigns', component: MOQCampaigns },
  { path: '/profile', component: Profile },
  { path: '/orders', component: Orders },
  { path: '/about', component: About },
  { path: '/contact', component: Contact },
  { path: '/cart', component: Cart },
  {
    path: "/category/:categoryId",
    name: "Category",
    component: CategoryPage,
  },
  {
    path: "/product/:category_slug/:product_slug",
    name: "ProductDetails",
    component: ProductDetails,
  },
  { path: '/:catchAll(.*)', redirect: '/' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
