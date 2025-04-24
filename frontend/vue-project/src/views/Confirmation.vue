<template>
  <MainLayout>
    <div class="confirmation-container">
      <div class="confirmation-card">
        <div v-if="loading" class="loading">Loading order details...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else-if="order">
          <div class="success-icon">✓</div>
          <h1>Order Confirmed!</h1>
          <p>Thank you for your purchase.</p>
          <div class="order-details">
            <h2>Order Summary</h2>
            <p>Order Number: #{{ order.id }}</p>
            <p>Subtotal: KES {{ formatPrice(orderSubtotal) }}</p>
            <p>Shipping Method: {{ order.shipping_method?.name || 'Not specified' }}</p>
            <p>Shipping Cost: KES {{ formatPrice(order.shipping_cost) }}</p>
            <p>Total Amount: KES {{ formatPrice(order.total_price) }}</p>
            <p>Delivery Status: {{ order.delivery_status }}</p>
          </div>
          <div class="actions">
            <router-link to="/orders" class="view-orders-btn">View My Orders</router-link>
            <router-link to="/" class="continue-shopping-btn">Continue Shopping</router-link>
          </div>
        </div>
        <div v-else>
          <p>Order not found.</p>
          <router-link to="/" class="continue-shopping-btn">Continue Shopping</router-link>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';
import api from '@/services/api';

const route = useRoute();
const store = useEcommerceStore();
const order = ref(null);
const loading = ref(true);
const error = ref(null);

// Format price to 2 decimal places
const formatPrice = (price) => (Math.round(price * 100) / 100).toFixed(2);

// Compute subtotal
const orderSubtotal = computed(() =>
  order.value ? order.value.items.reduce((sum, item) => sum + item.quantity * item.price, 0) : 0
);

onMounted(async () => {
  const orderId = route.query.orderId;
  if (!orderId) {
    error.value = 'No order specified';
    loading.value = false;
    return;
  }

  try {
    const apiInstance = api.createApiInstance(store);
    const response = await apiInstance.get(`/api/order/${orderId}/`);
    order.value = response.data;
  } catch (err) {
    if (err.response) {
      if (err.response.status === 404) {
        error.value = 'Order not found.';
      } else if (err.response.status === 401) {
        error.value = 'Please log in to view your order.';
      } else {
        error.value = 'Failed to load order details. Please try again later.';
      }
    } else {
      error.value = 'An unexpected error occurred.';
    }
    console.error('Failed to fetch order details:', err);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.order-details p {
  font-size: 1rem;
  margin: 0.5rem 0;
}
.confirmation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: #f4f4f4;
}

.confirmation-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 40px;
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.success-icon {
  font-size: 80px;
  color: #4CAF50;
  margin-bottom: 20px;
}

.order-details {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
}

.actions {
  display: flex;
  justify-content: space-between;
}

.view-orders-btn,
.continue-shopping-btn {
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.view-orders-btn {
  background-color: #4CAF50;
  color: white;
}

.continue-shopping-btn {
  background-color: #2196F3;
  color: white;
}

/* Added styles for loading and error states */
.loading {
  text-align: center;
  padding: 20px;
  font-size: 18px;
  color: #666;
}

.error {
  text-align: center;
  padding: 20px;
  font-size: 18px;
  color: #d9534f;
}
</style>