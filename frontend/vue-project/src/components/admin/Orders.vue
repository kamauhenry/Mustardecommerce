<template>
  <AdminLayout>
    <div class="orders">
      <h2>Manage Orders</h2>

      <!-- Navigation Buttons -->
      <div class="status-navigation">
        <button
          @click="scrollToStatus('processing')"
          class="status-button processing"
        >
          Processing
        </button>
        <button
          @click="scrollToStatus('shipped')"
          class="status-button shipped"
        >
          Shipped
        </button>
        <button
          @click="scrollToStatus('delivered')"
          class="status-button delivered"
        >
          Delivered
        </button>
        <button
          @click="scrollToMOQ"
          class="status-button moq"
        >
          MOQ Fulfilled
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading && Object.values(orders).every(arr => !arr.length)" class="loading">
        <div class="spinner"></div>
        Loading orders...
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="fetchAllOrders" class="retry-button">Retry</button>
      </div>

      <!-- Orders Table -->
      <div v-else class="orders-content">
        <!-- Bulk Actions -->
        <div class="bulk-actions" v-if="selectedOrders.length > 0">
          <button @click="bulkUpdateStatus('processing')" :disabled="loading">Mark as Processing</button>
          <button @click="bulkUpdateStatus('shipped')" :disabled="loading">Mark as Shipped</button>
          <button @click="bulkUpdateStatus('delivered')" :disabled="loading">Mark as Delivered</button>
        </div>

        <!-- Orders by Delivery Status -->
        <div v-for="status in ['processing', 'shipped', 'delivered']" :key="status" class="status-section" :id="`status-${status}`">
          <h3>{{ status.charAt(0).toUpperCase() + status.slice(1) }} Orders</h3>
          <table>
            <thead>
              <tr>
                <th><input type="checkbox" @change="selectAllOrders(status, $event)" /></th>
                <th>Order ID</th>
                <th>Customer Email</th>
                <th>Total (KES)</th>
                <th>Payment Status</th>
                <th>Delivery Status</th>
                <th>Delivery Location</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders[status]" :key="order.id">
                <td><input type="checkbox" :value="order.id" v-model="selectedOrders" /></td>
                <td>#{{ order.id }}</td>
                <td>{{ order.user?.email || 'N/A' }}</td>
                <td>{{ order.total_price != null ? order.total_price : 'N/A' }}</td>
                <td>
                  <span :class="getStatusClass(order.payment_status)">{{ order.payment_status || 'N/A' }}</span>
                </td>
                <td>
                  <span :class="getStatusClass(order.delivery_status)">{{ order.delivery_status || 'N/A' }}</span>
                </td>
                <td>{{ order.delivery_location?.address || 'N/A' }}</td>
                <td>{{ order.created_at ? new Date(order.created_at).toLocaleDateString() : 'N/A' }}</td>
                <td>
                  <button @click="viewOrderDetails(order.id)">View Details</button>
                  <select @change="updateSingleOrderStatus(order.id, $event)" :disabled="loading">
                    <option value="" disabled selected>Change Status</option>
                    <option value="processing">Processing</option>
                    <option value="shipped">Shipped</option>
                    <option value="delivered">Delivered</option>
                  </select>
                </td>
              </tr>
              <tr v-if="!orders[status].length">
                <td colspan="9" class="no-data">No {{ status }} orders available.</td>
              </tr>
            </tbody>
          </table>
          <!-- Per-Status Pagination -->
          <div class="pagination" v-if="totalPages[status] > 1">
            <button
              @click="changePage(status, currentPage[status] - 1)"
              :disabled="currentPage[status] === 1 || loading"
            >
              Previous
            </button>
            <span>Page {{ currentPage[status] }} of {{ totalPages[status] }}</span>
            <button
              @click="changePage(status, currentPage[status] + 1)"
              :disabled="currentPage[status] === totalPages[status] || loading"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <!-- MOQ Fulfilled Products -->
           <!-- MOQ Fulfilled Products -->
           <div class="moq-section" id="moq-section">
        <h3>MOQ Fulfilled Products</h3>
        <table>
          <thead>
            <tr>
              <th>Product Name</th>
              <th>MOQ Target</th>
              <th>Current MOQ</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in moqFulfilledProducts" :key="product.id">
              <td>{{ product.name }}</td>
              <td>{{ product.moq }}</td>
              <td>{{ product.current_moq }}</td>
              <td>
                <button @click="placeOrderForProduct(product.id)" :disabled="loading">Place Order</button>
              </td>
            </tr>
            <tr v-if="!moqFulfilledProducts.length">
              <td colspan="4" class="no-data">No products with fulfilled MOQ.</td>
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
import { useRouter } from 'vue-router';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import api from '@/services/api';
import { toast } from 'vue3-toastify';
import { debounce } from 'lodash';

