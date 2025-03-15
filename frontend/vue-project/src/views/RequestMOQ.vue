<template>
    <div class="modal-backdrop" v-if="isOpen" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Request MOQ Campaign</h3>
          <button class="close-button" @click="closeModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="submitForm">
            <div class="form-group">
              <label for="productName">Product Name</label>
              <input 
                type="text" 
                id="productName" 
                v-model="formData.productName" 
                required
              >
            </div>
            
            <div class="form-group">
              <label for="productLink">Product Link</label>
              <input 
                type="text" 
                id="productLink" 
                v-model="formData.productLink" 
                required
              >
            </div>
            
            <div class="form-group">
              <label for="quantity">Quantity</label>
              <input 
                type="number" 
                id="quantity" 
                v-model="formData.quantity" 
                required
              >
            </div>
            
            <div class="form-group">
              <label for="description">Description</label>
              <textarea 
                id="description" 
                v-model="formData.description" 
                placeholder="(Optional) Describe the product weight, size, colors, etc."
              ></textarea>
            </div>
            
            <div class="form-group">
              <label>Photo(s)</label>
              <div class="file-upload">
                <label for="photos" class="file-upload-btn">Choose Files</label>
                <input 
                  type="file" 
                  id="photos" 
                  @change="handleFileUpload" 
                  multiple
                  accept="image/*"
                  class="file-input"
                >
                <span class="file-name">{{ fileStatus }}</span>
              </div>
            </div>
            
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              {{ isSubmitting ? 'SUBMITTING...' : 'SUBMIT' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'RequestMOQ',
    props: {
      isOpen: {
        type: Boolean,
        default: false
      }
    },
    data() {
      return {
        formData: {
          productName: '',
          productLink: '',
          quantity: '',
          description: '',
          photos: []
        },
        isSubmitting: false,
        fileStatus: 'No file chosen'
      };
    },
    methods: {
      closeModal() {
        this.$emit('close');
      },
      
      handleFileUpload(event) {
        const files = event.target.files;
        if (files && files.length > 0) {
          this.formData.photos = Array.from(files);
          this.fileStatus = files.length === 1 
            ? files[0].name 
            : `${files.length} files selected`;
        } else {
          this.formData.photos = [];
          this.fileStatus = 'No file chosen';
        }
      },
      
      async submitForm() {
        this.isSubmitting = true;
        
        try {
          // Create FormData object to send files
          const formData = new FormData();
          formData.append('productName', this.formData.productName);
          formData.append('productLink', this.formData.productLink);
          formData.append('quantity', this.formData.quantity);
          formData.append('description', this.formData.description);
          
          // Append all photos
          this.formData.photos.forEach((file, index) => {
            formData.append(`photo${index}`, file);
          });
          
          // Replace with your actual API endpoint
          const response = await fetch('https://your-api-endpoint.com/request-moq', {
            method: 'POST',
            body: formData
          });
          
          if (response.ok) {
            // Success handling
            this.$emit('success', 'Your MOQ request has been submitted successfully');
            this.resetForm();
            this.closeModal();
          } else {
            // Error handling
            const error = await response.json();
            this.$emit('error', error.message || 'Failed to submit the request');
          }
        } catch (error) {
          console.error('Error submitting form:', error);
          this.$emit('error', 'An error occurred while submitting your request');
        } finally {
          this.isSubmitting = false;
        }
      },
      
      resetForm() {
        this.formData = {
          productName: '',
          productLink: '',
          quantity: '',
          description: '',
          photos: []
        };
        this.fileStatus = 'No file chosen';
      }
    }
  };
  </script>
  
  <style scoped>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    width: 90%;
    max-width: 500px;
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
  }
  
  .modal-header h3 {
    margin: 0;
    color: #8a8f38;
    font-weight: 500;
  }
  
  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 5px;
    color: #666;
    font-size: 14px;
  }
  
  input[type="text"],
  input[type="number"],
  textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #eee;
    border-radius: 4px;
    background-color: #f7f7f7;
    font-size: 14px;
  }
  
  textarea {
    min-height: 80px;
    resize: vertical;
  }
  
  .file-upload {
    display: flex;
    align-items: center;
  }
  
  .file-upload-btn {
    display: inline-block;
    padding: 8px 12px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    margin-right: 10px;
  }
  
  .file-input {
    display: none;
  }
  
  .file-name {
    color: #666;
    font-size: 14px;
  }
  
  .submit-btn {
    width: 100%;
    padding: 12px;
    background-color: #e67e22;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.3s;
    margin-top: 10px;
  }
  
  .submit-btn:hover {
    background-color: #d35400;
  }
  
  .submit-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  </style>