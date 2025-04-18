import './assets/main.css';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import createMyRouter from './router/index';
import axios from 'axios';
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';
import { useEcommerceStore } from '@/stores/ecommerce';

const pinia = createPinia();
const router = createMyRouter(pinia);

const initializeApp = (router, mountPoint) => {
  const app = createApp(App);
  app.config.globalProperties.$axios = axios;

  app.use(pinia);
  app.use(router);

  const store = useEcommerceStore(pinia);
  if (store.authToken && !store.apiInstance) {
    store.initializeApiInstance();
  }

  app.use(toast, {
    position: 'top-right',
    transition: 'bounce',
    maxToasts: 5, // Reduced to avoid clutter
    newestOnTop: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    closeOnClick: true,
    theme: 'colored',
    // Removed autoClose from global config
  });

  app.config.errorHandler = (err, vm, info) => {
    console.error('Vue Error:', err);
    console.error('Component:', vm?.$options?.name || 'Unknown');
    console.error('Info:', info);
    // Only show toast for network errors
    if (err.message.includes('Network Error') || err.message.includes('timeout')) {
      app.config.globalProperties.$toast.error(`Network issue: ${err.message}`, { autoClose: 5000 });
    }
  };

  app.mount(mountPoint);
};

initializeApp(router, '#app');