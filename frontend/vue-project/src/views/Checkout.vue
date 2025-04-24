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
        <button @click="retryFetch" class="action-button retry-button">Try Again</button>
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
                <p v-for="attr in item.variant_attributes" :key="attr.attribute_name">
                  {{ attr.attribute_name }}: {{ attr.value }}
                </p>
                <p>Qty: {{ item.quantity }}</p>
                <p>KES {{ formatPrice(item.price) }} each</p>
                <p>Total: KES {{ formatPrice(item.quantity * item.price) }}</p>
              </div>
            </div>
          </div>

          <!-- Delivery Location -->
          <div class="section delivery-location">
            <h3>Delivery Location</h3>
            <div v-if="deliveryLocations.length" class="location-select">
              <select v-model="selectedDeliveryLocationId" class="location-dropdown">
                <option :value="null" disabled>Select a delivery location</option>
                <option v-for="location in deliveryLocations" :key="location.id" :value="location.id">
                  {{ location.name }} - {{ location.address }}
                </option>
              </select>
              <button @click="addNewLocation" class="add-location-button">Add New Location</button>
            </div>
            <div v-else>
              <p>No delivery locations available.</p>
              <button @click="addNewLocation" class="add-location-button">Add New Location</button>
            </div>
          </div>

          <!-- Shipping Method -->
          <div class="section shipping-method">
            <h3>Shipping Method</h3>
            <div v-if="isLoadingShippingMethods" class="skeleton-shipping">
              <div class="skeleton-shipping-option"></div>
            </div>
            <div v-else-if="shippingMethods.length" class="shipping-options">
              <select v-model="selectedShippingMethodId" @change="updateShippingMethod" class="shipping-select">
                <option :value="null" disabled>Select a shipping method</option>
                <option v-for="method in shippingMethods" :key="method.id" :value="method.id">
                  {{ method.name }} (KES {{ formatPrice(method.price) }})
                </option>
              </select>
            </div>
            <div v-else>
              <p>No shipping methods available.</p>
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
            :disabled="!selectedDeliveryLocationId || !selectedShippingMethodId || !phoneNumber"
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
import axios from 'axios';

export default {
  components: { MainLayout },
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const route = useRoute();
    const loading = ref(false);
    const error = ref(null);
    const order = ref(null);
    const deliveryLocations = ref([]);
    const selectedDeliveryLocationId = ref(null);
    const shippingMethods = ref([]);
    const isLoadingShippingMethods = ref(false);
    const selectedShippingMethodId = ref(null);
    const phoneNumber = ref('');

    // Computed properties
    const isAuthenticated = computed(() => store.isAuthenticated);
    const orderSubtotal = computed(() =>
      order.value ? order.value.items.reduce((sum, item) => sum + item.quantity * item.price, 0) : 0
    );

    // Format price to 2 decimal places
    const formatPrice = (price) => (Math.round(price * 100) / 100).toFixed(2);

    // Navigation functions
    const goToLogin = () => router.push('/login');
    const goToCart = () => router.push('/cart');

    // Fetch order details
    const fetchOrder = async () => {
      const orderId = route.query.orderId;
      if (!orderId) {
        error.value = 'No order specified';
        return;
      }
      loading.value = true;
      try {
        const response = await store.apiInstance.get(`/api/order/${orderId}/`);
        order.value = response.data;
        selectedShippingMethodId.value = order.value.shipping_method?.id || null;
        selectedDeliveryLocationId.value = order.value.delivery_location?.id || null;
        error.value = null;
      } catch (err) {
        error.value = 'Failed to load order details';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    // Fetch delivery locations
    const fetchDeliveryLocations = async () => {
      try {
        const response = await store.apiInstance.get('/api/delivery-locations/');
        deliveryLocations.value = response.data;
      } catch (err) {
        console.error('Failed to fetch delivery locations:', err);
        toast.error('Failed to load delivery locations.', { autoClose: 3000 });
      }
    };

    // Fetch shipping methods
    const fetchShippingMethods = async () => {
      isLoadingShippingMethods.value = true;
      try {
        const response = await axios.get('/api/shipping-methods/', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        shippingMethods.value = response.data;
      } catch (err) {
        console.error('Failed to fetch shipping methods:', err);
        toast.error('Failed to load shipping methods.', { autoClose: 3000 });
      } finally {
        isLoadingShippingMethods.value = false;
      }
    };

    // Update shipping method
    const updateShippingMethod = async () => {
      try {
        await store.apiInstance.patch(`/api/order/${order.value.id}/update-shipping/`, {
          shippingMethodId: selectedShippingMethodId.value,
        });
        await fetchOrder();
        toast.success('Shipping method updated!', { autoClose: 3000 });
      } catch (err) {
        console.error('Failed to update shipping method:', err);
        toast.error('Failed to update shipping method.', { autoClose: 3000 });
      }
    };

    // Add new delivery location (placeholder)
    const addNewLocation = () => {
      toast.info('Add new delivery location functionality not implemented yet.', { autoClose: 3000 });
      // Implement navigation to a form or modal for adding a new location
    };

    // Confirm order
    const confirmOrder = async () => {
      try {
        const response = await store.apiInstance.post(`/api/order/${order.value.id}/confirm/`, {
          delivery_location_id: selectedDeliveryLocationId.value,
          phone_number: phoneNumber.value,
        });
        router.push({ path: '/confirmation', query: { orderId: order.value.id } });
        toast.success('Order confirmed successfully!', { autoClose: 3000 });
      } catch (err) {
        console.error('Failed to confirm order:', err);
        toast.error('Failed to confirm order. Please try again.', { autoClose: 3000 });
      }
    };

    // Retry fetching order
    const retryFetch = () => fetchOrder();

    onMounted(() => {
      if (!store.apiInstance) store.initializeApiInstance();
      fetchOrder();
      fetchDeliveryLocations();
      fetchShippingMethods();
    });

    return {
      loading,
      error,
      isAuthenticated,
      order,
      deliveryLocations,
      selectedDeliveryLocationId,
      shippingMethods,
      isLoadingShippingMethods,
      selectedShippingMethodId,
      phoneNumber,
      orderSubtotal,
      formatPrice,
      goToLogin,
      goToCart,
      retryFetch,
      updateShippingMethod,
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

.loading-state, .error-state, .auth-prompt, .empty-checkout {
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.action-button:hover {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
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
  width: 60px;
  height: 60px;
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

.location-select {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.location-dropdown, .shipping-select, .phone-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
}

.location-dropdown:focus, .shipping-select:focus, .phone-input:focus {
  outline: none;
  border-color: #f6ad55;
  box-shadow: 0 0 0 3px rgba(246, 173, 85, 0.2);
}

.add-location-button {
  background: #f6ad55;
  color: #fff;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.add-location-button:hover {
  background: #ed8936;
}

.skeleton-shipping {
  height: 40px;
  background: #e0e0e0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}

.skeleton-shipping-option {
  height: 20px;
  background: #e0e0e0;
  border-radius: 4px;
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

.confirm-button:hover {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
}

.confirm-button:disabled {
  background: #ccc;
  cursor: not-allowed;
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