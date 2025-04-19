<template>
  <div class="admin-layout">
    <!-- Header (shown only on mobile) -->
    <header class="admin-header">
      <!-- Hamburger button for mobile -->
      <button
        @click="toggleSidebar"
        class="hamburger-btn"
        :class="{ 'active': isSidebarOpen }"
        aria-label="Toggle navigation menu">
        <span></span>
        <span></span>
        <span></span>
      </button>
      <!-- Logo in header for smaller screens -->
      <div class="header-logo">
        <img src="../../assets/images/mustard-imports.png" alt="Icon" class="logo-icon" />
        <!-- <span class="logo-text">Mustard Imports</span> -->
      </div>
    </header>

    <!-- Overlay for mobile when sidebar is open -->
    <div
      v-if="isSidebarOpen"
      class="sidebar-overlay"
      @click="closeSidebar"></div>

    <!-- Sidebar with all navigation -->
    <aside class="sidebar" :class="{ 'open': isSidebarOpen }">
      <div class="logo">
        <img src="../../assets/images/mustard-imports.png" alt="Icon" class="logo-icon" />
        <!-- <span class="logo-text">Mustard Imports</span> -->
      </div>
      <ul>
        <li>
          <router-link
            to="/admin-page/dashboard"
            active-class="active"
            @click="closeSidebar">
            Dashboard
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin-page/orders"
            active-class="active"
            @click="closeSidebar">
            Orders
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin-page/products"
            active-class="active"
            @click="closeSidebar">
            Products
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin-page/categories"
            active-class="active"
            @click="closeSidebar">
            Categories
          </router-link>
        </li>
        <li>
          <router-link
            to="/admin-page/settings"
            active-class="active"
            @click="closeSidebar">
            Settings
          </router-link>
        </li>
        <li>
          <router-link
            to="/"
            class="view-site"
            @click="closeSidebar">
            View site
          </router-link>
        </li>
        <li>
          <button @click="handleLogout" class="logout-btn">
            Logout
          </button>
        </li>
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
import { useRouter, useRoute } from 'vue-router';
import { watch } from 'vue';

export default {
  name: 'AdminLayout',
  data() {
    return {
      isSidebarOpen: false
    };
  },
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const route = useRoute();

    const logout = async () => {
      try {
        await store.logout();
        router.push('/admin-page/login');
      } catch (error) {
        console.error('Logout failed:', error);
      }
    };

    // Watch for route changes to close the sidebar
    watch(() => route.path, () => {
      // Close sidebar on route change if it's open
      if (this.isSidebarOpen) {
        this.isSidebarOpen = false;
        document.body.style.overflow = '';
      }
    });

    return { logout };
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;

      // Prevent scrolling when sidebar is open
      if (this.isSidebarOpen) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    },
    closeSidebar() {
      this.isSidebarOpen = false;
      document.body.style.overflow = '';
    },
    handleLogout() {
      this.closeSidebar(); // Close sidebar before logging out
      this.logout();
    }
  }
}
</script>

<style scoped>
/* AdminLayout.vue Styles */
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  text-align: right;
}

.logo-icon {
  width: 160px;
  height: auto;
  margin-right: 8px;
}

.header-logo {
  display: none; /* Hidden by default, shown on smaller screens */
  align-items: center;
}

