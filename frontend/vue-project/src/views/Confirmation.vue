<template>
  <MainLayout>
    <div class="confirmation-container">
      <div class="confirmation-card">
        <!-- Show loading state while fetching order -->
        <div v-if="loading" class="loading">Loading order details...</div>
        <!-- Show error message if something goes wrong -->
        <div v-else-if="error" class="error">{{ error }}</div>
        <!-- Show order details if successfully fetched -->
        <div v-else-if="order">
          <div class="success-icon">✓</div>
          <h1>Order Confirmed!</h1>
          <p>Thank you for your purchase.</p>
          <div class="order-details">
            <h2>Order Summary</h2>
            <p>Order Number: #{{ order.id }}</p>
            <p>Total Amount: KES {{ order.total_price.toFixed(2) }}</p>
            <p>Shipping Method: {{ order.shipping_method }}</p>
            <p>Delivery Status: {{ order.delivery_status }}</p>
          </div>
          <div class="actions">
            <router-link to="/orders" class="view-orders-btn">View My Orders</router-link>
            <router-link to="/" class="continue-shopping-btn">Continue Shopping</router-link>
          </div>
        </div>
        <!-- Show message if order is not found -->
        <div v-else>
          <p>Order not found.</p>
          <router-link to="/" class="continue-shopping-btn">Continue Shopping</router-link>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useEcommerceStore } from '@/stores/ecommerce'
import MainLayout from '@/components/navigation/MainLayout.vue'
import api from '@/services/api'

// Initialize reactive variables
const route = useRoute()
const store = useEcommerceStore()
const order = ref(null)
const loading = ref(true) // Track loading state
const error = ref(null)  // Store error messages

// Fetch order details when component mounts
onMounted(async () => {
  const orderId = route.query.orderId

  // Check if orderId is present
  if (!orderId) {
    error.value = 'No order specified'
    loading.value = false
    return
  }

  try {
    // Create API instance with store (assumes it includes auth token)
    const apiInstance = api.createApiInstance(store)
    const response = await apiInstance.get(`/api/order/${orderId}/`)
    order.value = response.data
  } catch (err) {
    // Handle specific error cases
    if (err.response) {
      if (err.response.status === 404) {
        error.value = 'Order not found.'
      } else if (err.response.status === 401) {
        error.value = 'Please log in to view your order.'
      } else {
        error.value = 'Failed to load order details. Please try again later.'
      }
    } else {
      error.value = 'An unexpected error occurred.'
    }
    console.error('Failed to fetch order details:', err)
  } finally {
    // Ensure loading state is cleared
    loading.value = false
  }
})
</script>

<style scoped>
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