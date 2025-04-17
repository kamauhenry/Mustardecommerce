<template>
    <AdminLayout>
      <div class="settings">
        <h2>Profile Settings</h2>
        <form @submit.prevent="updateProfile">
          <div class="form-group">
            <label>Username</label>
            <input v-model="form.username" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Password (leave blank to keep unchanged)</label>
            <input v-model="form.password" type="password" />
          </div>
          <button type="submit">Update Profile</button>
        </form>
      </div>
    </AdminLayout>
  </template>

  <script>
  import { ref, onMounted } from 'vue';
  import { useEcommerceStore } from '@/stores/ecommerce';
  import AdminLayout from '@/components/admin/AdminLayout.vue';

  export default {
    components: { AdminLayout },
    setup() {
      const store = useEcommerceStore();
      const form = ref({
        username: '',
        email: '',
        password: '',
      });

      const fetchProfile = async () => {
        await store.fetchProfile();
        form.value.username = store.user.username;
        form.value.email = store.user.email;
      };

      const updateProfile = async () => {
        try {
          const data = { username: form.value.username, email: form.value.email };
          if (form.value.password) {
            data.password = form.value.password;
          }
          await store.updateProfile(data);
          alert('Profile updated successfully');
        } catch (error) {
          alert('Failed to update profile: ' + (error.response?.data?.error || 'Unknown error'));
        }
      };

      onMounted(() => {
        fetchProfile();
      });

      return { form, updateProfile };
    },
  };
  </script>
  <style scoped>
/* AdminSettings.vue Styles */
.settings {
  padding: 0;
  max-width: 600px;
}

h2 {
  font-size: 1.75rem;
  color: #4f46e5;
  margin-bottom: 24px;
  font-weight: 700;
}

form {
  background: #ffffff;
  padding: 28px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 8px;
  color: #4b5563;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  background-color: #f9fafb;
  color: #1f2937;
}

.form-group input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background-color: #fff;
}

.form-group input[type="password"] {
  letter-spacing: 0.1em;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #6366f1;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 8px;
}

button:hover {
  background-color: #4f46e5;
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0);
}

/* Responsive Adjustments */
@media (max-width: 640px) {
  .settings {
    padding: 0;
  }

  form {
    padding: 20px;
  }

  h2 {
    font-size: 1.5rem;
  }

  .form-group input {
    padding: 10px 12px;
  }
}
  </style>

