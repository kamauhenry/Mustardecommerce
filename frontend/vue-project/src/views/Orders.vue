<!-- views/MyOrders.vue -->
<template>
  <MainLayout>
    <div class="my-orders-page">
      <h1>My Orders</h1>

      <div class="orders-section">
        <h2>Active Orders</h2>
        <div v-if="orders.length" class="orders-list">
          <div v-for="order in orders" :key="order.id" class="order-card">
            <h3>Order #{{ order.id }}</h3>
            <p><strong>Product:</strong> {{ order.product.name }}</p>
            <p><strong>Variant:</strong> {{ order.variant.color }} / {{ order.variant.size }}</p>
            <p><strong>Quantity:</strong> {{ order.quantity }}</p>
            <p><strong>Price:</strong> KES {{ order.price }}</p>
            <p><strong>Shipping Method:</strong> {{ order.shipping_method }}</p>
            <p><strong>Shipping Address:</strong> {{ order.shipping_address }}</p>
            <p><strong>Payment Status:</strong> {{ order.payment_status }}</p>
            <p><strong>Delivery Status:</strong> {{ order.delivery_status }}</p>
            <p><strong>Order Date:</strong> {{ new Date(order.created_at).toLocaleString() }}</p>
            <button
              v-if="order.delivery_status === 'processing' || order.delivery_status === 'shipped'"
              @click="cancelOrder(order.id)"
              class="cancel-btn"
            >
              Cancel Order
            </button>
          </div>
        </div>
        <p v-else>No active orders.</p>
      </div>

      <div class="orders-section">
        <h2>Completed Orders</h2>
        <div v-if="completedOrders.length" class="orders-list">
          <div v-for="order in completedOrders" :key="order.id" class="order-card">
            <h3>Order #{{ order.order_number }}</h3>
            <p><strong>Product:</strong> {{ order.product?.name || 'N/A' }}</p>
            <p><strong>Variant:</strong> {{ order.variant_details.color }} / {{ order.variant_details.size }}</p>
            <p><strong>Quantity:</strong> {{ order.quantity }}</p>
            <p><strong>Price Paid:</strong> KES {{ order.price_paid }}</p>
            <p><strong>Shipping Method:</strong> {{ order.shipping_method }}</p>
            <p><strong>Payment Method:</strong> {{ order.payment_method }}</p>
            <p><strong>Order Date:</strong> {{ new Date(order.order_date).toLocaleString() }}</p>
            <p><strong>Completion Date:</strong> {{ new Date(order.completion_date).toLocaleString() }}</p>
          </div>
        </div>
        <p v-else>No completed orders.</p>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { useOrderStore } from '@/stores/orders';
import MainLayout from "@/components/navigation/MainLayout.vue";

export default {
  components: { MainLayout },
  setup() {
    const orderStore = useOrderStore();
    return { orderStore };
  },
  computed: {
    orders() {
      return this.orderStore.orders;
    },
    completedOrders() {
      return this.orderStore.completedOrders;
    },
  },
  async created() {
    await this.orderStore.fetchOrders();
    await this.orderStore.fetchCompletedOrders();
  },
  methods: {
    async cancelOrder(orderId) {
      try {
        await this.orderStore.cancelOrder(orderId);
        alert('Order cancelled successfully!');
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to cancel order. Please try again.');
      }
    },
  },
};
</script>

<style scoped>
.my-orders-page {
  padding: 20px;
  background: #1a1a1a;
  color: #fff;
  font-family: Arial, sans-serif;
}

.my-orders-page h1 {
  color: #ff6200;
  margin-bottom: 20px;
}

.orders-section {
  margin-bottom: 40px;
}

.orders-section h2 {
  color: #ffcc00;
  margin-bottom: 15px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.order-card {
  background: #333;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #444;
}

.order-card h3 {
  color: #fff;
  margin-bottom: 10px;
}

.order-card p {
  color: #ccc;
  margin: 5px 0;
}

.cancel-btn {
  margin-top: 10px;
  padding: 8px 15px;
  background: #ff4444;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #cc3333;
}
</style>
