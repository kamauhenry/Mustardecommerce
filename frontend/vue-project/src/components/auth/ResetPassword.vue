<template>
  <div class="reset-password-container">
    <h2>Reset Your Password</h2>
    <form @submit.prevent="resetPassword">
      <div class="form-group">
        <label for="new-password">New Password</label>
        <input type="password" v-model="newPassword" id="new-password" required />
      </div>
      <div class="form-group">
        <label for="confirm-password">Confirm Password</label>
        <input type="password" v-model="confirmPassword" id="confirm-password" required />
      </div>
        
      <button type="submit" :disabled="store.loading.auth">Reset Password</button>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">Password reset successfully! Redirecting to login...</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';

const route = useRoute();
const router = useRouter();
const newPassword = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const error = ref(null);
const success = ref(false);

const resetPassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match';
    return;
  }
  loading.value = true;
  error.value = null;
  success.value = false;
  try {
    const token = route.params.token;
    await api.createApiInstance().post(`auth/reset-password/${token}/`, {
      new_password: newPassword.value,
    });
    success.value = true;
    setTimeout(() => router.push('/'), 3000); // Redirect to home or login page
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to reset password';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.reset-password-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}
h2 {
  text-align: center;
  margin-bottom: 1.5rem;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}
button {
  width: 100%;
  padding: 0.75rem;
  background: #1a365d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
button:disabled {
  background: #4a5568;
  cursor: not-allowed;
}
.error {
  color: red;
  margin-top: 0.5rem;
}
.success {
  color: green;
  margin-top: 0.5rem;
}
</style>