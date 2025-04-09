<template>
  <MainLayout>
    <div class="checkout-container">
      <h1>Checkout</h1>

      <div v-if="loading">Loading...</div>
      <div v-else-if="error">{{ error }}</div>
      <div v-else class="checkout-content">
        <!-- Left Column: Payment -->
        <div v-if="paymentStatus === 'initial'" class="payment-section">
          <h2>Payment (M-Pesa)</h2>
          <input v-model="phoneNumber" placeholder="Phone (e.g., 0712345678)" />
          <span v-if="error && !phoneNumber" style="color: red;">{{ error }}</span>
          <button @click="updateAndPay">Pay</button>
        </div>
        <!-- Right Column: Order Summary and Shipping -->
        <div class="order-shipping-section">
          <!-- Order Summary -->
          <div v-if="order && order.items" class="order-summary">
            <h2>Order Summary</h2>
            <div v-for="item in order.items" :key="item.id">
              {{ item.product_name }} - Qty: {{ item.quantity }} - KES {{ (item.price * item.quantity).toFixed(2) }}
            </div>
            <p>Total: KES {{ Number(order.total_price || 0).toFixed(2) }}</p>
          </div>
          <div v-else>Loading order summary...</div>

          <!-- Shipping Section -->
          <div v-if="paymentStatus === 'initial'" class="shipping-section">
            <h2>Shipping Information</h2>
            <button @click="showAddLocation = true">Add New Location</button>
            <div class="location-section">
              <label>Select Saved Location:</label>
              <select v-model="selectedDeliveryLocation">
                <option v-for="loc in deliveryLocations" :key="loc.id" :value="loc.id">
                  {{ loc.name }} - {{ loc.address }}
                </option>
                <option v-if="deliveryLocations.length === 0" disabled>No locations available</option>
              </select>
            </div>

            <!-- Add New Location Popup -->
            <div v-if="showAddLocation" class="add-location-popup">
              <input v-model="newLocation.name" placeholder="Location Name" />
              <input v-model="newLocation.address" placeholder="Address" />
              <div class="popup-buttons">
                <button @click="addNewLocation">Save</button>
                <button @click="showAddLocation = false">Cancel</button>
              </div>
            </div>

            <div class="shipping-method">
              <label>Shipping Method:</label>
              <select v-model="shippingMethod">
                <option value="standard">Standard (KES 0)</option>
                <option value="express">Express (KES 500)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Payment Pending -->
        <div v-if="paymentStatus === 'pending'" class="payment-pending">
          <p>Payment pending. Complete on your phone.</p>
          <button @click="verifyPayment">Verify Payment</button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { ref, onMounted, onUnmounted, onServerPrefetch } from 'vue';
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
      console.log('onMounted: Starting checkout initialization');
      loading.value = true;
      try {
        if (!store.currentUser) {
          console.log('onMounted: Fetching current user info');
          await store.fetchCurrentUserInfo();
        }
        if (!store.isAuthenticated || !store.currentUser) {
          if (isMounted.value) {
            error.value = 'Please log in to proceed with checkout.';
            console.log('onMounted: Redirecting to login');
            store.showAuthModal = true;
            router.push('/login');
          }
          return;
        }

        console.log('onMounted: Fetching order and locations');
        const [fetchedOrder, fetchedLocations] = await Promise.all([
          store.fetchOrder(orderId),
          store.fetchDeliveryLocations(),
        ]);
        if (cancelPendingRequests || !isMounted.value) {
          console.log('onMounted: Component unmounted, aborting updates');
          return;
        }
        order.value = fetchedOrder || { items: [], total_price: 0 };
        deliveryLocations.value = Array.isArray(fetchedLocations) ? fetchedLocations : [];
        selectedDeliveryLocation.value =
          order.value.delivery_location?.id ||
          (deliveryLocations.value.length > 0 ? deliveryLocations.value[0].id : null);
        shippingMethod.value = order.value.shipping_method || 'standard';
        console.log('onMounted: Data loaded successfully', { order: order.value, locations: deliveryLocations.value });
      } catch (err) {
        if (cancelPendingRequests || !isMounted.value) {
          console.log('onMounted: Component unmounted during error, skipping');
          return;
        }
        error.value = err.message || 'Failed to load order or delivery locations';
        console.error('onMounted: Error occurred:', err);
      } finally {
        if (isMounted.value) {
          loading.value = false;
          console.log('onMounted: Loading complete');
        }
      }
    });

    onUnmounted(() => {
      console.log('onUnmounted: Cleaning up Checkout component');
      isMounted.value = false;
      cancelPendingRequests = true;
    });

    const addNewLocation = async () => {
      console.log('addNewLocation: Attempting to add new location');
      try {
        const newLoc = await store.addDeliveryLocation(newLocation.value);
        if (cancelPendingRequests || !isMounted.value) {
          console.log('addNewLocation: Component unmounted, aborting');
          return;
        }
        deliveryLocations.value.push(newLoc);
        selectedDeliveryLocation.value = newLoc.id;
        showAddLocation.value = false;
        newLocation.value = { name: '', address: '' };
        console.log('addNewLocation: New location added', newLoc);
      } catch (err) {
        if (isMounted.value) {
          error.value = err.message || 'Failed to add delivery location';
          console.error('addNewLocation: Failed to add location:', err);
        }
      }
    };

    const updateAndPay = async () => {
      console.log('updateAndPay: Starting payment process');
      try {
        if (!selectedDeliveryLocation.value) {
          if (isMounted.value) {
            error.value = 'Please select or add a delivery location';
            console.log('updateAndPay: No delivery location selected');
          }
          return;
        }
        if (!phoneNumber.value || !/^(0\d{9}|254\d{9})$/.test(phoneNumber.value)) {
          if (isMounted.value) {
            error.value = 'Please enter a valid phone number (e.g., 0712345678 or 254712345678)';
            console.log('updateAndPay: Invalid or missing phone number', phoneNumber.value);
          }
          return;
        }
        if (!orderId) {
          if (isMounted.value) {
            error.value = 'Order ID is missing';
            console.log('updateAndPay: No orderId provided');
          }
          return;
        }
        console.log('updateAndPay: Sending request', { orderId, phoneNumber: phoneNumber.value });
        await store.updateOrderShipping(orderId, shippingMethod.value, selectedDeliveryLocation.value);
        await store.initiatePayment(orderId, phoneNumber.value);
        if (cancelPendingRequests || !isMounted.value) {
          console.log('updateAndPay: Component unmounted, aborting');
          return;
        }
        paymentStatus.value = 'pending';
        console.log('updateAndPay: Payment initiated, status set to pending');
      } catch (err) {
        if (isMounted.value) {
          error.value = err.response?.data?.error || 'Failed to update or initiate payment';
          console.error('updateAndPay: Error occurred:', {
            message: err.message,
            response: err.response?.data,
            status: err.response?.status
          });
        }
      }
    };

    const verifyPayment = async () => {
      console.log('verifyPayment: Verifying payment status');
      try {
        const paymentDetails = await store.verifyPayment(orderId);
        if (cancelPendingRequests || !isMounted.value) {
          console.log('verifyPayment: Component unmounted, aborting');
          return;
        }
        if (paymentDetails.payment_status === 'completed') {
          console.log('verifyPayment: Payment completed, redirecting');
          router.push({ path: '/checkout/confirmation', query: { orderId } });
        } else {
          alert('Payment not completed yet');
          console.log('verifyPayment: Payment not completed');
        }
      } catch (err) {
        if (isMounted.value) {
          error.value = err.message || 'Payment verification failed';
          console.error('verifyPayment: Payment verification failed:', err);
        }
      }
    };

    return {
      order,
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
    };
  },
};
</script>



