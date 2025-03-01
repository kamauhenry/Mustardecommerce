import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/HomePage.vue";
import MOQCampaigns from "@/views/MOQCampaigns.vue";
import Profile from "@/views/Profile.vue";
import Orders from "@/views/Orders.vue";
import RequestMOQ from "@/components/modals/RequestMOQ.vue";
import TrackOrder from "@/components/modals/TrackOrder.vue";
import About from "@/views/About.vue";
import Contact from "@/views/Contact.vue";
import Cart from "@/views/Cart.vue";
import CategoryPage from "@/views/CategoryPage.vue"; // Import Category Page

const routes = [
  { path: "/", component: Home },
  { path: "/moq-campaigns", component: MOQCampaigns },
  { path: "/profile", component: Profile },
  { path: "/orders", component: Orders },
  { path: "/request-moq", component: RequestMOQ },
  { path: "/track-order", component: TrackOrder },
  { path: "/about", component: About },
  { path: "/contact", component: Contact },
  { path: "/cart", component: Cart },
  { path: "/category/:categoryName", component: CategoryPage, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
