
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
            <p>Order Number: {{ order.order_number }}</p>
            <div class="order-items">
              <h3>Items ({{ order.items.length }})</h3>
              <div v-for="item in order.items" :key="item.id" class="order-item">
                <p>{{ item.product_name }}</p>
                <p v-for="(value, attrName) in item.attributes" :key="attrName">
                  {{ attrName }}: {{ value }}
                </p>
                <p v-if="item.is_pick_and_pay && item.product.inventory" class="availability">
                  Available: {{ item.product.inventory.quantity }} units
                </p>
                <p v-else-if="item.product.moq_status === 'active'" class="moq-info">
                  MOQ: {{ item.product.moq_per_person || 'N/A' }} items
                  <span v-if="item.quantity < item.product.moq_per_person" class="moq-warning">
                    (Below MOQ)
                  </span>
                </p>
                <p>Qty: {{ item.quantity }}</p>
                <p>KES {{ formatPrice(item.is_pick_and_pay ? item.price : item.quantity < item.product.moq_per_person ? item.product.below_moq_price || item.price : item.price) }} each</p>
              </div>
            </div>
            <p>Subtotal: KES {{ formatPrice(orderSubtotal) }}</p>
            <p>Shipping Method: {{ isPayAndPickOrder ? 'Store Pickup (Free)' : order.shipping_method?.name || 'Not specified' }}</p>
            <p>Shipping Cost: KES {{ formatPrice(order.shipping_cost) }}</p>
            <p>Total Amount: KES {{ formatPrice(orderTotal) }}</p>
            <p>Delivery Status: {{ order.delivery_status }}</p>
            <p v-if="order.delivery_location && !isPayAndPickOrder">
              Delivery Location: {{ order.delivery_location.name }} - {{ order.delivery_location.address }}
            </p>
            <p v-else-if="isPayAndPickOrder">Delivery Location: Store Pickup</p>
            <p v-else>Delivery Location: None</p>
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

const route = useRoute();
const store = useEcommerceStore();
const order = ref(null);
const loading = ref(true);
const error = ref(null);

// Format price to 2 decimal places
const formatPrice = (price) => (Math.round(price * 100) / 100).toFixed(2);

// Compute order properties
const isPayAndPickOrder = computed(() => {
  return order.value?.items?.length > 0 && order.value.items.every(item => item.is_pick_and_pay);
});
const orderSubtotal = computed(() => {
  return order.value ? order.value.items.reduce((sum, item) => {
    const price = item.is_pick_and_pay
      ? item.price
      : item.quantity < item.product.moq_per_person ? item.product.below_moq_price || item.price : item.price;
    return sum + (price * item.quantity);
  }, 0) : 0;
});
const orderTotal = computed(() => {
  const shippingCost = isPayAndPickOrder.value ? 0 : parseFloat(order.value.shipping_cost || 0);
  return (orderSubtotal.value + shippingCost).toFixed(2);
});

onMounted(async () => {
  const orderId = route.query.orderId;
  if (!orderId) {
    error.value = 'No order specified';
    loading.value = false;
    return;
  }

  try {
    if (!store.apiInstance) store.initializeApiInstance();
    const response = await store.apiInstance.get(`/orders/${orderId.replace(/^MI/, '')}/`);
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
.confirmation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: #f4f4f4;
  padding: 1rem;
}

.confirmation-card {
  background-color: white;
  border-radius: 0.625rem;
  box-shadow: 0 0.25rem 0.375rem rgba(0, 0, 0, 0.1);
  padding: 2rem;
  text-align: center;
  width: 100%;
  max-width: 31.25rem;
}

.success-icon {
  font-size: 5rem;
  color: #4CAF50;
  margin-bottom: 1.25rem;
}

h1 {
  font-size: 1.75rem;
  margin: 0.5rem 0;
}

.order-details {
  background-color: #f9f9f9;
  padding: 1.25rem;
  border-radius: 0.5rem;
  margin: 1.25rem 0;
}

.order-details h2 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.order-details p {
  font-size: 0.875rem;
  margin: 0.375rem 0;
  line-height: 1.5;
}

.order-items {
  margin-bottom: 1rem;
}

.order-item {
  border-bottom: 1px solid #e2e8f0;
  padding: 0.5rem 0;
}

.moq-warning, .availability {
  color: #d9534f;
  font-size: 0.75rem;
}

.actions {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.view-orders-btn,
.continue-shopping-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  text-decoration: none;
  border-radius: 0.3125rem;
  transition: background-color 0.3s;
  font-size: 0.875rem;
  min-height: 2.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-orders-btn {
  background-color: #4CAF50;
  color: white;
}

.continue-shopping-btn {
  background-color: #2196F3;
  color: white;
}

.loading {
  text-align: center;
  padding: 1.25rem;
  font-size: 1rem;
  color: #666;
}

.error {
  text-align: center;
  padding: 1.25rem;
  font-size: 1rem;
  color: #d9534f;
}

@media (max-width: 765px) {
  .confirmation-card {
    padding: 1.5rem;
    max-width: 90%;
  }

  h1 {
    font-size: 1.5rem;
  }

  .success-icon {
    font-size: 4rem;
  }

  .order-details h2 {
    font-size: 1.125rem;
  }

  .order-details p {
    font-size: 0.8125rem;
  }

  .actions {
    flex-direction: column;
    gap: 0.5rem;
  }

  .view-orders-btn,
  .continue-shopping-btn {
    font-size: 0.8125rem;
  }
}

@media (max-width: 650px) {
  .confirmation-container {
    padding: 0.5rem;
  }

  .confirmation-card {
    padding: 1rem;
    max-width: 95%;
  }

  h1 {
    font-size: 1.25rem;
  }

  .success-icon {
    font-size: 3rem;
    margin-bottom: 0.75rem;
  }

  .order-details {
    padding: 0.75rem;
    margin: 0.75rem 0;
  }

  .order-details h2 {
    font-size: 1rem;
  }

  .order-details p {
    font-size: 0.75rem;
  }

  .loading,
  .error {
    font-size: 0.875rem;
    padding: 0.75rem;
  }
}
</style>
