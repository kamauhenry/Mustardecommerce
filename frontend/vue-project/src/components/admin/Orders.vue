<template>
  <AdminLayout>
    <div class="orders">
      <h2>Manage Orders</h2>

      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['tab-button', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Global Loading State -->
        <div v-if="globalLoading" class="loading">
          <div class="spinner"></div>
          Loading...
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-message">
          {{ error }}
          <button @click="fetchAllOrders" class="retry-button">Retry</button>
        </div>

        <!-- Orders Tabs (Processing, Shipped, Delivered) -->
        <div v-if="activeTab === 'processing' || activeTab === 'shipped' || activeTab === 'delivered'" class="orders-section">
          <div v-for="status in ['processing', 'shipped', 'delivered']" :key="status" v-show="activeTab === status">
            <h3>{{ status.charAt(0).toUpperCase() + status.slice(1) }} Orders</h3>
            <!-- Bulk Actions -->
            <div class="bulk-actions" v-if="selectedOrders.length > 0">
              <button @click="bulkUpdateStatus('processing')" :disabled="loading">Mark as Processing</button>
              <button @click="bulkUpdateStatus('shipped')" :disabled="loading">Mark as Shipped</button>
              <button @click="bulkUpdateStatus('delivered')" :disabled="loading">Mark as Delivered</button>
            </div>
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th><input type="checkbox" @change="selectAllOrders(status, $event)" /></th>
                    <th>Order Number</th>
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
                    <td>{{ order.order_number || 'N/A' }}</td>
                    <td>{{ order.user?.email || 'N/A' }}</td>
                    <td>{{ formatPrice(order.total_price) }}</td>
                    <td>
                      <span :class="getStatusClass(order.payment_status)">{{ order.payment_status || 'N/A' }}</span>
                    </td>
                    <td>
                      <span :class="getStatusClass(order.delivery_status)">{{ order.delivery_status || 'N/A' }}</span>
                    </td>
                    <td class="delivery-location">{{ order.delivery_location?.address || 'N/A' }}</td>
                    <td>{{ formatDate(order.created_at) }}</td>
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
                  <tr v-if="!orders[status].length && !loading">
                    <td colspan="9" class="no-data">No {{ status }} orders available.</td>
                  </tr>
                </tbody>
              </table>
            </div>
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

        <!-- MOQ Fulfilled Tab -->
        <div v-if="activeTab === 'moq'" class="moq-section">
          <h3>MOQ Fulfilled Products</h3>
          <div v-if="moqLoading" class="loading">
            <div class="spinner"></div>
            Loading MOQ products...
          </div>
          <div class="table-wrapper">
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
                  <td>{{ product.name || 'N/A' }}</td>
                  <td>{{ product.moq || '0' }}</td>
                  <td>{{ product.current_moq || '0' }}</td>
                  <td>
                    <button @click="placeOrderForProduct(product.id)" :disabled="loading">Place Order</button>
                  </td>
                </tr>
                <tr v-if="!moqFulfilledProducts.length && !moqLoading">
                  <td colspan="4" class="no-data">No products with fulfilled MOQ.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Shipping Methods Tab -->
        <div v-if="activeTab === 'shipping'" class="shipping-section">
          <h3>Manage Shipping Methods</h3>
          <div class="shipping-form">
            <h4>{{ editingShippingMethod ? 'Edit' : 'Add' }} Shipping Method</h4>
            <form @submit.prevent="saveShippingMethod">
              <div class="form-group">
                <label for="name">Name</label>
                <input
                  v-model="shippingForm.name"
                  type="text"
                  id="name"
                  required
                  placeholder="e.g., Standard Shipping"
                />
              </div>
              <div class="form-group">
                <label for="price">Price (KES)</label>
                <input
                  v-model.number="shippingForm.price"
                  type="number"
                  id="price"
                  required
                  min="0"
                  step="0.01"
                />
              </div>
              <div class="form-group">
                <label for="description">Description</label>
                <textarea
                  v-model="shippingForm.description"
                  id="description"
                  placeholder="Describe the shipping method"
                ></textarea>
              </div>
              <div class="form-group">
                <label>
                  <input type="checkbox" v-model="shippingForm.is_active" />
                  Active
                </label>
              </div>
              <div class="form-actions">
                <button type="submit" :disabled="loading">Save</button>
                <button
                  type="button"
                  @click="resetShippingForm"
                  v-if="editingShippingMethod"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Price (KES)</th>
                  <th>Description</th>
                  <th>Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="method in shippingMethods" :key="method.id">
                  <td>{{ method.name || 'N/A' }}</td>
                  <td>{{ formatPrice(method.price) }}</td>
                  <td>{{ method.description || 'N/A' }}</td>
                  <td>
                    <span :class="method.is_active ? 'status-completed' : 'status-pending'">
                      {{ method.is_active ? 'Yes' : 'No' }}
                    </span>
                  </td>
                  <td>
                    <button @click="editShippingMethod(method)">Edit</button>
                    <button @click="deleteShippingMethod(method.id)" :disabled="loading">Delete</button>
                  </td>
                </tr>
                <tr v-if="!shippingMethods.length && !loading">
                  <td colspan="5" class="no-data">No shipping methods available.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useRouter } from 'vue-router';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import api from '@/services/api';
