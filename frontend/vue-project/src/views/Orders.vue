<template>
  <MainLayout>
    <div class="orders-container">
      <div class="breadcrumb">
        <a href="/">Home</a> > <a href="/account">Account Home</a> > <span>Orders</span>
      </div>

      <h1 class="page-title">Orders <span class="order-count">({{ store.orders.length }})</span></h1>

      <div class="filter-container">
        <div class="filter-group">
          <label>Order Date</label>
          <div class="select-wrapper">
            <select v-model="dateFilter" class="filter-select">
              <option value="last1month">Last 1 Month</option>
              <option value="last3months">Last 3 Months</option>
              <option value="last6months">Last 6 Months</option>
              <option value="lastyear">Last Year</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>

        <div class="filter-group">
          <label>Order Status</label>
          <div class="select-wrapper">
            <select v-model="statusFilter" class="filter-select">
              <option value="all">All</option>
              <option value="unpaid">Unpaid</option>
              <option value="paid">Paid</option>
              <option value="pending">Pending MOQ</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search by order number (e.g., MI123)"
            class="search-input"
          />
        </div>
      </div>

      <div class="status-tabs">
        <button
          v-for="tab in statusTabs"
          :key="tab.value"
          :class="['tab-button', { active: activeTab === tab.value }]"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>

      <div v-if="loading" class="orders-list">
        <div v-for="n in 3" :key="n" class="order-item skeleton">
          <div class="order-header">
            <div class="order-info">
              <div class="skeleton-text skeleton-order-number"></div>
              <div class="skeleton-text skeleton-order-placed"></div>
              <div class="skeleton-text skeleton-order-items"></div>
              <div class="skeleton-text skeleton-order-total"></div>
            </div>
            <div class="order-actions">
              <div class="skeleton-button"></div>
            </div>
          </div>
          <div class="order-status-badge skeleton-badge"></div>
        </div>
      </div>

      <div v-else-if="filteredOrders.length === 0" class="no-orders">
        No orders matching your current filters.
      </div>

      <div v-else class="orders-list">
        <div v-for="order in filteredOrders" :key="order.id" class="order-item">
          <div class="order-header">
            <div class="order-info">
              <div class="order-number">Order: {{ order.order_number }}</div>
              <div class="order-placed">Placed on: {{ formatDate(order.created_at) }}</div>
              <div class="order-items-count">Items: {{ order.items.length }}</div>
              <div class="order-total">Total: KES {{ formatPrice(order.total_price) }}</div>
            </div>
            <div class="order-actions">
              <button @click="openOrderDetails(order.id)" class="view-details-btn">
                View Details
              </button>
            </div>
          </div>
          <div class="order-status-badge" :class="order.payment_status.toLowerCase()">
            {{ order.payment_status }}
          </div>
        </div>
      </div>

      <!-- Order Details Modal -->
      <div v-if="showModal" class="modal-overlay" @click="closeOrderDetails">
        <div class="modal-content" @click.stop>
          <div v-if="modalLoading" class="modal-loading">
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

          <div v-else-if="modalError" class="modal-error">
            {{ modalError }}
            <button @click="fetchOrderDetails(selectedOrderId)" class="retry-button">Retry</button>
          </div>

          <div v-else class="modal-receipt">
            <div class="receipt-header">
              <h2>Receipt {{ selectedOrder.order_number }}</h2>
              <p class="receipt-date">Placed on: {{ formatDate(selectedOrder.created_at) }}</p>
            </div>

            <div class="receipt-section">
              <h3>Order Summary</h3>
              <div class="receipt-row">
                <span>Payment Status:</span>
                <span class="status-badge" :class="selectedOrder.payment_status.toLowerCase()">
                  {{ selectedOrder.payment_status }}
                </span>
              </div>
              <div class="receipt-row">
                <span>Delivery Status:</span>
                <span class="status-badge" :class="selectedOrder.delivery_status.toLowerCase()">
                  {{ selectedOrder.delivery_status }}
                </span>
              </div>
            </div>

            <div class="receipt-section">
              <h3>Items Purchased</h3>
              <div v-for="item in selectedOrder.items" :key="item.id" class="receipt-item">
                <div class="item-details">
                  <p class="item-name">
                    {{ item.product_name }}
                    <span class="product-type-badge" :class="item.product.moq_status === 'active' ? 'moq' : 'pay-pick'">
                      {{ item.product.moq_status === 'active' ? 'MOQ' : 'Pay & Pick' }}
                    </span>
                  </p>
                  <p class="item-quantity">Qty: {{ item.quantity }}</p>
                  <p class="item-price">KES {{ formatPrice(item.price) }}</p>
                  <p v-if="item.product.moq_status === 'active' && item.product.moq" class="item-moq">
                    MOQ: {{ item.product.moq }} units
                    <span v-if="item.product.moq_progress">
                      (Progress: {{ item.product.moq_progress.percentage }}%)
                    </span>
                  </p>
                  <div v-if="item.attributes && Object.keys(item.attributes).length" class="item-attributes">
                    <p v-for="(value, key) in item.attributes" :key="key" class="attribute">
                      {{ formatAttributeKey(key) }}: {{ value }}
                    </p>
                  </div>
                </div>
                <p class="item-line-total">KES {{ formatPrice(item.line_total) }}</p>
              </div>
            </div>

            <div class="receipt-section">
              <h3>Shipping Information</h3>
              <div v-if="selectedOrder.items.every(item => item.product.is_pick_and_pay)">
                <p v-if="selectedOrder.delivery_location?.is_shop_pickup" class="location-info">
                  <span class="info-label">Pickup Location:</span> Mustard Imports Store
                </p>
                <p v-else-if="selectedOrder.delivery_location?.county || selectedOrder.delivery_location?.ward" class="location-info">
                  <span v-if="selectedOrder.delivery_location.county" class="info-label">County:</span>
                  {{ selectedOrder.delivery_location.county || '' }}
                  <br v-if="selectedOrder.delivery_location.county && selectedOrder.delivery_location.ward" />
                  <span v-if="selectedOrder.delivery_location.ward" class="info-label">Ward:</span>
                  {{ selectedOrder.delivery_location.ward || '' }}
                </p>
                <p v-else class="location-info">No delivery location specified.</p>
              </div>
              <div v-else>
                <p v-if="selectedOrder.delivery_location?.county || selectedOrder.delivery_location?.ward" class="location-info">
                  <span v-if="selectedOrder.delivery_location.county" class="info-label">County:</span>
                  {{ selectedOrder.delivery_location.county || '' }}
                  <br v-if="selectedOrder.delivery_location.county && selectedOrder.delivery_location.ward" />
                  <span v-if="selectedOrder.delivery_location.ward" class="info-label">Ward:</span>
                  {{ selectedOrder.delivery_location.ward || '' }}
                </p>
                <p v-else class="location-info">No delivery location specified.</p>
              </div>
              <p>
                <span class="info-label">Shipping Method:</span>
                {{ selectedOrder.shipping_method?.name || 'Not applicable' }}
              </p>
              <p>
                <span class="info-label">Shipping Cost:</span>
                KES {{ formatPrice(selectedOrder.shipping_cost || 0) }}
              </p>
            </div>

            <div class="receipt-section">
              <h3>Order Totals</h3>
              <div class="receipt-row">
                <span>Subtotal:</span>
                <span>KES {{ formatPrice(orderSubtotal) }}</span>
              </div>
              <div class="receipt-row">
                <span>Shipping Cost:</span>
                <span>KES {{ formatPrice(selectedOrder.shipping_cost || 0) }}</span>
              </div>
              <div class="receipt-row">
                <span>Total:</span>
                <span class="total-amount">KES {{ formatPrice(selectedOrder.total_price) }}</span>
              </div>
            </div>

            <div class="receipt-footer">
              <div class="receipt-actions">
                <button @click="printReceipt" class="print-button">Print Receipt</button>
                <button @click="closeOrderDetails" class="close-button">Close</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/modules/auth';
