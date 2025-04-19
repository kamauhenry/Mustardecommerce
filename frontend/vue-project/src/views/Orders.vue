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
              <router-link :to="{ name: 'OrderDetails', params: { orderId: order.id } }" class="view-details-btn">
                View Details
              </router-link>
            </div>
          </div>
          <div class="order-status-badge" :class="order.payment_status.toLowerCase()">
            {{ order.payment_status }}
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

const store = useEcommerceStore();
const router = useRouter();

const dateFilter = ref('last1month');
const statusFilter = ref('all');
const searchQuery = ref('');
const activeTab = ref('all');
const loading = ref(true);

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
</script>

<style scoped>
/* Existing styles remain unchanged, only adding skeleton styles */
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

.skeleton-order-number {
  width: 100px;
}

.skeleton-order-placed {
  width: 150px;
}

.skeleton-order-items {
  width: 120px;
}

.skeleton-order-total {
  width: 80px;
}

.skeleton-button {
  width: 100px;
  height: 30px;
  background: #e0e0e0;
  border-radius: 4px;
}

.skeleton-badge {
  width: 80px;
  height: 24px;
  background: #e0e0e0;
  border-radius: 20px;
  margin: 15px;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* Existing styles */
.orders-container {
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

.filter-container {
  display: flex;
  align-items: flex-end;
  justify-content: flex-start;
  gap: 1rem;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 14px;
  margin-bottom: 5px;
}

.select-wrapper {
  position: relative;
}

.filter-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
  appearance: none;
}

.select-wrapper::after {
  content: '▼';
  font-size: 12px;
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.search-group {
  display: flex;
  border-radius: 100px;
  width: 80%;
}

.search-input {
  flex: 1;
  border: none;
  padding: 0.8rem;
  border-radius: 25px;
  outline: none;
}

.status-tabs {
  display: flex;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-button {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  white-space: nowrap;
}

.tab-button.active {
  color: #ff9800;
  border-bottom-color: #ff9800;
}

.no-orders {
  padding: 40px;
  text-align: center;
  border-radius: 8px;
  color: #666;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-item {
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.order-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.order-info {
  display: grid;
  gap: 5px;
}

.order-number,
.order-placed,
.order-items-count,
.order-total {
  font-size: 14px;
}

.view-details-btn {
  padding: 6px 12px;
  cursor: pointer;
  color: #ff9800;
  display: inline-block;
  text-decoration: none;
}

.view-details-btn:hover {
  transform: translateY(-1px);
}

.view-details-btn::after {
  content: '';
  width: 0px;
  height: 1px;
  display: block;
  background: rgb(236, 132, 34);
  transition: 300ms;
}

.view-details-btn:hover::after {
  width: 100%;
}

.order-status-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  margin: 0 15px 15px;
}

.order-status-badge.pending {
  background-color: #ffb84d9a;
  color: #ffb74d;
}

.order-status-badge.paid {
  color: #4caf50;
  background-color: #4caf4f54;
}

.order-status-badge.cancelled {
  color: #f44336;
  background-color: #f4433654;
}

.order-status-badge.processing {
  color: #2196f3;
  background-color: #2195f350;
}

.order-status-badge.completed {
  color: #8bc34a;
  background-color: #8bc34a49;
}

.order-status-badge.unpaid {
  color: #ff9800;
  background-color: #ff990052;
}

@media (max-width: 768px) {
  .filter-container {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .filter-group {
    width: 35%;
  }

  .search-group {
    width: 100%;
  }

  .order-header {
    flex-direction: column;
  }

  .order-actions {
    margin-top: 10px;
    align-self: flex-end;
  }
}
</style>