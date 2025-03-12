<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <form @submit.prevent="register">
    <input v-model="username" placeholder="Username" required />
    <input v-model="email" type="email" placeholder="Email" required />
    <input v-model="password" type="password" placeholder="Password" required />
    <button type="submit">Register</button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/api';

const username = ref('');
const email = ref('');
const password = ref('');

const register = async () => {
  try {
    const response = await api.post('auth/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
    });
    console.log('Registered:', response.data);
  } catch (error) {
    console.error('Registration failed:', error.response?.data);
  }
};
</script>
