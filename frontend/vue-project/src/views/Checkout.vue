<template>
  <MainLayout>
    <div class="checkout-container">
      <h1>Checkout</h1>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading checkout...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="$router.go(0)" class="action-button retry-button">Try Again</button>
      </div>

      <div v-else class="checkout-content">
        <!-- Left Column: Payment and Shipping -->
        <div class="checkout-form">
          <!-- Payment Section -->
          <div v-if="paymentStatus === 'initial'" class="payment-section">
            <h2>Payment (M-Pesa)</h2>
            <div class="input-group">
              <span class="input-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M2 2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H2zm10.5 3.5a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V7.707l-4.146 4.147a.5.5 0 0 1-.708 0L5.5 10.207 2.853 12.854a.5.5 0 1 1-.708-.708L5.293 9 3.146 6.854a.5.5 0 1 1 .708-.708L6.5 8.793 9.146 6.146a.5.5 0 0 1 .708 0L12.5 8.793V6a.5.5 0 0 1 .5-.5z"/>
                </svg>
              </span>
              <input v-model="phoneNumber" placeholder="Phone (e.g., 0712345678)" aria-label="Phone number for M-Pesa payment" />
            </div>
            <span v-if="error && !phoneNumber" class="error-message">{{ error }}</span>
            <button @click="updateAndPay" class="action-button pay-button">Pay Now</button>
          </div>

          <!-- Shipping Section -->
          <div v-if="paymentStatus === 'initial'" class="shipping-section">
            <h2>Shipping Information</h2>
            <button @click="showAddLocation = true" class="add-location-button">Add New Location</button>
            <div class="location-section">
              <label>Select Saved Location:</label>
              <select v-model="selectedDeliveryLocation">
                <option v-for="loc in deliveryLocations" :key="loc.id" :value="loc.id">
                  {{ loc.name }} - {{ loc.address }}
                </option>
                <option v-if="deliveryLocations.length === 0" disabled>No locations available</option>
              </select>
            </div>

            <div class="shipping-method">
              <label>Shipping Method:</label>
              <select v-model="shippingMethod">
                <option value="standard">Standard (KES 0)</option>
                <option value="express">Express (KES 500)</option>
              </select>
            </div>
          </div>

          <!-- Payment Pending -->
          <div v-if="paymentStatus === 'pending'" class="payment-pending">
            <p>Payment pending. Complete on your phone.</p>
            <button @click="verifyPayment" class="action-button verify-button">Verify Payment</button>
          </div>
        </div>

        <!-- Right Column: Order Summary -->
        <div class="order-summary">
          <h2>Order Summary</h2>
          <div v-if="orderItems.length > 0">
            <div v-for="item in orderItems" :key="item.id" class="summary-item">
              <span>{{ item.product_name }}</span>
              <span>Qty: {{ item.quantity }} - KES {{ formatPrice(item.price * item.quantity) }}</span>
            </div>
            <div class="summary-total">
              <span>Total</span>
              <span>KES {{ formatPrice(orderTotal) }}</span>
            </div>
          </div>
          <div v-else class="loading-summary">
            <div class="spinner"></div>
            <p>Loading order summary...</p>
          </div>
        </div>
      </div>

      <!-- Add New Location Modal -->
      <div v-if="showAddLocation" class="modal-overlay" @click="showAddLocation = false">
        <div class="add-location-modal" @click.stop>
          <h3>Add New Location</h3>
          <div class="input-group">
            <input v-model="newLocation.name" placeholder="Location Name" />
          </div>
          <div class="input-group">
            <input v-model="newLocation.address" placeholder="Address" />
          </div>
          <div class="modal-buttons">
            <button @click="addNewLocation" class="action-button save-button">Save</button>
            <button @click="showAddLocation = false" class="cancel-button">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, onServerPrefetch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '../components/navigation/MainLayout.vue';