import { toast } from 'vue3-toastify';
import { debounce } from 'lodash';
import axios from 'axios';

// Store and Router
const store = useEcommerceStore();
const router = useRouter();

// Tab Management
const tabs = [
  { id: 'processing', label: 'Processing' },
  { id: 'shipped', label: 'Shipped' },
  { id: 'delivered', label: 'Delivered' },
  { id: 'moq', label: 'MOQ Fulfilled' },
  { id: 'shipping', label: 'Shipping Methods' },
];
const activeTab = ref('processing');

// Orders State
const orders = ref({
  processing: [],
  shipped: [],
  delivered: [],
});
const moqFulfilledProducts = ref([]);
const shippingMethods = ref([]);
const loading = ref(false);
const moqLoading = ref(false);
const globalLoading = ref(false);
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

// Shipping Methods State
const shippingForm = ref({
  id: null,
  name: '',
  price: 0,
  description: '',
  is_active: true,
});
const editingShippingMethod = ref(false);

// Utility Functions
const formatPrice = (price) => {
  if (price == null) return 'N/A';
  return (Math.round(price * 100) / 100).toFixed(2);
};
const formatDate = (dateString) => {
  return dateString
    ? new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    : 'N/A';
};

// Update Orders State
const updateOrdersState = (updatedOrders) => {
  const statusMap = { processing: [], shipped: [], delivered: [] };
  updatedOrders.forEach((order) => {
    if (statusMap[order.delivery_status]) {
      statusMap[order.delivery_status].push(order);
    }
  });
  Object.keys(statusMap).forEach((status) => {
    orders.value[status] = statusMap[status];
    totalOrders.value[status] = statusMap[status].length;
    totalPages.value[status] = Math.max(1, Math.ceil(statusMap[status].length / 10));
    currentPage.value[status] = 1;
  });
};

