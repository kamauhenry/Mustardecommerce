<template>
  <div>
    <h1>Your Orders</h1>
    <div v-if="!store.isAuthenticated">Please login to view your orders</div>
    <div v-else>
      <div v-if="store.loading.orders">Loading...</div>
      <div v-else-if="store.error.orders">{{ store.error.orders }}</div>
      <div v-else-if="store.orders.length">
        <div v-for="order in store.orders" :key="order.id">
          <p>Order #{{ order.id }} - {{ order.quantity }} x {{ order.product_name }}</p>
          <button v-if="order.delivery_status === 'processing'" @click="cancelOrder(order.id)">Cancel</button>
        </div>
      </div>
      <div v-else>No orders</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import api from '@/services/api';

// Move the store initialization inside the setup
const store = useEcommerceStore();

onMounted(() => {
  if (store.isAuthenticated && !store.orders.length) {
    store.fetchOrdersData();
  }
});

const cancelOrder = async (orderId) => {
  try {
    const apiInstance = api.createApiInstance(store);
    await api.cancelOrder(apiInstance, orderId);
    store.fetchOrdersData();
  } catch (error) {
    console.error('Cancel order failed:', error);
  }
};
</script>
