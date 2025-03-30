<template>
  <div class="request-moq-modal">
    <div class="modal-header">
      <h2>Request MOQ Campaign</h2>
      <!-- <button @click="$emit('close')" class="close-button">×</button> -->
    </div>
    <div class="modal-content">
      <div class="form-group">
        <input type="text" v-model="productName" placeholder="Product Name" />
      </div>
      <div class="form-group">
        <input type="text" v-model="productLink" placeholder="Product Link" />
      </div>
      <div class="form-group">
        <input type="number" v-model="quantity" placeholder="Quantity" />
      </div>
      <div class="form-group">
        <textarea v-model="description" placeholder="(Optional) Describe the product weight, size, colors etc." rows="4"></textarea>
      </div>
      <div class="form-group">
        <input type="file" @change="handleFileUpload" multiple />
      </div>
      <button @click="submitRequest" class="submit-button">SUBMIT</button>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['close'],
  data() {
    return {
      productName: '',
      productLink: '',
      quantity: '',
      description: '',
      files: [],
    };
  },
  methods: {
    handleFileUpload(event) {
      this.files = event.target.files;
      console.log('Uploaded files:', this.files);
    },
    submitRequest() {
      // Add your logic here to submit the MOQ request
      // This could involve making an API call to your backend
      console.log('Submitting MOQ request:', {
        productName: this.productName,
        productLink: this.productLink,
        quantity: this.quantity,
        description: this.description,
        files: this.files,
      });
    },
  },
};
</script>

<style scoped>
.request-moq-modal {
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

.modal-content input,
.modal-content textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.modal-content textarea {
  resize: vertical;
}

.submit-button {
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

.submit-button:hover {
  background-color: #d35400;
}
</style>
