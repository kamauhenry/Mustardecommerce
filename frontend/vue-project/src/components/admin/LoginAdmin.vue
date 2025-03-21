<template>
  <div class="login-admin">
    <h2>Admin Login</h2>
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" v-model="form.email" id="email" required />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" v-model="form.password" id="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import { useEcommerceStore } from '@/stores/ecommerce';
import { useRouter } from 'vue-router';
import api from '@/services/api';

export default {
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();

    return { store, router };
  },
  data() {
    return {
      form: {
        email: '',
        password: '',
      },
      error: null,
    };
  },
  methods: {
    async login() {
      try {
        await this.store.adminLogin(this.form);
        this.router.push('/admin-page/dashboard');
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed';
      }
    },
  },
};
</script>

<style scoped>
.login-admin {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background-color: #6f42c1;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #5a32a3;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
