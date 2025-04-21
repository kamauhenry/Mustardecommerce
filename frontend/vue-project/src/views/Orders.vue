<!-- eslint-disable vue/multi-word-component-names -->
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
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <div class="search-group">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search for orders...."
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
              <div class="order-number">Order : #MI{{ order.id }}</div>
              <div class="order-placed">Placed on: {{ formatDate(order.created_at) }}</div>
              <div class="order-items-count">Included Items: {{ order.items.length }}</div>
              <div class="order-total">Total: KES{{ order.total_price }}</div>
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
              <h2>Receipt #MI{{ selectedOrder.id }}</h2>
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
                  <p class="item-name">{{ item.product_name }}</p>
                  <p class="item-quantity">Qty: {{ item.quantity }}</p>
                  <p class="item-price">KES {{ item.price }}</p>
                </div>
                <p class="item-line-total">KES {{ item.line_total }}</p>
              </div>
            </div>

            <div class="receipt-section">
              <h3>Shipping Information</h3>
              <p v-if="selectedOrder.delivery_location">
                <span class="info-label">Address:</span> {{ selectedOrder.delivery_location.address }}<br />
                <span class="info-label">Name:</span> {{ selectedOrder.delivery_location.name }}
              </p>
              <p v-else>No delivery location specified.</p>
              <p><span class="info-label">Shipping Method:</span> {{ selectedOrder.shipping_method }}</p>
            </div>

            <div class="receipt-footer">
              <div class="receipt-total">
                <span>Total:</span>
                <span class="total-amount">KES {{ selectedOrder.total_price }}</span>
              </div>
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
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';
import { useRouter } from 'vue-router';
import logo from "../assets/images/mustard-imports.png";

const store = useEcommerceStore();
const router = useRouter();

const dateFilter = ref('last1month');
const statusFilter = ref('all');
const searchQuery = ref('');
const activeTab = ref('all');
const loading = ref(true);

// Modal state
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
  { label: 'Cancelled', value: 'cancelled' },
];

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
    await store.fetchOrdersData();
  } catch (error) {
    console.error('Error fetching orders:', error);
  } finally {
    loading.value = false;
  }
});

const filteredOrders = computed(() => {
  let result = store.orders;

  // Apply date filter
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
    return true; // 'all'
  });

  // Filter by status tab
  if (activeTab.value !== 'all') {
    result = result.filter((order) => order.payment_status.toLowerCase() === activeTab.value);
  }

  // Filter by status dropdown
  if (statusFilter.value !== 'all') {
    result = result.filter((order) =>
      order.payment_status.toLowerCase().includes(statusFilter.value.toLowerCase())
    );
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter((order) => order.id.toString().includes(query));
  }

  return result;
});

const openOrderDetails = async (orderId) => {
  selectedOrderId.value = orderId;
  showModal.value = true;
  modalLoading.value = true;
  modalError.value = null;
  await fetchOrderDetails(orderId);
};

const fetchOrderDetails = async (orderId) => {
  try {
    const response = await store.fetchOrder(orderId);
    selectedOrder.value = response;
  } catch (err) {
    modalError.value = 'Failed to load order details. Please try again.';
    console.error('Error fetching order details:', err);
  } finally {
    modalLoading.value = false;
  }
};

const closeOrderDetails = () => {
  showModal.value = false;
  selectedOrder.value = null;
  selectedOrderId.value = null;
  modalError.value = null;
};

