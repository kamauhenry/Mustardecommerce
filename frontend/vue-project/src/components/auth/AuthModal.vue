<template>
  <div class="auth-modal">


    <!-- Login View -->
    <div v-if="currentView === 'login'">
      <h2>Login</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="login-username">Username or Email</label>
          <input v-model="loginData.username" id="login-username" placeholder="Enter username or email" required />
        </div>
        <div class="form-group">
          <label for="login-password">Password</label>
          <input v-model="loginData.password" id="login-password" type="password" placeholder="Enter password" required />
        </div>
        <button type="submit" :disabled="loading">Login</button>
      </form>
      <div id="g_id_signin" class="google-signin"></div>
      <p class="flip-link">Don't have an account? <a @click="switchToRegister">Register</a></p>
      <p class="flip-link">Forgot password? <a @click="switchToForgotPassword">Click here</a></p>

    </div>

    <!-- Registration View -->
    <div v-else-if="currentView === 'register'">
      <h2>Register</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-grid">
          <div class="form-group">
            <label for="reg-username">Username</label>
            <input v-model="registerData.username" id="reg-username" placeholder="Enter username" required @input="saveFormData" />
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input v-model="registerData.email" id="email" type="email" placeholder="Enter email" required @input="saveFormData" />
          </div>
          <div class="form-group">
            <label for="first_name">First Name</label>
            <input v-model="registerData.first_name" id="first_name" placeholder="Enter first name" required @input="saveFormData" />
          </div>
          <div class="form-group">
            <label for="last_name">Last Name</label>
            <input v-model="registerData.last_name" id="last_name" placeholder="Enter last name" required @input="saveFormData" />
          </div>
          <div class="form-group">
            <label for="phone_number">Phone Number</label>
            <input v-model="registerData.phone_number" id="phone_number" placeholder="+254" required @input="saveFormData" />
          </div>
          <div class="form-group">
            <label for="reg-password">Password</label>
            <input
              v-model="registerData.password"
              id="reg-password"
              type="password"
              placeholder="Enter password"
              required
              @input="validatePassword"
            />
            <div class="password-guidelines">
              <p :class="{ valid: passwordRules.length }">• At least 8 characters</p>
              <p :class="{ valid: passwordRules.uppercase }">• At least one uppercase letter</p>
              <p :class="{ valid: passwordRules.lowercase }">• At least one lowercase letter</p>
              <p :class="{ valid: passwordRules.number }">• At least one number</p>
              <p :class="{ valid: passwordRules.special }">• Special character (e.g., !@#$%)</p>
            </div>
          </div>
          <div class="form-group">
            <label for="confirm-password">Confirm Password</label>
            <input
              v-model="registerData.confirmPassword"
              id="confirm-password"
              type="password"
              placeholder="Confirm password"
              required
              @input="validatePassword"
            />
            <p v-if="!passwordRules.match && registerData.confirmPassword" class="error">Passwords do not match</p>
          </div>
        </div>
        <button type="submit" :disabled="loading || !isPasswordValid">Register</button>
      </form>
      <p class="flip-link">Already have an account? <a @click="switchToLogin">Login</a></p>
    </div>

    <!-- OTP Verification View -->
    <div v-else-if="currentView === 'otp'">
      <h2>Verify OTP</h2>
      <p>Enter the OTP sent to {{ registerData.email }}</p>
      <form @submit.prevent="handleOtpVerification">
        <div class="form-group">
          <label for="otp">OTP</label>
          <input v-model="otpData.otp" id="otp" placeholder="Enter OTP" required />
        </div>
        <button type="submit" :disabled="loading">Verify</button>
      </form>
    </div>

    <!-- Forgot Password View -->
    <div v-else-if="currentView === 'forgotPassword'">
      <h2>Forgot Password</h2>
      <form @submit.prevent="handleForgotPassword">
        <div class="form-group">
          <label for="reset-email">Email</label>
          <input v-model="forgotPasswordData.email" id="reset-email" type="email" placeholder="Enter email" required />
        </div>
        <button type="submit" :disabled="loading">Send Reset Link</button>
      </form>
      <p class="flip-link">Back to <a @click="switchToLogin">Login</a></p>
    </div>

    <!-- Messages -->
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <p v-if="successMessage" class="success">{{ successMessage }}</p>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import api from '@/services/api';

// State Management
const currentView = ref('login');
const store = useEcommerceStore();
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const emit = defineEmits(['close']);
// Form Data
const loginData = reactive({ username: '', password: '' });
const registerData = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone_number: '',
  password: '',
  confirmPassword: '',
});
const otpData = reactive({ otp: '' });
const forgotPasswordData = reactive({ email: '' });

