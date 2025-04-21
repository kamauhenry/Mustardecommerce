<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="track-order-modal">
      <div class="modal-header">
        <h2>Track Order</h2>
        <button @click="$emit('close')" class="close-button">×</button>
      </div>
      <div class="modal-content">
        <div class="form-group">
          <input type="text" v-model="orderNumber" placeholder="e.g. 1Y5HXET" />
        </div>
        <button @click="validateOrder" class="validate-button">Validate</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['close'],
  data() {
    return {
      orderNumber: '',
    };
  },
  methods: {
    validateOrder() {
      console.log('Validating order number:', this.orderNumber);
    },
  },
};
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Track Order Modal */
.track-order-modal {
  background: linear-gradient(145deg, #ffffff, #f9fafb);
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  padding: 2.5rem;
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
  animation: fadeSlideIn 0.4s ease-out;
  backdrop-filter: blur(8px);
}

.track-order-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.track-order-modal .modal-header h2 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1f2a44;
  margin: 0;
  letter-spacing: -0.5px;
}

.track-order-modal .close-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.2s ease, transform 0.2s ease;
}

.track-order-modal .close-button:hover {
  color: #1f2a44;
  transform: scale(1.1);
}

.track-order-modal .modal-content .form-group {
  margin-bottom: 1.8rem;
}

.track-order-modal .modal-content input {
  width: 100%;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1.1rem;
  color: #1f2a44;
  background-color: #f9fafb;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.2s ease;
}

.track-order-modal .modal-content input:focus {
  border-color: #f6673b;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
  background-color: #ffffff;
  outline: none;
}

.track-order-modal .modal-content input::placeholder {
  color: #9ca3af;
  font-style: italic;
}

.track-order-modal .validate-button {
  background: linear-gradient(90deg, #f6673b, #fa9860);
  color: #ffffff;
  border: none;
  padding: 1rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  width: 100%;
  letter-spacing: 0.5px;
  transition: background 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
}

.track-order-modal .validate-button:hover {
  background: linear-gradient(90deg, #d45933, #c87a4d);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(246, 103, 59, 0.3);
}

.track-order-modal .validate-button:active {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(246, 103, 59, 0.2);
}

/* Animation for modal entrance */
@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 540px) {
  .track-order-modal {
    padding: 1.8rem;
    max-width: 92%;
  }

  .track-order-modal .modal-header h2 {
    font-size: 1.2rem;
  }

  .track-order-modal .close-button {
    font-size: 1.2rem;
  }

  .track-order-modal .modal-content input {
    font-size: 1rem;
    padding: 0.9rem;
  }

  .track-order-modal .validate-button {
    padding: 0.9rem;
    font-size: 1rem;
  }
}
</style>