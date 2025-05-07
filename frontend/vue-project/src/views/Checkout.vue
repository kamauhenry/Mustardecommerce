<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <MainLayout>
    <div class="checkout-container">
      <h2 class="checkout-title">Checkout</h2>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading checkout details...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="retryFetch" class="action-button retry-button" :disabled="isProcessing.retry">Try Again</button>
      </div>

      <div v-else-if="!isAuthenticated" class="auth-prompt">
        <p>Please login to proceed with checkout</p>
        <button @click="goToLogin" class="action-button login-button">Login</button>
      </div>

      <div v-else-if="!order" class="empty-checkout">
        <p>No order to process</p>
        <button @click="goToCart" class="action-button cart-button">Back to Cart</button>
      </div>

      <div v-else class="checkout-content">
        <div class="checkout-sections">
          <!-- Order Items -->
          <div class="section order-items">
            <h3>Order Items ({{ order.items.length }} items)</h3>
            <div v-for="item in order.items" :key="item.id" class="order-item">
              <div class="item-image">
                <img :src="item.product?.thumbnail || grey" alt="Item image" />
              </div>
              <div class="item-details">
                <h4>{{ item.product_name }}</h4>
                <p v-for="(value, attrName) in item.attributes" :key="attrName">
                  {{ attrName }}: {{ value }}
                </p>
                <p>Qty: {{ item.quantity }}</p>
                <p>KES {{ formatPrice(item.price) }} each</p>
                <p>Total: KES {{ formatPrice(item.line_total) }}</p>
              </div>
            </div>
          </div>

          <!-- Delivery Location -->
          <div class="section delivery-location">
            <h3>Delivery Location</h3>
            <div v-if="order.delivery_location">
              <p>{{ order.delivery_location.name }} - {{ order.delivery_location.address }}</p>
            </div>
            <div v-else>
              <p>No delivery location selected.</p>
            </div>
            <button @click="showAddLocationForm = true" class="add-location-button" :disabled="isProcessing.addLocation">Add New Location</button>

            <!-- Add Delivery Location Form -->
            <div v-if="showAddLocationForm" class="location-form">
              <h4>Add New Delivery Location</h4>
              <form @submit.prevent="addNewLocation">
                <div class="form-group">
                  <label for="location-name">Name</label>
                  <input
                    id="location-name"
                    v-model="newLocation.name"
                    type="text"
                    placeholder="e.g., Ngong"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="location-address">Address</label>
                  <input
                    id="location-address"
                    v-model="newLocation.address"
                    type="text"
                    placeholder="e.g., 123 Main St, Nairobi"
                    required
                  />
                </div>
                <div class="form-actions">
                  <button type="submit" class="action-button" :disabled="isProcessing.addLocation">Save</button>
                  <button type="button" @click="showAddLocationForm = false" class="action-button cancel-button" :disabled="isProcessing.addLocation">Cancel</button>
                </div>
              </form>
            </div>
          </div>

          <!-- Shipping Method -->
          <div class="section shipping-method">
            <h3>Shipping Method</h3>
            <div v-if="order.shipping_method">
              <p>{{ order.shipping_method.name }}</p>
            </div>
            <div v-else>
              <p>No shipping method selected.</p>
            </div>
          </div>

          <!-- Payment Details -->
          <div class="section payment-details">
            <h3>Payment Details</h3>
            <label for="phone-number">Phone Number (for M-Pesa)</label>
            <input
              id="phone-number"
              v-model="phoneNumber"
              type="text"
              placeholder="e.g., +254712345678"
              class="phone-input"
            />
          </div>
        </div>

        <!-- Order Summary -->
        <div class="order-summary">
          <h3>Order Summary</h3>
          <div class="summary-row">
            <span>Subtotal</span>
            <span>KES {{ formatPrice(orderSubtotal) }}</span>
          </div>
          <div class="summary-row">
            <span>Shipping Cost</span>
            <span>KES {{ formatPrice(order.shipping_cost) }}</span>
          </div>
          <div class="summary-row total">
            <span>Total</span>
            <span>KES {{ formatPrice(order.total_price) }}</span>
          </div>
          <button
            @click="confirmOrder"
            class="confirm-button"
            :disabled="!order.delivery_location || !order.shipping_method || !phoneNumber || isProcessing.confirm"
          >
            Confirm Order
          </button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import { toast } from 'vue3-toastify';
import MainLayout from '../components/navigation/MainLayout.vue';
import grey from '@/assets/images/placeholder.jpeg';

