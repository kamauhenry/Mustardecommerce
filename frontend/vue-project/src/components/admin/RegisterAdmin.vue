<template>
  <div class="register-admin">
    <h2>Admin Registration</h2>
    <form @submit.prevent="register">
      <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" v-model="form.email" id="email" required />
      </div>
      <div class="form-group">
        <label for="username">Username:</label>
        <input type="text" v-model="form.username" id="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" v-model="form.password" id="password" required />
      </div>
      <button type="submit">Register</button>
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
        username: '',
        password: '',
      },
      error: null,
    };
  },
  methods: {
    async register() {
      try {
        const apiInstance = api.createApiInstance(this.store);
        await api.adminRegister(apiInstance, this.form);
        await this.store.adminLogin({
          email: this.form.email,
          password: this.form.password,
        });
        this.router.push('/admin-page/dashboard');
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed';
      }
    },
  },
};
</script>

<style scoped>
.register-admin {
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
