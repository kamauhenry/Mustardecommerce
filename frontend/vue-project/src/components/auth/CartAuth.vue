<template>
  <div class="auth-buttons">
    <template v-if="authStore.isAuthenticated">
      <router-link to="/cart">
        <IconCart/>
      </router-link>
    </template>
    <template v-else>
      <button @click="openLoginModal" class="icon-button">
        <IconCart/>
      </button>
    </template>

    <Modal :isOpen="showLoginModal" @close="closeModals">
      <div class="modal-header">
        <div class="logo">
          <img src="@/assets/images/mustard-imports.png" alt="Mustard Imports Logo" class="logo-image" />
        </div>

      </div>
      <LoginModal
        @switch-to-register="switchToRegister"
        @close="closeModals"
      />
    </Modal>


  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useAuthStore } from '@/stores/modules/auth';
import Modal from '@/components/auth/Modal.vue';
import LoginModal from '@/components/auth/AuthModal.vue';


// Import the provided SVG icons as components
import IconCart from '../icons/IconCart.vue';

const props = defineProps({
  autoShowLogin: {
    type: Boolean,
    default: false
  }
});
const emit = defineEmits(['close']);
const closeModals = () => emit('close');

const authStore = useAuthStore();
const showLoginModal = ref(false);



onMounted(() => {
  if (props.autoShowLogin && !authStore.isAuthenticated) {
    openLoginModal();
  }
});

watch(() => props.autoShowLogin, (newValue) => {
  if (newValue && !authStore.isAuthenticated) {
    openLoginModal();
  }
});

const openLoginModal = () => {
  showLoginModal.value = true;
  
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
  fill:#D4A017; /* Orange on hover to match the theme */
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
  color:#D4A017; /* Orange on hover to match the theme */
}
</style>
