<template>
  <MainLayout>
    <div class="orders-container">
      <h1 class="page-title">Your Orders</h1>
      
      <div v-if="!store.isAuthenticated" class="auth-message">
        Please login to view your orders
      </div>
      
      <div v-else>
        <div v-if="store.loading.orders" class="loading-state">
          <div class="spinner"></div>
          <p>Loading orders...</p>
        </div>
        
        <div v-else-if="store.error.orders" class="error-state">
          {{ store.error.orders }}
        </div>
        
        <div v-else-if="store.orders.length" class="orders-grid">
          <div 
            v-for="order in store.orders" 
            :key="order.id" 
            class="order-card"
          >
            <div class="order-header">
              <span class="order-number">Order #{{ order.id }}</span>
              <span class="order-date">
                {{ new Date(order.created_at).toLocaleDateString() }}
              </span>
            </div>
            
            <div class="order-items">
              <div 
                v-for="item in order.items" 
                :key="item.id" 
                class="order-item"
              >
                <img 
                  :src="item.product.image" 
                  :alt="item.product.name" 
                  class="product-image"
                />
                <div class="product-details">
                  <h3>{{ item.product.name }}</h3>
                  <p>
                    Quantity: {{ item.quantity }} 
                    | Price: KES {{ (item.price * item.quantity).toFixed(2) }}
                  </p>
                </div>
              </div>
            </div>
            
            <div class="order-status">
              <div class="status-badge payment-status">
                Payment: {{ order.payment_status }}
              </div>
              <div class="status-badge delivery-status">
                Delivery: {{ order.delivery_status }}
              </div>
            </div>
            

          </div>
        </div>
        
        <div v-else class="no-orders">
          You have no orders yet.
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useEcommerceStore } from '@/stores/ecommerce'
import MainLayout from '@/components/navigation/MainLayout.vue'
import api from '@/services/api'

const store = useEcommerceStore()

onMounted(() => {
  if (store.isAuthenticated) {
    store.fetchOrdersData()
  }
})


</script>

<style scoped>
.orders-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
}

.orders-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.order-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  background-color: white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 10px;
}

.order-items {
  margin-bottom: 15px;
}

.order-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.product-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  margin-right: 15px;
  border-radius: 4px;
}

.order-status {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.status-badge {
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 0.8em;
}

.payment-status {
  background-color: #e7f5ff;
  color: #1971c2;
}

.delivery-status {
  background-color: #d3f9d8;
  color: #2b8a3e;
}


</style>