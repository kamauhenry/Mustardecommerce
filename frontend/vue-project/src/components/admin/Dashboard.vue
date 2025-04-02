<template>
  <AdminLayout>
    <div class="dashboard">
      <h2>Dashboard</h2>
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="card">
          <h3>Total Sales</h3>
          <p>{{ dashboardData?.total_sales || 0 }}</p>
          <span class="trend up">↑ 14% in the last month</span>
        </div>
        <div class="card">
          <h3>Total Orders</h3>
          <p>{{ dashboardData?.total_sales || 0 }}</p>
          <span class="trend down">↓ 17% in the last month</span>
        </div>
        <div class="card">
          <h3>Total Revenue</h3>
          <p>KES {{ dashboardData?.total_revenue || 0 }}</p>
          <span class="trend up">↑ 14% in the last month</span>
        </div>
        <div class="card">
          <h3>Total Customers</h3>
          <p>{{ dashboardData?.total_customers || 0 }}</p>
          <span class="trend down">↓ 11% in the last month</span>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts">
        <div class="chart-container">
          <h3>Revenue Trend</h3>
          <LineChart :data="revenueChartData" :options="chartOptions" />
        </div>
        <div class="chart-container">
          <h3>Sales by Location</h3>
          <BarChart :data="salesByLocationData" :options="chartOptions" />
        </div>
        <div class="chart-container">
          <h3>Total Sales Breakdown</h3>
          <DoughnutChart :data="totalSalesData" :options="chartOptions" />
        </div>
      </div>

      <div class="top-products">
        <h3>Top Selling Products</h3>
        <table>
          <thead>
            <tr>
              <th>Product Name</th>
              <th>Price</th>
              <th>Category</th>
              <th>Quantity</th>
              <th>Amount</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in dashboardData?.top_products" :key="product.id">
              <td>{{ product.name }}</td>
              <td>KES {{ product.price }}</td>
              <td>{{ product.category.name }}</td>
              <td>{{ product.moq || 0 }}</td>
              <td>KES {{ (product.price * (product.moq || 0)).toFixed(2) }}</td>
              <td>
                <router-link :to="`/admin-page/products/${product.id}`">Edit</router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { onMounted, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import { Line as LineChart, Bar as BarChart, Doughnut as DoughnutChart } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, BarElement, ArcElement, PointElement, LinearScale, CategoryScale } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, BarElement, ArcElement, PointElement, LinearScale, CategoryScale);

export default {
  components: { AdminLayout, LineChart, BarChart, DoughnutChart },
  setup() {
    const store = useEcommerceStore();

    const dashboardData = computed(() => store.dashboardData);

    const revenueChartData = computed(() => ({
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Current Week',
          data: dashboardData.value?.revenue_trend?.current || [0, 0, 0, 0, 0, 0],
          borderColor: '#28a745',
          backgroundColor: 'rgba(40, 167, 69, 0.2)',
          fill: true,
        },
        {
          label: 'Previous Week',
          data: dashboardData.value?.revenue_trend?.previous || [0, 0, 0, 0, 0, 0],
          borderColor: '#6f42c1',
          backgroundColor: 'rgba(111, 66, 193, 0.2)',
          fill: true,
        },
      ],
    }));

    const salesByLocationData = computed(() => ({
      labels: dashboardData.value?.sales_by_location?.map(item => item.location) || [],
      datasets: [
        {
          label: 'Sales',
          data: dashboardData.value?.sales_by_location?.map(item => item.sales) || [],
          backgroundColor: ['#6f42c1', '#28a745', '#dc3545', '#ffc107'],
        },
      ],
    }));

    const totalSalesData = computed(() => ({
      labels: dashboardData.value?.total_sales_breakdown?.map(item => item.channel) || [],
      datasets: [
        {
          data: dashboardData.value?.total_sales_breakdown?.map(item => item.sales) || [],
          backgroundColor: ['#6f42c1', '#28a745', '#dc3545', '#ffc107'],
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
      },
    };

    onMounted(() => {
      store.fetchDashboardData();
    });

    return { dashboardData, revenueChartData, salesByLocationData, totalSalesData, chartOptions };
  },
};
</script>

<style scoped>
.dashboard {
  padding: 1rem;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.card {
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card h3 {
  font-size: 1rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.card p {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
}

.trend {
  font-size: 0.9rem;
}

.trend.up {
  color: #28a745;
}

.trend.down {
  color: #dc3545;
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 300px;
}

.chart-container h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.top-products {
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.top-products h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
}

td a {
  color: #6f42c1;
  text-decoration: none;
}

td a:hover {
  text-decoration: underline;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .card p {
    font-size: 1.3rem;
  }

  .charts {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 250px;
  }

  th, td {
    padding: 0.5rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }

  .card p {
    font-size: 1.2rem;
  }

  .chart-container {
    height: 200px;
  }

  th, td {
    font-size: 0.8rem;
  }
}
</style>
