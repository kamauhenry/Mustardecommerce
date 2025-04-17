<template>
    <div class="admin-login-container">
      <div class="admin-login-card">
        <h2>Admin Login</h2>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username">Username</label>
            <input
              type="text"
              v-model="username"
              id="username"
              placeholder="Enter your username"
              required
            />
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input
              type="password"
              v-model="password"
              id="password"
              placeholder="Enter your password"
              required
            />
          </div>
          <button type="submit" :disabled="store.loading.auth">
            {{ store.loading.auth ? 'Logging in...' : 'Login' }}
          </button>
        </form>
        <p v-if="error" class="error-message">{{ error }}</p>
        <p class="register-link">
          No account? <router-link to="/admin-page/register">Create one</router-link>
        </p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, nextTick } from 'vue';
  import { useEcommerceStore } from '@/stores/ecommerce';
  import { useRouter } from 'vue-router';
  
  const username = ref('');
  const password = ref('');
  const error = ref(null);
  const store = useEcommerceStore();
  const router = useRouter();
  
  const login = async () => {
    error.value = null;
    try {
        const response = await store.adminLogin({ username: username.value, password: password.value });
        console.log(`Logged in as admin ${response.username}`);
        await nextTick(); // Ensure state updates
        router.push('/admin-page/dashboard');
    } catch (err) {
        error.value = err.response?.data?.error || err.message || 'Admin login failed';
        console.error('Admin login failed:', err);
    }
    };
  </script>
  
  <style scoped>
  .admin-login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f4f4f4;
  }
  
  .admin-login-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
  }
  
  .admin-login-card h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #333;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #555;
  }
  
  .form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }
  
  .form-group input.input-error {
    border-color: #e74c3c;
  }
  
  .error-message {
    color: #e74c3c;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  button {
    width: 100%;
    padding: 0.75rem;
    background-color: #2ecc71;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  button:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
  }
  
  button:hover:not(:disabled) {
    background-color: #27ae60;
  }
  
  .register-link {
    text-align: center;
    margin-top: 1rem;
    font-size: 0.875rem;
  }
  
  .register-link a {
    color: #3498db;
    text-decoration: none;
  }
  
  .register-link a:hover {
    text-decoration: underline;
  }
  </style>