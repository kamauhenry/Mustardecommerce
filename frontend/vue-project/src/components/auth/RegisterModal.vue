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
        <input v-model="username" type="text" placeholder="Username" required />
      </div>
      <div class="input-group">
        <input v-model="email" type="email" placeholder="Email" required />
      </div>
      <div class="input-group">
        <input v-model="phone_number" type="tel" placeholder="+254" required />
      </div>
      <div class="input-group">
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          required
          @input="validatePassword"
        />
      </div>
      <div class="password-guidelines">
        <p :class="{ valid: hasUppercase }">• At least one uppercase letter</p>
        <p :class="{ valid: hasLowercase }">• At least one lowercase letter</p>
        <p :class="{ valid: hasNumber }">• At least one number</p>
        <p :class="{ valid: hasSymbol }">• At least one special character (e.g., !@#$%)</p>
      </div>
      <div class="input-group">
        <input
          v-model="confirm_password"
          type="password"
          placeholder="Confirm Password"
          required
        />
        <p v-if="passwordMismatch" class="error">Passwords do not match</p>
      </div>

      <button type="submit" class="auth-button" :disabled="!isPasswordValid || passwordMismatch">
        REGISTER
      </button>
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
import { ref, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import api from '@/services/api';

const username = ref('');
const email = ref('');
const phone_number = ref('');
const first_name = ref('');
const last_name = ref('');
const password = ref('');
const confirm_password = ref('');
const error = ref(null);
const store = useEcommerceStore();

// Password validation states
const hasUppercase = ref(false);
const hasLowercase = ref(false);
const hasNumber = ref(false);
const hasSymbol = ref(false);

const validatePassword = () => {
  const pwd = password.value;
  hasUppercase.value = /[A-Z]/.test(pwd);
  hasLowercase.value = /[a-z]/.test(pwd);
  hasNumber.value = /\d/.test(pwd);
  hasSymbol.value = /[!@#$%^&*(),.?":{}|<>]/.test(pwd);
};

const isPasswordValid = computed(() => {
  return hasUppercase.value && hasLowercase.value && hasNumber.value && hasSymbol.value;
});

const passwordMismatch = computed(() => {
  return password.value !== confirm_password.value && confirm_password.value !== '';
});

const emit = defineEmits(['switch-to-login', 'close']);

const register = async () => {
  if (!isPasswordValid.value) {
    error.value = 'Password does not meet the requirements';
    return;
  }

  if (password.value !== confirm_password.value) {
    error.value = 'Passwords do not match';
    return;
  }

  error.value = null;
  try {
    const response = await api.createApiInstance(store).post('auth/register/', {
      username: username.value,
      email: email.value,
      first_name: first_name.value,
      last_name: last_name.value,
      phone_number: phone_number.value,
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
  padding: 1rem; /* Reduced padding */
  background-color: #e2cf1f;
  border-radius: 20px;
}

.input-group {
  width: 100%;
  margin-bottom: 0.5rem; /* Reduced margin */
}

.input-group input {
  width: 100%;
  padding: 0.5rem; /* Reduced padding */
  font-size: 0.9rem; /* Smaller font size */
  border: 1px solid #e0e0e0;
  border-radius: 8px; /* Slightly smaller border-radius */
  outline: none;
  transition: border-color 0.3s ease;
}

.input-group input:focus {
  border-color: #f28c38;
}

.input-group input::placeholder {
  color: #999;
  font-size: 0.9rem; /* Match input font size */
}

.password-guidelines {
  margin-bottom: 0.5rem; /* Reduced margin */
  font-size: 0.75rem; /* Smaller font size */
  color: #333;
}

.password-guidelines p {
  margin: 0.1rem 0; /* Reduced spacing */
}

.password-guidelines .valid {
  color: #28a745; /* Green for valid requirements */
}

.auth-button {
  width: 100%;
  padding: 0.5rem; /* Reduced padding */
  font-size: 0.9rem; /* Smaller font size */
  font-weight: 700;
  text-transform: uppercase;
  color: #fff;
  background-color: #f28c38;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.auth-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.auth-button:hover:not(:disabled) {
  background-color: #e07b30;
}

.error {
  color: #ff0000;
  font-size: 0.75rem; /* Smaller font size */
  margin: 0.25rem 0; /* Reduced margin */
}

.terms,
.switch-link {
  font-size: 0.75rem; /* Smaller font size */
  color: #333;
  margin: 0.25rem 0; /* Reduced margin */
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

@media (max-width: 540px) {
  .auth-modal {
    padding: 0.5rem; /* Further reduced padding */
  }

  .input-group {
    margin-bottom: 0.3rem; /* Further reduced margin */
  }

  .input-group input {
    padding: 0.4rem; /* Further reduced padding */
    font-size: 0.85rem; /* Slightly smaller font size */
  }

  .input-group input::placeholder {
    font-size: 0.85rem;
  }

  .password-guidelines {
    font-size: 0.7rem; /* Smaller font size */
    margin-bottom: 0.3rem;
  }

  .auth-button {
    padding: 0.4rem; /* Further reduced padding */
    font-size: 0.85rem;
  }

  .error,
  .terms,
  .switch-link {
    font-size: 0.7rem; /* Smaller font size */
    margin: 0.2rem 0; /* Further reduced margin */
  }
}
</style>