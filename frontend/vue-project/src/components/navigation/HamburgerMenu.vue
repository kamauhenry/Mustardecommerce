<template>
  <header class="navbar">
    <div class="nav-bar-one">
      <button class="hamburger" @click="isSidebarOpen = !isSidebarOpen">☰</button>
      <div class="logo">
        <img
          src="../../assets/images/mustard-imports.png"
          alt="Mustard Imports Logo"
          class="main-logo"
        />
      </div>
    </div>

    <div class="nav-icons">
      <div class="icon">
        <IconLightMode></IconLightMode>
      </div>
      <div class="icon">
        <IconCart></IconCart>
      </div>
      <div class="icon">
        <IconLogin></IconLogin>
      </div>
    </div>
  </header>
  <div class="search-container">
    <input type="text" v-model="query" placeholder="Search..." class="search-input" />
    <img
      src="../../assets/images/211817_search_strong_icon.png"
      alt="Search Icon"
      class="search-icon"
    />
  </div>

  <aside :class="['sidebar', { open: isSidebarOpen }]">
    <button class="close-btn" @click="isSidebarOpen = false">×</button>

    <nav>
      <div class="logo-image">
        <img
          src="../../assets/images/mustard-imports.png"
          alt="Mustard Imports Logo"
          class="main-logo"
        />
      </div>

      <ul class="page-list">
        <li><a href="/" :class="isActive('/')">Home</a></li>
        <li><a href="/moq-campaigns" :class="isActive('/moq-campaigns')">MOQ Campaigns</a></li>
        <li><a href="/profile" :class="isActive('/profile')">My Profile</a></li>
        <li><a href="/orders" :class="isActive('/orders')">My Orders</a></li>
        <li><a href="/request-moq" :class="isActive('/request-moq')">Request MOQ Campaign</a></li>
        <li><a href="/track-order" :class="isActive('/track-order')">Track Order</a></li>
        <li><a href="/about" :class="isActive('/about')">About Us</a></li>
        <li><a href="/contact" :class="isActive('/contact')">Contact Us</a></li>
      </ul>

      <hr />

      <h2 class="category-title">Our Categories</h2>

      <ul class="category-list">
        <li><a href="/home-kitchen" :class="isActive('/home-kitchen')">Home & Kitchen</a></li>
        <li><a href="/bags-footwear" :class="isActive('/bags-footwear')">Bags & Footwear</a></li>
        <li><a href="/electronics" :class="isActive('/electronics')">Electronics</a></li>
        <li>
          <a href="/beauty-health" :class="isActive('/beauty-health')">Beauty, Personal & Health</a>
        </li>
        <li>
          <a href="/machine-industrials" :class="isActive('/machine-industrials')"
            >Machine & Industrials</a
          >
        </li>
        <li>
          <a href="/clothes-apparels" :class="isActive('/clothes-apparels')">Clothes & Apparels</a>
        </li>
        <li>
          <a href="/sports-outdoor" :class="isActive('/sports-outdoor')"
            >Sports, Outdoor & Entertainment</a
          >
        </li>
        <li><a href="/ikea" :class="isActive('/ikea')">Ikea</a></li>
        <li>
          <a href="/baby-kids-games" :class="isActive('/baby-kids-games')">Baby, Kids & Games</a>
        </li>
        <li><a href="/office" :class="isActive('/office')">Office</a></li>
        <li><a href="/buy4me" :class="isActive('/buy4me')">Buy4Me</a></li>
        <li>
          <a href="/swag-gift-items" :class="isActive('/swag-gift-items')"
            >Swag/Branded Gift Items</a
          >
        </li>
        <li>
          <a href="/agriculture-food-drinks" :class="isActive('/agriculture-food-drinks')"
            >Agriculture, Food & Drinks</a
          >
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import IconLightMode from '../icons/IconLightMode.vue'
import IconCart from '../icons/IconCart.vue'
import IconLogin from '../icons/IconLogin.vue'
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const isActive = (path) => {
  return route.path === path ? 'active-link' : ''
}

const isSidebarOpen = ref(false)
const isMobile = ref(window.innerWidth <= 768)

const updateScreenSize = () => {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  window.addEventListener('resize', updateScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize)
})
</script>

<style scoped>
/* Navigation Bar */
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  background-color: var(--vt-c-white);
  z-index: 99;
}

.nav-bar-one {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 1.5rem;
}

nav {
  text-transform: uppercase;
}

.main-logo {
  width: 120px;
  height: auto;
}

.nav-icons {
  display: flex;
  gap: 1.4rem;
}

.nav-icons .icon {
  border: none;
  border-radius: 10%;
  background-color: var(--background-color-one);
  padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.hamburger {
  font-size: 2rem;
  background: none;
  border: none;
  cursor: pointer;
  display: none;
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: -100%;
  width: 250px;
  height: 100vh;
  background: white;
  transition: left 0.3s ease-in-out;
  padding: 1rem;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
}

.sidebar.open {
  left: 0;
}

.close-btn {
  font-size: 3.5rem;
  background: none;
  border: none;
  cursor: pointer;
  position: absolute;
  top: 10px;
  right: 10px;
}

/* Categories */
.category-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: #ff6600;
  margin-bottom: 1rem;
}

.page-list,
.category-list {
  list-style: none;
  padding: 0;
}

.page-list li,
.category-list li {
  margin-bottom: 0.7rem;
}

.page-list a,
.category-list a {
  text-decoration: none;
  color: black;
  font-weight: 700;
  display: block;
}

.page-list a.active-link,
.category-list a.active-link {
  color: #ff6600;
}

@media (max-width: 768px) {
  .hamburger {
    display: block;
  }
}

@media (min-width: 360px) and (max-width: 539px) {
  .main-logo {
    width: 120px;
    height: auto;
  }

  .nav-icons .icon {
    width: 2.2rem;
  }
}

@media (max-width: 359px) {
  .main-logo {
    width: 120px;
    height: auto;
  }

  .nav-icons .icon {
    width: 2.2rem;
  }
}

hr {
  margin: 2rem 0;
}

/* Scrollbar width */
::-webkit-scrollbar {
  width: 6px;
}

/* Scrollbar track (background) */
::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

/* Scrollbar handle (thumb) */
::-webkit-scrollbar-thumb {
  background: #c7c7c7;
  border-radius: 10px;
}

/* Scrollbar handle on hover */
::-webkit-scrollbar-thumb:hover {
  background: #b6b6b6;
}

/* Search Bar */
.search-container {
  display: flex;
  align-items: center;
  width: 100vw;
  background-color: var(--background-color-one);
  padding: 0.1rem 1.1rem;
  border: 1px solid transparent;
}

.search-input {
  background-color: var(--background-color-one);
  flex: 1;
  border: none;
  padding: 0.8rem;
  border-radius: 25px 0 0 25px;
  outline: none;
}

.search-icon {
  width: 30px;
  height: 30px;
}
</style>
