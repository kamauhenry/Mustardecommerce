<template>
  <header class="navbar" ref="navbar" aria-label="Main Navigation">
    <div class="nav-bar-one">
      <button class="hamburger" @click="toggleSidebar" aria-label="Toggle Menu">
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
      <div class="icon search-toggle" v-if="isMobile && !isSearchOpen" @click="toggleSearch">
        <img
          src="@/assets/images/211817_search_strong_icon.png"
          alt="Search Icon"
          class="search-icon"
        />
      </div>
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

  <div
    v-if="isSearchOpen || !isMobile"
    class="search-container"
    :class="{ 'is-open': isSearchOpen || !isMobile }"
    ref="searchContainer"
  >
    <input
      type="text"
      v-model="query"
      placeholder="Search products..."
      class="search-input"
      @keyup.enter="performSearch"
      @input="showSuggestions = true"
      aria-label="Search Products"
    />
    <img
      src="@/assets/images/211817_search_strong_icon.png"
      alt="Search Icon"
      class="search-icon"
      @click="performSearch"
    />
    <!-- Suggestions Dropdown -->
    <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
      <ul>
        <li
          v-for="suggestion in suggestions"
          :key="suggestion.id"
          @click="selectSuggestion(suggestion)"
          class="suggestion-item"
        >
          {{ suggestion.name }}
        </li>
      </ul>
    </div>
  </div>

  <aside :class="['sidebar', { open: isSidebarOpen }]" aria-label="Sidebar Navigation">
    <button class="close-btn" @click="closeSidebar" aria-label="Close Menu">×</button>

    <nav>
      <div class="categories-section">
        <button class="category-toggle" @click="toggleCategories" :aria-expanded="isCategoriesOpen" aria-controls="categories-dropdown">
          Our Categories
          <span class="toggle-icon">{{ isCategoriesOpen ? '−' : '+' }}</span>
        </button>

        <div v-if="isCategoriesOpen" id="categories-dropdown" class="categories-dropdown">
          <div v-if="productsStore.loading.categories" class="loading">
            Loading categories...
          </div>
          <div v-else-if="productsStore.error.categories" class="error">
            {{ productsStore.error.categories }}
            <button @click="productsStore.fetchCategories" class="retry-button">Retry</button>
          </div>
          <ul v-else class="category-list" itemscope itemtype="http://schema.org/ItemList">
            <li v-for="category in categories" :key="category.id" itemprop="itemListElement" itemscope itemtype="http://schema.org/Thing">
              <router-link :to="`/category/${category.slug}/products`" class="category-link" @click="handleNavigationWithSidebarClose" itemprop="url">
                <span itemprop="name">{{ category.name }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <hr />

      <ul class="page-list" itemscope itemtype="http://schema.org/SiteNavigationElement">
        <li><router-link to="/" :class="isActive('/')" @click="handleNavigationWithSidebarClose" itemprop="url"><span itemprop="name">Home</span></router-link></li>
        <li><router-link to="/pay-and-pick" :class="isActive('/pay-and-pick')" @click="handleNavigationWithSidebarClose" itemprop="url"><span itemprop="name">Pay & Pick</span></router-link></li>
        <li><router-link to="/moq-campaigns" :class="isActive('/moq-campaigns')" @click="handleNavigationWithSidebarClose" itemprop="url"><span itemprop="name">MOQ Campaigns</span></router-link></li>
        <li v-if="authStore.isAuthenticated"><router-link to="/profile" :class="isActive('/profile')" @click="handleNavigationWithSidebarClose" itemprop="url"><span itemprop="name">My Profile</span></router-link></li>
        <li v-if="authStore.isAuthenticated"><router-link to="/orders" :class="isActive('/orders')" @click="handleNavigationWithSidebarClose" itemprop="url"><span itemprop="name">My Orders</span></router-link></li>
        <li v-if="authStore.isAuthenticated"><a @click="handleRequestMOQ" class="nav-link" itemprop="url"><span itemprop="name">Request MOQ Campaign</span></a></li>
        <li v-else><a @click="openLoginModal" class="nav-link" itemprop="url"><span itemprop="name">Request MOQ Campaign</span></a></li>
        <li><router-link to="/about" :class="isActive('/about')" @click="handleNavigationWithSidebarClose" itemprop="url"><span itemprop="name">About Us</span></router-link></li>
        <li><router-link to="/contact" :class="isActive('/contact')" @click="handleNavigationWithSidebarClose" itemprop="url"><span itemprop="name">Contact Us</span></router-link></li>
      </ul>

      <hr />

      <div class="contact-section">
        <h3>Contact Us</h3>
        <p>Email: <a href="mailto:mustardimports@gmail.com">mustardimports@gmail.com</a></p>
        <p>Telephone: <a href="tel:+254724028971">+254 724 028971</a></p>
        <router-link to="/contact" class="contact-link" @click="handleNavigationWithSidebarClose">Get in Touch</router-link>
      </div>
    </nav>
  </aside>
  <div v-if="isSidebarOpen" class="overlay" @click="closeSidebar"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, inject, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useProductsStore } from '@/stores/modules/products';
