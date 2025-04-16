/* eslint-disable vue/multi-word-component-names */
import './assets/main.css';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import createMyRouter from './router/index';
import createAdminRouter from './router/admin';
import axios from 'axios';
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';

// Create Pinia instance
const pinia = createPinia();

// Function to initialize and mount an app
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
    theme: 'colored', // or 'light', 'dark'
  });

  // Global error handler
  app.config.errorHandler = (err, vm, info) => {
    console.error('Vue Error:', err);
    console.error('Component:', vm);
    console.error('Info:', info);
  };

  // Mount the app
  app.mount(mountPoint);
};

// Load Google Analytics based on cookie consent
function loadGoogleAnalytics() {
  if (localStorage.getItem('cookieConsent') === 'accepted') {
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=G-4HWLRPEN7Y';
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag() {
      window.dataLayer.push(arguments);
    }
    gtag('js', new Date());
    gtag('config', 'G-4HWLRPEN7Y');
  }
}

// Load GA on initial mount
loadGoogleAnalytics();

// Determine which app to mount based on the URL path
const path = window.location.pathname;

// Mount the admin app for /admin-page routes
if (path.startsWith('/admin-page')) {
  const adminRouter = createAdminRouter();
  initializeApp(adminRouter, '#admin-app');
} else {
  // Mount the main app for all other routes
  const mainRouter = createMyRouter();
  initializeApp(mainRouter, '#app');
}