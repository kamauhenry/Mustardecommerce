<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import SearchBar from './SearchBar.vue';
import IconLightMode from '@/components/icons/IconLightMode.vue';
import IconCart from '@/components/icons/IconCart.vue';
import IconLogin from '@/components/icons/IconLogin.vue';
import IconLogout from '@/components/icons/IconLogout.vue';
import LoginRegisterModal from '@/components/modals/LoginRegisterModal.vue';

const showModal = ref(false);
const authStore = useAuthStore();

// Initialize authentication on component mount
authStore.initializeAuth();

// Methods to handle modal and logout
const toggleModal = () => {
  showModal.value = !showModal.value;
};

const handleLogout = async () => {
  await authStore.logout();
  // Optionally redirect to home page
  window.location.href = '/';
};
</script>

<template>
  <div class="navbar">
    <div class="logo-image">
      <router-link to="/">
        <img
          src="@/assets/images/mustard-imports.png"
          alt="Mustard Imports Logo"
          class="main-logo"
        />
      </router-link>
    </div>
    <SearchBar></SearchBar>
    <div class="nav-icons">
      <div class="icon">
        <IconLightMode></IconLightMode>
      </div>
      <div class="icon">
        <IconCart></IconCart>
      </div>
      <div class="icon" @click="toggleModal">
        <IconLogin v-if="!authStore.isAuthenticated" />
        <IconLogout v-else @click="handleLogout" />
      </div>
    </div>
    <LoginRegisterModal
      v-if="showModal"
      :show="showModal"
      @close="showModal = false"
      :initial-tab="'login'"
    />
  </div>
</template>

<style scoped>
.navbar {
  padding: .3rem 0.1rem;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
}

.logo-image {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
}

.main-logo {
  width: 120px;
  height: 80px;
}

.nav-icons {
  display: flex;
  gap: 1.4rem;
}

.nav-icons .icon {
  border: none;
  border-radius: 30%;
  background-color: var(--background-color-one);
  padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
