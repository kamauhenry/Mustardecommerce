/* eslint-disable vue/multi-word-component-names */
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router';
import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:8000';


const app = createApp(App);
app.use(router);
app.use(createPinia());
app.mount('#app');
