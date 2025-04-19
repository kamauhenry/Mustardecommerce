<template>
    <MainLayout>
      <div class="order-details-container">
        <div class="breadcrumb">
          <a href="/">Home</a> > <a href="/account">Account Home</a> > <a href="/orders">Orders</a> > <span>Order #{{ orderId }}</span>
        </div>
  
        <h1 class="page-title">Order Details</h1>
  
        <div v-if="loading" class="order-details">
          <div class="skeleton-section">
            <div class="skeleton-text skeleton-title"></div>
            <div v-for="n in 2" :key="n" class="skeleton-item">
              <div class="skeleton-text skeleton-item-name"></div>
              <div class="skeleton-text skeleton-item-price"></div>
            </div>
          </div>
          <div class="skeleton-section">
            <div class="skeleton-text skeleton-title"></div>
            <div class="skeleton-text skeleton-info"></div>
          </div>
        </div>
  
        <div v-else-if="error" class="error-message">
          {{ error }}
        </div>
  
        <div v-else class="order-details">
          <div class="order-section">
            <h2>Order #{{ order.id }}</h2>
            <p><strong>Placed on:</strong> {{ formatDate(order.created_at) }}</p>
            <p><strong>Payment Status:</strong> {{ order.payment_status }}</p>
            <p><strong>Delivery Status:</strong> {{ order.delivery_status }}</p>
            <p><strong>Total:</strong> KES {{ order.total_price }}</p>
          </div>
  
          <div class="order-section">
            <h2>Items</h2>
            <div v-for="item in order.items" :key="item.id" class="order-item">
              <div class="item-info">
                <p><strong>{{ item.product_name }}</strong></p>
                <p>Quantity: {{ item.quantity }}</p>
                <p>Price: KES {{ item.price }}</p>
                <p>Line Total: KES {{ item.line_total }}</p>
              </div>
            </div>
          </div>
  
          <div class="order-section">
            <h2>Shipping Information</h2>
            <p v-if="order.delivery_location">
              <strong>Address:</strong> {{ order.delivery_location.address }}<br />
              <strong>Name:</strong> {{ order.delivery_location.name }}
            </p>
            <p v-else>No delivery location specified.</p>
            <p><strong>Shipping Method:</strong> {{ order.shipping_method }}</p>
          </div>
        </div>
      </div>
    </MainLayout>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue';
  import { useRoute } from 'vue-router';
  import { useEcommerceStore } from '@/stores/ecommerce';
  import MainLayout from '@/components/navigation/MainLayout.vue';
  
  const route = useRoute();
  const store = useEcommerceStore();
  const orderId = route.params.orderId;
  const order = ref(null);
  const loading = ref(true);
  const error = ref(null);
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };
  
  onMounted(async () => {
    if (!store.isAuthenticated) {
      router.push('/login');
      return;
    }
    try {
      const response = await store.fetchOrder(orderId);
      order.value = response;
    } catch (err) {
      error.value = 'Failed to load order details. Please try again.';
      console.error('Error fetching order:', err);
    } finally {
      loading.value = false;
    }
  });
  </script>
  
  <style scoped>
  .order-details-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
  }
  
  .breadcrumb {
    margin-bottom: 20px;
    font-size: 14px;
  }
  
  .breadcrumb a {
    text-decoration: none;
  }
  
  .breadcrumb a:hover {
    text-decoration: underline;
  }
  
  .page-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
  }
  
  .order-details {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 20px;
  }
  
  .order-section {
    margin-bottom: 20px;
  }
  
  .order-section h2 {
    font-size: 18px;
    margin-bottom: 10px;
  }
  
  .order-item {
    border-bottom: 1px solid #eee;
    padding: 10px 0;
  }
  
  .item-info p {
    margin: 5px 0;
  }
  
  .error-message {
    padding: 20px;
    text-align: center;
    color: #f44336;
    background: #fff;
    border-radius: 8px;
  }
  
  .skeleton-section {
    margin-bottom: 20px;
  }
  
  .skeleton {
    background: #f6f7f8;
    position: relative;
    overflow: hidden;
  }
  
  .skeleton::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: shimmer 1.5s infinite;
  }
  
  .skeleton-text {
    background: #e0e0e0;
    height: 16px;
    border-radius: 4px;
    margin-bottom: 8px;
  }
  
  .skeleton-title {
    width: 200px;
    height: 20px;
  }
  
  .skeleton-item-name {
    width: 150px;
  }
  
  .skeleton-item-price {
    width: 100px;
  }
  
  .skeleton-info {
    width: 250px;
  }
  
  @keyframes shimmer {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(100%);
    }
  }
  
  @media (max-width: 768px) {
    .order-details-container {
      padding: 10px;
    }
  
    .order-section h2 {
      font-size: 16px;
    }
  }
  </style>