// Fetch Orders
const fetchOrders = async (status, page = 1, retries = 3) => {
  try {
    loading.value = true;
    error.value = null;
    const apiInstance = api.createApiInstance(store);
    const response = await api.fetchAllOrdersAdmin(apiInstance, {
      page,
      delivery_status: status,
    });
    orders.value[status] = [...(response.results || [])];
    totalOrders.value[status] = response.total || 0;
    totalPages.value[status] = response.pages || 1;
    currentPage.value[status] = response.current_page || 1;
  } catch (err) {
    if (retries > 0) {
      console.warn(`Retrying fetchOrders for ${status} (${retries} attempts left)...`);
      await new Promise((resolve) => setTimeout(resolve, 1000));
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
    globalLoading.value = true;
    await Promise.all([
      fetchOrders('processing', currentPage.value.processing),
      fetchOrders('shipped', currentPage.value.shipped),
      fetchOrders('delivered', currentPage.value.delivered),
    ]);
  } catch (err) {
    console.error('Error fetching all orders:', err);
  } finally {
    globalLoading.value = false;
  }
};

// Fetch MOQ Fulfilled Products
const fetchMOQFulfilledProducts = async () => {
  try {
    moqLoading.value = true;
    const apiInstance = api.createApiInstance(store);
    const response = await api.getMOQFulfilledProducts(apiInstance);
    moqFulfilledProducts.value = response || [];
  } catch (err) {
    console.error('Failed to fetch MOQ fulfilled products:', err);
    toast.error('Failed to load MOQ fulfilled products.');
  } finally {
    moqLoading.value = false;
  }
};

// Direct API Call to Fetch Shipping Methods
const fetchShippingMethods = async () => {
  try {
    loading.value = true;
    const apiInstance = api.createApiInstance(store); // Use the configured API instance
    const response = await apiInstance.get('shipping_methods1/'); // Relative path, baseURL is handled by apiInstance
    shippingMethods.value = response.data || [];
  } catch (err) {
    console.error('Failed to fetch shipping methods:', err);
    toast.error('Failed to load shipping methods.');
  } finally {
    loading.value = false;
  }
};

// Save Shipping Method
const saveShippingMethod = async () => {
  try {
    loading.value = true;
    const apiInstance = api.createApiInstance(store);
    const payload = { ...shippingForm.value };
    await api.saveShippingMethod(apiInstance, payload);
    toast.success(editingShippingMethod.value ? 'Shipping method updated' : 'Shipping method created');
    await fetchShippingMethods();
    resetShippingForm();
  } catch (err) {
    console.error('Failed to save shipping method:', err);
    toast.error(err.response?.data?.error || 'Failed to save shipping method.');
  } finally {
    loading.value = false;
  }
};

// Edit Shipping Method
const editShippingMethod = (method) => {
  shippingForm.value = { ...method };
  editingShippingMethod.value = true;
};

// Delete Shipping Method
const deleteShippingMethod = async (id) => {
  if (!confirm('Are you sure you want to delete this shipping method?')) return;
  try {
    loading.value = true;
    const apiInstance = api.createApiInstance(store);
    await api.deleteShippingMethod(apiInstance, id);
    toast.success('Shipping method deleted');
    await fetchShippingMethods();
  } catch (err) {
    console.error('Failed to delete shipping method:', err);
    toast.error(err.response?.data?.error || 'Failed to delete shipping method.');
  } finally {
    loading.value = false;
  }
};

// Reset Shipping Form
const resetShippingForm = () => {
  shippingForm.value = {
    id: null,
    name: '',
    price: 0,
    description: '',
    is_active: true,
  };
  editingShippingMethod.value = false;
};

// Order Management
const selectAllOrders = (status, event) => {
  if (event.target.checked) {
    selectedOrders.value = [...new Set([...selectedOrders.value, ...orders.value[status].map((order) => order.id)])];
  } else {
    selectedOrders.value = selectedOrders.value.filter((id) => !orders.value[status].some((order) => order.id === id));
  }
};

const bulkUpdateStatus = async (deliveryStatus) => {
  if (selectedOrders.value.length === 0) {
    toast.error('Please select at least one order');
    return;
  }
  try {
    loading.value = true;
    const apiInstance = api.createApiInstance(store);
    const response = await api.bulkUpdateOrderStatus(apiInstance, selectedOrders.value, deliveryStatus);
    toast.success(response.message);
    updateOrdersState(response.orders);
    selectedOrders.value = [];
  } catch (err) {
    console.error('Failed to update orders:', err);
    toast.error(err.response?.data?.error || 'Failed to update orders.');
  } finally {
    loading.value = false;
  }
};

const updateSingleOrderStatus = async (orderId, event) => {
  const deliveryStatus = event.target.value;
  if (!deliveryStatus) return;
  try {
    loading.value = true;
    const apiInstance = api.createApiInstance(store);
    const response = await api.updateSingleOrderStatus(apiInstance, orderId, deliveryStatus);
    toast.success(response.message);
    updateOrdersState([response.order]);
  } catch (err) {
    console.error('Failed to update order status:', err);
    toast.error(err.response?.data?.error || 'Failed to update order status.');
  } finally {
    loading.value = false;
    event.target.value = '';
  }
};

const placeOrderForProduct = async (productId) => {
  try {
    loading.value = true;
    const apiInstance = api.createApiInstance(store);
    const response = await api.placeOrderForProduct(apiInstance, productId);
    toast.success(response.message);
    await fetchAllOrders();
    await fetchMOQFulfilledProducts();
  } catch (err) {
    console.error('Failed to place order for product:', err);
    toast.error(err.response?.data?.error || 'Failed to process MOQ order.');
  } finally {
    loading.value = false;
  }
};

const viewOrderDetails = (orderId) => {
  router.push(`/admin-page/orders/${orderId}`);
};

const changePage = debounce((status, page) => {
  if (page >= 1 && page <= totalPages.value[status]) {
    fetchOrders(status, page);
  }
}, 300);

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

// Initialize data on mount
onMounted(async () => {
  try {
    await fetchAllOrders();
    await fetchMOQFulfilledProducts();
    await fetchShippingMethods();
  } catch (err) {
    console.error('Initialization error:', err);
    error.value = 'Failed to initialize data. Please try again.';
  }
});
</script>

<style scoped>
.orders {
  padding: 1rem;
  background-color: transparent;
  border-radius: 0;
  box-shadow: none;
}

h2 {
  font-size: 1.75rem;
  color: #4f46e5;
  margin-bottom: 1.5rem;
  font-weight: 700;
}

h3 {
  font-size: 1.5rem;
  color: #4f46e5;
  margin-bottom: 1rem;
}

h4 {
  font-size: 1.25rem;
  color: #4f46e5;
  margin-bottom: 1rem;
}

.table-wrapper {
  overflow-x: auto;
  margin-bottom: 1.25rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 50rem;
}

th,
td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 0.0625rem solid #eee;
  font-size: 0.875rem;
}

th {
  background-color: #6f42c1;
  color: white;
  font-weight: 600;
}

td {
  vertical-align: middle;
}

