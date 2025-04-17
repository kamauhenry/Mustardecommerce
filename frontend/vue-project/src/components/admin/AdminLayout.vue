<template>
  <div class="admin-layout">
    <!-- Header -->
    <header class="admin-header">
      <div class="logo">
        <h1>Admin Panel</h1>
      </div>
      <nav class="header-nav">
        <router-link to="/admin-page/dashboard">Dashboard</router-link>
        <router-link to="/admin-page/orders">Orders</router-link>
        <router-link to="/admin-page/products">Products</router-link>
        <router-link to="/admin-page/categories">Categories</router-link>
        <router-link to="/admin-page/settings">Settings</router-link>
        <router-link to="/">View Site</router-link>
        <button @click="logout" class="logout-btn">Logout</button>
      </nav>
    </header>

    <!-- Sidebar -->
    <aside class="sidebar">
      <ul>
        <li><router-link to="/admin-page/dashboard" active-class="active">Dashboard</router-link></li>
        <li><router-link to="/admin-page/orders" active-class="active">Orders</router-link></li>
        <li><router-link to="/admin-page/products" active-class="active">Products</router-link></li>
        <li><router-link to="/admin-page/categories" active-class="active">Categories</router-link></li>
        <li><router-link to="/admin-page/settings" active-class="active">Settings</router-link></li>
      </ul>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <slot></slot>
    </main>
  </div>
</template>

<script>
import { useEcommerceStore } from '@/stores/ecommerce';
import { useRouter } from 'vue-router';

export default {
  name: 'AdminLayout',
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();

    const logout = async () => {
      try {
        await store.logout();
        router.push('/admin-page/login');
      } catch (error) {
        console.error('Logout failed:', error);
      }
    };

    return { logout };
  },
};
</script>

<style scoped>
/* AdminLayout.vue Styles */
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.admin-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background-color: #ffffff;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.logo h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #6366f1;
}

.header-nav {
  display: flex;
  gap: 24px;
  align-items: center;
}

.header-nav a {
  color: #4b5563;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  padding: 8px 0;
  position: relative;
  transition: all 0.2s ease;
}

.header-nav a:hover {
  color: #6366f1;
}

.header-nav a:after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #6366f1;
  transition: width 0.2s ease;
}

.header-nav a:hover:after {
  width: 100%;
}

.logout-btn {
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background-color: #fee2e2;
  color: #ef4444;
}

.sidebar {
  width: 250px;
  background-color: #ffffff;
  color: #4b5563;
  padding-top: 80px; /* Account for header height */
  position: fixed;
  top: 0;
  bottom: 0;
  box-shadow: 1px 0 3px rgba(0, 0, 0, 0.05);
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  padding: 4px 16px;
}

.sidebar a {
  color: #4b5563;
  text-decoration: none;
  font-size: 0.95rem;
  display: block;
  padding: 12px 16px;
  border-radius: 8px;
  margin: 4px 0;
  transition: all 0.2s ease;
}

.sidebar a:hover {
  background-color: #f3f4f6;
  color: #6366f1;
}

.sidebar a.active {
  background-color: #eff6ff;
  color: #6366f1;
  font-weight: 600;
}

.main-content {
  margin-left: 250px;
  margin-top: 64px;
  padding: 32px;
  flex: 1;
  background-color: #f8f9fa;
}
</style>