<style scoped>
.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #2c3e50; /* Darker shade for contrast */
  font-size: 2rem; /* Larger for prominence */
  font-weight: 700; /* Bold */
  margin-bottom: 25px;
  text-align: center; /* Centered for balance */
  letter-spacing: 1px; /* Slight spacing for elegance */
}

h2 {
  color: #34495e; /* Slightly lighter than h1 but still dark */
  font-size: 1.5rem;
  font-weight: 600; /* Semi-bold */
  margin-bottom: 15px;
  position: relative; /* For underline effect */
  padding-bottom: 5px; /* Space for underline */
}

/* Underline effect for h2 */
h2::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 50px; /* Fixed width for underline */
  height: 2px;
  background-color: #007bff; /* Matches button color */
}

.checkout-content {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.payment-section {
  flex: 1;
  min-width: 300px;
  background: #f9f9f9;
  padding: 20px; /* Increased padding */
  border-radius: 8px; /* Softer corners */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* Subtle shadow */
}

.order-shipping-section {
  flex: 2;
  min-width: 300px;
}

.order-summary {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.order-summary div {
  margin: 10px 0;
  font-size: 1rem;
}

.shipping-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.location-section, .shipping-method {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555; /* Softer color for labels */
}

select, input {
  width: 100%;
  padding: 10px; /* Slightly larger padding */
  margin-bottom: 10px;
  border: 1px solid #ccc; /* Lighter border */
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 1rem;
}

button {
  background-color: #007bff;
  color: white;
  padding: 12px 15px; /* Larger padding */
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  width: 100%;
  font-size: 1rem;
  font-weight: 500;
}

button:hover {
  background-color: #0056b3;
}

.add-location-popup {
  background: #fff;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); /* Stronger shadow for popup */
  margin-top: 10px;
}

.popup-buttons {
  display: flex;
  gap: 10px;
}

.payment-pending {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Responsive Design */
@media (max-width: 650px) {
  .checkout-content {
    flex-direction: column;
  }

  .payment-section, .order-shipping-section {
    min-width: 100%;
  }

  h1 {
    font-size: 1.75rem; /* Slightly smaller */
  }

  h2 {
    font-size: 1.25rem; /* Adjusted for smaller screens */
  }

  h2::after {
    width: 40px; /* Shorter underline */
  }

  select, input {
    font-size: 0.95rem;
    padding: 8px;
  }

  button {
    padding: 10px;
    font-size: 0.95rem;
  }

  .popup-buttons {
    flex-direction: column;
    gap: 5px;
  }

  .order-summary, .shipping-section, .payment-section {
    padding: 15px;
  }
}

@media (max-width: 400px) {
  h1 {
    font-size: 1.5rem;
  }

  h2 {
    font-size: 1.1rem;
  }

  h2::after {
    width: 30px;
  }

  .order-summary div {
    font-size: 0.9rem;
  }

  select, input {
    font-size: 0.9rem;
    padding: 6px;
  }

  button {
    padding: 8px;
    font-size: 0.9rem;
  }
}
</style>