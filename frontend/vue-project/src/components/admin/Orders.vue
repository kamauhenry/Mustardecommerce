<template>
  <AdminLayout>
    <div class="orders">
      <h2>Manage Orders</h2>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        Loading orders...
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="fetchOrders" class="retry-button">Retry</button>
      </div>

      <!-- Orders Table -->
      <div v-else class="orders-content">
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Total (KES)</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id">
              <td>#{{ order.id }}</td>
              <td>{{ order.customer_name || order.user?.username || 'N/A' }}</td>
              <td>{{ order.total != null ? order.total.toFixed(2) : 'N/A' }}</td>
              <td>
                <span :class="getStatusClass(order.status)">{{ order.status || 'N/A' }}</span>
              </td>
              <td>{{ order.created_at ? new Date(order.created_at).toLocaleDateString() : 'N/A' }}</td>
              <td>
                <button @click="deleteOrder(order.id)" :disabled="loading">Delete</button>
              </td>
            </tr>
            <tr v-if="!orders.length">
              <td colspan="6" class="no-data">No orders available.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import api from '@/services/api';

export default {
  components: { AdminLayout },
  setup() {
    const store = useEcommerceStore();
    const orders = ref([]);
    const loading = ref(false);
    const error = ref(null);

    const fetchOrders = async () => {
      try {
        loading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const response = await api.fetchAllOrders(apiInstance);
        orders.value = response || [];
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to load orders. Please try again.';
        console.error('Failed to fetch orders:', err);
      } finally {
        loading.value = false;
      }
    };

    const deleteOrder = async (id) => {
      if (confirm('Are you sure you want to delete this order?')) {
        try {
          loading.value = true;
          error.value = null;
          const apiInstance = api.createApiInstance(store);
          await api.deleteOrder(apiInstance, id);
          alert('Order deleted successfully');
          await fetchOrders();
        } catch (err) {
          error.value = err.response?.data?.error || 'Failed to delete order. Please try again.';
          console.error('Failed to delete order:', err);
        } finally {
          loading.value = false;
        }
      }
    };

    const getStatusClass = (status) => {
      switch (status?.toLowerCase()) {
        case 'completed':
          return 'status-completed';
        case 'pending':
          return 'status-pending';
        case 'cancelled':
          return 'status-cancelled';
        default:
          return '';
      }
    };

    onMounted(() => {
      fetchOrders();
    });

    return {
      orders,
      loading,
      error,
      fetchOrders,
      deleteOrder,
      getStatusClass,
    };
  },
};
</script>

<style scoped>
.orders {
  padding: 0;
  background-color: transparent;
  border-radius: 0;
  box-shadow: none;
}

h2 {
  font-size: 1.75rem;
  color: #4f46e5;
  margin-bottom: 24px;
  border-bottom: none;
  padding-bottom: 0;
  font-weight: 700;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #6f42c1;
  color: white;
  font-weight: 600;
}

tr:hover {
  background-color: #f9f9f9;
}

td button {
  padding: 6px 12px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

td button:hover:not(:disabled) {
  background-color: #c0392b;
}

td button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 20px;
}

.status-completed {
  color: #28a745;
  font-weight: 500;
}

.status-pending {
  color: #f4c430;
  font-weight: 500;
}

.status-cancelled {
  color: #e74c3c;
  font-weight: 500;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #666;
  margin: 20px 0;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #6f42c1;
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-message {
  color: #e74c3c;
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.2rem;
  font-weight: 500;
  padding: 15px;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  background-color: #ffe6e6;
}

.retry-button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.retry-button:hover {
  background-color: #5a32a3;
}

@media (max-width: 768px) {
  th,
  td {
    padding: 8px 10px;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  th,
  td {
    font-size: 0.8rem;
  }
}
</style>
