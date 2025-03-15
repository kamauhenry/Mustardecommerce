import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/HomePage.vue';
import MOQCampaigns from '@/views/MOQCampaigns.vue';
import Profile from '@/views/Profile.vue';
import Orders from '@/views/Orders.vue';
import About from '@/views/About.vue';
import Contact from '@/views/Contact.vue';
import Cart from '@/views/Cart.vue';
import CategoryPage from '@/views/CategoryPage.vue';
import LoginRegister from '@/components/home/LoginRegister.vue';
import CategoryProducts from '../components/home/CategoryProducts.vue';
import ProductDetails from '../views/ProductDetails.vue';


const routes = [
    { path: '/', component: Home },
    { path: '/moq-campaigns', component: MOQCampaigns },

    { path: '/profile', component: Profile },
    { path: '/orders', component: Orders },
    { path: '/about', component: About },
    { path: '/contact', component: Contact },
    { path: '/cart', component: Cart },
    { path: '/login', component: LoginRegister },
    { path: '/category/:categoryName', component: CategoryPage, props: true },
    {path: '/category/:categoryName/:productId', component: ProductDetails, props: true},
    { path: '/product/:categorySlug/:productSlug', component: ProductDetails, props: true },
    {path: '/category/:categoryName/:categorySlug', component: CategoryPage, props: true},
       // Catch-all route (Only for non-API routes)
    { path: '/:catchAll(.*)', redirect: '/' },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
