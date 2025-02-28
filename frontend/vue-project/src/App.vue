<script>
// import AdminDashboard from "./AdminDashboard.vue";
import HomePage from "./HomePage.vue";

export default {
  name: "app",
  components: {
    HomePage,
    // AdminDashboard,
  },
};
</script>

<template>
  <div id="app">
    <HomePage></HomePage>
    <!-- <AdminDashboard></AdminDashboard> -->
  </div>
</template>

<style scoped>

</style>
