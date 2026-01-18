<template>
  <AdminLayout>
    <div class="orders">
      <h2>Manage Orders</h2>

      <!-- Order Type Filter and Search -->
      <div class="order-type-filter">
        <div class="filter-group">
          <label>Filter by Order Type:</label>
          <div class="filter-buttons">
            <button
              :class="['filter-btn', { active: orderTypeFilter === 'all' }]"
              @click="setOrderTypeFilter('all')"
            >
              All Orders
            </button>
            <button
              :class="['filter-btn', { active: orderTypeFilter === 'moq' }]"
              @click="setOrderTypeFilter('moq')"
            >
              MOQ Orders
            </button>
            <button
              :class="['filter-btn', { active: orderTypeFilter === 'pick_pay' }]"
              @click="setOrderTypeFilter('pick_pay')"
            >
              Pick & Pay Orders
            </button>
          </div>
        </div>
        
        <!-- Search Bar with Suggestions -->
        <div class="search-group">
          <label for="search">Search Order Number:</label>
          <div class="search-container">
            <input
              id="search"
              v-model="searchQuery"
              type="text"
              placeholder="Enter order number..."
              class="search-input"
              @input="debouncedFetchSuggestions"
              @focus="showSuggestions = true"
              @blur="delayHideSuggestions"
            />
            <button @click="clearSearch" v-if="searchQuery" class="clear-search">×</button>
            <ul v-if="showSuggestions && suggestions.length" class="suggestions-list">
              <li
                v-for="suggestion in suggestions"
                :key="suggestion"
                @click="selectSuggestion(suggestion)"
                class="suggestion-item"
              >
                {{ suggestion }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['tab-button', { active: activeTab === tab.id }]"
          @click="setActiveTab(tab.id)"
          :disabled="isTabLoading(tab.id)"
        >
          {{ tab.label }}
          <span v-if="isTabLoading(tab.id)" class="tab-spinner">⟳</span>
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
          <button @click="retryCurrentTab" class="retry-button">Retry</button>
        </div>

        <!-- Orders Tabs (Processing, Shipped, Delivered) -->
        <div v-if="['processing', 'shipped', 'delivered'].includes(activeTab)" class="orders-section">
          <div class="tab-status-content">
            <h3>{{ activeTab.charAt(0).toUpperCase() + activeTab.slice(1) }} Orders ({{ currentTabOrders.length }})</h3>
            
            <!-- Tab Loading State -->
            <div v-if="isTabLoading(activeTab)" class="loading">
              <div class="spinner"></div>
              Loading {{ activeTab }} orders...
            </div>

            <!-- Bulk Actions -->
            <div class="bulk-actions" v-if="selectedOrders.length > 0 && !isTabLoading(activeTab)">
              <button @click="bulkUpdateStatus('processing')" :disabled="loading">Mark as Processing</button>
              <button @click="bulkUpdateStatus('shipped')" :disabled="loading">Mark as Shipped</button>
              <button @click="bulkUpdateStatus('delivered')" :disabled="loading">Mark as Delivered</button>
            </div>

            <div class="table-wrapper" v-if="!isTabLoading(activeTab)">
              <table>
                <thead>
                  <tr>
                    <th><input type="checkbox" @change="selectAllOrders($event)" /></th>
                    <th>Order Number</th>
                    <th>Customer Email</th>
                    <th>Order Type</th>
                    <th>Total (KES)</th>
                    <th>Payment Status</th>
                    <th>Delivery Status</th>
                    <th>Delivery Location</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="order in paginatedCurrentTabOrders" :key="order.id">
                    <td><input type="checkbox" :value="order.id" v-model="selectedOrders" /></td>
                    <td>{{ order.order_number || 'N/A' }}</td>
                    <td>{{ order.user?.email || 'N/A' }}</td>
                    <td>
                      <span :class="getOrderTypeClass(order)">
                        {{ getOrderType(order) }}
                      </span>
                    </td>
                    <td>{{ formatPrice(order.total_price) }}</td>
                    <td>
                      <span :class="getStatusClass(order.payment_status)">{{ order.payment_status || 'N/A' }}</span>
                    </td>
                    <td>
                      <span :class="getStatusClass(order.delivery_status)">{{ order.delivery_status || 'N/A' }}</span>
                    </td>
                    <td class="delivery-location">{{ order.delivery_location?.address || 'N/A' }}</td>
                    <td>{{ formatDate(order.created_at) }}</td>
                    <td class="actions-cell">
                      <button @click="viewOrderDetails(order)" class="view-btn">View Details</button>
                      <select @change="updateSingleOrderStatus(order.id, $event)" :disabled="loading" class="status-select">
                        <option value="" disabled selected>Change Status</option>
                        <option value="processing">Processing</option>
                        <option value="shipped">Shipped</option>
                        <option value="delivered">Delivered</option>
                      </select>
                    </td>
                  </tr>
                  <tr v-if="!paginatedCurrentTabOrders.length && !isTabLoading(activeTab)">
                    <td colspan="10" class="no-data">No {{ activeTab }} orders available.</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div class="pagination" v-if="Math.ceil(currentTabOrders.length / itemsPerPage) > 1 && !isTabLoading(activeTab)">
              <button
                @click="changePage(currentPage - 1)"
                :disabled="currentPage === 1 || loading"
              >
                Previous
              </button>
              <span>Page {{ currentPage }} of {{ Math.ceil(currentTabOrders.length / itemsPerPage) }}</span>
              <button
                @click="changePage(currentPage + 1)"
                :disabled="currentPage === Math.ceil(currentTabOrders.length / itemsPerPage) || loading"
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
          <div class="table-wrapper" v-if="!moqLoading">
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

    <!-- Order Details Modal -->
    <div v-if="showOrderModal" class="modal-overlay" @click="closeOrderModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Order Details - {{ selectedOrder?.order_number }}</h3>
          <button @click="closeOrderModal" class="close-btn">×</button>
        </div>
        <div class="modal-body" v-if="selectedOrder">
          <!-- Customer Information -->
          <div class="section">
            <h4>Customer Information</h4>
            <div class="info-grid">
              <div class="info-item">
                <label>Name:</label>
                <span>{{ selectedOrder.user?.first_name }} {{ selectedOrder.user?.last_name }}</span>
              </div>
              <div class="info-item">
                <label>Email:</label>
                <span>{{ selectedOrder.user?.email || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Phone:</label>
                <span>{{ selectedOrder.user?.phone_number || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Delivery Location:</label>
                <span>{{ selectedOrder.delivery_location?.address || 'N/A' }}</span>
              </div>
            </div>
          </div>

          <!-- Order Information -->
          <div class="section">
            <h4>Order Information</h4>
            <div class="info-grid">
              <div class="info-item">
                <label>Order Type:</label>
                <span :class="getOrderTypeClass(selectedOrder)">
                  {{ getOrderType(selectedOrder) }}
                </span>
              </div>
              <div class="info-item">
                <label>Payment Status:</label>
                <span :class="getStatusClass(selectedOrder.payment_status)">
                  {{ selectedOrder.payment_status || 'N/A' }}
                </span>
              </div>
              <div class="info-item">
                <label>Delivery Status:</label>
                <span :class="getStatusClass(selectedOrder.delivery_status)">
                  {{ selectedOrder.delivery_status || 'N/A' }}
                </span>
              </div>
              <div class="info-item">
                <label>Shipping Method:</label>
                <span>{{ selectedOrder.shipping_method?.name || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <label>Shipping Cost:</label>
                <span>KES {{ formatPrice(selectedOrder.shipping_cost) }}</span>
              </div>
              <div class="info-item">
                <label>Total Paid:</label>
                <span class="total-amount">KES {{ formatPrice(selectedOrder.total_price) }}</span>
              </div>
            </div>
          </div>

          <!-- Order Items -->
          <div class="section">
            <h4>Order Items</h4>
            <div class="items-list">
              <div v-for="item in selectedOrder.items" :key="item.id" class="item-card">
                <div class="item-info">
                  <h5>{{ item.product_name }}</h5>
                  <div class="item-details">
                    <div class="attributes" v-if="item.attributes && Object.keys(item.attributes).length">
                      <strong>Attributes:</strong>
                      <span v-for="(value, key) in item.attributes" :key="key" class="attribute-tag">
                        {{ key }}: {{ value }}
                      </span>
                    </div>
                    <div class="quantity-price">
                      <span>Quantity: {{ item.quantity }}</span>
                      <span>Unit Price: KES {{ formatPrice(item.price) }}</span>
                      <span class="line-total">Line Total: KES {{ formatPrice(item.line_total) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeOrderModal" class="close-modal-btn">Close</button>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>


<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useAuthStore } from '@/stores/modules/auth';
import { useOrdersStore } from '@/stores/modules/orders';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import api from '@/services/api';
import { toast } from 'vue3-toastify';
import { debounce } from 'lodash';

// Store
const authStore = useAuthStore();
const ordersStore = useOrdersStore();
// Create minimal store object for api.js compatibility
const store = { isAuthenticated: computed(() => authStore.isAuthenticated) };

// Tab Management
const tabs = [
  { id: 'processing', label: 'Processing' },
  { id: 'shipped', label: 'Shipped' },
  { id: 'delivered', label: 'Delivered' },
  { id: 'moq', label: 'MOQ Fulfilled' },
  { id: 'shipping', label: 'Shipping Methods' },
];
const activeTab = ref('processing');

// Orders State - Fixed structure
const orders = ref({
  processing: [],
  shipped: [],
  delivered: [],
});

// Other state
const moqFulfilledProducts = ref([]);
const shippingMethods = ref([]);
const loading = ref(false);
const globalLoading = ref(true); // Start with global loading
const error = ref(null);
const selectedOrders = ref([]);

// Pagination - separate for each tab
const currentPage = ref(1);
const itemsPerPage = 10;

// Loading states for individual tabs
const tabLoading = ref({
  processing: false,
  shipped: false,
  delivered: false,
});
const moqLoading = ref(false);

// Filtering and Search State
const orderTypeFilter = ref('all');
const searchQuery = ref('');
const suggestions = ref([]);
const showSuggestions = ref(false);

// Modal State
const showOrderModal = ref(false);
const selectedOrder = ref(null);

// Shipping Methods State
const shippingForm = ref({
  id: null,
  name: '',
  price: 0,
  description: '',
  is_active: true,
});
const editingShippingMethod = ref(false);

// Track active API calls to prevent duplicates
const activeApiCalls = ref(new Set());

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

const getOrderType = (order) => {
  if (!order) return 'Unknown';
  
  if (order.order_type) {
    return order.order_type === 'moq' ? 'MOQ Order' : 'Pick & Pay';
  }
  
  const shippingCost = parseFloat(order.shipping_cost);
  if (!isNaN(shippingCost) && shippingCost > 0) {
    return 'MOQ Order';
  }
  
  return 'Pick & Pay';
};

const getOrderTypeClass = (order) => {
  const orderType = getOrderType(order);
  return orderType === 'MOQ Order' ? 'order-type-moq' : 'order-type-pick-pay';
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

// Helper function to check if a tab is loading
const isTabLoading = (tabId) => {
  if (['processing', 'shipped', 'delivered'].includes(tabId)) {
    return tabLoading.value[tabId];
  }
  if (tabId === 'moq') {
    return moqLoading.value;
  }
  return false;
};

// Get current tab orders with filtering - FIXED
const currentTabOrders = computed(() => {
  if (!['processing', 'shipped', 'delivered'].includes(activeTab.value)) {
    return [];
  }

  let filteredList = [...(orders.value[activeTab.value] || [])];

  // Apply order type filter
  if (orderTypeFilter.value !== 'all') {
    filteredList = filteredList.filter(order => {
      const orderType = getOrderType(order);
      if (orderTypeFilter.value === 'moq') {
        return orderType === 'MOQ Order';
      } else if (orderTypeFilter.value === 'pick_pay') {
        return orderType === 'Pick & Pay';
      }
      return true;
    });
  }

  // Apply search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    filteredList = filteredList.filter(order => {
      return (
        order.order_number?.toLowerCase().includes(query) ||
        order.user?.email?.toLowerCase().includes(query) ||
        order.user?.first_name?.toLowerCase().includes(query) ||
        order.user?.last_name?.toLowerCase().includes(query)
      );
    });
  }

  return filteredList;
});

// Paginated orders for current tab
const paginatedCurrentTabOrders = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return currentTabOrders.value.slice(start, end);
});

// FIXED: Simplified watchers to prevent infinite loops
watch([orderTypeFilter, searchQuery], () => {
  currentPage.value = 1; // Reset pagination only
  // Don't trigger new API calls - let computed properties handle filtering
});

// FIXED: Tab watcher with proper state management
watch(activeTab, async (newTab, oldTab) => {
  if (newTab === oldTab) return;
  
  console.log(`Switching from ${oldTab} to ${newTab}`);
  
  // Reset states immediately
  currentPage.value = 1;
  selectedOrders.value = [];
  error.value = null;
  
  // Clear filters when switching tabs
  if (!['processing', 'shipped', 'delivered'].includes(newTab)) {
    searchQuery.value = '';
    suggestions.value = [];
    orderTypeFilter.value = 'all';
  }

  // Wait for next tick to ensure UI updates
  await nextTick();
  
  // Load data for the new tab
  if (['processing', 'shipped', 'delivered'].includes(newTab)) {
    if (!orders.value[newTab] || orders.value[newTab].length === 0) {
      await fetchOrders(newTab);
    }
  } else if (newTab === 'moq') {
    if (moqFulfilledProducts.value.length === 0) {
      await fetchMOQFulfilledProducts();
    }
  } else if (newTab === 'shipping') {
    if (shippingMethods.value.length === 0) {
      await fetchShippingMethods();
    }
  }
});

// Filter and Search Functions
const setOrderTypeFilter = (type) => {
  orderTypeFilter.value = type;
  currentPage.value = 1;
};

const clearSearch = () => {
  searchQuery.value = '';
  suggestions.value = [];
  showSuggestions.value = false;
  currentPage.value = 1;
};

const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion;
  showSuggestions.value = false;
  currentPage.value = 1;
};

const debouncedFetchSuggestions = debounce(async () => {
  if (searchQuery.value.trim()) {
    try {
      const apiInstance = api.createApiInstance(store);
      const response = await apiInstance.get('/orders/search-suggestions/', {
        params: { q: searchQuery.value }
      });
      suggestions.value = response.data || [];
      showSuggestions.value = true;
    } catch (err) {
      console.error('Failed to fetch suggestions:', err);
      suggestions.value = [];
      showSuggestions.value = false;
    }
  } else {
    suggestions.value = [];
    showSuggestions.value = false;
  }
}, 300);

const delayHideSuggestions = () => {
  setTimeout(() => {
    showSuggestions.value = false;
  }, 200);
};

const setActiveTab = (tabId) => {
  if (activeTab.value === tabId) return; // Prevent unnecessary changes
  activeTab.value = tabId;
};

const retryCurrentTab = () => {
  error.value = null;
  if (['processing', 'shipped', 'delivered'].includes(activeTab.value)) {
    fetchOrders(activeTab.value);
  } else if (activeTab.value === 'moq') {
    fetchMOQFulfilledProducts();
  } else if (activeTab.value === 'shipping') {
    fetchShippingMethods();
  }
};

// Modal Functions
const viewOrderDetails = (order) => {
  selectedOrder.value = order;
  showOrderModal.value = true;
};

const closeOrderModal = () => {
  showOrderModal.value = false;
  selectedOrder.value = null;
};

// FIXED: Fetch Functions with proper call tracking
const fetchOrders = async (status) => {
  const callKey = `orders-${status}`;
  
  // Prevent multiple simultaneous calls for the same status
  if (activeApiCalls.value.has(callKey)) {
    console.log(`Already fetching ${status} orders, skipping...`);
    return;
  }

  try {
    activeApiCalls.value.add(callKey);
    tabLoading.value[status] = true;
    error.value = null;
    
    console.log(`Fetching ${status} orders...`);
    
    const apiInstance = api.createApiInstance(store);
    const response = await api.fetchAllOrdersAdmin(apiInstance, {
      page: 1,
      delivery_status: status,
      per_page: 100, // Get more results for better client-side filtering
    });
    
    // Only update if we're still on the same tab
    if (activeTab.value === status) {
      orders.value[status] = response.results || [];
      console.log(`Successfully fetched ${response.results?.length || 0} ${status} orders`);
    }
    
  } catch (err) {
    console.error(`Failed to fetch ${status} orders:`, err);
    if (activeTab.value === status) {
      error.value = err.response?.data?.error || `Failed to load ${status} orders.`;
      orders.value[status] = [];
    }
  } finally {
    tabLoading.value[status] = false;
    activeApiCalls.value.delete(callKey);
  }
};

const fetchMOQFulfilledProducts = async () => {
  const callKey = 'moq-products';
  
  if (activeApiCalls.value.has(callKey)) {
    return;
  }

  try {
    activeApiCalls.value.add(callKey);
    moqLoading.value = true;
    error.value = null;
    
    const apiInstance = api.createApiInstance(store);
    const response = await api.getMOQFulfilledProducts(apiInstance);
    moqFulfilledProducts.value = response || [];
  } catch (err) {
    console.error('Failed to fetch MOQ fulfilled products:', err);
    error.value = 'Failed to load MOQ fulfilled products.';
    moqFulfilledProducts.value = [];
  } finally {
    moqLoading.value = false;
    activeApiCalls.value.delete(callKey);
  }
};

const fetchShippingMethods = async () => {
  const callKey = 'shipping-methods';
  
  if (activeApiCalls.value.has(callKey)) {
    return;
  }

  try {
    activeApiCalls.value.add(callKey);
    loading.value = true;
    error.value = null;
    
    const apiInstance = api.createApiInstance(store);
    const response = await apiInstance.get('shipping_methods1/');
    shippingMethods.value = response.data || [];
  } catch (err) {
    console.error('Failed to fetch shipping methods:', err);
    error.value = 'Failed to load shipping methods.';
    shippingMethods.value = [];
  } finally {
    loading.value = false;
    activeApiCalls.value.delete(callKey);
  }
};

// Order Management
const selectAllOrders = (event) => {
  if (event.target.checked) {
    selectedOrders.value = [...new Set([...selectedOrders.value, ...paginatedCurrentTabOrders.value.map(order => order.id)])];
  } else {
    selectedOrders.value = selectedOrders.value.filter(id => !paginatedCurrentTabOrders.value.some(order => order.id === id));
  }
};

const bulkUpdateStatus = async (deliveryStatus) => {
  if (!selectedOrders.value.length) {
    toast.error('Please select at least one order');
    return;
  }
  try {
    loading.value = true;
    const apiInstance = api.createApiInstance(store);
    const response = await api.bulkUpdateOrderStatus(apiInstance, selectedOrders.value, deliveryStatus);
    toast.success(response.message);
    
    // Refresh only the affected tabs
    const tabsToRefresh = ['processing', 'shipped', 'delivered'];
    await Promise.all(tabsToRefresh.map(tab => {
      // Clear the tab data first to force a refresh
      orders.value[tab] = [];
      return fetchOrders(tab);
    }));
    
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
    
    // Refresh only the affected tabs
    const tabsToRefresh = ['processing', 'shipped', 'delivered'];
    await Promise.all(tabsToRefresh.map(tab => {
      orders.value[tab] = [];
      return fetchOrders(tab);
    }));
    
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
    
    // Refresh relevant data
    await Promise.all([
      fetchOrders('processing'),
      fetchMOQFulfilledProducts()
    ]);
  } catch (err) {
    console.error('Failed to place order for product:', err);
    toast.error(err.response?.data?.error || 'Failed to process MOQ order.');
  } finally {
    loading.value = false;
  }
};

// Pagination
const changePage = (page) => {
  const maxPages = Math.ceil(currentTabOrders.value.length / itemsPerPage);
  if (page >= 1 && page <= maxPages) {
    currentPage.value = page;
  }
};

// Shipping Methods Management
const saveShippingMethod = async () => {
  try {
    loading.value = true;
    const apiInstance = api.createApiInstance(store);
    const payload = { ...shippingForm.value };
    
    if (editingShippingMethod.value) {
      await api.updateShippingMethod(apiInstance, shippingForm.value.id, payload);
      toast.success('Shipping method updated');
    } else {
      await api.createShippingMethod(apiInstance, payload);
      toast.success('Shipping method created');
    }
    
    await fetchShippingMethods();
    resetShippingForm();
  } catch (err) {
    console.error('Failed to save shipping method:', err);
    toast.error(err.response?.data?.error || 'Failed to save shipping method.');
  } finally {
    loading.value = false;
  }
};

const editShippingMethod = (method) => {
  shippingForm.value = { ...method };
  editingShippingMethod.value = true;
};

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

// FIXED: Initialize only once
onMounted(async () => {
  try {
    globalLoading.value = true;
    
    // Load initial data for the default tab
    await fetchOrders('processing');
    
    console.log('Initialization completed');
  } catch (err) {
    console.error('Initialization error:', err);
    error.value = 'Failed to initialize data.';
  } finally {
    globalLoading.value = false;
  }
});
</script>

<style scoped>
.orders {
  padding: 1rem;
  background-color: transparent;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.order-type-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-buttons {
  display: flex;
  gap: 0.75rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
  background-color: #f4f4f4;
  color: #333;
}

.filter-btn.active {
  background-color: #6f42c1;
  color: #fff;
}

.filter-btn:hover:not(.active) {
  background-color: #e0e0e0;
}

.search-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 15rem;
  position: relative;
}

.search-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.5rem 2.5rem 0.5rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s;
}

.search-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(111, 66, 193, 0.2);
}

.clear-search {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: #ff4d4f;
  color: white;
  border-radius: 50%;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.clear-search:hover {
  background: #d9363e;
}

.suggestions-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 0.25rem;
}

.suggestion-item {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.suggestion-item:hover {
  background-color: #f4f4f4;
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
}

.form-group input,
.form-group textarea {
  width: 100%;
  max-width: 25rem;
  padding: 0.5rem;
  border: 0.0625rem solid #ddd;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.form-group textarea {
  min-height: 6.25rem;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 0.625rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-in-out;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  max-width: 40rem;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-in-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #eee;
  text-align: right;
}

.section {
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item label {
  font-weight: 500;
  color: #333;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.item-card {
  border: 1px solid #eee;
  border-radius: 0.25rem;
  padding: 1rem;
}

.item-info h5 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.attributes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.attribute-tag {
  background: #f4f4f4;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
}

.quantity-price {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@media (max-width: 765px) {
  .orders { padding: 0.75rem; }
  h2 { font-size: 1.5rem; }
  h3 { font-size: 1.25rem; }
  h4 { font-size: 1.125rem; }
  .tab-button { padding: 0.5rem 0.75rem; font-size: 0.8125rem; }
  th, td { padding: 0.5rem; font-size: 0.8125rem; }
  .delivery-location { max-width: 10rem; }
  button:not(.tab-button), select { padding: 0.375rem 0.625rem; font-size: 0.8125rem; }
  .bulk-actions { flex-direction: column; }
  .pagination button { padding: 0.375rem 0.75rem; }
  .filter-buttons { gap: 0.5rem; }
  .search-input { font-size: 0.8125rem; }
  .modal-content { width: 95%; }
}

@media (max-width: 650px) {
  .orders { padding: 0.5rem; }
  h2 { font-size: 1.25rem; }
  h3 { font-size: 1.125rem; }
  h4 { font-size: 1rem; }
  .tab-button { padding: 0.25rem 0.625rem; font-size: 0.75rem; }
  th, td { padding: 0.375rem; font-size: 0.75rem; }
  .delivery-location { max-width: 8rem; }
  button:not(.tab-button), select { padding: 0.25rem 0.5rem; font-size: 0.75rem; }
  .no-data { padding: 0.75rem; }
  .filter-buttons { gap: 0.375rem; }
  .search-input { font-size: 0.75rem; }
  .modal-content { width: 98%; }
}
</style>