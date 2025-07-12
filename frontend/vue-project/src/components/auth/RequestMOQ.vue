<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="request-moq-modal">
      <div class="modal-header">
        <h2>Request MOQ Campaign</h2>
        <button @click="$emit('close')" class="close-button">×</button>
      </div>
      
      <div class="modal-content">
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
          <p class="loading-text">Submitting your request...</p>
        </div>
        
        <div v-if="error" class="error-message">
          <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          {{ error }}
        </div>
        
        <div v-if="success" class="success-message">
          <svg class="success-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M9 12l2 2 4-4"/>
            <circle cx="12" cy="12" r="10"/>
          </svg>
          MOQ request submitted successfully!
        </div>
        
        <form @submit.prevent="submitRequest" class="form-container">
          <div class="form-group">
            <label for="productName" class="form-label">Product Name</label>
            <input 
              id="productName"
              type="text" 
              v-model="productName" 
              placeholder="Enter product name" 
              required
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="productLink" class="form-label">Product Link</label>
            <input 
              id="productLink"
              type="url" 
              v-model="productLink" 
              placeholder="https://example.com/product" 
              required
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="quantity" class="form-label">Quantity</label>
            <input 
              id="quantity"
              type="number" 
              v-model="quantity" 
              placeholder="Enter quantity" 
              min="1"
              required
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="description" class="form-label">Description (Optional)</label>
            <textarea 
              id="description"
              v-model="description" 
              placeholder="Describe the product weight, size, colors, etc." 
              rows="4"
              class="form-textarea"
            ></textarea>
          </div>
          
          <button type="submit" class="submit-button" :disabled="loading">
            <span v-if="loading" class="button-spinner"></span>
            <span>{{ loading ? 'Submitting...' : 'Submit Request' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RequestMOQModal',
  emits: ['close', 'submitted'],
  props: {
    store: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      productName: '',
      productLink: '',
      quantity: '',
      description: '',
      loading: false,
      error: '',
      success: false
    };
  },
  
  methods: {
    // Get auth token from localStorage
    getAuthToken() {
      return localStorage.getItem('authToken');
    },

    // Get CSRF token from cookies
    getCsrfTokenFromCookies() {
      const name = 'csrftoken';
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) {
          return value;
        }
      }
      return null;
    },

    // Make API request using fetch
    async makeRequest(url, options = {}) {
      const token = this.getAuthToken();
      const csrfToken = this.getCsrfTokenFromCookies();
      
      const defaultOptions = {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      };
      
      // Add auth token if available
      if (token) {
        defaultOptions.headers['Authorization'] = `Token ${token}`;
      }
      
      // Add CSRF token for POST/PUT/DELETE requests
      if (['POST', 'PUT', 'DELETE'].includes(options.method?.toUpperCase())) {
        if (csrfToken) {
          defaultOptions.headers['X-CSRFToken'] = csrfToken;
        }
      }
      
      const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
          ...defaultOptions.headers,
          ...options.headers
        }
      };
      
      const response = await fetch(url, finalOptions);
      
      // Handle authentication errors
      if (response.status === 401 || response.status === 403) {
        localStorage.removeItem('authToken');
        if (this.store && typeof this.store.logout === 'function') {
          this.store.logout();
        }
        throw new Error('Authentication required');
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    },

    async submitRequest() {
      // Validation
      if (!this.productName || !this.productLink || !this.quantity) {
        this.error = 'Please fill in all required fields';
        setTimeout(() => { this.error = ''; }, 5000);
        return;
      }
      
      this.loading = true;
      this.error = '';
      this.success = false;
      
      try {
        const payload = {
          product_name: this.productName,
          product_link: this.productLink,
          quantity: parseInt(this.quantity),
          description: this.description || ''
        };
        
        const response = await this.makeRequest('https://mustardimports.co.ke/api/moqrequest/', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        
        this.success = true;
        this.$emit('submitted', response);
        
        // Auto-close after 3 seconds
        setTimeout(() => {
          this.$emit('close');
        }, 3000);
        
      } catch (error) {
        console.error('Error submitting MOQ request:', error);
        
        if (error.message === 'Authentication required') {
          this.error = 'Please log in to submit an MOQ request';
        } else {
          this.error = error.message || 'Failed to submit request. Please try again.';
        }
        
        // Auto-clear error after 5 seconds
        setTimeout(() => { this.error = ''; }, 5000);
      } finally {
        this.loading = false;
      }
    },
    
    resetForm() {
      this.productName = '';
      this.productLink = '';
      this.quantity = '';
      this.description = '';
      this.error = '';
      this.success = false;
    },

    handleKeyDown(event) {
      if (event.key === 'Escape') {
        this.$emit('close');
      }
    }
  },
  
  mounted() {
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
    
    // Add keyboard event listener
    document.addEventListener('keydown', this.handleKeyDown);
    
    // Focus on first input
    this.$nextTick(() => {
      const firstInput = this.$el.querySelector('#productName');
      if (firstInput) {
        firstInput.focus();
      }
    });
  },
  
  beforeUnmount() {
    // Re-enable body scroll
    document.body.style.overflow = '';
    
    // Remove keyboard event listener
    document.removeEventListener('keydown', this.handleKeyDown);
  }
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
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
  padding: 1rem;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* Request MOQ Modal */
