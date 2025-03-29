<template>
  <div class="auth-buttons">
    <template v-if="store.isAuthenticated">
      <!-- <span class="welcome-text">Welcome, {{ store.username }}</span> -->
      <button @click="store.logout" class="icon-button">
        <LogoutIcon />
      </button>
    </template>
    <template v-else>
      <button @click="openLoginModal" class="icon-button">
        <LoginIcon />
      </button>
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
import { ref, watch, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import Modal from '@/components/auth/Modal.vue';
import LoginModal from '@/components/auth/LoginModal.vue';
import RegisterModal from '@/components/auth/RegisterModal.vue';

// Import the provided SVG icons as components
import LoginIcon from '@/components/icons/IconLogin.vue';
import LogoutIcon from '@/components/icons/IconLogout.vue';

const props = defineProps({
  autoShowLogin: {
    type: Boolean,
    default: false
  }
});

const store = useEcommerceStore();
const showLoginModal = ref(false);
const showRegisterModal = ref(false);


onMounted(() => {
  if (props.autoShowLogin && !store.isAuthenticated) {
    openLoginModal();
  }
});

watch(() => props.autoShowLogin, (newValue) => {
  if (newValue && !store.isAuthenticated) {
    openLoginModal();
  }
});

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
.auth-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.welcome-text {
  font-size: 0.9rem;
  color: #333;
}

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
  width: 70%;
}

.tab {
  flex: 1;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #c9c9c9;
  background-color: #ebebeb; /* Orange to match the screenshot */
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.tab.active {
  background-color: #e2cf1f;
  color: #ffffff;
}

.tab:hover {
  background-color: #e2ce1f8f; /* Slightly darker orange on hover */
}

/* Style for the icon buttons */
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
  fill: #838636; /* Matches the fill color of the provided SVGs */
  transition: fill 0.3s ease;
}

.icon-button:hover svg {
  fill: #f28c38; /* Orange on hover to match the theme */
}

/* Style for the text button (Register) */
.text-button {
  background: none;
  border: none;
  padding: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #838636;
  cursor: pointer;
  transition: color 0.3s ease;
}

.text-button:hover {
  color: #f28c38; /* Orange on hover to match the theme */
}
</style>
