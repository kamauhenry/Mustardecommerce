<template>
  <AdminLayout>
    <div class="dashboard">
      <h2>Admin Dashboard</h2>

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
        <!-- Summary Cards -->
        <div class="summary-cards">
          <div class="card">
            <h3>Total Sales</h3>
            <p>{{ dashboardData.total_sales }}</p>
          </div>
          <div class="card">
            <h3>Total Revenue</h3>
            <p>KES{{ dashboardData.total_revenue?.toFixed(2) }}</p>
          </div>
          <div class="card">
            <h3>Total Customers</h3>
            <p>{{ dashboardData.total_customers }}</p>
          </div>
          <div class="card">
            <h3>Active Orders</h3>
            <p>{{ dashboardData.active_orders }}</p>
          </div>
        </div>

        <!-- Charts Section -->
        <div class="charts-section">
          <!-- Revenue Trend Chart -->
          <div class="chart-container">
            <h3>Revenue Trend (Last 6 Months)</h3>
            <Chart type="bar" :data="revenueChartData" :options="chartOptions" />
          </div>

          <!-- Top Products Chart -->
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
                <th>Customer</th>
                <th>Total (KES)</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in dashboardData.recent_orders" :key="order.id">
                <td>#{{ order.id }}</td>
                <td>{{ order.customer_name || 'N/A' }}</td>
                <td>{{ order.total?.toFixed(2) }}</td>
                <td>
                  <span :class="getStatusClass(order.status)">{{ order.status }}</span>
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

// Register Chart.js components
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

    // Fetch dashboard data
    const fetchDashboard = async () => {
      try {
        error.value = null;
        await store.fetchDashboardData();
      } catch (err) {
        error.value = err.message || 'Failed to load dashboard data. Please try again later.';
        console.error('Dashboard fetch error:', err);
      }
    };

    const retryFetchDashboard = async () => {
      await fetchDashboard();
    };

    onMounted(fetchDashboard);

    // Define dashboardData computed property
    const dashboardData = computed(() => store.dashboardData || {});

    // Chart data and options
    const revenueChartData = computed(() => ({
      labels: dashboardData.value.revenue_trend?.labels || [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
      ],
      datasets: [
        {
          label: 'Revenue (KES)',
          data: dashboardData.value.revenue_trend?.data || [12000, 19000, 3000, 5000, 20000, 30000],
          backgroundColor: '#6f42c1',
          borderColor: '#5a32a3',
          borderWidth: 1,
        },
      ],
    }));

    const topProductsChartData = computed(() => ({
      labels: dashboardData.value.top_products?.map((p) => p.name) || [
        'Product A',
        'Product B',
        'Product C',
        'Product D',
      ],
      datasets: [
        {
          label: 'Sales',
          data: dashboardData.value.top_products?.map((p) => p.sales) || [300, 200, 150, 100],
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
        legend: {
          position: 'top',
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.dataset.label || '';
              const value = context.parsed.y || context.parsed;
              return `${label}: KES${value.toLocaleString()}`;
            },
          },
        },
      },
    };

    // Helper to determine status class
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

    // View order details
    const viewOrder = (orderId) => {
      router.push(`/admin-page/orders/${orderId}`);
    };

    return {
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
/* AdminDashboard.vue Styles */
.dashboard {
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

h3 {
  font-size: 1.1rem;
  color: #374151;
  margin-bottom: 16px;
  font-weight: 600;
}

/* Loading Spinner */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: #6b7280;
  margin: 32px 0;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #6366f1;
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error Message */
.error-message {
  color: #ef4444;
  text-align: center;
  margin: 24px 0;
  font-size: 1rem;
  font-weight: 500;
  padding: 16px;
  border: 1px solid #fecaca;
  border-radius: 12px;
  background-color: #fee2e2;
}

.retry-button {
  margin-top: 12px;
  padding: 8px 20px;
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
  margin-left: 12px;
  transition: all 0.2s ease;
}

.retry-link:hover {
  color: #4f46e5;
  text-decoration: underline;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.card {
  padding: 24px;
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
  margin: 0 0 8px;
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

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

@media (max-width: 1024px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

.chart-container {
  background-color: #ffffff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}

.chart-container h3 {
  margin: 0 0 16px;
  font-size: 1rem;
  color: #374151;
  font-weight: 600;
}

.chart-container canvas {
  height: 300px !important;
}

/* Table Section */
.table-section {
  background-color: #ffffff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}

.table-section h3 {
  margin: 0 0 16px;
  font-size: 1rem;
  color: #374151;
  font-weight: 600;
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.data-table th,
.data-table td {
  padding: 14px 16px;
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
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-block;
}

.status-pending {
  color: #f59e0b;
  font-weight: 600;
  background-color: #fffbeb;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-block;
}

.status-cancelled {
  color: #ef4444;
  font-weight: 600;
  background-color: #fee2e2;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-block;
}

.action-btn {
  padding: 6px 14px;
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
</style>
