import './assets/main.css';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createHead } from '@vueuse/head';
import App from './App.vue';
import createMyRouter from './router/index';
import axios from 'axios';
import Vue3Toastify, { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';
import { useEcommerceStore } from '@/stores/ecommerce';

const pinia = createPinia();
const router = createMyRouter(pinia);
const head = createHead();

const initializeApp = (router, mountPoint) => {
  const app = createApp(App);
  app.config.globalProperties.$axios = axios;

  app.use(pinia);
  app.use(router);
  app.use(head); // Add vueuse/head
  app.use(Vue3Toastify, {
    position: 'top-right',
    transition: 'bounce',
    maxToasts: 5,
    newestOnTop: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    closeOnClick: true,
    theme: 'colored',
  });

  const store = useEcommerceStore(pinia);
  if (store.authToken && !store.apiInstance) {
    console.log('Initializing apiInstance in main.js');
    store.initializeApiInstance();
  }

  app.config.errorHandler = (err, vm, info) => {
    console.error('Vue Error:', err);
    console.error('Component:', vm?.$options?.name || 'Unknown');
    console.error('Info:', info);
    console.error('Error stack:', err.stack);
    if (err.message.includes('Network Error') || err.message.includes('timeout')) {
      console.log('Showing toast: Network issue:', err.message);
      toast.error(`Network issue: ${err.message}`, { autoClose: 5000 });
    } else {
      console.log('Unhandled error, not showing toast:', err.message);
    }
  };

  app.mount(mountPoint);
};

initializeApp(router, '#app');