import { useSearchStore } from '@/stores/modules/search';
import { useAuthStore } from '@/stores/modules/auth';
import IconHamburger from '../icons/IconHamburger.vue';
import IconLightMode from '../icons/IconLightMode.vue';
import IconCart from '../icons/IconCart.vue';
import IconLogin from '../icons/IconLogin.vue';
import AuthModals from '../auth/AuthModals.vue';

const route = useRoute();
const router = useRouter();
const productsStore = useProductsStore();
const searchStore = useSearchStore();
const authStore = useAuthStore();

// Use inject with fallbacks to prevent errors
const openRequestMOQ = inject('openRequestMOQ', () => {
  console.warn('openRequestMOQ not provided, using fallback');
  return () => {};
});
const openLoginModal = inject('openLoginModal', () => {
  console.warn('openLoginModal not provided, using fallback');
  return () => {};
});

const isActive = (path) => {
  return route.path === path ? 'active-link' : '';
};

const isSidebarOpen = ref(false);
const isCategoriesOpen = ref(false);
const isMobile = ref(window.innerWidth <= 500);
const isSearchOpen = ref(false);
const query = ref('');
const showSuggestions = ref(false);
const navbar = ref(null);
const searchContainer = ref(null);
let debounceTimeout = null;
let hideTimeout = null;
let resizeTimeout = null;
let shouldCloseSidebar = ref(false);

// Computed property to access search suggestions from the store
const suggestions = computed(() => {
  console.log('Computed suggestions:', searchStore.suggestions);
  return searchStore.suggestions;
});

// Fetch suggestions with debounce
watch(query, (newQuery) => {
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }
  if (hideTimeout) {
    clearTimeout(hideTimeout);
  }
  debounceTimeout = setTimeout(() => {
    if (newQuery.trim()) {
      console.log('Fetching suggestions for:', newQuery);
      searchStore.fetchSuggestions(newQuery);
      showSuggestions.value = true;
      hideTimeout = setTimeout(() => {
        setTimeout(() => {
          showSuggestions.value = false;
          console.log('Suggestions hidden after 3s timeout');
        }, 100);
      }, 6000);
    } else {
      searchStore.clearSuggestions();
      showSuggestions.value = false;
    }
  }, 200);
});

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
  if (!isSidebarOpen.value) {
    isSearchOpen.value = false;
    showSuggestions.value = false;
    document.body.style.overflow = '';
  } else {
    document.body.style.overflow = 'hidden';
  }
};

const closeSidebar = () => {
  isSidebarOpen.value = false;
  isCategoriesOpen.value = false;
  isSearchOpen.value = false;
  showSuggestions.value = false;
  document.body.style.overflow = '';
};

const handleNavigationWithSidebarClose = () => {
  shouldCloseSidebar.value = true;
};

const handleRequestMOQ = () => {
  openRequestMOQ();
  closeSidebar();
};

const toggleCategories = () => {
  isCategoriesOpen.value = !isCategoriesOpen.value;
};

