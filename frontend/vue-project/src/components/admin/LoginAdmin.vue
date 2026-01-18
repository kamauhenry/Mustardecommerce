<template>
  <div class="auth-container">
    <div class="card-container" :class="{ 'is-flipped': showRegister }">
      <!-- Login Side (Front) -->
      <div class="card-face card-face-front">
        <div class="auth-card">
          <h2>Admin Login</h2>
          <form v-if="!showForgotPassword" @submit.prevent="login">
            <div class="form-group">
              <label for="username">Username</label>
              <div class="input-wrapper">
                <input
                  type="text"
                  v-model="loginForm.username"
                  id="username"
                  placeholder="Enter your username"
                  required
                />
              </div>
            </div>
            <div class="form-group">
              <label for="login-password">Password</label>
              <div class="input-wrapper">
                <input
                  type="password"
                  v-model="loginForm.password"
                  id="login-password"
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>
            <button type="submit" :disabled="authStore.isLoggingIn" class="auth-button">
              <span v-if="!authStore.isLoggingIn">Login</span>
              <div v-else class="loader-container">
                <div class="loader"></div>
                <span>Logging in</span>
              </div>
            </button>
          </form>
          <form v-else @submit.prevent="requestPasswordReset">
            <div class="form-group">
              <label for="reset-email">Email</label>
              <div class="input-wrapper">
                <input
                  type="email"
                  v-model="resetEmail"
                  id="reset-email"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>
            <button type="submit" class="auth-button">Send Reset Link</button>
          </form>
          <p v-if="loginError" class="error-message">{{ loginError }}</p>
          <p class="flip-link">
            <a href="#" @click.prevent="toggleForgotPassword">
              {{ showForgotPassword ? 'Back to Login' : 'Forgot Password?' }}
            </a>
          </p>
          <p v-if="!showForgotPassword" class="flip-link">
            No account? <a href="#" @click.prevent="flipCard">Create one</a>
          </p>
        </div>
      </div>
      
      <!-- Register Side (Back) -->
      <div class="card-face card-face-back">
        <div class="auth-card">
          <h2>Admin Registration</h2>
          <form @submit.prevent="register" class="register-form">
            <div class="form-grid">
              <div class="form-group">
                <label for="reg-username">Username</label>
                <div class="input-wrapper">
                  <input
                    type="text"
                    v-model="registerForm.username"
                    id="reg-username"
                    placeholder="Enter your username"
                    required
                  />
                </div>
              </div>
              <div class="form-group">
                <label for="email">Email</label>
                <div class="input-wrapper">
                  <input
                    type="email"
                    v-model="registerForm.email"
                    id="email"
                    placeholder="Enter your email"
                    required
                  />
                </div>
              </div>
              <div class="form-group">
                <label for="first_name">First Name</label>
                <div class="input-wrapper">
                  <input
                    type="text"
                    v-model="registerForm.first_name"
                    id="first_name"
                    placeholder="Enter your first name"
                  />
                </div>
              </div>
              <div class="form-group">
                <label for="last_name">Last Name</label>
                <div class="input-wrapper">
                  <input
                    type="text"
                    v-model="registerForm.last_name"
                    id="last_name"
                    placeholder="Enter your last name"
                  />
                </div>
              </div>
              <div class="form-group">
                <label for="phone_number">Phone Number</label>
                <div class="input-wrapper">
                  <input
                    type="text"
                    v-model="registerForm.phone_number"
                    id="phone_number"
                    placeholder="Enter your phone number"
                  />
                </div>
              </div>
              <div class="form-group">
                <label for="reg-password">Password</label>
                <div class="input-wrapper">
                  <input
                    type="password"
                    v-model="registerForm.password"
                    id="reg-password"
                    placeholder="Enter your password"
                    required
                  />
                </div>
              </div>
            </div>
            <button type="submit" :disabled="store.loading.auth" class="auth-button">
              <span v-if="!store.loading.auth">Register</span>
              <div v-else class="loader-container">
                <div class="loader"></div>
                <span>Registering</span>
              </div>
            </button>
          </form>
          <p v-if="registerError" class="error-message">{{ registerError }}</p>
          <p class="flip-link">
            Already have an account? <a href="#" @click.prevent="flipCard">Login</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue';
import { useAuthStore } from '@/stores/modules/auth';
import { useRouter } from 'vue-router';
import api from '@/services/api';