export default {
  components: { MainLayout },
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const route = useRoute();
    const loading = ref(false);
    const error = ref(null);
    const order = ref(null);
    const phoneNumber = ref('');
    const showAddLocationForm = ref(false);
    const newLocation = ref({
      name: '',
      address: '',
    });
    const isProcessing = ref({
      addLocation: false,
      confirm: false,
      retry: false,
    });

    // Computed properties
    const isAuthenticated = computed(() => store.isAuthenticated);
    const orderSubtotal = computed(() =>
      order.value ? order.value.items.reduce((sum, item) => sum + item.line_total, 0) : 0
    );

    // Format price to 2 decimal places
    const formatPrice = (price) => (Math.round(price * 100) / 100).toFixed(2);

    // Navigation functions
    const goToLogin = () => router.push('/login');
    const goToCart = () => router.push('/cart');

    // Fetch order details
    const fetchOrder = async () => {
      let orderId = route.query.orderId;
      if (!orderId) {
        error.value = 'No order specified';
        return;
      }
      // Remove 'MI' prefix if present
      orderId = orderId.replace(/^MI/, '');
      loading.value = true;
      isProcessing.value.retry = true;
      try {
        const response = await store.apiInstance.get(`orders/${orderId}/`);
        order.value = response.data;
        error.value = null;
      } catch (err) {
        error.value = 'Failed to load order details';
        console.error(err);
        toast.error('Failed to load order details. Please try again.', { autoClose: 3000 });
      } finally {
        loading.value = false;
        isProcessing.value.retry = false;
      }
    };

    // Add new delivery location
    const addNewLocation = async () => {
      isProcessing.value.addLocation = true;
      try {
        // Check if user has a default delivery location
        const deliveryLocations = await store.fetchDeliveryLocations();
        const hasDefault = deliveryLocations.some(loc => loc.is_default);
        const locationData = {
          ...newLocation.value,
          isDefault: !hasDefault, // Set as default if no default exists
        };
        const response = await store.addDeliveryLocation(locationData);
        // Update order's delivery location directly
        order.value.delivery_location = {
          id: response.id,
          name: response.name,
          address: response.address,
          is_default: response.is_default,
          created_at: response.created_at,
          updated_at: response.updated_at,
        };
        await store.updateOrderShipping(order.value.id, order.value.shipping_method.id, response.id);
        toast.success('Delivery location added successfully!', { autoClose: 3000 });
        showAddLocationForm.value = false;
        newLocation.value = { name: '', address: '' };
      } catch (err) {
        console.error('Failed to add delivery location:', err);
        toast.error(err.response?.data?.error || 'Failed to add delivery location. Please try again.', { autoClose: 3000 });
      } finally {
        isProcessing.value.addLocation = false;
      }
    };

    // Confirm order
    const confirmOrder = async () => {
      isProcessing.value.confirm = true;
      try {
        const response = await store.initiatePayment(order.value.id, phoneNumber.value);
        router.push({ path: '/confirmation', query: { orderId: order.value.id } });
        toast.success('Order confirmed successfully!', { autoClose: 3000 });
      } catch (err) {
        console.error('Failed to confirm order:', err);
        toast.error(err.response?.data?.error || 'Failed to confirm order. Please try again.', { autoClose: 3000 });
      } finally {
        isProcessing.value.confirm = false;
      }
    };

    // Retry fetching order
    const retryFetch = () => fetchOrder();

    onMounted(() => {
      if (!store.apiInstance) store.initializeApiInstance();
      fetchOrder();
    });

    return {
      loading,
      error,
      isAuthenticated,
      order,
      phoneNumber,
      showAddLocationForm,
      newLocation,
      isProcessing,
      orderSubtotal,
      formatPrice,
      goToLogin,
      goToCart,
      retryFetch,
      addNewLocation,
      confirmOrder,
      grey,
    };
  },
};
</script>

<style scoped>
.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.checkout-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.loading-state,
.error-state,
.auth-prompt,
.empty-checkout {
  padding: 2rem;
  text-align: center;
  margin: 1rem 0;
  border: none;
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
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.add-location-button {
  background: linear-gradient(135deg, #f6ad55, #ed8936);
  color: #fff;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button {
  background: linear-gradient(135deg, #f6ad55, #ed8936);
  color: #fff;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
}

.action-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.cancel-button {
  background: #e2e8f0;
  color: #2d3748;
}

.cancel-button:hover:not(:disabled) {
  background: #cbd5e0;
}

.checkout-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.checkout-sections {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.order-item {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details h4 {
  font-size: 1rem;
  font-weight: 600;
}

.item-details p {
  font-size: 0.875rem;
  margin: 0.25rem 0;
}

.location-form {
  margin-top: 1rem;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 8px;
}

.location-form h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
}

.form-group input:focus {
  outline: none;
  border-color: #f6ad55;
  box-shadow: 0 0 0 3px rgba(246, 173, 85, 0.2);
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.order-summary {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 1rem;
}

.order-summary h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.summary-row.total {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 1rem;
  padding-top: 1rem;
}

.confirm-button {
  background: linear-gradient(135deg, #f6ad55, #ed8936);
  color: #fff;
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1.5rem;
}

.confirm-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
}

.confirm-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.phone-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
}

.phone-input:focus {
  outline: none;
  border-color: #f6ad55;
  box-shadow: 0 0 0 3px rgba(246, 173, 85, 0.2);
}

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
    padding: 15px;
  }

  .checkout-title {
    font-size: 1.5rem;
  }

  .section {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .checkout-container {
    padding: 10px;
  }

  .checkout-title {
    font-size: 1.25rem;
  }
}
</style>