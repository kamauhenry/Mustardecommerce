import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';
import Toast from 'vue-toastification';
import axios from 'axios';
import 'vue-toastification/dist/index.css';

const app = createApp(App);
const pinia = createPinia();

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

axios.get('http://127.0.0.1:8000/api/csrf/', { withCredentials: true })
  .then(() => {
    console.log('CSRF token fetched successfully');
    console.log('Cookies after CSRF fetch:', document.cookie);
  })
  .catch(error => {
    console.error('Failed to fetch CSRF token:', error);
  });

axios.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrftoken');
  console.log('CSRF token in cookie before request:', csrfToken);
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
    axios.defaults.xsrfCookieName = "csrftoken";
    console.log('X-CSRFToken header set:', csrfToken);
  } else {
    console.warn('No CSRF token found in cookie');
  }
  console.log('Axios request config:', config);
  return config;
}, (error) => {
  return Promise.reject(error);
});

axios.defaults.withCredentials = true;

const toastOptions = {
  position: 'top-right',
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: true,
  closeButton: 'button',
  icon: true,
  rtl: false,
};

app.use(router);
app.use(pinia);
app.use(Toast, toastOptions);
app.config.globalProperties.$axios = axios;

app.mount('#app');
