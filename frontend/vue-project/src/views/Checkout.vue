<template>
  <MainLayout>
    <div class="checkout-container">
      <h2 class="checkout-title">Checkout</h2>

      <!-- Loading, Error, Auth, and Empty States -->
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

      <!-- Checkout Content -->
      <div v-else class="checkout-content">
        <div class="checkout-sections">
          <!-- Order Items -->
          <div class="section order-items">
            <h3>Order Items ({{ order.items.length }} items)</h3>
            <div v-for="item in order.items" :key="item.id" class="order-item">
              <div class="item-image">
                <img :src="item.product?.thumbnail || grey" :alt="item.product_name" />
              </div>
              <div class="item-details">
                <h4>{{ item.product_name }}</h4>
                <p v-if="item.is_pick_and_pay" class="pick-and-pay-label">Pick & Pay</p>
                <p v-for="(value, attrName) in item.attributes" :key="attrName">{{ attrName }}: {{ value }}</p>
                <p v-if="item.is_pick_and_pay && item.product.inventory">Available: {{ item.product.inventory.quantity }} units</p>
                <p v-else-if="item.product.moq_status === 'active'">MOQ: {{ item.product.moq_per_person || 'N/A' }} items</p>
                <p>Qty: {{ item.quantity }}</p>
                <p>Total: KES {{ formatPrice(calculateLineTotal(item)) }}</p>
              </div>
            </div>
          </div>

          <!-- Delivery Location -->
          <div class="section delivery-location">
            <h3>{{ isPayAndPickOrder ? 'Pickup Location' : 'Delivery Location' }}</h3>
            <div class="delivery-location-select">
              <select v-model="selectedDeliveryLocationId" :disabled="isProcessing.confirm">
                <option :value="null">Select a {{ isPayAndPickOrder ? 'pickup' : 'delivery' }} location</option>
                <option v-for="loc in filteredDeliveryLocations" :key="loc.id" :value="loc.id">
                  {{ loc.name }} ({{ loc.county }}, {{ loc.ward }})
                </option>
              </select>
              <button @click="showAddLocationForm = true" class="add-location-button" v-if="!isProcessing.confirm">Add New Location</button>
            </div>
            <div v-if="showAddLocationForm" class="location-form">
              <h4>Add New {{ isPayAndPickOrder ? 'Pickup' : 'Delivery' }} Location</h4>
              <div class="form-group">
                <label for="location-name">Name</label>
                <input v-model="newLocation.name" id="location-name" required />
              </div>
              <div class="form-group">
                <label for="location-county">County</label>
                <select v-model="newLocation.county" id="location-county" @change="fetchWards" required>
                  <option :value="null">Select County</option>
                  <option v-for="county in counties" :key="county" :value="county">{{ county }}</option>
                </select>
              </div>
              <div class="form-group">
                <label for="location-ward">Ward</label>
                <select v-model="newLocation.ward" id="location-ward" :disabled="!newLocation.county" required>
                  <option :value="null">Select Ward</option>
                  <option v-for="ward in wards" :key="ward" :value="ward">{{ ward }}</option>
                </select>
              </div>
              <div class="form-actions">
                <button @click="addNewLocation" class="action-button" :disabled="isProcessing.addLocation">Save</button>
                <button @click="showAddLocationForm = false" class="action-button cancel-button">Cancel</button>
              </div>
            </div>
          </div>

          <!-- Shipping Method (MOQ Only) -->
          <div class="section shipping-method" v-if="!isPayAndPickOrder">
            <h3>Shipping Method</h3>
            <p v-if="order.shipping_method">{{ order.shipping_method.name }} (KES {{ formatPrice(order.shipping_cost) }})</p>
            <p v-else>No shipping method selected.</p>
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
              @input="phoneError = null"
              :disabled="isProcessing.confirm"
            />
            <p v-if="phoneError" class="error-message">{{ phoneError }}</p>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="order-summary">
          <h3>Order Summary</h3>
          <div class="summary-row">
            <span>Subtotal</span>
            <span>KES {{ formatPrice(orderSubtotal) }}</span>
          </div>
          <div class="summary-row" v-if="!isPayAndPickOrder">
            <span>Shipping Cost</span>
            <span>KES {{ formatPrice(order.shipping_cost) }}</span>
          </div>
          <div class="summary-row total">
            <span>Total</span>
            <span>KES {{ formatPrice(orderTotal) }}</span>
          </div>
          <button
            @click="initiatePayment"
            class="confirm-button"
            :disabled="!canConfirm || isProcessing.confirm"
          >
            {{ isProcessing.confirm ? 'Processing...' : 'Make Payment' }}
          </button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/modules/auth';
import { useOrdersStore } from '@/stores/modules/orders';
import { useUserStore } from '@/stores/modules/user';
import { useApiInstance } from '@/stores/composables/useApiInstance';
import { toast } from 'vue3-toastify';
import MainLayout from '../components/navigation/MainLayout.vue';
import grey from '@/assets/images/placeholder.jpeg';

