<template>
  <div class="admin-register-container">
    <div class="admin-register-card">
      <h2>Admin Registration</h2>
      <form @submit.prevent="register" class="form-grid">
        <!-- Column 1 -->
        <div class="form-column">
          <div class="form-group">
            <label for="username">Username</label>
            <input
              type="text"
              v-model="form.username"
              id="username"
              placeholder="Enter your username"
              required
              :class="{ 'input-error': formErrors.username }"
              @input="clearError('username')"
            />
            <span v-if="formErrors.username" class="error-message">{{ formErrors.username }}</span>
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input
              type="email"
              v-model="form.email"
              id="email"
              placeholder="Enter your email"
              required
              :class="{ 'input-error': formErrors.email }"
              @input="clearError('email')"
            />
            <span v-if="formErrors.email" class="error-message">{{ formErrors.email }}</span>
          </div>
          <div class="form-group">
            <label for="first_name">First Name</label>
            <input
              type="text"
              v-model="form.first_name"
              id="first_name"
              placeholder="Enter your first name"
              :class="{ 'input-error': formErrors.first_name }"
              @input="clearError('first_name')"
            />
            <span v-if="formErrors.first_name" class="error-message">{{ formErrors.first_name }}</span>
          </div>
          <div class="form-group">
            <label for="last_name">Last Name</label>
            <input
              type="text"
              v-model="form.last_name"
              id="last_name"
              placeholder="Enter your last name"
              :class="{ 'input-error': formErrors.last_name }"
              @input="clearError('last_name')"
            />
            <span v-if="formErrors.last_name" class="error-message">{{ formErrors.last_name }}</span>
          </div>
          <div class="form-group">
            <label for="phone_number">Phone Number</label>
            <input
              type="text"
              v-model="form.phone_number"
              id="phone_number"
              placeholder="Enter your phone number"
              :class="{ 'input-error': formErrors.phone_number }"
              @input="clearError('phone_number')"
            />
            <span v-if="formErrors.phone_number" class="error-message">{{ formErrors.phone_number }}</span>
          </div>
        </div>
        <!-- Column 2 -->
        <div class="form-column">
          <div class="form-group">
            <label for="location">Location</label>
            <input
              type="text"
              v-model="form.location"
              id="location"
              placeholder="Enter your location"
              :class="{ 'input-error': formErrors.location }"
              @input="clearError('location')"
            />
            <span v-if="formErrors.location" class="error-message">{{ formErrors.location }}</span>
          </div>
          <div class="form-group">
            <label for="country_code">Country Code</label>
            <input
              type="text"
              v-model="form.country_code"
              id="country_code"
              placeholder="Enter your country code (e.g., +1)"
              required
              :class="{ 'input-error': formErrors.country_code }"
              @input="clearError('country_code')"
            />
            <span v-if="formErrors.country_code" class="error-message">{{ formErrors.country_code }}</span>
          </div>
          <div class="form-group">
            <label for="delivery_location">Delivery Location</label>
            <input
              type="text"
              v-model="form.delivery_location"
              id="delivery_location"
              placeholder="Enter your delivery location"
              :class="{ 'input-error': formErrors.delivery_location }"
              @input="clearError('delivery_location')"
            />
            <span v-if="formErrors.delivery_location" class="error-message">{{ formErrors.delivery_location }}</span>
          </div>
          <div class="form-group">
            <label for="other_locations">Other Locations (JSON format)</label>
            <textarea
              v-model="form.other_locations"
              id="other_locations"
              placeholder='Enter other locations as JSON (e.g., ["Location1", "Location2"])'
              :class="{ 'input-error': formErrors.other_locations }"
              @input="clearError('other_locations')"
            ></textarea>
            <span v-if="formErrors.other_locations" class="error-message">{{ formErrors.other_locations }}</span>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input
              type="password"
              v-model="form.password"
              id="password"
              placeholder="Enter your password"
              required
              :class="{ 'input-error': formErrors.password }"
              @input="clearError('password')"
            />
            <span v-if="formErrors.password" class="error-message">{{ formErrors.password }}</span>
          </div>
        </div>
        <!-- Submit Button (Full Width) -->
        <div class="form-group full-width">
          <button type="submit" :disabled="store.loading.auth">
            {{ store.loading.auth ? 'Registering...' : 'Register' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { useEcommerceStore } from '@/stores/ecommerce';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';

export default {
  name: 'AdminRegister',
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const toast = useToast();

    return { store, router, toast };
  },
  data() {
    return {
      form: {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        location: '',
        country_code: '+254',
        delivery_location: 'Nairobi',
        other_locations: '',
        password: '',
        user_type: 'admin', // Set automatically
      },
      formErrors: {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        location: '',
        country_code: '',
        delivery_location: '',
        other_locations: '',
        password: '',
      },
    };
  },
  methods: {
    clearError(field) {
      this.formErrors[field] = '';
    },
    validateForm() {
      let isValid = true;
      this.formErrors = {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        location: '',
        country_code: '',
        delivery_location: '',
        other_locations: '',
        password: '',
      };

      if (!this.form.username) {
        this.formErrors.username = 'Username is required';
        isValid = false;
      }
      if (!this.form.email) {
        this.formErrors.email = 'Email is required';
        isValid = false;
      }
      if (!this.form.password) {
        this.formErrors.password = 'Password is required';
        isValid = false;
      }
      if (this.form.other_locations) {
        try {
          JSON.parse(this.form.other_locations);
        } catch (e) {
          this.formErrors.other_locations = 'Other locations must be valid JSON (e.g., ["Location1", "Location2"])';
          isValid = false;
        }
      }

      return isValid;
    },
    async register() {
      if (!this.validateForm()) {
        this.toast.error('Please fill in all required fields correctly');
        return;
      }

      try {
        await this.store.adminRegister(this.form);
        this.toast.success('Admin registration successful! Logging in...');
        await this.store.adminLogin({
          username: this.form.username,
          password: this.form.password,
        });
        this.router.push('/admin-page/dashboard');
      } catch (err) {
        const errorMessage = err.response?.data?.error || 'Registration failed. Please try again.';
        this.toast.error(errorMessage);
      }
    },
  },
};
</script>

<style scoped>
.admin-register-container {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Align to top to allow page scrolling */
  min-height: 100vh;
  background: linear-gradient(135deg, #8c69cc, #4a00e0);
  padding: 40px 20px; /* Increased top padding for better spacing */
}

.admin-register-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  padding: 2rem;
  width: 100%;
  max-width: 900px; /* Increased max-width for two columns */
  text-align: center;
  transition: transform 0.3s ease;
}

.admin-register-card:hover {
  transform: translateY(-5px);
}

h2 {
  color: #333;
  margin-bottom: 2rem;
  font-size: 1.8rem;
  font-weight: 600;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; /* Two columns on large screens */
  gap: 1.5rem;
}

.form-column {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.form-group.full-width {
  grid-column: 1 / -1; /* Button spans both columns */
  margin-top: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.95rem;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  color: #333;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6f42c1;
  box-shadow: 0 0 0 3px rgba(111, 66, 193, 0.1);
}

.form-group .input-error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.3rem;
  display: block;
}

button {
  background-color: #6f42c1;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.1s ease;
  width: 100%;
}

button:hover {
  background-color: #5a32a3;
}

button:active {
  transform: scale(0.98);
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr; /* Single column on small screens */
  }

  .admin-register-container {
    padding: 20px 15px;
  }

  .admin-register-card {
    padding: 1.5rem;
    max-width: 90%;
  }

  h2 {
    font-size: 1.5rem;
  }

  .form-group input,
  .form-group textarea {
    padding: 0.65rem;
    font-size: 0.9rem;
  }

  button {
    padding: 0.65rem 1.2rem;
    font-size: 0.9rem;
  }
}
</style>
