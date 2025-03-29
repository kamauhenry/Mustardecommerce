/* eslint-disable vue/multi-word-component-names */
import './assets/main.css'
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import createMyRouter from './router'; // Import function
import axios from 'axios';
import Toast from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-bootstrap.css';

const app = createApp(App);
const pinia = createPinia();
const router = createMyRouter(); // EXECUTE the function
app.config.globalProperties.$axios = axios;
app.use(pinia);
app.use(router); // Use the initialized router
app.use(Toast, {
  transition: 'Vue-Toastification__bounce',
  maxToasts: 20,
  newestOnTop: true,
});
app.mount('#app');