export default {
  components: { MainLayout },
  setup() {
    const authStore = useAuthStore();
    const ordersStore = useOrdersStore();
    const userStore = useUserStore();
    const { api } = useApiInstance();
    const router = useRouter();
    const route = useRoute();
    const loading = ref(false);
    const error = ref(null);
    const order = ref(null);
    const phoneNumber = ref('');
    const deliveryLocations = ref([]);
    const selectedDeliveryLocationId = ref(null);
    const showAddLocationForm = ref(false);
    const counties = ref([]);
    const wards = ref([]);
    const newLocation = ref({

      county: null,
      ward: null,
    });
    const isProcessing = ref({
      addLocation: false,
      confirm: false,
      retry: false,
    });
    const phoneError = ref(null);

    // Computed Properties
    const isAuthenticated = computed(() => authStore.isAuthenticated);
    const isPayAndPickOrder = computed(() => {
      return order.value?.items?.length > 0 && order.value.items.every(item => item.is_pick_and_pay);
    });
    const orderSubtotal = computed(() => {
      return order.value ? order.value.items.reduce((sum, item) => {
        const price = item.is_pick_and_pay
          ? parseFloat(item.price || 0)
          : item.quantity < (item.product.moq_per_person || 1)
          ? parseFloat(item.product.below_moq_price || item.price || 0)
          : parseFloat(item.price || 0);
        return sum + (price * item.quantity);
      }, 0) : 0;
    });
    const orderTotal = computed(() => {
      const shippingCost = isPayAndPickOrder.value ? 0 : parseFloat(order.value.shipping_cost || 0);
      return (orderSubtotal.value + shippingCost).toFixed(2);
    });
    const filteredDeliveryLocations = computed(() => {
      return deliveryLocations.value.filter(loc => 
        isPayAndPickOrder.value ? loc.is_shop_pickup : !loc.is_shop_pickup
      );
    });
    const canConfirm = computed(() => {
      if (!isAuthenticated.value || !order.value) return false;
      if (isPayAndPickOrder.value) {
        return !!phoneNumber.value && 
               !validatePhoneNumber(phoneNumber.value) && 
               !!selectedDeliveryLocationId.value;
      } else {
        return !!phoneNumber.value && 
               !validatePhoneNumber(phoneNumber.value) && 
               !!selectedDeliveryLocationId.value;
      }
    });

    // Functions
    const validatePhoneNumber = (phone) => {
      const phoneRegex = /^(\+2547|07)\d{8}$/;
      if (!phone) return 'Phone number is required';
      if (!phoneRegex.test(phone)) return 'Please enter a valid Kenyan phone number (e.g., +254712345678 or 0712345678)';
      return null;
    };

    const formatPrice = (price) => {
      const num = parseFloat(price || 0);
      return isNaN(num) ? '0.00' : (Math.round(num * 100) / 100).toFixed(2);
    };

    const calculateLineTotal = (item) => {
      const price = item.is_pick_and_pay
        ? item.price
        : item.quantity < item.product.moq_per_person
        ? item.product.below_moq_price || item.price
        : item.price;
      return price * item.quantity;
    };

    const goToLogin = () => router.push('/login');
    const goToCart = () => router.push('/cart');

    const fetchOrder = async () => {
      let orderId = route.query.orderId;
      if (!orderId) {
        error.value = 'No order specified';
        return;
      }
      orderId = orderId.replace(/^MI/, '');
      loading.value = true;
      try {
        const response = await ordersStore.fetchOrder(orderId);
        order.value = response;
        error.value = null;
      } catch (err) {
        error.value = 'Failed to load order details';
        toast.error('Failed to load order details.', { autoClose: 3000 });
      } finally {
        loading.value = false;
      }
    };

    const fetchDeliveryLocations = async () => {
      try {
        deliveryLocations.value = await userStore.fetchAddresses();
        const defaultLocation = deliveryLocations.value.find(loc => loc.is_default && (isPayAndPickOrder.value ? loc.is_shop_pickup : !loc.is_shop_pickup));
        if (defaultLocation) selectedDeliveryLocationId.value = defaultLocation.id;
      } catch (err) {
        toast.error('Failed to fetch delivery locations.', { autoClose: 3000 });
      }
    };

    const fetchCounties = async () => {
      try {
        const response = await api.get('/counties/');
        counties.value = response.data?.counties || response.counties || [];
      } catch (err) {
        toast.error('Failed to fetch counties.', { autoClose: 3000 });
      }
    };

    const fetchWards = async () => {
      if (!newLocation.value.county) {
        wards.value = [];
        return;
      }
      try {
        const response = await api.get(`/wards/?county=${newLocation.value.county}`);
        wards.value = response.data?.wards || response.wards || [];
      } catch (err) {
        toast.error('Failed to fetch wards.', { autoClose: 3000 });
      }
    };

    const addNewLocation = async () => {
      if (!newLocation.value.name || !newLocation.value.county || !newLocation.value.ward) {
        toast.error('Please fill in all location fields.', { autoClose: 3000 });
        return;
      }
      isProcessing.value.addLocation = true;
      try {
        const locationData = {
          ...newLocation.value,
          is_shop_pickup: isPayAndPickOrder.value,
        };
        const response = await userStore.addAddress(locationData);
        deliveryLocations.value.push(response);
        selectedDeliveryLocationId.value = response.id;
        showAddLocationForm.value = false;
        newLocation.value = {  county: null, ward: null };
        toast.success('Location added successfully!', { autoClose: 3000 });
      } catch (err) {
        toast.error('Failed to add location.', { autoClose: 3000 });
      } finally {
        isProcessing.value.addLocation = false;
      }
    };

    const initiatePaymentHandler = async () => {
      phoneError.value = validatePhoneNumber(phoneNumber.value);
      if (phoneError.value) {
        toast.error(phoneError.value, { autoClose: 3000 });
        return;
      }
      if (!selectedDeliveryLocationId.value) {
        toast.error('Please select a delivery or pickup location.', { autoClose: 3000 });
        return;
      }
      isProcessing.value.confirm = true;
      try {
        // Update order with delivery location
        await ordersStore.updateOrderShipping(order.value.id, null, selectedDeliveryLocationId.value);
        // Initiate payment
        await ordersStore.initiatePayment(order.value.id, phoneNumber.value);
        router.push({ path: '/confirmation', query: { orderId: order.value.id } });
        toast.success('Payment initiated! Awaiting confirmation...', { autoClose: 3000 });
      } catch (err) {
        toast.error(err.message || 'Failed to initiate payment.', { autoClose: 3000 });
      } finally {
        isProcessing.value.confirm = false;
      }
    };

    onMounted(() => {
      fetchOrder();
      fetchDeliveryLocations();
      fetchCounties();
    });

    return {
      loading,
      error,
      isAuthenticated,
      order,
      phoneError,
      phoneNumber,
      showAddLocationForm,
      newLocation,
      deliveryLocations,
      selectedDeliveryLocationId,
      counties,
      wards,
      fetchWards,
      addNewLocation,
      isProcessing,
      orderSubtotal,
      orderTotal,
      isPayAndPickOrder,
      filteredDeliveryLocations,
      canConfirm,
      formatPrice,
      calculateLineTotal,
      goToLogin,
      goToCart,
      initiatePayment: initiatePaymentHandler,
      retryFetch: fetchOrder,
      grey,
    };
  },
};
</script>
<style scoped>
/* General styles for all dropdowns */
select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: #fff;
  color: #2d3748;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%232d3748' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1.5em;
  cursor: pointer;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

