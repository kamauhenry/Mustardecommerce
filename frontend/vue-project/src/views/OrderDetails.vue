<template>
  <div class="order-details-page">
    <div v-if="isAdmin">
      <AdminLayout>
        <div class="order-details-content">
          <h2>Order #{{ orderDetails?.id }}</h2>
          <slot name="content"></slot>
        </div>
      </AdminLayout>
    </div>
    <div v-else>
      <MainLayout>
        <div class="order-details-content">
          <h2>Order #{{ orderDetails?.id }}</h2>
          <slot name="content"></slot>
        </div>
        </MainLayout>
    </div>

    <!-- Loading and Error States -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      Loading order details...
    </div>
    <div v-else-if="error" class="error-message">
      {{ error }}
      <br />
      <button @click="fetchOrderDetails" class="retry-button">Retry</button>
      <router-link v-if="isAdmin" to="/admin-page/orders" class="retry-link">Back to Orders</router-link>
      <router-link v-else to="/profile" class="retry-link">Back to Profile</router-link>
    </div>

    <!-- Order Details -->
    <div v-else class="order-details">
      <div class="summary-section">
        <h3>Order Summary</h3>
        <p><strong>Order Number:</strong> {{ orderDetails.order_number }}</p>
        <p><strong>Date:</strong> {{ new Date(orderDetails.created_at).toLocaleDateString() }}</p>
        <p><strong>Customer:</strong> {{ orderDetails.user?.email || 'N/A' }}</p>
        <p><strong>Payment Status:</strong> <span :class="getStatusClass(orderDetails.payment_status)">{{ orderDetails.payment_status }}</span></p>
        <p><strong>Delivery Status:</strong> <span :class="getStatusClass(orderDetails.delivery_status)">{{ orderDetails.delivery_status }}</span></p>
        <p><strong>Total:</strong> KES{{ orderDetails.total_price?.toFixed(2) }}</p>
        <p v-if="orderDetails.shipping_cost"><strong>Shipping Cost:</strong> KES{{ orderDetails.shipping_cost.toFixed(2) }}</p>
        <p v-if="orderDetails.shipping_method"><strong>Shipping Method:</strong> {{ orderDetails.shipping_method.name }}</p>
        <p v-if="orderDetails.delivery_location"><strong>Delivery Location:</strong> {{ orderDetails.delivery_location.address }}</p>
      </div>

      <div class="items-section">
        <h3>Items</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Image</th>
              <th>Product</th>
              <th>Attributes</th>
              <th>Quantity</th>
              <th>Price (KES)</th>
              <th>Total (KES)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in orderDetails.items" :key="item.id">
              <td>
                <img
                  v-if="item.product?.images.length > 0 ? product.images[0].image : ''"
                  :src="item.product.images.length > 0 ? product.images[0].image : ''"
                  alt="Product image"
                  class="product-image"
             
                />
                <span v-else>No image</span>
              </td>
              <td>{{ item.product_name }}</td>
              <td>{{ formatAttributes(item.attributes) }}</td>
              <td>{{ item.quantity }}</td>
              <td>{{ parseFloat(item.price).toFixed(2) }}</td>
              <td>{{ parseFloat(item.line_total).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/modules/auth';
import { useOrdersStore } from '@/stores/modules/orders';
import { useRouter, useRoute } from 'vue-router';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import MainLayout from '@/components/navigation/MainLayout.vue';

export default {
  name: 'OrderDetails',
  components: {
    AdminLayout,
    MainLayout,
  },
  setup() {
    const authStore = useAuthStore();
    const ordersStore = useOrdersStore();
    const router = useRouter();
    const route = useRoute();
    const orderId = computed(() => parseInt(route.params.orderId));
    const loading = computed(() => ordersStore.isLoadingOrder);
    const error = ref(null);
    const orderDetails = computed(() => ordersStore.currentOrder);
    const isAdmin = computed(() => authStore.isAdmin);

    const fetchOrderDetails = async () => {
      try {
        error.value = null;
        await ordersStore.fetchOrder(orderId.value);
      } catch (err) {
        console.error('Order details fetch error:', err);
        error.value = 'Failed to load order details';
      }
    };

    const getStatusClass = (status) => {
      switch (status?.toLowerCase()) {
        case 'paid':
        case 'delivered':
          return 'status-completed';
        case 'pending':
        case 'processing':
          return 'status-pending';
        case 'shipped':
          return 'status-shipped';
        default:
          return '';
      }
    };

    const formatAttributes = (attributes) => {
      if (!attributes || !Array.isArray(attributes) || attributes.length === 0) {
        return 'No attributes';
      }
      return attributes
        .map(attr => `${attr.name}: ${attr.values.map(v => v.value).join(', ')}`)
        .join('; ');
    };

    onMounted(fetchOrderDetails);

    return {
      orderId,
      loading,
      error,
      orderDetails,
      isAdmin,
      fetchOrderDetails,
      getStatusClass,
      formatAttributes,
    };
  },
};
</script>

<style scoped>
.order-details-page {
  max-width: 1200px;
  margin: 0 auto;
}

.order-details-content {
  padding: 1.5rem;
}

h2 {
  font-size: 1.75rem;
  color: #4f46e5;
  margin-bottom: 1.5rem;
  font-weight: 700;
}

h3 {
  font-size: 1.1rem;
  color: #374151;
  margin-bottom: 1rem;
  font-weight: 600;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: #6b7280;
  margin: 2rem 0;
}

.spinner {
  width: 1.75rem;
  height: 1.75rem;
  border: 3px solid #6366f1;
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.75rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #ef4444;
  text-align: center;
  margin: 1.5rem 0;
  font-size: 1rem;
  font-weight: 500;
  padding: 1rem;
  border: 1px solid #fecaca;
  border-radius: 12px;
  background-color: #fee2e2;
}

.retry-button {
  margin-top: 0.75rem;
  padding: 0.5rem 1.25rem;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background-color: #4f46e5;
}

.retry-link {
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.75rem;
}

.retry-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

.order-details {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}

.summary-section {
  margin-bottom: 2rem;
}

.summary-section p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.summary-section p strong {
  color: #374151;
  font-weight: 600;
  display: inline-block;
  width: 150px;
}

.items-section {
  margin-bottom: 2rem;
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.data-table th {
  background-color: #f9fafb;
  color: #4b5563;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-table th:first-child {
  border-top-left-radius: 8px;
}

.data-table th:last-child {
  border-top-right-radius: 8px;
}

.data-table tr:last-child td:first-child {
  border-bottom-left-radius: 8px;
}

.data-table tr:last-child td:last-child {
  border-bottom-right-radius: 8px;
}

.data-table tr:hover {
  background-color: #f9fafb;
}

.product-image {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
}

.status-completed {
  color: #10b981;
  font-weight: 600;
  background-color: #ecfdf5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-block;
}

.status-pending {
  color: #f59e0b;
  font-weight: 600;
  background-color: #fffbeb;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-block;
}

.status-shipped {
  color: #007bff;
  font-weight: 600;
  background-color: #dbeafe;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-block;
}

@media (max-width: 768px) {
  .order-details-content {
    padding: 1rem;
  }

  .data-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }

  .data-table th,
  .data-table td {
    min-width: 100px;
  }

  .data-table th:first-child,
  .data-table td:first-child {
    min-width: 80px;
  }

  .summary-section p strong {
    width: 120px;
  }

  .product-image {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 320px) {
  .order-details-content {
    padding: 0.5rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  h3 {
    font-size: 1rem;
  }

  .summary-section p {
    font-size: 0.85rem;
  }

  .summary-section p strong {
    width: 100px;
  }

  .product-image {
    width: 30px;
    height: 30px;
  }
}
</style>