.request-moq-modal {
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  animation: modalSlideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  margin: auto;
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  position: sticky;
  top: 0;
  background: #ffffff;
  z-index: 10;
  border-radius: 24px 24px 0 0;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  letter-spacing: -0.025em;
}

.close-button {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #1e293b;
  transform: scale(1.05);
}

/* Modal Content */
.modal-content {
  padding: 1.5rem 2rem 2rem;
  position: relative;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 20;
  border-radius: 0 0 24px 24px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f1f5f9;
  border-top: 3px solid #f97316;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 1rem;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Messages */
.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  animation: messageSlideIn 0.3s ease;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.success-message {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

.error-icon,
.success-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

/* Form Styles */
.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  letter-spacing: -0.025em;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  color: #1f2937;
  background: #ffffff;
  transition: all 0.2s ease;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #9ca3af;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

/* Submit Button */
.submit-button {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #ffffff;
  border: none;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.submit-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #ea580c, #dc2626);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(249, 115, 22, 0.3);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.button-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Animations */
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive Design for tablets and below (760px and below) */
@media (max-width: 760px) {
  .modal-overlay {
    padding: 0.5rem;
    align-items: flex-start;
    padding-top: 2rem;
  }

  .request-moq-modal {
    max-width: 100%;
    max-height: calc(100vh - 4rem);
    border-radius: 20px;
  }

  .modal-header {
    padding: 1.5rem 1.5rem 1rem;
    border-radius: 20px 20px 0 0;
  }

  .modal-header h2 {
    font-size: 1.25rem;
  }

  .close-button {
    width: 36px;
    height: 36px;
    font-size: 1.25rem;
  }

  .modal-content {
    padding: 1rem 1.5rem 1.5rem;
  }

  .form-container {
    gap: 1.25rem;
  }

  .form-input,
  .form-textarea {
    padding: 0.75rem;
    font-size: 0.875rem;
  }

  .form-textarea {
    min-height: 80px;
  }

  .submit-button {
    padding: 0.875rem 1.25rem;
    font-size: 0.875rem;
  }

  .error-message,
  .success-message {
    padding: 0.875rem;
    font-size: 0.8125rem;
  }
}

/* Extra small devices (480px and below) */
@media (max-width: 480px) {
  .modal-overlay {
    padding: 0.25rem;
    padding-top: 1rem;
  }

  .request-moq-modal {
    border-radius: 16px;
    max-height: calc(100vh - 2rem);
  }

  .modal-header {
    padding: 1.25rem 1.25rem 0.75rem;
    border-radius: 16px 16px 0 0;
  }

  .modal-header h2 {
    font-size: 1.125rem;
  }

  .close-button {
    width: 32px;
    height: 32px;
    font-size: 1.125rem;
  }

  .modal-content {
    padding: 0.75rem 1.25rem 1.25rem;
  }

  .form-container {
    gap: 1rem;
  }

  .form-input,
  .form-textarea {
    padding: 0.6875rem;
    font-size: 0.875rem;
  }

  .form-textarea {
    min-height: 70px;
  }

  .submit-button {
    padding: 0.8125rem 1rem;
    font-size: 0.875rem;
  }
}

/* Custom scrollbar for webkit browsers */
.request-moq-modal::-webkit-scrollbar {
  width: 6px;
}

.request-moq-modal::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.request-moq-modal::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.request-moq-modal::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>