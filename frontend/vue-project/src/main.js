/* eslint-disable vue/multi-word-component-names */
import './assets/main.css';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import createMyRouter from './router/index';
import axios from 'axios';
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';
import { useEcommerceStore } from '@/stores/ecommerce'; // Import here to define the store

// Create Pinia instance
const pinia = createPinia();

// Create the router instance
const router = createMyRouter(pinia);

// Function to initialize and mount the app
const initializeApp = (router, mountPoint) => {
  const app = createApp(App);
  app.config.globalProperties.$axios = axios;

  // Use Pinia and router
  app.use(pinia);
  app.use(router);

  // Access the store after Pinia is initialized
  const store = useEcommerceStore(pinia); // Pass the pinia instance to ensure initialization
  if (store.authToken && !store.apiInstance) {
    store.initializeApiInstance();
  }

  app.use(toast, {
    autoClose: 5000,
    position: 'top-right',
    transition: 'bounce',
    maxToasts: 20,
    newestOnTop: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    closeOnClick: true,
    theme: 'colored',
  });

  app.config.errorHandler = (err, vm, info) => {
    console.error('Vue Error:', err);
    console.error('Component:', vm?.$options?.name || 'Unknown');
    console.error('Info:', info);
    const errorMessage = err.message || 'An unexpected error occurred';
    if (app.config.globalProperties.$toast) {
      app.config.globalProperties.$toast.error(`App error: ${errorMessage}`);
    } else {
      console.error(`App error (toast unavailable): ${errorMessage}`);
    }
  };

  app.mount(mountPoint);
};

// Mount the app
initializeApp(router, '#app');
