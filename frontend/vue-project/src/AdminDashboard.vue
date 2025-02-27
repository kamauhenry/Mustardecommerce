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
  import Sidebar from './components/Sidebar.vue';
  import OrdersTable from './components/OrdersTable.vue';
  import StatsPanel from './components/StatsPanel.vue';

  export default {
    components: {
      Sidebar,
      OrdersTable,
      StatsPanel,
    },
  };
</script>
