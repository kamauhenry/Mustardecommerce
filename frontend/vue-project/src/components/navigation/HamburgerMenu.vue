<template>
  <header class="navbar" aria-label="Main Navigation">
    <div class="nav-bar-one">
      <button class="hamburger" @click="isSidebarOpen = !isSidebarOpen" aria-label="Toggle Menu">
        <IconHamburger />
      </button>
      <div class="logo">
        <img
          src="@/assets/images/mustard-imports.png"
          alt="Mustard Imports Logo"
          class="main-logo"
        />
      </div>
    </div>

    <div class="nav-icons">
      <div class="icon">
        <IconLightMode aria-label="Toggle Light Mode" />
      </div>
      <div class="icon">
        <router-link to="/cart" aria-label="View Cart">
          <IconCart />
        </router-link>
      </div>
      <div class="icon">
        <AuthModals>
          <IconLogin aria-label="Login or Register" />
        </AuthModals>
      </div>
    </div>
  </header>

  <div class="search-container">
    <input
      type="text"
      v-model="query"
      placeholder="Search products..."
      class="search-input"
      @keyup.enter="performSearch"
      aria-label="Search Products"
    />
    <img
      src="@/assets/images/211817_search_strong_icon.png"
      alt="Search Icon"
      class="search-icon"
    />
  </div>

  <aside :class="['sidebar', { open: isSidebarOpen }]" aria-label="Sidebar Navigation">
    <button class="close-btn" @click="closeSidebar" aria-label="Close Menu">×</button>

    <nav>
      <div class="logo-image">
        <img
          src="@/assets/images/mustard-imports.png"
          alt="Mustard Imports Logo"
          class="main-logo"
        />
      </div>

      <ul class="page-list" itemscope itemtype="http://schema.org/SiteNavigationElement">
        <li><router-link to="/" :class="isActive('/')" itemprop="url"><span itemprop="name">Home</span></router-link></li>
        <li><router-link to="/moq-campaigns" :class="isActive('/moq-campaigns')" itemprop="url"><span itemprop="name">MOQ Campaigns</span></router-link></li>
        <li v-if="store.isAuthenticated"><router-link to="/profile" :class="isActive('/profile')" itemprop="url"><span itemprop="name">My Profile</span></router-link></li>
        <li v-if="store.isAuthenticated"><router-link to="/orders" :class="isActive('/orders')" itemprop="url"><span itemprop="name">My Orders</span></router-link></li>
        <li v-if="store.isAuthenticated"><a @click="openRequestMOQ" class="nav-link" itemprop="url"><span itemprop="name">Request MOQ Campaign</span></a></li>
        <li v-else><a @click="openLoginModal" class="nav-link" itemprop="url"><span itemprop="name">Request MOQ Campaign</span></a></li>
        <li v-if="store.isAuthenticated"><a @click="openTrackOrder" class="nav-link" itemprop="url"><span itemprop="name">Track Order</span></a></li>
        <li v-else><a @click="openLoginModal" class="nav-link" itemprop="url"><span itemprop="name">Track Order</span></a></li>
        <li><router-link to="/about" :class="isActive('/about')" itemprop="url"><span itemprop="name">About Us</span></router-link></li>
        <li><router-link to="/contact" :class="isActive('/contact')" itemprop="url"><span itemprop="name">Contact Us</span></router-link></li>
      </ul>

      <hr />

      <h2 class="category-title">Our Categories</h2>

      <div v-if="store.loading.categories" class="loading">
        Loading categories...
      </div>
      <div v-else-if="store.error.categories" class="error">
        {{ store.error.categories }}
        <button @click="store.fetchCategories" class="retry-button">Retry</button>
      </div>
      <ul v-else class="category-list" itemscope itemtype="http://schema.org/ItemList">
        <li v-for="category in categories" :key="category.id" itemprop="itemListElement" itemscope itemtype="http://schema.org/Thing">
          <router-link :to="`/category/${category.slug}/products`" class="category-link" itemprop="url">
            <span itemprop="name">{{ category.name }}</span>
          </router-link>
        </li>
      </ul>
    </nav>
  </aside>
  <div v-if="isSidebarOpen" class="overlay" @click="closeSidebar"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, inject } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import IconHamburger from '../icons/IconHamburger.vue';
