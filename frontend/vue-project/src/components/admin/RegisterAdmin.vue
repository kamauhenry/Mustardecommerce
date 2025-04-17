<template>
    <div class="admin-register-container">
      <div class="admin-register-card">
        <h2>Admin Registration</h2>
        <form @submit.prevent="register" class="form-grid">
          <div class="form-column">
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
              <label for="email">Email</label>
              <input
                type="email"
                v-model="email"
                id="email"
                placeholder="Enter your email"
                required
              />
            </div>
            <div class="form-group">
              <label for="first_name">First Name</label>
              <input
                type="text"
                v-model="first_name"
                id="first_name"
                placeholder="Enter your first name"
              />
            </div>
            <div class="form-group">
              <label for="last_name">Last Name</label>
              <input
                type="text"
                v-model="last_name"
                id="last_name"
                placeholder="Enter your last name"
              />
            </div>
            <div class="form-group">
              <label for="phone_number">Phone Number</label>
              <input
                type="text"
                v-model="phone_number"
                id="phone_number"
                placeholder="Enter your phone number"
              />
            </div>
          </div>
          <div class="form-column">
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
          </div>
          <div class="form-group full-width">
            <button type="submit" :disabled="store.loading.auth">
              {{ store.loading.auth ? 'Registering...' : 'Register' }}
            </button>
          </div>
        </form>
        <p v-if="error" class="error-message">{{ error }}</p>
        <p class="login-link">
          Already have an account? <router-link to="/admin-page/login">Login</router-link>
        </p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { useEcommerceStore } from '@/stores/ecommerce';
  import { useRouter } from 'vue-router';
  
  const username = ref('');
  const email = ref('');
  const phone_number = ref('');
  const first_name = ref('');
  const last_name = ref('');
  const password = ref('');
  const error = ref(null);
  const store = useEcommerceStore();
  const router = useRouter();
  
  const register = async () => {
    error.value = null;
    try {
      const response = await store.adminRegister({
        username: username.value,
        email: email.value,
        first_name: first_name.value,
        last_name: last_name.value,
        phone_number: phone_number.value,
        password: password.value,
        user_type: 'admin',
      });
      console.log(`Registered as admin ${response.username}`);
      router.push('/admin-page/login');
    } catch (err) {
      error.value = err.response?.data?.error || err.message || 'Admin registration failed';
      console.error('Admin registration failed:', err.response?.data);
    }
  };
  </script>
  
  <style scoped>
  .admin-register-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f4f4f4;
  }
  
  .admin-register-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 600px;
  }
  
  .admin-register-card h2 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #333;
  }
  
  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  
  .form-column {
    display: flex;
    flex-direction: column;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-group.full-width {
    grid-column: 1 / -1;
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