select:focus {
  outline: none;
  border-color: #f6ad55;
  box-shadow: 0 0 0 3px rgba(246, 173, 85, 0.2);
}

select:invalid,
select option[value=""] {
  color: #a0aec0; /* Gray out placeholder option */
}

/* Delivery location select container */
.delivery-location-select {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

/* Add New Location button */
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
  align-self: flex-start;
}

.add-location-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
}

.add-location-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.checkout-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.loading-state,
.error-state,
.auth-prompt,
.empty-checkout {
  padding: 1.5rem;
  text-align: center;
  margin: 0.75rem 0;
  border: none;
}

.spinner {
  border: 4px solid #edf2f7;
  border-top: 4px solid #f6ad55;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 0.75rem;
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
  gap: 1rem;
}

.checkout-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.order-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
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

.pick-and-pay-label {
  color: #2b6cb0;
  font-size: 0.875rem;
  font-weight: 500;
  background: #ebf8ff;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.availability,
.moq-info {
  color: #d9534f;
  font-size: 0.875rem;
}

.low-stock-warning,
.moq-warning {
  font-size: 0.75rem;
  color: #d9534f;
}

.location-form {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 8px;
}

.location-form h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.form-group {
  margin-bottom: 0.75rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #f6ad55;
  box-shadow: 0 0 0 3px rgba(246, 173, 85, 0.2);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
}

.order-summary {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 1rem;
}

.order-summary h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.summary-row.total {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
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
  margin-top: 1rem;
}

.confirm-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
}

.confirm-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.phone-input,
.form-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
}

.phone-input:focus,
.form-input:focus {
  outline: none;
  border-color: #f6ad55;
  box-shadow: 0 0 0 3px rgba(246, 173, 85, 0.2);
}

/* Responsive adjustments */
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
    padding: 10px;
  }

  .checkout-title {
    font-size: 1.5rem;
  }

  .section {
    padding: 1rem;
  }

  .delivery-location-select {
    gap: 0.5rem;
  }

  select {
    padding: 0.4rem;
    font-size: 0.85rem;
  }

  .add-location-button {
    padding: 0.6rem 1.2rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .checkout-container {
    padding: 8px;
  }

  .checkout-title {
    font-size: 1.25rem;
  }

  select {
    font-size: 0.8rem;
  }

  .add-location-button {
    width: 100%;
    padding: 0.6rem;
  }
}
</style>