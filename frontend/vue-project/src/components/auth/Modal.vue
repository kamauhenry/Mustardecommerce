<template>
  <div v-if="isOpen" class="modal-overlay">
    <div class="modal-content">
      <button class="modal-close" @click="closeModal">×</button>
      <div class="modal-body">
        <slot></slot>
      </div>
      <RequestMOQModal 
        v-if="showMOQModal" 
        @close="closeMOQModal" 
        @submitted="onMOQSubmitted" 
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close']);

const closeModal = () => {
  emit('close');
};

// Prevent background scrolling when modal is open
onMounted(() => {
  if (props.isOpen) {
    document.body.style.overflow = 'hidden';
  }
});

onUnmounted(() => {
  document.body.style.overflow = '';
});

// Watch for changes in isOpen to toggle body overflow
watch(
  () => props.isOpen,
  (newValue) => {
    document.body.style.overflow = newValue ? 'hidden' : '';
  }
);
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Position at the top */
  z-index: 1000;
  overflow-y: auto; /* Allow scrolling if modal content overflows viewport */
  padding: 0.5rem; /* Minimal padding */
  padding-top: 5rem; /* Slightly reduced to bring modal higher */
}

.modal-content {
  background: white;
  border-radius: 20px;
  position: relative;
  width: 350px; /* Reduced width for better fit */
  max-width: 90%;
  max-height: 100vh; /* Reduced to ensure modal fits better on small screens */
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-out;
}

.modal-body {
  overflow-y: auto; /* Make the content scrollable */
  padding: 0.5rem; /* Minimal padding */
  max-height: 90vh; /* Reduced to fit within modal-content */
}

.modal-close {
  position: absolute;
  top: 8px; /* Reduced to save space */
  right: 8px;
  background: none;
  border: none;
  font-size: 20px; /* Slightly smaller */
  color: #333;
  cursor: pointer;
  transition: color 0.3s ease;
}

.modal-close:hover {
  color:#D4A017;
}

/* Animation for modal entrance */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 540px) {
  .modal-overlay {
    padding: 0.25rem; /* Further reduced padding */
    padding-top: 2.5rem; /* Minimal offset from top */
  }

  .modal-content {
    width: 90%; /* Use most of the screen width */
    max-height: 60vh; /* Further reduced for mobile */
    border-radius: 12px; /* Slightly smaller border-radius for mobile */
  }

  .modal-body {
    max-height: 50vh; /* Adjusted to fit within modal-content */
    padding: 0.25rem; /* Minimal padding */
  }

  .modal-close {
    top: 6px;
    right: 6px;
    font-size: 18px;
  }
}

@media (max-width: 400px) {
  .modal-content {
    width: 95%; /* Maximize width for very small screens */
    max-height: 55vh; /* Further reduced */
  }

  .modal-body {
    max-height: 45vh; /* Adjusted */
  }
}
</style>