const toggleSearch = () => {
  isSearchOpen.value = !isSearchOpen.value;
  showSuggestions.value = false;
  updateContentOffset();
};

const performSearch = async () => {
  if (!query.value.trim()) return;

  searchStore.setLoading(true);
  try {
    const response = await fetch(
      `https://mustardimports.co.ke/api/products/search/?search=${encodeURIComponent(query.value)}`
    );
    if (!response.ok) throw new Error('Failed to fetch products');
    const data = await response.json();

    searchStore.setResults(data.results || []);
    searchStore.setTotalResults(data.count || 0);
    searchStore.addRecentSearch(query.value);

    router.push({
      name: 'search-results',
      query: { q: query.value },
    });

    showSuggestions.value = false;
    if (hideTimeout) {
      clearTimeout(hideTimeout);
    }
    query.value = '';
    closeSidebar();
    isSearchOpen.value = false;
    updateContentOffset();
  } catch (error) {
    console.error('Error searching products:', error);
    searchStore.setResults([]);
    searchStore.setTotalResults(0);
  } finally {
    searchStore.setLoading(false);
  }
};

const selectSuggestion = (suggestion) => {
  query.value = suggestion.name;
  showSuggestions.value = false;
  performSearch();
};

const handleOutsideClick = (event) => {
  if (
    isSearchOpen.value &&
    searchContainer.value &&
    !searchContainer.value.contains(event.target) &&
    !event.target.closest('.search-toggle')
  ) {
    isSearchOpen.value = false;
    showSuggestions.value = false;
    updateContentOffset();
  }
};

const updateContentOffset = async () => {
  if (!navbar.value || !searchContainer.value) return;
  await nextTick();
  const mainContent = document.querySelector('main.main-content');
  if (mainContent) {
    const navbarHeight = navbar.value.offsetHeight;
    const searchHeight = (isMobile.value && !isSearchOpen.value) ? 0 : searchContainer.value.offsetHeight;
    const totalHeight = navbarHeight + searchHeight;
    mainContent.style.marginTop = `${totalHeight}px`;
  }
};

const updateScreenSize = () => {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  resizeTimeout = setTimeout(() => {
    isMobile.value = window.innerWidth <= 500;
    if (!isMobile.value) {
      isSearchOpen.value = false;
      showSuggestions.value = false;
    }
    updateContentOffset();
  }, 100);
};

const categories = computed(() => productsStore.categories);

onMounted(() => {
  window.addEventListener('resize', updateScreenSize);
  document.addEventListener('click', handleOutsideClick);
  if (!productsStore.categories.length) {
    productsStore.fetchCategories();
  }
  updateContentOffset();

  router.afterEach(() => {
    if (shouldCloseSidebar.value) {
      closeSidebar();
      shouldCloseSidebar.value = false;
    }
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize);
  document.removeEventListener('click', handleOutsideClick);
  if (debounceTimeout) clearTimeout(debounceTimeout);
  if (hideTimeout) clearTimeout(hideTimeout);
  if (resizeTimeout) clearTimeout(resizeTimeout);
  document.body.style.overflow = '';
  const mainContent = document.querySelector('main.main-content');
  if (mainContent) {
    mainContent.style.marginTop = '';
  }
});
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
}

.nav-bar-one {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  display: flex;
  align-items: center;
}

.main-logo {
  height: 80px;
  width: auto;
  max-width: 200px;
}

