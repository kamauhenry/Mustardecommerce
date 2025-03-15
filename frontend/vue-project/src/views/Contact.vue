<script setup>
import MainLayout from "@/components/navigation/MainLayout.vue";
import { ref, reactive } from 'vue';

// Form data state
const formData = reactive({
  firstName: '',
  lastName: '',
  email: '',
  subject: '',
  message: '',
  service: ''
});

// Form submission state
const isSubmitting = ref(false);
const formMessage = ref('');
const formMessageType = ref('success');

// Company information
const companyInfo = reactive({
  location: '123 Business Avenue, City, Country',
  email: 'contact@company.com',
  telephone: '+1 (123) 456-7890',
  callHours: '9:00 AM - 5:00 PM (Mon-Fri)'
});

// Form submission handler
const submitForm = async () => {
  isSubmitting.value = true;
  formMessage.value = '';
  
  try {
    // Replace with your actual API endpoint
    const apiUrl = 'https://your-api-endpoint.com/contact';
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    const result = await response.json();
    
    if (response.ok) {
      formMessage.value = 'Thank you! Your message has been sent successfully.';
      formMessageType.value = 'success';
      resetForm();
    } else {
      formMessage.value = result.message || 'An error occurred while submitting the form.';
      formMessageType.value = 'error';
    }
  } catch (error) {
    console.error('Form submission error:', error);
    formMessage.value = 'An error occurred. Please try again later.';
    formMessageType.value = 'error';
  } finally {
    isSubmitting.value = false;
  }
};

// Reset form fields
const resetForm = () => {
  Object.keys(formData).forEach(key => {
    formData[key] = '';
  });
};
</script>

<template>
  <MainLayout>
    <div class="contact-container">
      <h1 class="page-title">CONTACT US</h1>
      
      <div class="contact-grid">
        <!-- Get in Touch Section -->
        <div class="get-in-touch">
          <h2>GET IN TOUCH</h2>
          <p>We are here for you. How can we help?</p>
          
          <form @submit.prevent="submitForm" class="contact-form">
            <div class="form-row">
              <div class="form-group">
                <input 
                  type="text" 
                  v-model="formData.firstName" 
                  placeholder="First name"
                  required
                >
              </div>
              <div class="form-group">
                <input 
                  type="text" 
                  v-model="formData.lastName" 
                  placeholder="Last name"
                  required
                >
              </div>
            </div>
            
            <div class="form-group">
              <input 
                type="email" 
                v-model="formData.email" 
                placeholder="e.g. john@example.com"
                required
              >
            </div>
            
            <div class="form-group">
              <input 
                type="text" 
                v-model="formData.subject" 
                placeholder="Subject"
                required
              >
            </div>
            
            <div class="form-group">
              <textarea 
                v-model="formData.message" 
                placeholder="Message..."
                rows="4"
                required
              ></textarea>
            </div>
            
            <div class="form-group">
              <select 
                v-model="formData.service" 
                required
              >
                <option value="" disabled selected>Select a service</option>
                <option value="consultation">Consultation</option>
                <option value="support">Technical Support</option>
                <option value="quote">Request Quote</option>
                <option value="general">General Inquiry</option>
              </select>
            </div>
            
            <div class="form-actions">
              <button 
                type="submit" 
                :disabled="isSubmitting"
                class="submit-button"
              >
                {{ isSubmitting ? 'Sending...' : 'Send message' }}
              </button>
            </div>
          </form>
          
          <div v-if="formMessage" :class="['form-message', formMessageType]">
            {{ formMessage }}
          </div>
        </div>
        
        <!-- Head Office Section -->
        <div class="head-office">
          <h2>HEAD OFFICE</h2>
          <div class="office-details">
            <p><strong>Location:</strong> {{ companyInfo.location }}</p>
            <p><strong>Email:</strong> {{ companyInfo.email }}</p>
            <p><strong>Telephone:</strong> {{ companyInfo.telephone }}</p>
            <p>We are available on call during {{ companyInfo.callHours }}</p>
          </div>
          
          <div class="social-media">
            <h3>Connect with us on social media</h3>
            <div class="social-icons">
              <a href="#" title="Instagram"><i class="fa-brands fa-instagram"></i></a>
              <a href="#" title="LinkedIn"><i class="fa-brands fa-linkedin"></i></a>
              <a href="#" title="Twitter"><i class="fa-brands fa-twitter"></i></a>
              <a href="#" title="Facebook"><i class="fa-brands fa-facebook"></i></a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<style>
.contact-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-title {
  color: #8a8f38;
  margin-bottom: 2rem;
  font-weight: 500;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 768px) {
  .contact-grid {
    grid-template-columns: 1fr;
  }
}

h2 {
  color: #8a8f38;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.contact-form {
  margin-top: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (max-width: 500px) {
  .form-row {
    flex-direction: column;
  }
}

.form-group {
  flex: 1;
  margin-bottom: 1rem;
}

input, textarea, select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e2e2;
  border-radius: 4px;
  font-size: 1rem;
  background-color: #f9f9f9;
}

textarea {
  resize: vertical;
  min-height: 120px;
}

.submit-button {
  background-color: #e67e22;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #d35400;
}

.submit-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.form-message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
}

.form-message.success {
  background-color: #d4edda;
  color: #155724;
}

.form-message.error {
  background-color: #f8d7da;
  color: #721c24;
}

.office-details p {
  margin-bottom: 0.5rem;
}

.social-media {
  margin-top: 2rem;
}

.social-icons {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.social-icons a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f0f0f0;
  color: #333;
  text-decoration: none;
  transition: all 0.3s;
}

.social-icons a:hover {
  background-color: #8a8f38;
  color: white;
}
</style>