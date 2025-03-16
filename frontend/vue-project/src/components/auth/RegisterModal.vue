<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div>
        <label>Username:</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>Email:</label>
        <input v-model="email" type="email" required />
      </div>
      <div>
        <label>Password:</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">Register</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <p>Already have an account? <a href="#" @click="switchToLogin">Login</a></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import api from '@/services/api';

const username = ref('');
const email = ref('');
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
      password: password.value,
      user_type: 'customer',
      location: '',
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
.error {
  color: red;
}
</style>
