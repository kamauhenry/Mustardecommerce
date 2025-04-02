/* eslint-disable vue/multi-word-component-names */
import './assets/main.css'
import { createApp } from 'vue';
import App from './App.vue';
import createMyRouter from './router/index';
import createAdminRouter from './router/admin';
import { createPinia } from 'pinia';
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';

// Create Pinia instance
const pinia = createPinia();

// Function to initialize and mount an app
const initializeApp = (router, mountPoint) => {
  const app = createApp(App);
  app.use(pinia);
  app.use(router);

  app.use(Toast, {
    transition: 'Vue-Toastification__bounce',
    maxToasts: 20,
    newestOnTop: true,
    position: 'top-right',
    timeout: 5000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: 'button',
    icon: true,
    rtl: false,
  });

  // Global error handler
  app.config.errorHandler = (err, vm, info) => {
    console.error('Vue Error:', err);
    console.error('Component:', vm);
    console.error('Info:', info);
  };
  app.mount(mountPoint);
};

// Determine which app to mount based on the URL path
const path = window.location.pathname;

// Mount the admin app for /admin routes
if (path.startsWith('/admin-page')) {
  const adminRouter = createAdminRouter();
  initializeApp(adminRouter, '#admin-app');
} else {
  // Mount the main app for all other routes
  const mainRouter = createMyRouter();
  initializeApp(mainRouter, '#app');
}