import { useOrdersStore } from '@/stores/modules/orders';
import MainLayout from '@/components/navigation/MainLayout.vue';
import { useRouter } from 'vue-router';
import { toast } from 'vue3-toastify';
import logo from '../assets/images/mustard-imports.png';

const authStore = useAuthStore();
const ordersStore = useOrdersStore();
const router = useRouter();

// Expose store for template
const store = ordersStore;

const dateFilter = ref('last1month');
const statusFilter = ref('all');
const searchQuery = ref('');
const activeTab = ref('all');
const loading = ref(true);
const showModal = ref(false);
const modalLoading = ref(false);
const modalError = ref(null);
const selectedOrder = ref(null);
const selectedOrderId = ref(null);

const statusTabs = [
  { label: 'All', value: 'all' },
  { label: 'Pending MOQ', value: 'pending' },
  { label: 'Unpaid', value: 'unpaid' },
  { label: 'Paid', value: 'paid' },
  { label: 'Completed', value: 'completed' },
];

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
};

const formatPrice = (price) => (price != null ? (Math.round(price * 100) / 100).toFixed(2) : '0.00');

const formatAttributeKey = (key) => {
  return key
    .replace(/[_-]/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

const orderSubtotal = computed(() =>
  selectedOrder.value
    ? selectedOrder.value.items.reduce((sum, item) => sum + (item.line_total || 0), 0)
    : 0
);

const filteredOrders = computed(() => {
  let result = store.orders;
  const now = new Date();
  result = result.filter((order) => {
    const orderDate = new Date(order.created_at);
    if (dateFilter.value === 'last1month') {
      return orderDate >= new Date(now.setMonth(now.getMonth() - 1));
    } else if (dateFilter.value === 'last3months') {
      return orderDate >= new Date(now.setMonth(now.getMonth() - 3));
    } else if (dateFilter.value === 'last6months') {
      return orderDate >= new Date(now.setMonth(now.getMonth() - 6));
    } else if (dateFilter.value === 'lastyear') {
      return orderDate >= new Date(now.setFullYear(now.getFullYear() - 1));
    }
    return true;
  });

  if (activeTab.value !== 'all') {
    result = result.filter((order) => order.payment_status.toLowerCase() === activeTab.value);
  }

  if (statusFilter.value !== 'all') {
    result = result.filter((order) =>
      order.payment_status.toLowerCase().includes(statusFilter.value.toLowerCase())
    );
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().replace(/^mi/, '');
    result = result.filter((order) => order.order_number.toLowerCase().includes(query));
  }

  return result;
});

const fetchOrdersData = async () => {
  try {
    loading.value = true;
    await ordersStore.fetchOrders();
  } catch (error) {
    console.error('Error fetching orders:', error);
    toast.error(error.response?.data?.error || 'Failed to load orders.');
  } finally {
    loading.value = false;
  }
};

const fetchOrderDetails = async (orderId) => {
  try {
    modalLoading.value = true;
    modalError.value = null;
    selectedOrder.value = await ordersStore.fetchOrder(orderId);
  } catch (error) {
    console.error('Error fetching order details:', error);
    modalError.value = error.response?.data?.error || 'Failed to load order details.';
  } finally {
    modalLoading.value = false;
  }
};

const openOrderDetails = async (orderId) => {
  selectedOrderId.value = orderId;
  showModal.value = true;
  await fetchOrderDetails(orderId);
};

const closeOrderDetails = () => {
  showModal.value = false;
  selectedOrder.value = null;
  selectedOrderId.value = null;
  modalError.value = null;
};

const printReceipt = () => {
  const orderNumber = selectedOrder.value.order_number;
  const isPickAndPay = selectedOrder.value.items.every(item => item.product.is_pick_and_pay);
  const printWindow = window.open('', '_blank');
  printWindow.document.write(`
    <html>
      <head>
        <link href="${logo}" rel="icon">
        <title>Receipt ${orderNumber}</title>
        <style>
          body {
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 1rem;
            background: #f0f0f0;
          }
          .receipt {
            max-width: 21.875rem;
            margin: 0 auto;
            padding: 1rem;
            background: #fff;
            box-shadow: 0 0.125rem 0.625rem rgba(0, 0, 0, 0.1);
            position: relative;
            border-radius: 0.25rem;
          }
          .receipt::before,
          .receipt::after {
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            height: 0.625rem;
            background: repeating-linear-gradient(
              90deg,
              #fff 0px,
              #fff 0.3125rem,
              #ddd 0.3125rem,
              #ddd 0.625rem
            );
          }
          .receipt::before { top: -0.3125rem; }
          .receipt::after { bottom: -0.3125rem; }
          .receipt-header {
            text-align: center;
            margin-bottom: 1rem;
            border-bottom: 0.125rem dashed #ccc;
            padding-bottom: 0.75rem;
          }
          .receipt-header img {
            max-width: 7.5rem;
            height: auto;
            margin-bottom: 0.625rem;
          }
          .receipt-header h2 {
            font-size: 1rem;
            margin: 0;
            color: #333;
          }
          .receipt-date {
            font-size: 0.75rem;
            color: #666;
            margin-top: 0.3125rem;
          }
          .receipt-section {
            margin-bottom: 1rem;
          }
          .receipt-section h3 {
            font-size: 0.875rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.625rem;
            border-left: 0.1875rem solid #D4A017;
            padding-left: 0.5rem;
          }
          .receipt-row,
          .item-details {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: #333;
            padding: 0.3125rem 0;
          }
          .receipt-item {
            border-bottom: 0.0625rem dashed #ddd;
            padding: 0.5rem 0;
          }
          .receipt-section p,
          .location-info {
            font-size: 0.75rem;
            color: #666;
            line-height: 1.5;
          }
          .item-attributes,
          .attribute {
            font-size: 0.75rem;
            color: #666;
            margin: 0.25rem 0;
          }
          .product-type-badge {
            padding: 0.125rem 0.5rem;
            border-radius: 0.75rem;
            font-size: 0.6875rem;
            margin-left: 0.5rem;
          }
          .product-type-badge.moq {
            background-color: #e3f2fd;
            color: #2196f3;
          }
          .product-type-badge.pay-pick {
            background-color: #fff8e1;
            color: #ffa000;
          }
          .receipt-footer {
            border-top: 0.125rem dashed #ccc;
            padding-top: 0.75rem;
            margin-top: 1rem;
            text-align: center;
          }
          .barcode {
            width: 100%;
            height: 2.5rem;
            background: repeating-linear-gradient(
              90deg,
              #000 0px,
              #000 0.1875rem,
              #fff 0.1875rem,
              #fff 0.375rem
            );
            margin-top: 0.75rem;
          }
          @media (max-width: 650px) {
            body { padding: 0.5rem; }
            .receipt { padding: 0.75rem; }
            .receipt-header h2 { font-size: 0.875rem; }
            .receipt-date { font-size: 0.6875rem; }
            .receipt-section h3 { font-size: 0.8125rem; }
            .receipt-row,
            .item-details,
            .receipt-section p,
            .location-info,
            .item-attributes,
            .attribute { font-size: 0.6875rem; }
            .product-type-badge { font-size: 0.625rem; }
          }
        </style>
      </head>
      <body>
        <div class="receipt">
          <div class="receipt-header">
            <img src="${logo}" alt="Mustard Imports Logo" />
            <h2>Receipt ${orderNumber}</h2>
            <p class="receipt-date">Placed on: ${formatDate(selectedOrder.value.created_at)}</p>
          </div>
          <div class="receipt-section">
            <h3>Order Summary</h3>
            <div class="receipt-row">
              <span>Payment Status:</span>
              <span>${selectedOrder.value.payment_status}</span>
            </div>
            <div class="receipt-row">
              <span>Delivery Status:</span>
              <span>${selectedOrder.value.delivery_status}</span>
            </div>
          </div>
          <div class="receipt-section">
            <h3>Items Purchased</h3>
            ${selectedOrder.value.items
              .map(
                (item) => `
              <div class="receipt-item">
                <div class="item-details">
                  <span>${item.product_name}
                    <span class="product-type-badge ${item.product.moq_status === 'active' ? 'moq' : 'pay-pick'}">
                      ${item.product.moq_status === 'active' ? 'MOQ' : 'Pay & Pick'}
                    </span>
                  </span>
                  <span>Qty: ${item.quantity}</span>
                  <span>KES ${formatPrice(item.price)}</span>
                  ${
                    item.product.moq_status === 'active' && item.product.moq
                      ? `<span>MOQ: ${item.product.moq} units${
                          item.product.moq_progress
                            ? ` (Progress: ${item.product.moq_progress.percentage}%)`
                            : ''
                        }</span>`
                      : ''
                  }
                  ${
                    item.attributes && Object.keys(item.attributes).length
                      ? `<div class="item-attributes">${Object.entries(item.attributes)
                          .map(
                            ([key, value]) =>
                              `<p class="attribute">${formatAttributeKey(key)}: ${value}</p>`
                          )
                          .join('')}</div>`
                      : ''
                  }
                </div>
                <span>KES ${formatPrice(item.line_total)}</span>
              </div>`
              )
              .join('')}
          </div>
          <div class="receipt-section">
            <h3>Shipping Information</h3>
            ${
              isPickAndPay
                ? selectedOrder.value.delivery_location?.is_shop_pickup
                  ? `<p class="location-info">Pickup Location: Mustard Imports Store</p>`
                  : selectedOrder.value.delivery_location?.county ||
                    selectedOrder.value.delivery_location?.ward
                  ? `<p class="location-info">
                      ${selectedOrder.value.delivery_location.county ? `County: ${selectedOrder.value.delivery_location.county}` : ''}
                      ${
                        selectedOrder.value.delivery_location.county &&
                        selectedOrder.value.delivery_location.ward
                          ? '<br>'
                          : ''
                      }
                      ${selectedOrder.value.delivery_location.ward ? `Ward: ${selectedOrder.value.delivery_location.ward}` : ''}
                    </p>`
                  : `<p class="location-info">No delivery location specified.</p>`
                : selectedOrder.value.delivery_location?.county ||
                  selectedOrder.value.delivery_location?.ward
                ? `<p class="location-info">
                    ${selectedOrder.value.delivery_location.county ? `County: ${selectedOrder.value.delivery_location.county}` : ''}
                    ${
                      selectedOrder.value.delivery_location.county &&
                      selectedOrder.value.delivery_location.ward
                        ? '<br>'
                        : ''
                    }
                    ${selectedOrder.value.delivery_location.ward ? `Ward: ${selectedOrder.value.delivery_location.ward}` : ''}
                  </p>`
                : `<p class="location-info">No delivery location specified.</p>`
            }
            <p>Shipping Method: ${selectedOrder.value.shipping_method?.name || 'Not applicable'}</p>
            <p>Shipping Cost: KES ${formatPrice(selectedOrder.value.shipping_cost || 0)}</p>
          </div>
          <div class="receipt-section">
            <h3>Order Totals</h3>
            <div class="receipt-row">
              <span>Subtotal:</span>
              <span>KES ${formatPrice(orderSubtotal.value)}</span>
            </div>
            <div class="receipt-row">
              <span>Shipping Cost:</span>
              <span>KES ${formatPrice(selectedOrder.value.shipping_cost || 0)}</span>
            </div>
            <div class="receipt-row">
              <span>Total:</span>
              <span>KES ${formatPrice(selectedOrder.value.total_price)}</span>
            </div>
          </div>
          <div class="receipt-footer">
            <div class="barcode"></div>
          </div>
        </div>
      </body>
    </html>
  `);
  printWindow.document.close();
  printWindow.print();
};

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  try {
    await fetchOrdersData();
  } catch (error) {
    console.error('Initialization error:', error);
    toast.error('Failed to initialize data.');
  }
});
</script>