export default {
  components: { AdminLayout },
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const orders = ref({
      processing: [],
      shipped: [],
      delivered: [],
    });
    const moqFulfilledProducts = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const selectedOrders = ref([]);
    const currentPage = ref({
      processing: 1,
      shipped: 1,
      delivered: 1,
    });
    const totalPages = ref({
      processing: 1,
      shipped: 1,
      delivered: 1,
    });
    const totalOrders = ref({
      processing: 0,
      shipped: 0,
      delivered: 0,
    });

    const fetchOrders = async (status, page = 1, retries = 3) => {
      try {
        loading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const response = await api.fetchAllOrdersAdmin(apiInstance, {
          page,
          delivery_status: status,
        });
        console.log(`Fetch ${status} orders response:`, response);
        orders.value[status] = [...(response.results || [])];
        console.log(`Updated ${status} orders:`, orders.value[status]);
        totalOrders.value[status] = response.total || 0;
        totalPages.value[status] = response.pages || 1;
        currentPage.value[status] = response.current_page || 1;
      } catch (err) {
        if (retries > 0) {
          console.warn(`Retrying fetchOrders for ${status} (${retries} attempts left)...`);
          await new Promise(resolve => setTimeout(resolve, 6000));
          return fetchOrders(status, page, retries - 1);
        }
        error.value = err.response?.data?.error || `Failed to load ${status} orders. Please try again.`;
        console.error(`Failed to fetch ${status} orders:`, err);
      } finally {
        loading.value = false;
      }
    };

    const fetchAllOrders = async () => {
      try {
        loading.value = true;
        // Fetch sequentially
        await fetchOrders('processing', currentPage.value.processing);
        await fetchOrders('shipped', currentPage.value.shipped);
        await fetchOrders('delivered', currentPage.value.delivered);
      } catch (err) {
        console.error('Error fetching all orders:', err);
      }
    };

    const fetchMOQFulfilledProducts = async () => {
      try {
        loading.value = true;
        const apiInstance = api.createApiInstance(store);
        const response = await api.getMOQFulfilledProducts(apiInstance);
        moqFulfilledProducts.value = response || [];
      } catch (err) {
        console.error('Failed to fetch MOQ fulfilled products:', err);
      } finally {
        loading.value = false;
      }
    };

    const selectAllOrders = (status, event) => {
      if (event.target.checked) {
        selectedOrders.value = [...new Set([...selectedOrders.value, ...orders.value[status].map(order => order.id)])];
      } else {
        selectedOrders.value = selectedOrders.value.filter(id => !orders.value[status].some(order => order.id === id));
      }
    };

    const bulkUpdateStatus = async (deliveryStatus) => {
      if (selectedOrders.value.length === 0) {
        toast.error('Please select at least one order');
        return;
      }
      try {
        loading.value = true;
        console.log('Bulk updating orders:', selectedOrders.value, 'to status:', deliveryStatus);
        const apiInstance = api.createApiInstance(store);
        const response = await api.bulkUpdateOrderStatus(apiInstance, selectedOrders.value, deliveryStatus);
        toast.success(response.message);
        await fetchAllOrders();
        selectedOrders.value = [];
      } catch (err) {
        const errorMessage = err.response?.data?.error || 'Failed to update orders. Please try again.';
        console.error('Failed to update orders:', err.response?.data || err);
        toast.error(errorMessage);
      } finally {
        loading.value = false;
      }
    };

    const updateSingleOrderStatus = async (orderId, event) => {
      const deliveryStatus = event.target.value;
      if (!deliveryStatus) return;
      try {
        loading.value = true;
        console.log('Updating single order:', orderId, 'to status:', deliveryStatus);
        const apiInstance = api.createApiInstance(store);
        const response = await api.updateSingleOrderStatus(apiInstance, orderId, deliveryStatus);
        toast.success(response.message);
        await fetchAllOrders();
      } catch (err) {
        const errorMessage = err.response?.data?.error || 'Failed to update order status. Please try again.';
        console.error('Failed to update order status:', err.response?.data || err);
        toast.error(errorMessage);
      } finally {
        loading.value = false;
        event.target.value = '';
      }
    };

    const placeOrderForProduct = async (productId) => {
      try {
        loading.value = true;
        const apiInstance = api.createApiInstance(store);
        await api.placeOrderForProduct(apiInstance, productId);
        toast.success('Orders for this product moved to processing');
        await fetchAllOrders();
        await fetchMOQFulfilledProducts();
      } catch (err) {
        console.error('Failed to place order for product:', err);
        toast.error('Failed to process MOQ order. Please try again.');
      } finally {
        loading.value = false;
      }
    };

    const viewOrderDetails = (orderId) => {
      router.push(`/admin/orders/${orderId}`);
    };

    const changePage = debounce((status, page) => {
      if (page >= 1 && page <= totalPages.value[status]) {
        fetchOrders(status, page);
      }
    }, 300);
    const scrollToMOQ = () => {
      const element = document.getElementById('moq-section');
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    };
    const scrollToTop = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    const scrollToStatus = (status) => {
      const element = document.getElementById(`status-${status}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
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

    onMounted(() => {
      fetchAllOrders();
      fetchMOQFulfilledProducts();
    });

    return {
      orders,
      moqFulfilledProducts,
      loading,
      error,
      selectedOrders,
      fetchOrders,
      fetchAllOrders,
      selectAllOrders,
      bulkUpdateStatus,
      updateSingleOrderStatus,
      placeOrderForProduct,
      viewOrderDetails,
      changePage,
      scrollToStatus,
      getStatusClass,
      currentPage,
      totalPages,
      totalOrders,
      scrollToMOQ,
      scrollToTop,
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

h2, h3 {
  font-size: 1.75rem;
  color: #4f46e5;
  margin-bottom: 24px;
  font-weight: 700;
}

h3 {
  font-size: 1.5rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

th, td {
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

button:not(.status-button), select {
  padding: 6px 12px;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:not(.status-button):hover:not(:disabled), select:hover:not(:disabled) {
  background-color: #5a32a3;
}

button:disabled, select:disabled {
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

.status-shipped {
  color: #007bff;
  font-weight: 500;
}

.loading, .error-message {
  text-align: center;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.bulk-actions {
  margin-bottom: 20px;
}

.bulk-actions button {
  margin-right: 10px;
}

.status-section {
  margin-bottom: 40px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
}

.moq-section {
  margin-top: 40px;
}

.status-navigation {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #fff;
  padding: 10px 0;
  display: flex;
  gap: 10px;
  border-bottom: 1px solid #eee;
}

.status-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.status-button.processing {
  background-color: #f4c430;
  color: #fff;
}

.status-button.processing:hover {
  background-color: #e0b028;
}

.status-button.shipped {
  background-color: #007bff;
  color: #fff;
}

.status-button.shipped:hover {
  background-color: #0056b3;
}

.status-button.delivered {
  background-color: #28a745;
  color: #fff;
}

.status-button.delivered:hover {
  background-color: #218838;
}


.status-button.moq {
  background-color: #6f42c1;
  color: #fff;
}

.status-button.moq:hover {
  background-color: #5a32a3;
}
</style>