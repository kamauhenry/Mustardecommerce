<template>
  <div class="auth-buttons">
    <template v-if="authStore.isAuthenticated">
      <button @click="authStore.logout" class="icon-button">
        <LogoutIcon />
      </button>
    </template>
    <template v-else>
      <button @click="openAuthModal" class="icon-button">
        <LoginIcon />
      </button>
    </template>

    <Modal :isOpen="showAuthModal" @close="closeModal">
      <div class="modal-header">
        <div class="logo">
          <img src="@/assets/images/mustard-imports.png" alt="Mustard Imports Logo" class="logo-image" />
        </div>
      </div>
      <AuthModal @close="closeModal" />
    </Modal>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useAuthStore } from '@/stores/modules/auth';
import Modal from '@/components/auth/Modal.vue';
import AuthModal from '@/components/auth/AuthModal.vue';
import LoginIcon from '@/components/icons/IconLogin.vue';
import LogoutIcon from '@/components/icons/IconLogout.vue';

const props = defineProps({
  autoShowLogin: {
    type: Boolean,
    default: false,
  },
});

const authStore = useAuthStore();
const showAuthModal = ref(false);

onMounted(() => {
  if (props.autoShowLogin && !authStore.isAuthenticated) {
    openAuthModal();
  }
});

watch(
  () => props.autoShowLogin,
  (newValue) => {
    if (newValue && !authStore.isAuthenticated) {
      openAuthModal();
    }
  }
);

const openAuthModal = () => {
  showAuthModal.value = true;
};

const closeModal = () => {
  showAuthModal.value = false;
};
</script>

<style scoped>
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.logo {
  width: 200px;
  height: auto;
  display: flex;
  justify-content: center;
  margin: 1rem;
}

.logo-image {
  width: 200px;
  height: auto;
  margin-bottom: 0.5rem;
}

.icon-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
}

.icon-button svg {
  display: flex;
  justify-content: center;
  width: 1.5rem;
  height: auto;
  fill: #838636;
  transition: fill 0.3s ease;
}

.icon-button:hover svg {
  fill: #D4A017;
}
</style>