.delivery-location {
  max-width: 12.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

tr:hover {
  background-color: #f9f9f9;
}

button:not(.tab-button),
select {
  padding: 0.5rem 0.75rem;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  min-height: 2.75rem;
  touch-action: manipulation;
}

button:not(.tab-button):hover:not(:disabled),
select:hover:not(:disabled) {
  background-color: #5a32a3;
}

button:disabled,
select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 1.25rem;
  font-size: 0.875rem;
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

.loading,
.error-message {
  text-align: center;
  margin: 1.25rem 0;
  font-size: 0.875rem;
}

.spinner {
  display: inline-block;
  width: 1.5rem;
  height: 1.5rem;
  border: 0.1875rem solid #6f42c1;
  border-top: 0.1875rem solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.625rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.bulk-actions {
  margin-bottom: 1rem;
  display: flex;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.625rem;
  margin: 1rem 0;
}

.pagination button {
  padding: 0.5rem 1rem;
}

.tab-navigation {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #fff;
  padding: 0.625rem 0;
  display: flex;
  gap: 0.625rem;
  border-bottom: 0.0625rem solid #eee;
  margin-bottom: 1rem;
  overflow-x: auto;
  scrollbar-width: none;
}

.tab-navigation::-webkit-scrollbar {
  display: none;
}

.tab-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
  background-color: #f4f4f4;
  color: #333;
  font-size: 0.875rem;
  white-space: nowrap;
}

.tab-button.active {
  background-color: #6f42c1;
  color: #fff;
}

.tab-button:hover:not(.active) {
  background-color: #e0e0e0;
}

.shipping-form {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 0.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
  font-size: 0.875rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  max-width: 25rem;
  padding: 0.5rem;
  border: 0.0625rem solid #ddd;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  box-sizing: border-box;
}

.form-group textarea {
  min-height: 6.25rem;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.form-actions button {
  padding: 0.5rem 1rem;
}

@media (max-width: 765px) {
  .orders {
    padding: 0.75rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  h3 {
    font-size: 1.25rem;
  }

  h4 {
    font-size: 1.125rem;
  }

  .tab-navigation {
    padding: 0.5rem 0;
    gap: 0.5rem;
  }

  .tab-button {
    padding: 0—Es5rem 0.75rem;
    font-size: 0.8125rem;
  }

  th,
  td {
    padding: 0.5rem;
    font-size: 0.8125rem;
  }

  .delivery-location {
    max-width: 10rem;
  }

  button:not(.tab-button),
  select {
    padding: 0.375rem 0.625rem;
    font-size: 0.8125rem;
    min-height: 2.5rem;
  }

  .bulk-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination button {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
  }

  .shipping-form {
    padding: 0.75rem;
  }

  .form-group label {
    font-size: 0.8125rem;
  }

  .form-group input,
  .form-group textarea {
    font-size: 0.8125rem;
    padding: 0.375rem;
    max-width: 100%;
  }

  .form-actions button {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
  }

  .loading,
  .error-message {
    font-size: 0.8125rem;
  }

  .spinner {
    width: 1.25rem;
    height: 1.25rem;
  }
}

@media (max-width: 650px) {
  .orders {
    padding: 0.5rem;
  }

  h2 {
    font-size: 1.25rem;
    margin-bottom: 1rem;
  }

  h3 {
    font-size: 1.125rem;
  }

  h4 {
    font-size: 1rem;
  }

  .tab-navigation {
    padding: 0.375rem 0;
    gap: 0.375rem;
  }

  .tab-button {
    padding: 0.25rem 0.625rem;
    font-size: 0.75rem;
  }

  .table-wrapper {
    margin-bottom: 0.75rem;
  }

  th,
  td {
    padding: 0.375rem;
    font-size: 0.75rem;
  }

  .delivery-location {
    max-width: 8rem;
  }

  button:not(.tab-button),
  select {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    min-height: 2.25rem;
  }

  .no-data {
    padding: 0.75rem;
    font-size: 0.75rem;
  }

  .bulk-actions {
    gap: 0.5rem;
  }

  .pagination {
    gap: 0.5rem;
  }

  .pagination button {
    padding: 0.25rem 0.625rem;
    font-size: 0.75rem;
  }

  .shipping-form {
    padding: 0.5rem;
  }

  .form-group {
    margin-bottom: 0.75rem;
  }

  .form-group label {
    font-size: 0.75rem;
    margin-bottom: 0.375rem;
  }

  .form-group input,
  .form-group textarea {
    font-size: 0.75rem;
    padding: 0.25rem;
  }

  .form-group textarea {
    min-height: 5rem;
  }

  .form-actions {
    gap: 0.5rem;
  }

  .form-actions button {
    padding: 0.25rem 0.625rem;
    font-size: 0.75rem;
  }

  .loading,
  .error-message {
    font-size: 0.75rem;
    margin: 0.75rem 0;
  }

  .spinner {
    width: 1rem;
    height: 1rem;
    border-width: 0.125rem;
  }
}
</style>