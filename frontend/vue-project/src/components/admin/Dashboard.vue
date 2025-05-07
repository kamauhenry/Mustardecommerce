<template>
  <AdminLayout>
    <div class="dashboard">
      <h2>Admin Dashboard</h2>

      <!-- Tabs -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Loading and Error States -->
      <div v-if="loading.dashboard" class="loading">
        <div class="spinner"></div>
        Loading dashboard data...
      </div>
      <div v-else-if="error" class="error-message">
        {{ error }}
        <br />
        <button @click="retryFetchDashboard" class="retry-button">Retry</button>
        <router-link to="/admin-page/login" class="retry-link">Log in as Admin</router-link>
      </div>

      <!-- Dashboard Content -->
      <div v-else class="dashboard-content">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="tab-content">
          <!-- Summary Cards -->
          <div class="summary-cards">
            <div class="card">
              <h3>Total Sales</h3>
              <p>{{ dashboardData.total_sales || 0 }}</p>
            </div>
            <div class="card">
              <h3>Total Revenue</h3>
              <p>KES{{ (dashboardData.total_revenue || 0).toFixed(2) }}</p>
            </div>
            <div class="card">
              <h3>Total Customers</h3>
              <p>{{ dashboardData.total_customers || 0 }}</p>
            </div>
            <div class="card">
              <h3>Active Orders</h3>
              <p>{{ dashboardData.active_orders || 0 }}</p>
            </div>
          </div>

          <!-- Charts Section -->
          <div class="charts-section">
            <div class="chart-container">
              <h3>Revenue Trend (Last 6 Months)</h3>
              <Chart type="bar" :data="revenueChartData" :options="chartOptions" />
            </div>
            <div class="chart-container">
              <h3>Top Products by Sales</h3>
              <Chart type="doughnut" :data="topProductsChartData" :options="chartOptions" />
            </div>
          </div>

          <!-- Recent Orders Table -->
          <div class="table-section">
            <h3>Recent Orders</h3>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer Email</th>
                  <th>Total (KES)</th>
                  <th>Payment Status</th>
                  <th>Delivery Status</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in dashboardData.recent_orders" :key="order.id">
                  <td>#{{ order.id }}</td>
                  <td>{{ order.user__email || 'N/A' }}</td>
                  <td>{{ order.total_price != null ? parseFloat(order.total_price).toFixed(2) : 'N/A' }}</td>
                  <td>
                    <span :class="getStatusClass(order.payment_status)">{{ order.payment_status || 'N/A' }}</span>
                  </td>
                  <td>
                    <span :class="getStatusClass(order.delivery_status)">{{ order.delivery_status || 'N/A' }}</span>
                  </td>
                  <td>{{ new Date(order.created_at).toLocaleDateString() }}</td>
                  <td>
                    <button class="action-btn view-btn" @click="viewOrder(order.id)">View</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Users Tab -->
        <div v-if="activeTab === 'users'" class="tab-content">
          <div class="table-section">
            <h3>User Leaderboard (Top Purchasers)</h3>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Total Products Purchased</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(user, index) in dashboardData.user_leaderboard" :key="user.id">
                  <td>{{ index + 1 }}</td>
                  <td>{{ user.username || 'N/A' }}</td>
                  <td>{{ user.email || 'N/A' }}</td>
                  <td>{{ user.total_purchases || 0 }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useRouter } from 'vue-router';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import { Chart } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement);

export default {
  name: 'AdminDashboard',
  components: {
    AdminLayout,
    Chart,
  },
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const error = ref(null);
    const loading = computed(() => store.loading);
    const activeTab = ref('overview');
    const tabs = [
      { id: 'overview', label: 'Overview' },
      { id: 'users', label: 'Users' },
    ];

    const fetchDashboard = async () => {
      try {
        error.value = null;
        await store.fetchDashboardData();
      } catch (err) {
        error.value = err.message || 'Failed to load dashboard data. Please try again later.';
        console.error('Dashboard fetch error:', {
          message: err.message,
          status: err.response?.status,
          data: err.response?.data,
        });
      }
    };

    const retryFetchDashboard = async () => {
      await fetchDashboard();
    };

    onMounted(fetchDashboard);

    const dashboardData = computed(() => store.dashboardData || {});

    const revenueChartData = computed(() => ({
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Revenue (KES)',
          data: dashboardData.value.revenue_trend?.current || [0, 0, 0, 0, 0, 0],
          backgroundColor: '#6f42c1',
          borderColor: '#5a32a3',
          borderWidth: 1,
        },
      ],
    }));

    const topProductsChartData = computed(() => ({
      labels: dashboardData.value.top_products?.map((p) => p.name) || [],
      datasets: [
        {
          label: 'Sales',
          data: dashboardData.value.top_products?.map((p) => p.moq_count) || [],
          backgroundColor: ['#6f42c1', '#00c4b4', '#f4c430', '#e74c3c'],
          borderColor: '#fff',
          borderWidth: 2,
        },
      ],
    }));

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: KES${context.parsed.y?.toLocaleString() || 0}`,
          },
        },
      },
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

    const viewOrder = (orderId) => {
      router.push(`/admin-page/orders/${orderId}`);
    };

    return {
      activeTab,
      tabs,
      dashboardData,
      error,
      loading,
      retryFetchDashboard,
      revenueChartData,
      topProductsChartData,
      chartOptions,
      getStatusClass,
      viewOrder,
    };
  },
};
</script>

<style scoped>
.dashboard {
  padding: 1.5rem;
  background-color: transparent;
  max-width: 1200px;
  margin: 0 auto;
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

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  overflow-x: auto;
  white-space: nowrap;
}

.tabs button {
  padding: 0.5rem 1rem;
  border: none;
  background: #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tabs button.active {
  background: #6f42c1;
  color: white;
}

.tabs button:hover:not(.active) {
  background: #e5e7eb;
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

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.card {
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  background-color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 1px solid #f3f4f6;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
}

.card h3 {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: #6b7280;
  font-weight: 500;
}

.card p {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: #6366f1;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-container {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}

.chart-container canvas {
  height: 250px !important;
}

.table-section {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
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

.action-btn {
  padding: 0.375rem 0.875rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.view-btn {
  background-color: #eff6ff;
  color: #3b82f6;
}

.view-btn:hover {
  background-color: #dbeafe;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }

  .tabs {
    flex-wrap: nowrap;
  }

  .tabs button {
    font-size: 0.85rem;
    padding: 0.4rem 0.8rem;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .chart-container canvas {
    height: 200px !important;
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

  .data-table th:nth-child(2),
  .data-table td:nth-child(2) {
    min-width: 150px;
  }
}

@media (max-width: 320px) {
  .dashboard {
    padding: 0.5rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  h3 {
    font-size: 1rem;
  }

  .tabs button {
    font-size: 0.8rem;
    padding: 0.3rem 0.6rem;
  }

  .card p {
    font-size: 1.5rem;
  }

  .action-btn {
    padding: 0.3rem 0.7rem;
    font-size: 0.8rem;
  }
}
</style>