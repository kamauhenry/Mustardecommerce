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
      <div class="modal-header">
        <div class="logo">
          <img src="@/assets/images/mustard-imports.png" alt="Mustard Imports Logo" class="logo-image" />
        </div>
        <div class="tabs">
          <button
            class="tab active"
            @click="switchToLogin"
          >
            LOGIN
          </button>
          <button
            class="tab"
            @click="switchToRegister"
          >
            REGISTER
          </button>
        </div>
      </div>
      <LoginModal
        @switch-to-register="switchToRegister"
        @close="closeModals"
      />
    </Modal>

    <Modal :isOpen="showRegisterModal" @close="closeModals">
      <div class="modal-header">
        <div class="logo">
          <img src="@/assets/images/mustard-imports.png" alt="Mustard Imports Logo" class="logo-image" />
        </div>
        <div class="tabs">
          <button
            class="tab"
            @click="switchToLogin"
          >
            LOGIN
          </button>
          <button
            class="tab active"
            @click="switchToRegister"
          >
            REGISTER
          </button>
        </div>
      </div>
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

<style scoped>
.modal-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.logo-image {
  width: 120px;
  height: auto;
  margin-bottom: 0.5rem;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 0;
  width: 100%;
}

.tab {
  flex: 1;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #fff;
  background-color: #f28c38; /* Orange to match the screenshot */
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.tab.active {
  background-color: #fff;
  color: #f28c38;
}

.tab:hover {
  background-color: #e07b30; /* Slightly darker orange on hover */
}
</style>