.header-logo-img {
  width: 100px;
  height: auto;
  max-width: 100%;
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

/* Hamburger button styles */
.hamburger-btn {
  display: none;
  width: 32px;
  height: 24px;
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 1010;
}

.hamburger-btn span {
  display: block;
  width: 100%;
  height: 3px;
  background-color: #4b5563;
  margin: 5px 0;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.hamburger-btn.active span:nth-child(1) {
  transform: translateY(8px) rotate(45deg);
}

.hamburger-btn.active span:nth-child(2) {
  opacity: 0;
}

.hamburger-btn.active span:nth-child(3) {
  transform: translateY(-8px) rotate(-45deg);
}

/* Sidebar styles */
.sidebar {
  width: 250px;
  background-color: #ffffff;
  color: #4b5563;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  padding-top: 80px; /* Account for header height on mobile */
  z-index: 990;
  box-shadow: 1px 0 3px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease-in-out;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  padding: 4px 16px;
}

.sidebar a, .sidebar .logout-btn {
  color: #4b5563;
  text-decoration: none;
  font-size: 0.95rem;
  display: block;
  padding: 12px 16px;
  border-radius: 8px;
  margin: 4px 0;
  transition: all 0.2s ease;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 700;
}

.sidebar a:hover, .sidebar .logout-btn:hover {
  background-color: #f3f4f6;
  color: #6366f1;
}

.sidebar a.active {
  background-color: #eff6ff;
  color: #6366f1;
  font-weight: 600;
}

.sidebar .logout-btn:hover {
  background-color: #fee2e2;
  color: #ef4444;
}

.sidebar .view-site {
  margin-top: 24px;
  color: #6366f1;
}

/* Overlay for mobile */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 980;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.main-content {
  margin-left: 250px;
  margin-top: 64px; /* Account for header height on mobile */
  padding: 32px;
  flex: 1;
  background-color: #f8f9fa;
  transition: margin-left 0.3s ease-in-out;
}

/* Responsive Styles */
@media (min-width: 1200px) {
  .admin-header {
    display: none; /* Hide header on large screens */
  }

  .sidebar {
    width: 280px;
    padding-top: 20px; /* No header, so reduce padding */
  }

  .main-content {
    margin-left: 280px;
    margin-top: 0; /* No header, so remove margin-top */
  }

  .logo {
    padding: 20px;
  }

  .logo-text {
    font-size: 1.4rem;
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .admin-header {
    display: none; /* Hide header on large screens */
  }

  .sidebar {
    width: 220px;
    padding-top: 14px; /* No header, so reduce padding */
  }

  .main-content {
    margin-left: 220px;
    margin-top: 0; /* No header, so remove margin-top */
  }

  .logo {
    padding: 14px;
  }

  .logo-text {
    font-size: 1.3rem;
  }

  .sidebar a, .sidebar .logout-btn {
    font-size: 0.9rem;
    padding: 10px 14px;
  }
}

@media (min-width: 768px) and (max-width: 991px) {
  .admin-header {
    display: none; /* Hide header on large screens */
  }

  .sidebar {
    width: 200px;
    padding-top: 12px; /* No header, so reduce padding */
  }

  .main-content {
    margin-left: 200px;
    margin-top: 0; /* No header, so remove margin-top */
  }

  .logo {
    padding: 12px;
  }

  .logo-text {
    font-size: 1.2rem;
  }

  .sidebar a, .sidebar .logout-btn {
    font-size: 0.85rem;
    padding: 8px 12px;
  }
}

@media (max-width: 767px) {
  .admin-header {
    display: flex; /* Show header on mobile */
  }

  .hamburger-btn {
    display: block;
  }

  .header-logo {
    display: flex;
  }

  .sidebar {
    transform: translateX(-100%);
    width: 260px; /* Slightly wider for better readability */
    padding-top: 64px; /* Account for header height */
    z-index: 1000;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-overlay {
    display: block;
  }

  .main-content {
    margin-left: 0;
    padding: 16px;
  }

  .logo {
    display: none; /* Hide sidebar logo on mobile since header logo is shown */
  }

  .header-logo-img {
    width: 80px;
  }

  .logo-text {
    font-size: 1rem;
  }

  .sidebar a, .sidebar .logout-btn {
    font-size: 0.9rem;
    padding: 10px 14px;
  }
}

@media (max-width: 480px) {
  .admin-header {
    padding: 5px 16px;
    height: 60px;
    margin-bottom: 1rem;
  }

  .sidebar {
    width: 240px;
    padding-top: 56px;
  }

  .main-content {
    margin-top: 56px;
    padding: 12px;
  }

  .header-logo-img {
    width: 120px;
    height: auto;
    margin: 10px;
  }

  .logo-text {
    font-size: 0.9rem;
  }

  .sidebar a, .sidebar .logout-btn {
    font-size: 0.85rem;
    padding: 8px 12px;
  }

  .hamburger-btn {
    width: 28px;
    height: 20px;
  }

  .hamburger-btn span {
    height: 2px;
    margin: 4px 0;
  }

  .hamburger-btn.active span:nth-child(1) {
    transform: translateY(6px) rotate(45deg);
  }

  .hamburger-btn.active span:nth-child(3) {
    transform: translateY(-6px) rotate(-45deg);
  }
}

@media (max-width: 360px) {
  .admin-header {
    padding: 5px 16px;
    height: 80px;
    margin-bottom: 1rem;
  }

  .sidebar {
    width: 220px;
  }

  .main-content {
    padding: 8px;
  }

  .header-logo-img {
    width: 160px;
    height: auto;
    margin: 10px;
  }

  .logo-text {
    font-size: 0.85rem;
  }

  .sidebar a, .sidebar .logout-btn {
    font-size: 0.8rem;
    padding: 6px 10px;
  }
}
</style>
