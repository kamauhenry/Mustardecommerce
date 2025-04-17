/* eslint-disable vue/multi-word-component-names */
import './assets/main.css';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import createMyRouter from './router/index';
import axios from 'axios';
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';

// Create Pinia instance
const pinia = createPinia();

// Function to initialize and mount the app
const initializeApp = (router, mountPoint) => {
  const app = createApp(App);

  // Add axios globally
  app.config.globalProperties.$axios = axios;

  // Use Pinia and router
  app.use(pinia);
  app.use(router);

  // Configure vue3-toastify
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

  // Global error handler
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

  // Mount the app
  app.mount(mountPoint);
};

// Mount the app with the single router
const router = createMyRouter();
initializeApp(router, '#app');