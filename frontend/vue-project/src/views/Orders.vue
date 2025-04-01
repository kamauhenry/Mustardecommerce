<template>
  <MainLayout>
    <div class="orders-container">
      <div class="breadcrumb">
        <a href="/">Home</a> &gt; <a href="/account">Account Home</a> &gt; <span>Orders</span>
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

      <div v-if="filteredOrders.length === 0" class="no-orders">
        No orders matching your current filters.
      </div>

      <div v-else class="orders-list">
        <div
          v-for="order in filteredOrders"
          :key="order.id"
          class="order-item"
        >
          <div class="order-header">
            <div class="order-info">
              <div class="order-number">Order #: {{ order.id }}</div>
              <div class="order-placed">Placed on: {{ order.date }}</div>
              <div class="order-items-count">Included Items: {{ order.items }}</div>
              <div class="order-total">Total: ${{ order.total }}</div>
            </div>

            <div class="order-actions">
              <a href="" class="view-details-btn">View Details</a>
            </div>
          </div>

          <div class="order-status-badge" :class="order.status.toLowerCase()">
            {{ order.status }}
          </div>

          <div class="order-notes">
            <div class="notes-label">Order Notes:</div>
            <div class="notes-content">{{ order.notes }}</div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEcommerceStore } from '@/stores/ecommerce'
import MainLayout from '@/components/navigation/MainLayout.vue'

const store = useEcommerceStore()

const dateFilter = ref('last1month')
const statusFilter = ref('all')
const searchQuery = ref('')
const activeTab = ref('all')

const statusTabs = [
  { label: 'All', value: 'all' },
  { label: 'Pending MOQ', value: 'pending' },
  { label: 'Unpaid', value: 'unpaid' },
  { label: 'Paid', value: 'paid' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
]

// Sample data based on screenshots
const sampleOrders = [
  {
    id: '1290855',
    date: 'March 19, 2024',
    items: '1',
    total: '14.55',
    status: 'Unpaid',
    notes: 'Lorem ipsum dolor sit amet consectetur. Tincidunt ornare morbi nulla ornare diam malesuada at enim vitae. Amet scelerisque rutrum arcu quis mauris molestie tellus adipiscing pulvinar.'
  },
  {
    id: '1290855',
    date: 'March 19, 2024',
    items: '2',
    total: '14.55',
    status: 'Paid',
    notes: 'Lorem ipsum dolor sit amet consectetur. Tincidunt ornare morbi nulla ornare diam malesuada at enim vitae. Amet scelerisque rutrum arcu quis mauris molestie tellus adipiscing pulvinar.'
  },
  {
    id: '1290855',
    date: 'March 19, 2024',
    items: '2',
    total: '14.55',
    status: 'Cancelled',
    notes: 'Lorem ipsum dolor sit amet consectetur. Tincidunt ornare morbi nulla ornare diam malesuada at enim vitae. Amet scelerisque rutrum arcu quis mauris molestie tellus adipiscing pulvinar.'
  },
  {
    id: '09345657',
    date: 'March 19, 2024',
    items: '2',
    total: '29.10',
    status: 'Pending MOQ',
    notes: 'Lorem ipsum dolor sit amet consectetur. Tincidunt ornare morbi nulla ornare diam malesuada at enim vitae. Amet scelerisque rutrum arcu quis mauris molestie tellus adipiscing pulvinar.'
  },
  {
    id: '09345657',
    date: 'March 19, 2024',
    items: '2',
    total: '29.10',
    status: 'Completed',
    notes: 'Lorem ipsum dolor sit amet consectetur. Tincidunt ornare morbi nulla ornare diam malesuada at enim vitae. Amet scelerisque rutrum arcu quis mauris molestie tellus adipiscing pulvinar.'
  }
]

// Initialize store with sample data
onMounted(() => {
  store.orders = sampleOrders
})

const filteredOrders = computed(() => {
  let result = store.orders

  // Filter by status tab
  if (activeTab.value !== 'all') {
    result = result.filter(order => {
      if (activeTab.value === 'pending') return order.status.toLowerCase().includes('pending')
      if (activeTab.value === 'unpaid') return order.status.toLowerCase().includes('unpaid')
      if (activeTab.value === 'paid') return order.status.toLowerCase().includes('paid')
      if (activeTab.value === 'completed') return order.status.toLowerCase().includes('completed')
      if (activeTab.value === 'cancelled') return order.status.toLowerCase().includes('cancelled')
      if (activeTab.value === 'submitted') return order.status.toLowerCase().includes('submitted')
      if (activeTab.value === 'paid') return order.status.toLowerCase().includes('paid')
      return true
    })
  }

  // Filter by status dropdown
  if (statusFilter.value !== 'all') {
    result = result.filter(order =>
      order.status.toLowerCase().includes(statusFilter.value.toLowerCase())
    )
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(order =>
      order.id.toLowerCase().includes(query) ||
      order.notes.toLowerCase().includes(query)
    )
  }

  return result
})
</script>

<style scoped>
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

/* .page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
} */

.order-count {
  font-size: 18px;
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
  /* width: 180px; */
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
  padding: .8rem;
  border-radius: 25px;
  outline: none;
}

.search-button {
  border-left: none;
  border-radius: 0 4px 4px 0;
  padding: 0 12px;
  cursor: pointer;
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

.order-number, .order-placed, .order-items-count, .order-total {
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

.view-details-btn::after{
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
  margin: 0 15px;
}

.order-status-badge.submitted {
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

.order-status-badge.pending {
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

.order-status-badge.paid {
  color: #9c27b0;
  background-color: #9b27b04f;
}

.order-notes {
  padding: 15px;
}

.notes-label {
  font-weight: bold;
  margin-bottom: 5px;
  font-size: 14px;
}

.notes-content {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
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
