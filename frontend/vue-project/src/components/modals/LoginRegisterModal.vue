<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useToast } from 'vue-toastification';

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  initialTab: {
    type: String,
    default: 'login',
  },
});
const emit = defineEmits(['close']);

const activeTab = ref(props.initialTab);
const toast = useToast();

const loginData = ref({
  email: '',
  password: '',
});
const registerData = ref({
  firstName: '',
  lastName: '',
  companyName: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const authStore = useAuthStore();

const handleLogin = async (event) => {
  event.preventDefault();
  if (!loginData.value.email || !loginData.value.password) {
    toast.error('Please fill in all required fields.', { position: 'top-right', timeout: 3000 });
    return;
  }
  try {
    await authStore.login({
      email: loginData.value.email,
      password: loginData.value.password,
    });
    emit('close');
    toast.success('Login successful!', { position: 'top-right', timeout: 3000 });
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Login failed. Please try again.';
    toast.error(errorMessage, { position: 'top-right', timeout: 3000 });
  }
};

const handleRegister = async (event) => {
  event.preventDefault();
  if (!registerData.value.firstName || !registerData.value.lastName || !registerData.value.email || !registerData.value.password || !registerData.value.confirmPassword) {
    toast.error('Please fill in all required fields.', { position: 'top-right', timeout: 3000 });
    return;
  }
  if (registerData.value.password !== registerData.value.confirmPassword) {
    toast.error('Passwords do not match.', { position: 'top-right', timeout: 3000 });
    return;
  }
  try {
    console.log('Register data before calling authStore:', registerData.value);
    await authStore.register({
      firstName: registerData.value.firstName,
      lastName: registerData.value.lastName,
      companyName: registerData.value.companyName,
      email: registerData.value.email,
      password: registerData.value.password,
    });
    emit('close');
    toast.success('Registration successful! You are now logged in.', { position: 'top-right', timeout: 3000 });
  } catch (error) {
    let errorMessage = 'Registration failed. Please try again.';
    if (error.response?.status === 403 && error.response?.data?.detail?.includes('CSRF')) {
      errorMessage = 'CSRF token missing or invalid. Please refresh the page and try again.';
    } else if (error.response?.data) {
      if (error.response.data.email) {
        errorMessage = `Email: ${error.response.data.email[0]}`;
      } else if (error.response.data.password) {
        errorMessage = `Password: ${error.response.data.password[0]}`;
      } else if (error.response.data['re_password']) {
        errorMessage = `Password Confirmation: ${error.response.data['re_password'][0]}`;
      } else if (error.response.data.first_name) {
        errorMessage = `First Name: ${error.response.data.first_name[0]}`;
      } else if (error.response.data.last_name) {
        errorMessage = `Last Name: ${error.response.data.last_name[0]}`;
      } else if (error.response.data.location) {
        errorMessage = `Location: ${error.response.data.location[0]}`;
      } else if (error.response.data.non_field_errors) {
        errorMessage = error.response.data.non_field_errors[0];
      } else if (error.response.data.detail) {
        errorMessage = error.response.data.detail;
      } else {
        errorMessage = 'An unexpected error occurred. Please try again or contact support.';
      }
    } else if (error.request) {
      errorMessage = 'Network error: Unable to reach the server. Please try again later.';
    }
    toast.error(errorMessage, { position: 'top-right', timeout: 3000 });
  }
};
</script>

<template>
  <div v-if="show" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <div class="logo">
          <img src="@/assets/images/mustard-imports.png" alt="Mustard Imports Logo" />
          <span>Mustard Imports</span>
        </div>
        <div class="tabs">
          <button :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">LOGIN</button>
          <button :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">REGISTER</button>
        </div>
      </div>

      <div v-if="activeTab === 'login'" class="form">
        <form @submit="handleLogin">
          <input v-model="loginData.email" type="text" placeholder="Email" class="input-field" required />
          <input v-model="loginData.password" type="password" placeholder="Password" class="input-field" required />
          <button type="submit" class="submit-btn">LOGIN</button>
        </form>
        <p class="forgot-password">Forgot Password? <a href="#">Click Here</a></p>
      </div>

      <div v-if="activeTab === 'register'" class="form">
        <form @submit="handleRegister">
          <input v-model="registerData.firstName" type="text" placeholder="First Name" class="input-field" required />
          <input v-model="registerData.lastName" type="text" placeholder="Last Name" class="input-field" required />
          <input v-model="registerData.companyName" type="text" placeholder="Company Name (Optional)" class="input-field" />
          <input v-model="registerData.email" type="email" placeholder="Email" class="input-field" required />
          <input v-model="registerData.password" type="password" placeholder="Password" class="input-field" required />
          <input v-model="registerData.confirmPassword" type="password" placeholder="Confirm Password" class="input-field" required />
          <button type="submit" class="submit-btn">CREATE ACCOUNT</button>
        </form>
      </div>

      <p class="terms">
        By Clicking {{ activeTab === 'login' ? 'LOGIN' : 'REGISTER' }} You Agree With Our
        <a href="#">Terms Of Service</a> Stipulated <a href="#">HERE</a>
      </p>
      <button class="close-btn" @click="emit('close')">✖</button>
    </div>
  </div>
</template>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border: 5px solid #ff6200;
  border-radius: 10px;
  width: 400px;
  padding: 20px;
  position: relative;
}

.modal-header {
  text-align: center;
  margin-bottom: 20px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.logo img {
  width: 40px;
  margin-right: 10px;
}

.logo span {
  font-size: 24px;
  font-weight: bold;
  color: #ff6200;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: none;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  color: #333;
}

.tabs button.active {
  background: #ff6200;
  color: #fff;
  border-radius: 5px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-field {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 14px;
}

.submit-btn {
  padding: 10px;
  background: #ff6200;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
}

.submit-btn:hover {
  background: #e55b00;
}

.forgot-password {
  text-align: center;
  font-size: 12px;
  color: #333;
}

.forgot-password a {
  color: #ff6200;
  text-decoration: none;
}

.forgot-password a:hover {
  text-decoration: underline;
}

.terms {
  text-align: center;
  font-size: 12px;
  color: #333;
  margin-top: 15px;
}

.terms a {
  color: #ff6200;
  text-decoration: none;
}

.terms a:hover {
  text-decoration: underline;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}
</style>