export default {
  components: { MainLayout },
  setup() {
    const store = useEcommerceStore();
    const route = useRoute();
    const router = useRouter();

    const orderId = route.query.orderId;
    const order = ref(null);
    const deliveryLocations = ref([]);
    const selectedDeliveryLocation = ref(null);
    const shippingMethod = ref('standard');
    const phoneNumber = ref('');
    const paymentStatus = ref('initial');
    const loading = ref(true);
    const error = ref(null);
    const showAddLocation = ref(false);
    const newLocation = ref({ name: '', address: '' });
    const isMounted = ref(true);
    let cancelPendingRequests = false;

    const isClient = typeof window !== 'undefined';

    // Computed properties for order summary, similar to Cart.vue
    const orderItems = computed(() => order.value?.items || []);
    const orderTotal = computed(() =>
      orderItems.value.reduce((sum, item) => sum + (item.price * item.quantity || 0), 0)
    );

    // Format price to 2 decimal places, matching Cart.vue
    const formatPrice = (price) => (Math.round(price * 100) / 100).toFixed(2);

    onServerPrefetch(async () => {
      if (store.isAuthenticated) {
        try {
          await Promise.all([store.fetchOrder(orderId), store.fetchDeliveryLocations()]);
        } catch (err) {
          console.error('Server prefetch error:', err);
        }
      }
    });

    onMounted(async () => {
      if (!isClient) return;
      loading.value = true;
      try {
        if (!store.currentUser) {
          await store.fetchCurrentUserInfo();
        }
        if (!store.isAuthenticated || !store.currentUser) {
          if (isMounted.value) {
            error.value = 'Please log in to proceed with checkout.';
            store.showAuthModal = true;
            router.push('/login');
          }
          return;
        }

        const [fetchedOrder, fetchedLocations] = await Promise.all([
          store.fetchOrder(orderId),
          store.fetchDeliveryLocations(),
        ]);
        if (cancelPendingRequests || !isMounted.value) return;
        order.value = fetchedOrder || { items: [], total_price: 0 };
        deliveryLocations.value = Array.isArray(fetchedLocations) ? fetchedLocations : [];
        selectedDeliveryLocation.value =
          order.value.delivery_location?.id ||
          (deliveryLocations.value.length > 0 ? deliveryLocations.value[0].id : null);
        shippingMethod.value = order.value.shipping_method || 'standard';
      } catch (err) {
        if (cancelPendingRequests || !isMounted.value) return;
        error.value = err.message || 'Failed to load order or delivery locations';
      } finally {
        if (isMounted.value) loading.value = false;
      }
    });

    onUnmounted(() => {
      isMounted.value = false;
      cancelPendingRequests = true;
    });

    const addNewLocation = async () => {
      try {
        const newLoc = await store.addDeliveryLocation(newLocation.value);
        if (cancelPendingRequests || !isMounted.value) return;
        deliveryLocations.value.push(newLoc);
        selectedDeliveryLocation.value = newLoc.id;
        showAddLocation.value = false;
        newLocation.value = { name: '', address: '' };
      } catch (err) {
        if (isMounted.value) {
          error.value = err.message || 'Failed to add delivery location';
        }
      }
    };

    const updateAndPay = async () => {
      try {
        if (!selectedDeliveryLocation.value) {
          if (isMounted.value) error.value = 'Please select or add a delivery location';
          return;
        }
        if (!phoneNumber.value || !/^(0\d{9}|254\d{9})$/.test(phoneNumber.value)) {
          if (isMounted.value) error.value = 'Please enter a valid phone number (e.g., 0712345678 or 254712345678)';
          return;
        }
        if (!orderId) {
          if (isMounted.value) error.value = 'Order ID is missing';
          return;
        }
        await store.updateOrderShipping(orderId, shippingMethod.value, selectedDeliveryLocation.value);
        await store.initiatePayment(orderId, phoneNumber.value);
        if (cancelPendingRequests || !isMounted.value) return;
        paymentStatus.value = 'pending';
      } catch (err) {
        if (isMounted.value) {
          error.value = err.response?.data?.error || 'Failed to update or initiate payment';
        }
      }
    };

    const verifyPayment = async () => {
      try {
        const paymentDetails = await store.verifyPayment(orderId);
        if (cancelPendingRequests || !isMounted.value) return;
        if (paymentDetails.payment_status === 'completed') {
          router.push({ path: '/checkout/confirmation', query: { orderId } });
        } else {
          alert('Payment not completed yet');
        }
      } catch (err) {
        if (isMounted.value) {
          error.value = err.message || 'Payment verification failed';
        }
      }
    };

    return {
      order,
      orderItems,
      orderTotal,
      deliveryLocations,
      selectedDeliveryLocation,
      shippingMethod,
      phoneNumber,
      paymentStatus,
      loading,
      error,
      showAddLocation,
      newLocation,
      addNewLocation,
      updateAndPay,
      verifyPayment,
      orderId,
      formatPrice,
    };
  },
};
</script>

