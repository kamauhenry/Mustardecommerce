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
.settings {
  padding: 1rem;
  max-width: 500px;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #6f42c1;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

button:hover {
  opacity: 0.9;
}

/* Responsive Adjustments */
@media (max-width: 480px) {
  .settings {
    padding: 0.5rem;
  }

  h2 {
    font-size: 1.3rem;
  }

  .form-group input {
    font-size: 0.9rem;
  }
}
</style>