// Password Validation
const passwordRules = reactive({
  length: false,
  uppercase: false,
  lowercase: false,
  number: false,
  special: false,
  match: true,
});

const validatePassword = () => {
  passwordRules.length = registerData.password.length >= 8;
  passwordRules.uppercase = /[A-Z]/.test(registerData.password);
  passwordRules.lowercase = /[a-z]/.test(registerData.password);
  passwordRules.number = /\d/.test(registerData.password);
  passwordRules.special = /[!@#$%^&*(),.?":{}|<>]/.test(registerData.password);
  passwordRules.match = registerData.password === registerData.confirmPassword && registerData.password !== '';
};

const isPasswordValid = computed(() => {
  return (
    passwordRules.length &&
    passwordRules.uppercase &&
    passwordRules.lowercase &&
    passwordRules.number &&
    passwordRules.special &&
    passwordRules.match
  );
});

// Load saved form data and initialize Google Sign-In
onMounted(async () => {
  // Load saved registration data
  const savedData = JSON.parse(localStorage.getItem('registerForm')) || {};
  registerData.username = savedData.username || '';
  registerData.email = savedData.email || '';
  registerData.first_name = savedData.first_name || '';
  registerData.last_name = savedData.last_name || '';
  registerData.phone_number = savedData.phone_number || '';

  // Initialize Google Sign-In
  window.google.accounts.id.initialize({
    client_id: '974928309201-n6nkaqko0qcju8uvhuf0m827dhp2bn1l.apps.googleusercontent.com',
    callback: handleCredentialResponse,
  });

  // Render Google Sign-In button if login view is active
  if (currentView.value === 'login') {
    await nextTick();
    renderGoogleButton();
  }
});

// Watch currentView to render Google button when switching to login
watch(currentView, async (newView) => {
  if (newView === 'login') {
    await nextTick();
    renderGoogleButton();
  }
});

// Render Google Sign-In button
const renderGoogleButton = () => {
  const googleButton = document.getElementById('g_id_signin');
  if (googleButton) {
    window.google.accounts.id.renderButton(googleButton, { theme: 'outline', size: 'large' });
  } else {
    console.warn('Google Sign-In div not found');
  }
};

// Save form data to localStorage
const saveFormData = () => {
  const formData = {
    username: registerData.username,
    email: registerData.email,
    first_name: registerData.first_name,
    last_name: registerData.last_name,
    phone_number: registerData.phone_number,
  };
  localStorage.setItem('registerForm', JSON.stringify(formData));
};

// View Switching Methods
const switchToLogin = () => {
  currentView.value = 'login';
  errorMessage.value = '';
  successMessage.value = '';
};

const switchToRegister = () => {
  currentView.value = 'register';
  errorMessage.value = '';
  successMessage.value = '';
};

const switchToOtp = () => {
  currentView.value = 'otp';
  errorMessage.value = '';
  successMessage.value = '';
};

const switchToForgotPassword = () => {
  currentView.value = 'forgotPassword';
  errorMessage.value = '';
  successMessage.value = '';
};

// Form Submission Handlers
const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = ''; // Clear any previous error messages
  try {
    const response = await store.login(loginData.username, loginData.password);
    console.log(`Logged in as ${response.username}`);
    successMessage.value = 'Login successful!'; // Optional: Show success message
    await nextTick(); // Ensure DOM updates before emitting close
    loginData.username = ''; // Clear form data
    loginData.password = '';

    emit('close'); // Emit close event to parent component
  } catch (err) {
    // Handle specific backend error messages
    const errorData = err.response?.data;
    console.log('errorData:', errorData)
    if (errorData && errorData.error) {
      errorMessage.value = errorData.error; // Display specific backend error
      console.log('error data 2')
    } else {
      errorMessage.value = 'Login failed: Wrong password or username';
      console.log('error data 3')
    }
    console.error('Login failed:', err.response?.data);
    console.log('auth modal failed ')
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  if (!isPasswordValid.value) {
    errorMessage.value = 'Please meet all password requirements';
    return;
  }
  loading.value = true;
  errorMessage.value = '';
  try {
    const response = await api.createApiInstance(store).post('auth/register/', {
      username: registerData.username,
      email: registerData.email,
      first_name: registerData.first_name,
      last_name: registerData.last_name,
      phone_number: registerData.phone_number,
      password: registerData.password,
      user_type: 'customer',
    });
    console.log(`Registered as ${response.data.username}`);
    await api.createApiInstance(store).post('auth/send-otp/', { email: registerData.email });
    localStorage.removeItem('registerForm');
    successMessage.value = 'Registration successful. Please enter the OTP sent to your email.';
    switchToOtp();
  } catch (err) {
    // Extract specific error message from backend response
    const errorData = err.response?.data;
    if (errorData && errorData.username && Array.isArray(errorData.username)) {
      errorMessage.value = errorData.username[0];
    } else if (errorData && errorData.email && Array.isArray(errorData.email)) {
      errorMessage.value = errorData.email[0];
    } else if (errorData && errorData.error) {
      errorMessage.value = errorData.error;
    } else {
      errorMessage.value = 'Registration failed';
    }
    console.error('Registration failed:', err.response?.data);
  } finally {
    loading.value = false;
  }
};

const handleOtpVerification = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    await api.createApiInstance(store).post('auth/verify-otp/', {
      email: registerData.email,
      otp: otpData.otp,
    });
    console.log('OTP verified');
    successMessage.value = 'OTP verified successfully';
    switchToLogin();
  } catch (err) {
    errorMessage.value = 'Invalid OTP';
  } finally {
    loading.value = false;
  }
};

