<template>
  <div class="container">
    <Sidebar />
    <div class="content">
      <StatsPanel />
      <OrdersTable />
    </div>
  </div>
</template>

<script>
  import Sidebar from '../components/adminDashboardComponents/Sidebar.vue';
  import OrdersTable from '../components/adminDashboardComponents/OrdersTable.vue';
  import StatsPanel from '../components/adminDashboardComponents/StatsPanel.vue';

  export default {
    components: {
      Sidebar,
      OrdersTable,
      StatsPanel,
    },
  };
</script>

<style scoped>
.container {
    display: flex;
    height: 100vh;
}

.sidebar {
    width: 250px;
    background: #f8f9fa;
    padding: 20px;
}

.content {
    flex-grow: 1;
    padding: 20px;
    background: #ffffff;
}

.orders-table, .stats-panel {
    background: #fff;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status.paid {
    color: green;
    font-weight: bold;
}

.amount {
    font-size: 1.5em;
    font-weight: bold;
}
</style>
