import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/HomePage.vue';
import MOQCampaigns from '@/views/MOQCampaigns.vue';
import Profile from '@/views/Profile.vue';
import Orders from '@/views/Orders.vue';
import RequestMOQ from '@/components/RequestMOQ.vue';
import TrackOrder from '@/components/TrackOrder.vue';
import About from '@/views/About.vue';
import Contact from '@/views/Contact.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/moq-campaigns', component: MOQCampaigns },
  { path: '/profile', component: Profile },
  { path: '/orders', component: Orders },
  { path: '/request-moq', component: RequestMOQ },
  { path: '/track-order', component: TrackOrder },
  { path: '/about', component: About },
  { path: '/contact', component: Contact }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