const printReceipt = () => {
  const orderId = selectedOrder.value.id;

  const printWindow = window.open('', '_blank');
  printWindow.document.write(`
    <html>
      <head>
        <link href=${logo} rel="icon">
        <title>Receipt #MI${orderId}</title>
        <style>
          body {
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
          }
          .receipt {
            max-width: 350px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: relative;
            border-radius: 4px;
          }
          /* Perforated edge effect */
          .receipt::before,
          .receipt::after {
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            height: 10px;
            background: repeating-linear-gradient(
              90deg,
              #fff 0px,
              #fff 5px,
              #ddd 5px,
              #ddd 10px
            );
          }
          .receipt::before {
            top: -5px;
          }
          .receipt::after {
            bottom: -5px;
          }
          .receipt-header {
            text-align: center;
            margin-bottom: 20px;
            border-bottom: 2px dashed #ccc;
            padding-bottom: 15px;
          }
          .receipt-header img {
            max-width: 120px;
            height: auto;
            margin-bottom: 10px;
          }
          .receipt-header h2 {
            font-size: 18px;
            margin: 0;
            color: #333;
          }
          .receipt-date {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
          }
          .receipt-section {
            margin-bottom: 20px;
          }
          .receipt-section h3 {
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            border-left: 3px solid #f28c38;
            padding-left: 8px;
          }
          .receipt-row,
          .item-details {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #333;
            padding: 5px 0;
          }
          .receipt-item {
            border-bottom: 1px dashed #ddd;
            padding: 8px 0;
          }
          .receipt-section p {
            font-size: 12px;
            color: #666;
            line-height: 1.5;
          }
          .receipt-footer {
            border-top: 2px dashed #ccc;
            padding-top: 15px;
            margin-top: 20px;
            text-align: center;
          }
          .receipt-total {
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
          }
          .barcode {
            width: 100%;
            height: 40px;
            background: repeating-linear-gradient(
              90deg,
              #000 0px,
              #000 3px,
              #fff 3px,
              #fff 6px
            );
            margin-top: 15px;
          }
        </style>
      </head>
      <body>
        <div class="receipt">
          <div class="receipt-header">
            <img src=${logo} alt="Mustard Imports Logo" />
            <h2>Receipt #MI${orderId}</h2>
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
                  <span>${item.product_name}</span>
                  <span>Qty: ${item.quantity}</span>
                  <span>KES ${item.price}</span>
                </div>
                <span>KES ${item.line_total}</span>
              </div>`
              )
              .join('')}
          </div>
          <div class="receipt-section">
            <h3>Shipping Information</h3>
            <p>
              ${selectedOrder.value.delivery_location
                ? `Address: ${selectedOrder.value.delivery_location.address}<br />
                   Name: ${selectedOrder.value.delivery_location.name}`
                : 'No delivery location specified.'}
            </p>
            <p>Shipping Method: ${selectedOrder.value.shipping_method}</p>
          </div>
          <div class="receipt-footer">
            <div class="receipt-total">
              Total: KES ${selectedOrder.value.total_price}
            </div>
          </div>
        </div>
      </body>
    </html>
  `);
  printWindow.document.close();
  printWindow.print();
};
</script>

<style scoped>
.orders-container {
    margin: 0 auto;
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  font-family: 'Roboto', Arial, sans-serif;
}

.breadcrumb {
  margin-bottom: 20px;
  font-size: 14px;
}

.breadcrumb a {
  text-decoration: none;
  color: #f28c38;
  transition: color 0.2s ease;
}

.breadcrumb a:hover {
  text-decoration: underline;
  color: #e67e22;
}

.order-count {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 500;
}

.filter-container {
  display: flex;
  align-items: flex-end;
  justify-content: flex-start;
  gap: 1.5rem;
  margin-bottom: 25px;
  flex-wrap: wrap;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 180px;
}

.filter-group label {
  font-size: 14px;
  margin-bottom: 8px;
  font-weight: 500;
}

.select-wrapper {
  position: relative;
}

.filter-select {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid transparent;
  border-radius: 6px;
  border: 1px solid #ddd;
  appearance: none;
  font-size: 14px;
  color: #333;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.filter-select:focus {
  border-color: #34495e;
  box-shadow: 0 0 0 2px rgba(242, 140, 56, 0.2);
  outline: none;
}

.select-wrapper::after {
  content: '▼';
  font-size: 12px;
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #7f8c8d;
}

.search-group {
  flex-grow: 1;
  min-width: 250px;
  border: 1px solid transparent;
}

.search-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 25px;
  outline: none;
  font-size: 14px;
  transition: border-color 0.3s, box-shadow 0.3s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23666' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: 15px center;
  padding-left: 40px;
}

.search-input:focus {
  border-color: #f28c38;
  box-shadow: 0 0 0 2px rgba(242, 140, 56, 0.2);
}

.status-tabs {
  display: flex;
  margin-bottom: 25px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.status-tabs::-webkit-scrollbar {
  display: none;
}

.tab-button {
  padding: 12px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: #7f8c8d;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.tab-button:hover {
  color: #f28c38;
}

.tab-button.active {
  color: #f28c38;
  border-bottom-color: #f28c38;
}

.no-orders {
  padding: 50px;
  text-align: center;
  border-radius: 10px;
  color: #7f8c8d;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  font-weight: 500;
  font-size: 16px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-item {
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.order-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.order-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.order-info {
  display: grid;
  gap: 8px;
}

.order-number {
  font-size: 16px;
  font-weight: 600;
}

.order-placed,
.order-items-count,
.order-total {
  font-size: 14px;
}

.view-details-btn {
  padding: 8px 15px;
  cursor: pointer;
  color: #f28c38;
  font-weight: 500;
  display: inline-block;
  text-decoration: none;
  border-radius: 6px;
  background: none;
  border: none;
  transition: all 0.3s ease;
}

.view-details-btn:hover {
  background-color: rgba(242, 140, 56, 0.1);
  transform: translateY(-2px);
}

.order-status-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  margin: 0 20px 20px;
}

.order-status-badge.pending {
  background-color: #fff8e1;
  color: #ffa000;
}

.order-status-badge.paid {
  background-color: #e8f5e9;
  color: #4caf50;
}

.order-status-badge.cancelled {
  background-color: #ffebee;
  color: #f44336;
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

/* Modal Styles */
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
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  position: relative;
  animation: slideIn 0.3s ease;
}

.modal-loading,
.modal-error {
  padding: 30px;
  text-align: center;
}

.modal-error {
  color: #e74c3c;
  font-size: 16px;
}

.retry-button {
  margin-top: 15px;
  padding: 8px 20px;
  background-color: #f28c38;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.retry-button:hover {
  background-color: #e67e22;
}

/* Receipt Styles */
.modal-receipt {
  font-family: 'Courier New', monospace;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 25px;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
}

.receipt-header {
  text-align: center;
  border-bottom: 2px dashed #ccc;
  padding-bottom: 15px;
  margin-bottom: 20px;
}

.receipt-header h2 {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.receipt-date {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.receipt-section {
  margin-bottom: 25px;
}

.receipt-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #f28c38;
  margin-bottom: 15px;
  border-left: 3px solid #f28c38;
  padding-left: 10px;
}

.receipt-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  color: #333;
}

.receipt-row span {
  font-weight: 500;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
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

.status-badge.cancelled {
  background-color: #ffebee;
  color: #f44336;
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
  padding: 12px 0;
  border-bottom: 1px dashed #ddd;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.item-quantity,
.item-price {
  font-size: 13px;
  color: #666;
}

.item-line-total {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.info-label {
  font-weight: 600;
  color: #333;
}

.receipt-section p {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.receipt-footer {
  border-top: 2px dashed #ccc;
  padding-top: 15px;
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.receipt-total {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.total-amount {
  color: #f28c38;
}

.receipt-actions {
  display: flex;
  gap: 10px;
}

.print-button,
.close-button {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.print-button {
  background-color: #f28c38;
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
  width: 0px;
}
.modal-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.modal-content::-webkit-scrollbar-thumb {
  background: #f28c38;
  border-radius: 4px;
}

/* Skeleton Loader for Modal */
.skeleton-section {
  margin-bottom: 30px;
}

.skeleton-text {
  background: #e0e0e0;
  height: 16px;
  border-radius: 4px;
  margin-bottom: 12px;
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
  height: 24px;
  margin-bottom: 20px;
}

.skeleton-item {
  padding: 15px 0;
  border-bottom: 1px dashed #ddd;
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

/* Skeleton Loader for Orders List */
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
  width: 120px;
}

.skeleton-order-placed {
  width: 180px;
}

.skeleton-order-items {
  width: 140px;
}

.skeleton-order-total {
  width: 100px;
}

.skeleton-button {
  width: 120px;
  height: 35px;
  background: #e0e0e0;
  border-radius: 6px;
}

.skeleton-badge {
  width: 90px;
  height: 26px;
  background: #e0e0e0;
  border-radius: 20px;
  margin: 20px;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Responsive Design */
@media (max-width: 768px) {
  .orders-container {
    padding: 20px 15px;
  }

  .filter-container {
    padding: 15px;
  }

  .filter-group {
    width: calc(50% - 0.75rem);
    min-width: auto;
  }

  .search-group {
    width: 100%;
  }

  .order-header {
    flex-direction: column;
    gap: 15px;
  }

  .order-actions {
    align-self: flex-end;
  }

  .modal-content {
    width: 95%;
    max-height: 85vh;
  }

  .modal-receipt {
    padding: 20px;
  }

  .receipt-header h2 {
    font-size: 20px;
  }

  .receipt-section h3 {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }

  .order-count {
    font-size: 16px;
  }

  .filter-group {
    width: 100%;
  }

  .status-tabs {
    padding-bottom: 5px;
  }

  .tab-button {
    padding: 10px 15px;
    font-size: 13px;
  }

  .view-details-btn {
    padding: 6px 12px;
    font-size: 13px;
  }

  .modal-receipt {
    padding: 15px;
  }

  .receipt-row,
  .receipt-item {
    font-size: 13px;
  }

  .receipt-footer {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }

  .receipt-actions {
    justify-content: center;
  }
}
</style>
