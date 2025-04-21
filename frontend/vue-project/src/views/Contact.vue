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

// FAQ data
const faqItems = reactive([
{
    question: 'What does minimum order quantity (MOQ) mean?',
    answer: 'Minimum Order Quantity (MOQ) refers to the smallest amount of products a seller is willing to sell at once. Some sellers on our platform set MOQs to make their business operations profitable. MOQs are clearly indicated on product pages where applicable. If you need to purchase below the MOQ, please contact the seller directly to discuss options.',
    isOpen: false
  },
  {
    question: 'How long will my order take to be shipped outside Nairobi?',
    answer: 'For deliveries within Nairobi, all orders made before 11 am will be handled the same day. Any delivery requests after will get to you by midday the next day. For outbound deliveries outside Nairobi, you will receive your packages the next morning. Delivery times may vary during peak seasons or promotional periods.',
    isOpen: false
  },
  {
    question: 'How do I check the orders I have made on the platform?',
    answer: 'To check your order history, simply log into your account and click on "My Orders" in your dashboard. Here you can view all your past orders, track current orders, download invoices, and initiate returns if needed. You can also track your order status through the "Track Order" feature using your order number and email.',
    isOpen: false
  },
  {
    question: 'Why can\'t I make my order payments immediately?',
    answer: 'Payment issues may occur due to several reasons including bank processing delays, unstable internet connection, or system maintenance. We accept M-Pesa, Airtel Money, bank transfers, and major credit/debit cards. If you encounter payment issues, please ensure your payment details are correct and try again after a few minutes. For persistent issues, contact our customer support.',
    isOpen: false
  },
  {
    question: 'A wrong order was delivered to me. How do I return it and have my correct order delivered?',
    answer: 'If you received an incorrect order, please don\'t accept the package or sign for it. If you\'ve already accepted it, contact our customer service within 48 hours and initiate a return through your account. Select "Wrong item received" as the reason. Once we verify your claim, we will expedite the delivery of your correct order and arrange for the return pickup at no cost to you.',
    isOpen: false
  },
  {
    question: 'I would like to request for a product that is not on your platform. How do I request for such an MOQ to be run?',
    answer: 'We\'re always expanding our product range. For products not yet available on our platform, please use the "Product Request" form available in your account dashboard. Provide detailed information about the product, including brand, specifications, and quantity needed. Our sourcing team will contact you within 2-3 business days regarding availability and pricing.',
    isOpen: false
  },
  {
    question: 'How long should I wait before requesting for a delivery?',
    answer: 'After placing your order, please allow the processing time indicated on the product page (typically 1-2 business days for local items and 7-15 days for international items). If you haven\'t received any shipping updates after this period, please contact our customer service. For urgent deliveries, you can select express shipping during checkout for an additional fee.',
    isOpen: false
  },
  {
    question: 'How do I know if my order has been confirmed?',
    answer: 'Once your order is successfully placed, you will receive an order confirmation email and SMS containing your order number and summary. You can also check your order status in the "My Orders" section of your account. The status will update from "Pending" to "Confirmed" once your payment has been processed and verified.',
    isOpen: false
  },
  {
    question: 'Can I change or cancel my order after it has been placed?',
    answer: 'You can cancel or modify your order only if it hasn\'t been processed yet. To do this, go to "My Orders" in your account, select the order you wish to modify, and click on "Cancel Order" or "Modify Order". If the order has already been processed, you will need to wait for delivery and then initiate a return for refund or exchange.',
    isOpen: false
  },
  {
    question: 'Do you offer free shipping?',
    answer: 'We offer free shipping on select items and during promotional periods. Items eligible for free shipping are clearly marked. Additionally, orders above Ksh 10,000 qualify for free shipping within Nairobi. For all other orders, shipping costs are calculated based on weight, dimensions, and delivery location, and will be displayed during checkout before payment.',
    isOpen: false
  }
]);