.nav-icons {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-icons .icon {
  background-color: #f5f5f5;
  padding: 0.6rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  cursor: pointer;
}

.nav-icons .icon:hover {
  background-color: #e0e0e0;
}

.search-toggle .search-icon {
  width: 24px;
  height: 24px;
}

.search-container {
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  padding: 0.5rem 1rem;
  border-radius: 25px;
  z-index: 999;
  position: fixed;
  top: 90px;
  left: 0;
  width: calc(100% - 2rem);
  margin: 0 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: opacity 0.3s ease, transform 0.3s ease, visibility 0.3s ease;
}

.search-container.is-open {
  opacity: 1;
  transform: translateY(0);
  visibility: visible;
}

.search-container:not(.is-open) {
  opacity: 0;
  transform: translateY(-10px);
  visibility: hidden;
  pointer-events: none;
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
  cursor: pointer;
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 10px;
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.suggestions-dropdown ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  padding: 10px;
  cursor: pointer;
}

.suggestion-item:hover {
  background-color: #f0f0f0;
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
  padding: 0.6rem;
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
  transition: transform 0.3s ease-in-out;
  padding: 1.5rem;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
  z-index: 100;
}

.sidebar.open {
  transform: translateX(280px);
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
  margin-bottom: 0.5rem;
}

.logo-image .main-logo {
  height: 90px;
  width: auto;
  max-width: 220px;
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
  color: #D4A017;
}

.page-list a:hover,
.category-list a:hover {
  color: #D4A017;
}

.nav-link {
  cursor: pointer;
}

.categories-section {
  margin: 0.5rem 0;
  margin-top: 55px;
}

.category-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0.5rem 0;
  background: none;
  border: none;
  font-size: 1.1rem;
  font-weight: 700;
  color: #D4A017;
  text-transform: uppercase;
  cursor: pointer;
  transition: color 0.2s;
}

.category-toggle:hover {
  color: #e67d21;
}

.toggle-icon {
  font-size: 1.2rem;
}

.categories-dropdown {
  max-height: 300px;
  overflow-y: auto;
  margin-top: 0.5rem;
  padding: 0.5rem 0;
}

.category-list {
  padding: 0;
}

.retry-button {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #D4A017;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button:hover {
  background-color: #e67d21;
}

hr {
  margin: 1rem 0;
  border: 0;
  border-top: 1px solid #e0e0e0;
}

.loading,
.error {
  font-size: 1rem;
  color: #666;
  padding: 0.5rem 0;
}

/* Contact Section */
.contact-section {
  margin-top: 1rem;
  color: #333;
}

.contact-section h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #D4A017;
  margin-bottom: 0.5rem;
}

.contact-section p {
  font-size: 0.9rem;
  margin: 0.3rem 0;
}

.contact-section a {
  color: #D4A017;
  text-decoration: none;
}

.contact-section a:hover {
  color: #e67d21;
}

.contact-link {
  display: inline-block;
  margin-top: 0.5rem;
  font-weight: 600;
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
@media (max-width: 500px) {
  .navbar {
    padding: 0.6rem;
  }

  .main-logo {
    height: 60px;
    max-width: 160px;
  }

  .nav-icons .icon {
    padding: 0.5rem;
  }

  .hamburger {
    padding: 0.5rem;
  }

  .search-toggle .search-icon {
    width: 22px;
    height: 22px;
  }

  .sidebar {
    width: 260px;
  }

  .search-container {
    top: 80px;
    padding: 0.5rem;
  }

  .search-input {
    font-size: 0.85rem;
  }

  .search-icon {
    width: 20px;
    height: 20px;
  }

  .suggestions-dropdown {
    border-radius: 10px;
    max-height: 150px;
  }

  .suggestion-item {
    padding: 8px;
    font-size: 0.85rem;
  }

  .contact-section h3 {
    font-size: 1rem;
  }

  .contact-section p {
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 0.5rem;
  }

  .main-logo {
    height: 50px;
    max-width: 140px;
  }

  .nav-icons .icon {
    padding: 0.4rem;
  }

  .hamburger {
    padding: 0.4rem;
  }

  .search-toggle .search-icon {
    width: 20px;
    height: 20px;
  }

  .sidebar {
    width: 240px;
    padding: 1rem;
  }

  .close-btn {
    font-size: 1.8rem;
  }

  .page-list li,
  .category-list li {
    margin-bottom: 0.6rem;
  }

  .category-toggle {
    font-size: 1rem;
  }

  .search-container {
    top: 70px;
  }

  .search-input {
    font-size: 0.85rem;
  }

  .search-icon {
    width: 20px;
    height: 20px;
  }

  .contact-section h3 {
    font-size: 0.9rem;
  }

  .contact-section p {
    font-size: 0.8rem;
  }
}
</style>