const handleForgotPassword = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    await api.createApiInstance(store).post('auth/forgot-password/', { email: forgotPasswordData.email });
    successMessage.value = 'If the email exists, a reset link has been sent.';
    switchToLogin();
  } catch (err) {
    errorMessage.value = 'Failed to send reset link';
  } finally {
    loading.value = false;
  }
};

const handleCredentialResponse = async (response) => {
  const idToken = response.credential;
  try {
    const resp = await store.googleLogin(idToken);
    console.log(`Logged in with Google as ${resp.username}`);
    emit('close');
  } catch (err) {
    errorMessage.value = 'Google login failed';
    console.error('Google login failed:', err);
  }
};

// Watch for changes to save form data
watch(
  () => ({
    username: registerData.username,
    email: registerData.email,
    first_name: registerData.first_name,
    last_name: registerData.last_name,
    phone_number: registerData.phone_number,
  }),
  saveFormData
);
</script>

<style scoped>
.auth-modal {
  position: relative;
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 700px;
  font-family: 'Inter', sans-serif;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

h2 {
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

.form-group input {
  width: 100%;
  padding: 0.875rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
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

.password-guidelines {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #4a5568;
}

.password-guidelines p {
  margin: 0.1rem 0;
}

.password-guidelines .valid {
  color: #28a745;
}

button {
  width: 50%;
  padding: 0.875rem;
  margin: 1rem auto;
  background-color: #e2cf1f;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

button:disabled {
  background-color: #4a5568;
  cursor: not-allowed;
  opacity: 0.7;
}

button:hover:not(:disabled) {
  background-color: #e07b30;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(26, 54, 93, 0.25);
}

.error {
  color: #e53e3e;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: #fff5f5;
  border-radius: 6px;
  border-left: 3px solid #e53e3e;
}

.success {
  color: #28a745;
  font-size: 0.875rem;
  margin-top: 0.5rem;
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
  cursor: pointer;
}

.flip-link a:hover {
  color: #1a365d;
  text-decoration: underline;
}

.google-signin {
  margin-top: 20px;
  text-align: center;
}
</style>