<template>
    <div class="admin-login-container">
      <div class="admin-login-card">
        <h2>Admin Login</h2>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username">Username</label>
            <input
              type="text"
              v-model="form.username"
              id="username"
              placeholder="Enter your username"
              required
              :class="{ 'input-error': formErrors.username }"
              @input="clearError('username')"
            />
            <span v-if="formErrors.username" class="error-message">{{ formErrors.username }}</span>
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input
              type="email"
              v-model="form.email"
              id="email"
              placeholder="Enter your email"
              required
              :class="{ 'input-error': formErrors.email }"
              @input="clearError('email')"
            />
            <span v-if="formErrors.email" class="error-message">{{ formErrors.email }}</span>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input
              type="password"
              v-model="form.password"
              id="password"
              placeholder="Enter your password"
              required
              :class="{ 'input-error': formErrors.password }"
              @input="clearError('password')"
            />
            <span v-if="formErrors.password" class="error-message">{{ formErrors.password }}</span>
          </div>
          <button type="submit" :disabled="store.loading.auth">
            {{ store.loading.auth ? 'Logging in...' : 'Login' }}
          </button>
        </form>
        <p class="register-link">
          No account? <router-link to="/admin-page/register">Create one</router-link>
        </p>
      </div>
    </div>
  </template>
  
  <script>
  import { useEcommerceStore } from '@/stores/ecommerce';
  import { useRouter } from 'vue-router';
  
  export default {
    name: 'AdminLogin',
    setup() {
      const store = useEcommerceStore();
      const router = useRouter();
  
      return { store, router };
    },
    data() {
      return {
        form: {
          username: '',
          email: '',
          password: '',
        },
        formErrors: {
          username: '',
          email: '',
          password: '',
        },
      };
    },
    methods: {
      clearError(field) {
        this.formErrors[field] = '';
      },
      validateForm() {
        let isValid = true;
        this.formErrors = { username: '', email: '', password: '' };
  
        if (!this.form.username) {
          this.formErrors.username = 'Username is required';
          isValid = false;
        }
        if (!this.form.email) {
          this.formErrors.email = 'Email is required';
          isValid = false;
        }
        if (!this.form.password) {
          this.formErrors.password = 'Password is required';
          isValid = false;
        }
  
        return isValid;
      },
      async login() {
        if (!this.validateForm()) {
          this.$toast.error('Please fill in all required fields');
          return;
        }
  
        try {
          await this.store.adminLogin({
            username: this.form.username,
            password: this.form.password,
          });
          this.$toast.success('Admin login successful!');
          this.router.push('/admin-page/dashboard');
        } catch (err) {
          const errorMessage = err.response?.data?.error || 'Login failed. Please try again.';
          this.$toast.error(errorMessage);
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .admin-login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #6f42c1, #4a00e0);
    padding: 20px;
  }
  
  .admin-login-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    padding: 2rem;
    width: 100%;
    max-width: 450px;
    text-align: center;
    transition: transform 0.3s ease;
  }
  
  .admin-login-card:hover {
    transform: translateY(-5px);
  }
  
  h2 {
    color: #333;
    margin-bottom: 1.5rem;
    font-size: 1.8rem;
    font-weight: 600;
  }
  
  .form-group {
    margin-bottom: 1.5rem;
    text-align: left;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #555;
    font-size: 0.95rem;
    font-weight: 500;
  }
  
  .form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
    color: #333;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
  }
  
  .form-group input:focus {
    outline: none;
    border-color: #6f42c1;
    box-shadow: 0 0 0 3px rgba(111, 66, 193, 0.1);
  }
  
  .form-group .input-error {
    border-color: #e74c3c;
  }
  
  .error-message {
    color: #e74c3c;
    font-size: 0.85rem;
    margin-top: 0.3rem;
    display: block;
  }
  
  button {
    background-color: #6f42c1;
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.1s ease;
    width: 100%;
  }
  
  button:hover {
    background-color: #5a32a3;
  }
  
  button:active {
    transform: scale(0.98);
  }
  
  button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .register-link {
    margin-top: 1rem;
    font-size: 0.95rem;
    color: #555;
  }
  
  .register-link a {
    color: #6f42c1;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
  }
  
  .register-link a:hover {
    color: #5a32a3;
    text-decoration: underline;
  }
  
  /* Responsive Design */
  @media (max-width: 480px) {
    .admin-login-container {
      padding: 15px;
    }
  
    .admin-login-card {
      padding: 1.5rem;
      max-width: 90%;
    }
  
    h2 {
      font-size: 1.5rem;
    }
  
    .form-group input {
      padding: 0.65rem;
      font-size: 0.9rem;
    }
  
    button {
      padding: 0.65rem 1.2rem;
      font-size: 0.9rem;
    }
  
    .register-link {
      font-size: 0.85rem;
    }
  }
  </style>