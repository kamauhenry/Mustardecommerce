<template>
  <div class="auth-modal">
    <form @submit.prevent="login">
      <div class="input-group">
        <input v-model="username" type="text" placeholder="example@gmail.com" required />
      </div>
      <div class="input-group">
        <input v-model="password" type="password" placeholder="Password" required />
      </div>
      <button type="submit" class="auth-button">LOGIN</button>
    </form>
    <!-- Google Sign-In Button -->
    <div id="g_id_signin" class="google-signin"></div>
    <p v-if="error" class="error">{{ error }}</p>
    <p class="forgot-password">
      <a href="#" @click.prevent>Forgot Password? Click Here</a>
    </p>
    <p class="terms">
      By Clicking LOGIN You Agree With Our
      <a href="#" @click.prevent>Terms of Service Stipulated HERE</a>
    </p>
    <p class="switch-link">
      Don't have an account? <a href="#" @click="switchToRegister">Register</a>
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';

const username = ref('');
const password = ref('');
const error = ref(null);
const store = useEcommerceStore();
const emit = defineEmits(['switch-to-register', 'close']);

const login = async () => {
  error.value = null;
  try {
    const response = await store.login(username.value, password.value);
    console.log(`Logged in as ${response.username}`);
    emit('close');
  } catch (err) {
    error.value =  'Login failed, Wrong password or Email';
    console.error('Login failed:', err);
  }
};

const switchToRegister = () => {
  emit('switch-to-register');
};

// Initialize and render Google Sign-In button
onMounted(() => {
  window.google.accounts.id.initialize({
    client_id: '370920112183-0pd7i0jqlf78bqjph6j6ocg1s3gkhe9d.apps.googleusercontent.com',
    callback: handleCredentialResponse,
  });
  window.google.accounts.id.renderButton(
    document.getElementById('g_id_signin'),
    { theme: 'outline', size: 'large' }
  );
});

// Handle Google authentication response
const handleCredentialResponse = async (response) => {
  const idToken = response.credential;
  try {
    const resp = await store.googleLogin(idToken);
    console.log(`Logged in with Google as ${resp.username}`);
    emit('close');
  } catch (err) {
    error.value = 'Google login failed';
    console.error('Google login failed:', err);
  }
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
.google-signin {
  margin-top: 20px;
  text-align: center;
}
.input-group {
  width: 100%;
  margin-bottom: 1rem;
}

.input-group input {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  border: none;
  border-radius: 10px;
  outline: none;
  transition: border-color 0.3s ease;
}

.input-group input:focus {
  border-color:#D4A017;
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
  background-color:#D4A017; /* Orange to match the screenshot */
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

.forgot-password,
.terms,
.switch-link {
  font-size: 0.85rem;
  color: #333;
  margin: 0.5rem 0;
  text-align: center;
}

.forgot-password a,
.terms a,
.switch-link a {
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
}

.forgot-password a:hover,
.terms a:hover,
.switch-link a:hover {
  text-decoration: underline;
}
</style>
