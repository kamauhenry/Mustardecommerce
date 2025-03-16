<template>
  <div>
    <template v-if="store.isAuthenticated">
      <span>Welcome, User {{ store.userId }}</span>
      <button @click="store.logout">Logout</button>
    </template>
    <template v-else>
      <button @click="openLoginModal">Login</button>
      <button @click="openRegisterModal">Register</button>
    </template>

    <Modal :isOpen="showLoginModal" @close="closeModals">
      <LoginModal
        @switch-to-register="switchToRegister"
        @close="closeModals"
      />
    </Modal>

    <Modal :isOpen="showRegisterModal" @close="closeModals">
      <RegisterModal
        @switch-to-login="switchToLogin"
        @close="closeModals"
      />
    </Modal>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import Modal from './Modal.vue';
import LoginModal from './LoginModal.vue';
import RegisterModal from './RegisterModal.vue';

const store = useEcommerceStore();
const showLoginModal = ref(false);
const showRegisterModal = ref(false);

const openLoginModal = () => {
  showLoginModal.value = true;
  showRegisterModal.value = false;
};

const openRegisterModal = () => {
  showRegisterModal.value = true;
  showLoginModal.value = false;
};

const switchToRegister = () => {
  showLoginModal.value = false;
  showRegisterModal.value = true;
};

const switchToLogin = () => {
  showRegisterModal.value = false;
  showLoginModal.value = true;
};

const closeModals = () => {
  showLoginModal.value = false;
  showRegisterModal.value = false;
};
</script>
