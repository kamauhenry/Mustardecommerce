<template>
  <div class="auth-modal">
    <form @submit.prevent="register">
      <div class="input-group">
        <input v-model="first_name" type="text" placeholder="First Name" required />
      </div>
      <div class="input-group">
        <input v-model="last_name" type="text" placeholder="Last Name" required />
      </div>
      <div class="input-group">
        <input
          v-model="username"
          type="text"
          placeholder="Username"
          required
        />
      </div>
      <div class="input-group">
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          required
        />
      </div>
      <div class="input-group">
        <input
          v-model="phone_number"
          type="tell"
          placeholder="+254"
          required
        />
      </div>
      <div class="input-group">
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          required
        />
      </div>

      <button type="submit" class="auth-button">REGISTER</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <p class="terms">
      By Clicking REGISTER You Agree With Our
      <a href="#" @click.prevent>Terms of Service Stipulated HERE</a>
    </p>
    <p class="switch-link">
      Already have an account? <a href="#" @click="switchToLogin">Login</a>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import api from '@/services/api';

const username = ref('');
const email = ref('');
const phone_number = ref(''); 
const first_name = ref('');
const last_name = ref('');

const password = ref('');
const error = ref(null);
const store = useEcommerceStore();

const emit = defineEmits(['switch-to-login', 'close']);

const register = async () => {
  error.value = null;
  try {
    const response = await api.createApiInstance(store).post('auth/register/', {
      username: username.value,
      email: email.value,
      first_name: first_name.value,
      last_name: last_name.value,
      phone_number:phone_number.value,
      user_type: 'customer',
      password: password.value,
    });
    const { user_id, username: userName } = response.data;
    store.setUserId(user_id);
    console.log(`Registered as ${userName}`);
    emit('switch-to-login');
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed';
    console.error('Registration failed:', err.response?.data);
  }
};

const switchToLogin = () => {
  emit('switch-to-login');
};
</script>

<style scoped>
.auth-modal {
  display: flex;
  flex-direction: column;
  /* align-items: center; */
  padding: 2rem;
  background-color: #e2cf1f;
  border-radius: 20px;
}

.input-group {
  width: 100%;
  margin-bottom: 1rem;
}

.input-group input {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.3s ease;
}

.input-group input:focus {
  border-color: #f28c38;
}

.input-group input::placeholder {
  color: #999;
}

.auth-button {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #fff;
  background-color: #f28c38; /* Orange to match the screenshot */
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.auth-button:hover {
  background-color: #e07b30; /* Slightly darker orange on hover */
}

.error {
  color: #ff0000;
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

.terms,
.switch-link {
  font-size: 0.85rem;
  color: #333;
  margin: 0.5rem 0;
  text-align: center;
}

.terms a,
.switch-link a {
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
}

.terms a:hover,
.switch-link a:hover {
  text-decoration: underline;
}
</style>
