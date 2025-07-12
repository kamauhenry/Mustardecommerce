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
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div v-if="success" class="success-message">
          MOQ request submitted successfully!
        </div>
        
        <form @submit.prevent="submitRequest">
          <div class="form-group">
            <input 
              type="text" 
              v-model="productName" 
              placeholder="Product Name*" 
              required
            />
          </div>
          
          <div class="form-group">
            <input 
              type="url" 
              v-model="productLink" 
              placeholder="Product Link*" 
              required
            />
          </div>
          
          <div class="form-group">
            <input 
              type="number" 
              v-model="quantity" 
              placeholder="Quantity*" 
              min="1"
              required
            />
          </div>
          
          <div class="form-group">
            <textarea 
              v-model="description" 
              placeholder="(Optional) Describe the product weight, size, colors etc." 
              rows="4"
            ></textarea>
          </div>
          
          <button type="submit" class="submit-button" :disabled="loading">
            {{ loading ? 'Submitting...' : 'Submit' }}
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
        
        // Auto-close after 2 seconds
        setTimeout(() => {
          this.$emit('close');
        }, 2000);
        
      } catch (error) {
        console.error('Error submitting MOQ request:', error);
        
        if (error.message === 'Authentication required') {
          this.error = 'Please log in to submit an MOQ request';
        } else {
          this.error = error.message || 'Failed to submit request. Please try again.';
        }
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
    }
  },
  
  mounted() {
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
    
    // Focus on first input
    this.$nextTick(() => {
      const firstInput = this.$el.querySelector('input[type="text"]');
      if (firstInput) {
        firstInput.focus();
      }
    });
  },
  
  beforeUnmount() {
    // Re-enable body scroll
    document.body.style.overflow = '';
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  overflow-y: auto;
  padding: 20px;
}

/* Request MOQ Modal */
.request-moq-modal {
  background: linear-gradient(145deg, #ffffff, #f9fafb);
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  padding: 2.5rem;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  margin: auto;
  font-family: 'Inter', sans-serif;
  animation: fadeSlideIn 0.4s ease-out;
  backdrop-filter: blur(8px);
  position: relative;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-shrink: 0;
}

.modal-header h2 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1f2a44;
  margin: 0;
  letter-spacing: -0.5px;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.2s ease, transform 0.2s ease;
}

.close-button:hover {
  color: #1f2a44;
  transform: scale(1.1);
}

.modal-content {
  overflow-y: auto;
  max-height: calc(90vh - 150px);
  padding-right: 10px;
  margin-right: -10px;
}

/* Scrollbar styling */
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.form-group {
  margin-bottom: 1.8rem;
}

.modal-content input,
.modal-content textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1.1rem;
  color: #1f2a44;
  background-color: #f9fafb;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, background-color 0.2s ease;
  box-sizing: border-box;
}

.modal-content input:focus,
.modal-content textarea:focus {
  border-color: #f6673b;
  box-shadow: 0 0 10px rgba(246, 103, 59, 0.2);
  background-color: #ffffff;
  outline: none;
}

.modal-content input::placeholder,
.modal-content textarea::placeholder {
  color: #9ca3af;
  font-style: italic;
}

.modal-content textarea {
  resize: vertical;
  min-height: 120px;
}

.submit-button {
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
  font-size: 1.1rem;
}

.submit-button:hover:not(:disabled) {
  background: linear-gradient(90deg, #d45933, #c87a4d);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(246, 103, 59, 0.3);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0