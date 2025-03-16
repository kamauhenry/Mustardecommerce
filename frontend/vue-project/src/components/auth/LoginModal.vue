<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div>
        <label>Username:</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>Password:</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <p>Don't have an account? <a href="#" @click="switchToRegister">Register</a></p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import api from '@/services/api';

const username = ref('');
const password = ref('');
const error = ref(null);
const store = useEcommerceStore();

const emit = defineEmits(['switch-to-register', 'close']);

const login = async () => {
  error.value = null;
  try {
    // Create an API instance with the store
    const apiInstance = api.createApiInstance(store);

    // Use the instance for the request
    const response = await apiInstance.post('auth/login/', {
      username: username.value,
      password: password.value,
    });

    const { user_id, username: userName } = response.data;
    store.setUserId(user_id);
    console.log(`Logged in as ${userName}`);
    emit('close');
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed';
    console.error('Login failed:', err.response?.data);
  }
};

const switchToRegister = () => {
  emit('switch-to-register');
};
</script>

<style scoped>
.error {
  color: red;
}
</style>
