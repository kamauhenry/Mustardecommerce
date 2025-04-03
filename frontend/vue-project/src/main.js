/* eslint-disable vue/multi-word-component-names */
import './assets/main.css'
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import Toast from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-bootstrap.css';

const app = createApp(App);
const pinia = createPinia();

app.config.globalProperties.$axios = axios;

app.use(pinia);
app.use(router); // Use the initialized router

app.use(Toast, {
  transition: 'Vue-Toastification__bounce',
  maxToasts: 20,
  newestOnTop: true,
});



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
app.mount('#app');