const showRegister = ref(false);
const showForgotPassword = ref(false);
const loginError = ref(null);
const registerError = ref(null);
const resetEmail = ref('');
const authStore = useAuthStore();
const router = useRouter();

const loginForm = reactive({
  username: '',
  password: ''
});

const registerForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone_number: '',
  password: ''
});

const flipCard = () => {
  loginError.value = null;
  registerError.value = null;
  showForgotPassword.value = false;
  showRegister.value = !showRegister.value;
};

const toggleForgotPassword = () => {
  showForgotPassword.value = !showForgotPassword.value;
  loginError.value = null;
};

const login = async () => {
  loginError.value = null;

  // Use the same login method for admin
  // The authStore.isAdmin computed property will determine admin status
  const success = await authStore.login(loginForm.username, loginForm.password);

  if (success) {
    console.log(`Logged in as admin ${authStore.currentUser?.username}`);
    await nextTick();

    // Check if user is actually an admin
    if (authStore.isAdmin) {
      router.push('/admin-page/dashboard');
    } else {
      loginError.value = 'Access denied: Not an admin account';
      await authStore.logout();
    }
  } else {
    loginError.value = authStore.loginMessage || 'Admin login failed: Wrong Password or Username';
  }
};

const register = async () => {
  registerError.value = null;
  try {
    // Use direct API for admin registration (different endpoint than customer registration)
    const apiInstance = api.createApiInstance({ authToken: null });
    const response = await apiInstance.post('auth/register/', {
      username: registerForm.username,
      email: registerForm.email,
      first_name: registerForm.first_name,
      last_name: registerForm.last_name,
      phone_number: registerForm.phone_number,
      password: registerForm.password,
      user_type: 'admin',
    });
    console.log(`Registered as admin ${response.data.username}`);
    showRegister.value = false;
    await nextTick();
  } catch (err) {
    // Extract the specific error message from the backend response
    const errorData = err.response?.data;
    if (errorData && errorData.username && Array.isArray(errorData.username)) {
      registerError.value = errorData.username[0];
    } else if (errorData && errorData.email && Array.isArray(errorData.email)) {
      registerError.value = errorData.email[0];
    } else if (errorData && errorData.error) {
      registerError.value = errorData.error;
    } else {
      registerError.value = 'Admin registration failed';
    }
    console.error('Admin registration failed:', err.response?.data);
  }
};

const requestPasswordReset = async () => {
  loginError.value = null;
  try {
    await api.createApiInstance(store).post('auth/forgot-password/', { email: resetEmail.value });
    alert('If the email exists, a reset link has been sent.');
    showForgotPassword.value = false;
  } catch (err) {
    loginError.value = 'Failed to send reset link';
    console.error('Reset request failed:', err);
  }
};
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
  background-color: #f8f9fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  perspective: 1200px;
  padding: 2rem 1rem;
}

.card-container {
  width: 100%;
  max-width: 700px;
  height: auto;
  position: relative;
  transition: transform 0.8s ease;
  transform-style: preserve-3d;
}

.card-container.is-flipped {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.card-face-front {
  z-index: 2;
}

.card-face-back {
  transform: rotateY(180deg);
}

.auth-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  width: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.auth-card h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #1a365d;
  font-weight: 600;
  font-size: 1.75rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4a5568;
  font-weight: 500;
  font-size: 0.95rem;
}

.input-wrapper {
  position: relative;
}

.form-group input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f8fafc;
  color: #1a202c;
}

.form-group input:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.15);
  background: white;
}

.form-group input::placeholder {
  color: #a0aec0;
}

.form-group input.input-error {
  border-color: #e53e3e;
  background-color: #fff5f5;
}

.error-message {
  color: #e53e3e;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #fff5f5;
  border-radius: 6px;
  border-left: 3px solid #e53e3e;
}

.auth-button {
  width: 50%;
  padding: 0.875rem;
  margin: 1rem auto;
  background-color: #1a365d;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 3.25rem;
}

.auth-button:disabled {
  background-color: #4a5568;
  cursor: not-allowed;
  opacity: 0.7;
}

.auth-button:hover:not(:disabled) {
  background-color: #2c5282;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(26, 54, 93, 0.25);
}

.flip-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.95rem;
  color: #4a5568;
}

.flip-link a {
  color: #2b6cb0;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
  cursor: pointer;
}

.flip-link a:hover {
  color: #1a365d;
  text-decoration: underline;
}

.register-form {
  min-height: 320px;
}

.loader-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.loader {
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 2px solid white;
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>