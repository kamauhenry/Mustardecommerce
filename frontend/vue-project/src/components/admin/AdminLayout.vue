
<template>
    <div class="admin-layout">
      <nav class="sidebar">
        <h2>Admin Panel</h2>
        <ul>
          <li><router-link to="/admin-page/dashboard">Dashboard</router-link></li>
          <li><router-link to="/admin-page/products">Products</router-link></li>
          <li><router-link to="/admin-page/categories">Categories</router-link></li>
          <li><router-link to="/admin-page/orders">Orders</router-link></li>
          <li><router-link to="/admin-page/settings">Settings</router-link></li>
          <li><button @click="logout">Logout</button></li>
        </ul>
      </nav>
      <div class="content">
        <router-view></router-view>
      </div>
    </div>
  </template>
  
  <script>
  import { useEcommerceStore } from '@/stores/ecommerce';
  import { useRouter } from 'vue-router';
  
  export default {
    setup() {
      const store = useEcommerceStore();
      const router = useRouter();
  
      const logout = async () => {
        await store.logout();
        router.push('/admin-page/login');
      };
  
      return { logout };
    },
  };
  </script>
  
  <style scoped>
  .admin-layout {
    display: flex;
    min-height: 100vh;
  }
  
  .sidebar {
    width: 250px;
    background: #6f42c1;
    color: white;
    padding: 20px;
  }
  
  .sidebar h2 {
    margin-bottom: 20px;
  }
  
  .sidebar ul {
    list-style: none;
    padding: 0;
  }
  
  .sidebar li {
    margin-bottom: 10px;
  }
  
  .sidebar a {
    color: white;
    text-decoration: none;
    font-size: 16px;
  }
  
  .sidebar a:hover {
    text-decoration: underline;
  }
  
  .sidebar button {
    background: #dc3545;
    color: white;
    border: none;
    padding: 10px;
    width: 100%;
    text-align: left;
    cursor: pointer;
  }
  
  .content {
    flex: 1;
    padding: 20px;
    background: #f4f4f9;
  }
  </style>
  
  