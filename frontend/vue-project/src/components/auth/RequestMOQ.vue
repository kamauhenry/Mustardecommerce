<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="request-moq-modal">
      <div class="modal-header">
        <h2>Request MOQ Campaign</h2>
        <button @click="$emit('close')" class="close-button">×</button>
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
        <button @click="submitRequest" class="submit-button">Submit</button>
      </div>
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

/* Request MOQ Modal */
.request-moq-modal {
  background: linear-gradient(145deg, #ffffff, #f9fafb);
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  padding: 2.5rem;
  width: 100%;
  max-width: 560px;
  margin: 0 auto;
  font-family: 'Inter', sans-serif;
  animation: fadeSlideIn 0.4s ease-out;
  backdrop-filter: blur(8px);
}

.request-moq-modal .modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.request-moq-modal .modal-header h2 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1f2a44;
  margin: 0;
  letter-spacing: -0.5px;
}

.request-moq-modal .close-button {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.2s ease, transform 0.2s ease;
}

.request-moq-modal .close-button:hover {
  color: #1f2a44;
  transform: scale(1.1);
}

.request-moq-modal .modal-content .form-group {
  margin-bottom: 1.8rem;
}

.request-moq-modal .modal-content input,
.request-moq-modal .modal-content textarea,
.request-moq-modal .modal-content input[type="file"] {
  width: 100%;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1.1rem;
  color: #1f2a44;
  background-color: #f9fafb;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.2s ease;
}

.request-moq-modal .modal-content input:focus,
.request-moq-modal .modal-content textarea:focus,
.request-moq-modal .modal-content input[type="file"]:focus {
  border-color: #f6673b;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
  background-color: #ffffff;
  outline: none;
}

.request-moq-modal .modal-content input::placeholder,
.request-moq-modal .modal-content textarea::placeholder {
  color: #9ca3af;
  font-style: italic;
}

.request-moq-modal .modal-content textarea {
  resize: vertical;
  min-height: 120px;
}

.request-moq-modal .modal-content input[type="file"] {
  padding: 0.75rem;
  cursor: pointer;
  border: 1px dashed #d1d5db;
  background-color: #f9fafb;
}

.request-moq-modal .modal-content input[type="file"]::-webkit-file-upload-button {
  background: #e5e7eb;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.request-moq-modal .modal-content input[type="file"]::-webkit-file-upload-button:hover {
  background: #d1d5db;
}

.request-moq-modal .submit-button {
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

.request-moq-modal .submit-button:hover {
  background: linear-gradient(90deg, #d45933, #c87a4d);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(246, 103, 59, 0.3);
}

.request-moq-modal .submit-button:active {
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
  .request-moq-modal {
    padding: 1.8rem;
    max-width: 92%;
  }

  .request-moq-modal .modal-header h2 {
    font-size: 1.2rem;
  }

  .request-moq-modal .close-button {
    font-size: 1.2rem;
  }

  .request-moq-modal .modal-content input,
  .request-moq-modal .modal-content textarea,
  .request-moq-modal .modal-content input[type="file"] {
    font-size: 1rem;
    padding: 0.9rem;
  }

  .request-moq-modal .submit-button {
    padding: 0.9rem;
    font-size: 1rem;
  }

  .request-moq-modal .modal-content textarea {
    min-height: 100px;
  }
}
</style>