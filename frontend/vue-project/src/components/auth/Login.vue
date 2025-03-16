<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <form @submit.prevent="login">
    <input v-model="username" placeholder="Username" required />
    <input v-model="password" type="password" placeholder="Password" required />
    <button type="submit">Login</button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/api';

const username = ref('');
const password = ref('');

const login = async () => {
  try {
    const response = await api.post('auth/login/', {
      username: username.value,
      password: password.value,
    });
    console.log('Logged in:', response.data);
  } catch (error) {
    console.error('Login failed:', error.response?.data);
  }
};
</script>
