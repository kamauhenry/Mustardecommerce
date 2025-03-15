import { defineStore } from 'pinia';
import axios from 'axios';

console.log('Loading auth.js with re_password [March 15, 2025 - Final]');

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
  }),
  actions: {
    async login({ email, password }) {
      try {
        console.log('Login called with:', { email, password });
        const response = await axios.post('/api/auth/token/login/', { email, password });
        this.token = response.data.auth_token;
        const userResponse = await axios.get('/api/auth/users/me/', {
          headers: { Authorization: `Token ${this.token}` },
        });
        this.user = userResponse.data;
        localStorage.setItem('token', this.token);
        localStorage.setItem('user', JSON.stringify(this.user));
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`;
      } catch (error) {
        console.error('Login failed:', error.response?.data || error.message);
        throw error;
      }
    },
    async register({ firstName, lastName, companyName, email, password }) {
      try {
        console.log('Register action called with:', { firstName, lastName, companyName, email, password });
        const payload = {
          email,
          password,
          re_password: password,
          first_name: firstName,
          last_name: lastName,
          location: companyName || '',
        };
        console.log('Registration payload before sending:', JSON.stringify(payload, null, 2));
        const config = { data: payload };
        console.log('Axios config before sending:', JSON.stringify(config, null, 2));
        const response = await axios.post('/api/auth/users/', payload);
        console.log('Registration response:', response.data);
        await this.login({ email, password });
      } catch (error) {
        console.error('Registration failed:', error.response?.data || error.message);
        throw error;
      }
    },
    async logout() {
      try {
        await axios.post('/api/auth/token/logout/', {}, {
          headers: { Authorization: `Token ${this.token}` },
        });
        this.user = null;
        this.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        delete axios.defaults.headers.common['Authorization'];
      } catch (error) {
        console.error('Logout failed:', error.response?.data || error.message);
      }
    },
    initializeAuth() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`;
      }
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user,
  },
});