<style scoped>
.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #2d3748;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  text-align: left;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #f7fafc;
  padding-bottom: 0.5rem;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

/* Loading and Error States */
.loading-state, .error-state {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid #edf2f7;
  margin: 1rem 0;
}

.spinner {
  border: 4px solid #edf2f7;
  border-top: 4px solid #f6ad55;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p, .error-state p {
  font-size: 1rem;
  color: #4a5568;
  margin-bottom: 1.5rem;
}

.error-message {
  color: #e53e3e;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  display: block;
}

/* Checkout Content */
.checkout-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  align-items: start;
}

.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Payment and Shipping Sections */
.payment-section, .shipping-section, .payment-pending {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #edf2f7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.payment-pending {
  text-align: center;
}

.payment-pending p {
  font-size: 1rem;
  color: #4a5568;
  margin-bottom: 1rem;
}

/* Form Inputs */
.input-group {
  position: relative;
  margin-bottom: 1rem;
}

.input-icon {
  position: absolute;
  top: 50%;
  left: 0.75rem;
  transform: translateY(-50%);
  color: #a0aec0;
}

input, select {
  width: 100%;
  padding: 0.75rem;
  padding-left: 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #2d3748;
  transition: all 0.2s ease;
}

select {
  padding-left: 0.75rem;
}

input:focus, select:focus {
  outline: none;
  border-color: #f6ad55;
  box-shadow: 0 0 0 3px rgba(246, 173, 85, 0.1);
}

label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.location-section, .shipping-method {
  margin-bottom: 1rem;
}

/* Buttons */
.action-button {
  background: linear-gradient(135deg, #f6ad55, #ed8936);
  color: #fff;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  width: 100%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-button:hover {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.add-location-button {
  background: none;
  border: 1px solid #e2e8f0;
  color: #f6ad55;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-location-button:hover {
  background: #f7fafc;
  border-color: #f6ad55;
}

/* Order Summary */
.order-summary {
  background: linear-gradient(135deg, #f7fafc, #edf2f7);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 1rem;
  border: 1px solid #e2e8f0;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #4a5568;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #e2e8f0;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  font-size: 1.25rem;
  font-weight: 700;
  color: #2d3748;
  margin-top: 1rem;
  border-top: 1px dashed #e2e8f0;
  padding-top: 1rem;
}

.loading-summary {
  text-align: center;
  padding: 1rem;
}

/* Add Location Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.add-location-modal {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease;
}

.add-location-modal h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 1rem;
}

.modal-buttons {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.cancel-button {
  background: #edf2f7;
  color: #4a5568;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  width: 100%;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background: #e2e8f0;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .checkout-content {
    grid-template-columns: 1fr;
  }

  .order-summary {
    position: static;
  }
}

@media (max-width: 768px) {
  .checkout-container {
    padding: 1rem;
  }

  h1 {
    font-size: 1.5rem;
  }

  h2 {
    font-size: 1.125rem;
  }

  .payment-section, .shipping-section, .payment-pending {
    padding: 1rem;
  }

  input, select {
    padding: 0.5rem;
    padding-left: 2rem;
    font-size: 0.75rem;
  }

  .action-button, .cancel-button {
    padding: 0.5rem;
    font-size: 0.75rem;
  }

  .summary-item, .summary-total {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .checkout-container {
    padding: 0.75rem;
  }

  h1 {
    font-size: 1.25rem;
  }

  .add-location-modal {
    width: 95%;
    padding: 1rem;
  }

  .modal-buttons {
    flex-direction: column;
  }
}
</style>