<style scoped>
.orders-container {
  max-width: 75rem;
  margin: 0 auto;
  padding: 1.875rem 1.25rem;
  font-family: 'Roboto', Arial, sans-serif;
}

.breadcrumb {
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
}

.breadcrumb a {
  text-decoration: none;
  color: #D4A017;
  transition: color 0.2s ease;
}

.breadcrumb a:hover {
  text-decoration: underline;
  color: #e67e22;
}

.page-title {
  font-size: 1.75rem;
  margin-bottom: 1rem;
}

.order-count {
  font-size: 0.75rem;
  color: #7f8c8d;
  font-weight: 500;
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  padding: 1rem;
  border-radius: 0.625rem;
  box-shadow: 0 0.125rem 0.5rem rgba(0, 0, 0, 0.08);
}

.filter-group {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.filter-group label {
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.select-wrapper {
  position: relative;
}

.filter-select {
  width: 100%;
  padding: 0.625rem;
  border: 0.0625rem solid #ddd;
  border-radius: 0.375rem;
  appearance: none;
  font-size: 0.875rem;
  color: #333;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.filter-select:focus {
  border-color: #34495e;
  box-shadow: 0 0 0 0.125rem rgba(242, 140, 56, 0.2);
  outline: none;
}

.select-wrapper::after {
  content: '▼';
  font-size: 0.75rem;
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #7f8c8d;
}

.search-group {
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 0.625rem 0.9375rem;
  border: 0.0625rem solid #ddd;
  border-radius: 1.5625rem;
  outline: none;
  font-size: 0.875rem;
  transition: border-color 0.3s, box-shadow 0.3s;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23666' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z'%3E%3C/path%3E%3C/svg%3E") no-repeat 0.9375rem center;
  padding-left: 2.5rem;
}

.search-input:focus {
  border-color: #D4A017;
  box-shadow: 0 0 0 0.125rem rgba(242, 140, 56, 0.2);
}

.status-tabs {
  display: flex;
  margin-bottom: 1.25rem;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  gap: 0.5rem;
  padding-bottom: 0.3125rem;
}

.status-tabs::-webkit-scrollbar {
  display: none;
}

.tab-button {
  padding: 0.625rem 1rem;
  background: none;
  border: none;
  border-bottom: 0.1875rem solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: #7f8c8d;
  white-space: nowrap;
  transition: all 0.3s ease;
  font-size: 0.875rem;
}

.tab-button:hover {
  color: #D4A017;
}

.tab-button.active {
  color: #D4A017;
  border-bottom-color: #D4A017;
}

.no-orders {
  padding: 2rem;
  text-align: center;
  border-radius: 0.625rem;
  color: #7f8c8d;
  box-shadow: 0 0.125rem 0.5rem rgba(0, 0, 0, 0.08);
  font-weight: 500;
  font-size: 0.875rem;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.order-item {
  border-radius: 0.625rem;
  overflow: hidden;
  box-shadow: 0 0.1875rem 0.625rem rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.order-item:hover {
  transform: translateY(-0.0625rem);
  box-shadow: 0 0.375rem 0.9375rem rgba(0, 0, 0, 0.15);
}

.order-header {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.order-info {
  display: grid;
  gap: 0.5rem;
}

.order-number {
  font-size: 0.9375rem;
  font-weight: 600;
}

.order-placed,
.order-items-count,
.order-total {
  font-size: 0.8125rem;
}

.order-actions {
  align-self: stretch;
}

.view-details-btn {
  width: 100%;
  padding: 0.5rem 0.9375rem;
  cursor: pointer;
  color: #D4A017;
  font-weight: 500;
  text-decoration: none;
  border-radius: 0.375rem;
  background: none;
  border: none;
  transition: all 0.3s ease;
  font-size: 0.875rem;
  min-height: 2.75rem;
}

.view-details-btn:hover {
  background-color: rgba(242, 140, 56, 0.1);
  transform: translateY(-0.125rem);
}

.order-status-badge {
  display: inline-block;
  padding: 0.3125rem 0.75rem;
  border-radius: 1.25rem;
  font-size: 0.8125rem;
  font-weight: 500;
  margin: 0 1rem 1rem;
}

.order-status-badge.pending {
  background-color: #fff8e1;
  color: #ffa000;
}

.order-status-badge.paid {
  background-color: #e8f5e9;
  color: #4caf50;
}

.order-status-badge.processing {
  background-color: #e3f2fd;
  color: #2196f3;
}

.order-status-badge.completed {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.order-status-badge.unpaid {
  background-color: #fff3e0;
  color: #ff9800;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: #fff;
  border-radius: 1rem;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 0.625rem 1.875rem rgba(0, 0, 0, 0.2);
  position: relative;
  animation: slideIn 0.3s ease;
  padding: 1rem;
}

.modal-loading,
.modal-error {
  padding: 1.25rem;
  text-align: center;
}

.modal-error {
  color: #e74c3c;
  font-size: 0.875rem;
}

.retry-button {
  margin-top: 0.75rem;
  padding: 0.5rem 1.25rem;
  background-color: #D4A017;
  color: #fff;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 0.875rem;
  min-height: 2.75rem;
}

.retry-button:hover {
  background-color: #e67e22;
}

.modal-receipt {
  font-family: 'Courier New', monospace;
  background: #f9f9f9;
  border: 0.0625rem solid #e0e0e0;
  border-radius: 0.75rem;
  padding: 1rem;
  box-shadow: inset 0 0 0.625rem rgba(0, 0, 0, 0.05);
}

.receipt-header {
  text-align: center;
  border-bottom: 0.125rem dashed #ccc;
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
}

.receipt-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.receipt-date {
  font-size: 0.8125rem;
  color: #666;
  margin-top: 0.3125rem;
}

.receipt-section {
  margin-bottom: 1rem;
}

.receipt-section h3 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #D4A017;
  margin-bottom: 0.75rem;
  border-left: 0.1875rem solid #D4A017;
  padding-left: 0.625rem;
}

.receipt-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  font-size: 0.8125rem;
  color: #333;
}

.receipt-row span {
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.625rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.pending {
  background-color: #fff8e1;
  color: #ffa000;
}

.status-badge.paid {
  background-color: #e8f5e9;
  color: #4caf50;
}

.status-badge.processing {
  background-color: #e3f2fd;
  color: #2196f3;
}

.status-badge.completed {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-badge.unpaid {
  background-color: #fff3e0;
  color: #ff9800;
}

.receipt-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 0.0625rem dashed #ddd;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-name {
  font-weight: 600;
  font-size: 0.8125rem;
  color: #333;
}

.item-quantity,
.item-price,
.item-moq {
  font-size: 0.75rem;
  color: #666;
}

.item-line-total {
  font-weight: 600;
  font-size: 0.8125rem;
  color: #333;
}

.info-label {
  font-weight: 600;
  color: #333;
}

.receipt-section p {
  font-size: 0.8125rem;
  color: #666;
  line-height: 1.6;
}

.receipt-footer {
  border-top: 0.125rem dashed #ccc;
  padding-top: 0.75rem;
  margin-top: 1rem;
  display: flex;
  justify-content: center;
}

.receipt-actions {
  display: flex;
  gap: 0.625rem;
  flex-wrap: wrap;
  justify-content: center;
}

.print-button,
.close-button {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  min-height: 2.75rem;
}

.print-button {
  background-color: #D4A017;
  color: #fff;
}

.print-button:hover {
  background-color: #e67e22;
}

.close-button {
  background-color: #e0e0e0;
  color: #333;
}

.close-button:hover {
  background-color: #d0d0d0;
}

.modal-content::-webkit-scrollbar {
  width: 0;
}

.skeleton-section {
  margin-bottom: 1.25rem;
}

.skeleton-text {
  background: #e0e0e0;
  height: 0.875rem;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
  position: relative;
  overflow: hidden;
}

.skeleton-text::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.5), transparent);
  animation: shimmer 1.8s infinite;
}

.skeleton-title {
  width: 60%;
  height: 1.25rem;
  margin-bottom: 0.75rem;
}

.skeleton-item {
  padding: 0.75rem 0;
  border-bottom: 0.0625rem dashed #ddd;
}

.skeleton-item:last-child {
  border-bottom: none;
}

.skeleton-item-name {
  width: 70%;
}

.skeleton-item-price {
  width: 40%;
}

.skeleton-info {
  width: 80%;
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
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
  animation: shimmer 1.8s infinite;
}

.skeleton-order-number {
  width: 7.5rem;
}

.skeleton-order-placed {
  width: 10rem;
}

.skeleton-order-items {
  width: 8.75rem;
}

.skeleton-order-total {
  width: 6.25rem;
}

.skeleton-button {
  width: 100%;
  height: 2rem;
  background: #e0e0e0;
  border-radius: 0.375rem;
}

.skeleton-badge {
  width: 5rem;
  height: 1.5rem;
  background: #e0e0e0;
  border-radius: 1.25rem;
  margin: 0.75rem;
}

.product-type-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

.product-type-badge.moq {
  background-color: #e3f2fd;
  color: #2196f3;
}

.product-type-badge.pay-pick {
  background-color: #fff8e1;
  color: #ffa000;
}

.location-info {
  font-size: 0.8125rem;
  color: #666;
  line-height: 1.6;
}

.item-attributes {
  margin-top: 0.25rem;
}

.attribute {
  font-size: 0.75rem;
  color: #666;
  margin: 0.125rem 0;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(1.25rem); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@media (max-width: 765px) {
  .orders-container {
    padding: 1rem;
  }
  .page-title {
    font-size: 1.5rem;
  }
  .filter-container {
    padding: 0.75rem;
  }
  .filter-group {
    width: 100%;
  }
  .filter-select,
  .search-input {
    font-size: 0.8125rem;
    padding: 0.5rem;
  }
  .search-input {
    padding-left: 2rem;
    background-position: 0.625rem center;
  }
  .tab-button {
    padding: 0.5rem 0.75rem;
    font-size: 0.8125rem;
  }
  .order-item {
    padding: 0.75rem;
  }
  .order-number {
    font-size: 0.875rem;
  }
  .order-placed,
  .order-items-count,
  .order-total {
    font-size: 0.75rem;
  }
  .view-details-btn {
    font-size: 0.8125rem;
    padding: 0.375rem 0.75rem;
  }
  .order-status-badge {
    font-size: 0.75rem;
    margin: 0 0.75rem 0.75rem;
  }
  .modal-content {
    width: 98%;
    padding: 0.75rem;
  }
  .modal-receipt {
    padding: 0.75rem;
  }
  .receipt-header h2 {
    font-size: 1.125rem;
  }
  .receipt-date {
    font-size: 0.75rem;
  }
  .receipt-section h3 {
    font-size: 0.875rem;
  }
  .receipt-row,
  .item-name,
  .item-line-total,
  .receipt-section p {
    font-size: 0.75rem;
  }
  .item-quantity,
  .item-price,
  .item-moq {
    font-size: 0.6875rem;
  }
  .status-badge {
    font-size: 0.6875rem;
  }
  .print-button,
  .close-button {
    font-size: 0.8125rem;
    padding: 0.375rem 0.75rem;
  }
  .skeleton-text {
    height: 0.75rem;
  }
  .skeleton-title {
    height: 1rem;
  }
  .skeleton-button {
    height: 1.75rem;
  }
  .skeleton-badge {
    width: 4rem;
    height: 1.25rem;
  }
  .product-type-badge {
    font-size: 0.6875rem;
    padding: 0.1rem 0.4rem;
  }
  .location-info,
  .attribute {
    font-size: 0.75rem;
  }
}

@media (max-width: 650px) {
  .orders-container {
    padding: 0.75rem;
  }
  .page-title {
    font-size: 1.25rem;
  }
  .order-count {
    font-size: 0.6875rem;
  }
  .breadcrumb {
    font-size: 0.75rem;
  }
  .filter-container {
    gap: 0.5rem;
    padding: 0.5rem;
  }
  .filter-group label {
    font-size: 0.8125rem;
  }
  .filter-select,
  .search-input {
    font-size: 0.75rem;
    padding: 0.375rem;
  }
  .search-input {
    padding-left: 1.75rem;
    background-size: 0.875rem;
    background-position: 0.5rem center;
  }
  .select-wrapper::after {
    font-size: 0.625rem;
    right: 0.5rem;
  }
  .tab-button {
    padding: 0.375rem 0.625rem;
    font-size: 0.75rem;
  }
  .no-orders {
    padding: 1.25rem;
    font-size: 0.8125rem;
  }
  .order-item {
    padding: 0.5rem;
  }
  .order-header {
    padding: 0.5rem;
    gap: 0.5rem;
  }
  .order-number {
    font-size: 0.8125rem;
  }
  .order-placed,
  .order-items-count,
  .order-total {
    font-size: 0.6875rem;
  }
  .view-details-btn {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
  .order-status-badge {
    font-size: 0.6875rem;
    padding: 0.25rem 0.5rem;
    margin: 0 0.5rem 0.5rem;
  }
  .modal-content {
    width: 100%;
    border-radius: 0.5rem;
    padding: 0.5rem;
  }
  .modal-receipt {
    padding: 0.5rem;
  }
  .receipt-header h2 {
    font-size: 1rem;
  }
  .receipt-date {
    font-size: 0.6875rem;
  }
  .receipt-section {
    margin-bottom: 0.75rem;
  }
  .receipt-section h3 {
    font-size: 0.8125rem;
    padding-left: 0.5rem;
  }
  .receipt-row {
    padding: 0.375rem 0;
  }
  .receipt-row,
  .item-name,
  .item-line-total,
  .receipt-section p {
    font-size: 0.6875rem;
  }
  .item-quantity,
  .item-price,
  .item-moq {
    font-size: 0.625rem;
  }
  .status-badge {
    font-size: 0.625rem;
    padding: 0.1875rem 0.5rem;
  }
  .receipt-item {
    padding: 0.375rem 0;
  }
  .receipt-footer {
    padding-top: 0.5rem;
    margin-top: 0.75rem;
  }
  .receipt-actions {
    gap: 0.5rem;
  }
  .print-button,
  .close-button {
    font-size: 0.75rem;
    padding: 0.25rem 0.625rem;
    min-height: 2.25rem;
  }
  .modal-loading,
  .modal-error {
    padding: 0.75rem;
  }
  .modal-error {
    font-size: 0.8125rem;
  }
  .retry-button {
    font-size: 0.75rem;
    padding: 0.25rem 0.625rem;
  }
  .skeleton-text {
    height: 0.625rem;
  }
  .skeleton-title {
    height: 0.875rem;
  }
  .skeleton-item {
    padding: 0.5rem 0;
  }
  .skeleton-button {
    height: 1.5rem;
  }
  .skeleton-badge {
    width: 3.5rem;
    height: 1rem;
  }
  .product-type-badge {
    font-size: 0.625rem;
    padding: 0.075rem 0.3rem;
  }
  .location-info,
  .attribute {
    font-size: 0.6875rem;
  }
}
</style>