// Toggle FAQ item function
const toggleFaq = (index) => {
  // Close all FAQ items
  faqItems.forEach((item, i) => {
    if (i !== index) {
      item.isOpen = false;
    }
  });

  // Toggle the clicked item
  faqItems[index].isOpen = !faqItems[index].isOpen;
};

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
          <h2 class="about-h2">GET IN TOUCH</h2>
          <p class='about-p'>We are here for you. How can we help?</p>

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
          <h2 class="about-h2">HEAD OFFICE</h2>
          <div class="office-details">
            <p class='about-p'><strong>Location:</strong> {{ companyInfo.location }}</p>
            <p class='about-p'><strong>Email:</strong> {{ companyInfo.email }}</p>
            <p class='about-p'><strong>Telephone:</strong> {{ companyInfo.telephone }}</p>
            <p class='about-p'>We are available on call during {{ companyInfo.callHours }}</p>
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

      <div class="faq-section">
        <h2 class="about-h2" style="margin-bottom: 1rem;">FREQUENTLY ASKED QUESTIONS</h2>

        <div class="faq-container">
          <div class="faq-item" v-for="(item, index) in faqItems" :key="index">
            <div
              class="faq-question"
              @click="toggleFaq(index)"
              :class="{ 'active': item.isOpen }"
            >
              <span class="faq-icon">{{ item.isOpen ? '−' : '+' }}</span>
              <span class="question-text">{{ item.question }}</span>
            </div>
            <div class="faq-answer" v-show="item.isOpen">
              {{ item.answer }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<style scoped>
.contact-container {
    margin: 0 auto;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.about-h2 {
  font-size: 1.2rem;
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

.faq-section {
  margin-top: 2.5rem;
  margin-bottom: 2rem;
  width: 100%;
}

.faq-container {
  border: 1px solid inherit;
  border-radius: 10px;
  overflow: hidden;
  width: 100%;
}

.faq-item {
  border-bottom: 1px solid inherit;
  width: 100%;
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-question {
  padding: 1rem;
  font-weight: 500;
  /* background-color: #f9f9f9; */
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.3s;
  width: 100%;
  position: relative;
}

.faq-question.active {
  /* background-color: #f0f0f0; */
  color: #8a8f38;
}

.faq-icon {
  margin-right: 0.75rem;
  font-size: 1.2rem;
  width: 20px;
  display: inline-block;
  text-align: center;
  flex-shrink: 0;
}

.faq-answer {
  padding: 1rem;
  /* background-color: white; */
  line-height: 1.6;
  width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .faq-question {
    padding: 0.875rem;
    font-size: 0.95rem;
  }

  .faq-answer {
    padding: 0.875rem;
    font-size: 0.95rem;
  }
}

@media (max-width: 480px) {
  .faq-question {
    padding: 0.75rem;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .faq-answer {
    padding: 0.75rem;
    font-size: 0.9rem;
  }

  .faq-icon {
    margin-right: 0.5rem;
    font-size: 1rem;
    width: 16px;
  }
}

/* Ensure long question text doesn't overflow */
.faq-question {
  flex-wrap: wrap;
}

.faq-question span:first-child {
  flex-shrink: 0;
}

.faq-question span:last-child {
  flex: 1;
}

@media (max-width: 768px) {
  .contact-grid {
    grid-template-columns: 1fr;
  }
  .form-row {
    flex-direction: column;
  }
}

/* Adjust layout for even smaller screens */
@media (max-width: 500px) {
  .form-row {
    gap: 0.5rem;
  }
  .form-group {
    margin-bottom: 0.5rem;
  }
}

/* Adjust FAQ section for smaller screens */
@media (max-width: 480px) {
  .faq-question {
    padding: 0.75rem;
    font-size: 0.9rem;
    line-height: 1.4;
  }
  .faq-answer {
    padding: 0.75rem;
    font-size: 0.9rem;
  }
  .faq-icon {
    margin-right: 0.5rem;
    font-size: 1rem;
    width: 16px;
  }
}
</style>