import IconLightMode from '../icons/IconLightMode.vue';
import IconCart from '../icons/IconCart.vue';
import IconLogin from '../icons/IconLogin.vue';
import AuthModals from '../auth/AuthModals.vue';

const route = useRoute();
const router = useRouter();
const store = useEcommerceStore();

const openTrackOrder = inject('openTrackOrder');
const openRequestMOQ = inject('openRequestMOQ');
const openLoginModal = inject('openLoginModal');

const isActive = (path) => {
  return route.path === path ? 'active-link' : '';
};

const isSidebarOpen = ref(false);
const isMobile = ref(window.innerWidth <= 768);
const query = ref('');

const updateScreenSize = () => {
  isMobile.value = window.innerWidth <= 768;
};

const closeSidebar = () => {
  isSidebarOpen.value = false;
};

const performSearch = () => {
  if (query.value.trim()) {
    store.addRecentSearch(query.value);
    router.push({ name: 'search-results', query: { q: query.value } });
    query.value = '';
    closeSidebar();
  }
};

onMounted(() => {
  window.addEventListener('resize', updateScreenSize);
  if (!store.categories.length) {
    store.fetchCategories();
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize);
});

const categories = computed(() => store.categories);
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 99;
}

.nav-bar-one {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.main-logo {
  height: 40px;
  width: auto;
}

.nav-icons {
  display: flex;
  gap: 0.8rem;
}

.nav-icons .icon {
  background-color: #f5f5f5;
  padding: 0.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.nav-icons .icon:hover {
  background-color: #e0e0e0;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 50;
}

.hamburger {
  background-color: #f5f5f5;
  border: none;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar {
  position: fixed;
  top: 0;
  left: -280px;
  width: 280px;
  height: 100vh;
  background-color: #fff;
  transition: left 0.3s ease-in-out;
  padding: 1.5rem;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
  z-index: 100;
}

.sidebar.open {
  left: 0;
}

.close-btn {
  font-size: 2rem;
  background: none;
  border: none;
  cursor: pointer;
  position: absolute;
  top: 1rem;
  right: 1rem;
  color: #333;
}

.logo-image {
  margin-bottom: 1.5rem;
}

.logo-image .main-logo {
  height: 50px;
}

.page-list,
.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.page-list li,
.category-list li {
  margin-bottom: 0.8rem;
}

.page-list a,
.category-list a {
  text-decoration: none;
  font-weight: 600;
  color: #333;
  display: block;
  padding: 0.5rem 0;
  transition: color 0.2s;
}

.page-list a.active-link,
.category-list a.active-link {
  color: #f28c38;
}

.page-list a:hover,
.category-list a:hover {
  color: #f28c38;
}

.nav-link {
  cursor: pointer;
}

.category-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #f28c38;
  margin: 1.5rem 0 1rem;
  text-transform: uppercase;
}

.retry-button {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f28c38;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button:hover {
  background-color: #e67d21;
}

hr {
  margin: 1.5rem 0;
  border: 0;
  border-top: 1px solid #e0e0e0;
}

.search-container {
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  padding: 0.5rem 1rem;
  border-radius: 25px;
  margin: 0.5rem 1rem;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.5rem;
  outline: none;
  font-size: 0.9rem;
}

.search-icon {
  width: 24px;
  height: 24px;
}

.loading,
.error {
  font-size: 0.9rem;
  color: #666;
  padding: 0.5rem 0;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #c7c7c7;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #b6b6b6;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .navbar {
    padding: 0.5rem;
  }

  .main-logo {
    height: 35px;
  }

  .nav-icons .icon {
    padding: 0.4rem;
  }

  .sidebar {
    width: 260px;
  }

  .search-container {
    margin: 0.5rem;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 0.4rem;
  }

  .main-logo {
    height: 30px;
  }

  .nav-icons .icon {
    padding: 0.3rem;
  }

  .sidebar {
    width: 240px;
    padding: 1rem;
  }

  .close-btn {
    font-size: 1.8rem;
  }

  .logo-image .main-logo {
    height: 40px;
  }

  .page-list li,
  .category-list li {
    margin-bottom: 0.6rem;
  }

  .category-title {
    font-size: 1rem;
  }

  .search-container {
    margin: 0.4rem;
  }

  .search-input {
    font-size: 0.85rem;
  }

  .search-icon {
    width: 20px;
    height: 20px;
  }
}
</style>