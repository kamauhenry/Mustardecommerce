/* eslint-disable vue/multi-word-component-names */
import './assets/main.css'
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import createMyRouter from './router'; // Import function
import axios from 'axios';

const app = createApp(App);
const pinia = createPinia();
const router = createMyRouter(); // EXECUTE the function
app.config.globalProperties.$axios = axios;
app.use(pinia);
app.use(router); // Use the initialized router
app.mount('#app');
