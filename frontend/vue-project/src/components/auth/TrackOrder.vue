<template>
  <div class="track-order-modal">
    <div class="modal-header">
      <h2>Track Order</h2>
      <button @click="$emit('close')" class="close-button">×</button>
    </div>
    <div class="modal-content">
      <div class="form-group">
        <input type="text" v-model="orderNumber" placeholder="e.g. 1Y5HXET" />
      </div>
      <button @click="validateOrder" class="validate-button">VALIDATE</button>
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
      // Add your logic here to validate the order number
      // This could involve making an API call to your backend
      console.log('Validating order number:', this.orderNumber);
    },
  },
};
</script>

<style scoped>
.track-order-modal {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h2 {
  font-size: 1.5rem;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #666;
}

.modal-content .form-group {
  margin-bottom: 20px;
}

.modal-content input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.validate-button {
  background-color: #e67e22;
  color: #fff;
  border: none;
  padding: 12px 20px;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
}

.validate-button:hover {
  background-color: #d35400;
}
</style>
