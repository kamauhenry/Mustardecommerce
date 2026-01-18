# Mustard Ecommerce Frontend Refactoring Plan

**Generated**: 2026-01-12
**Status**: Ready for Implementation
**Priority**: Security Fixes First, Then Code Quality
**Scope**: Moderate Refactoring (Critical + Recommended Improvements)

---

## Executive Summary

This plan addresses critical security vulnerabilities, removes hardcoded configurations, and improves code maintainability in the Mustard ecommerce Vue.js frontend application. The refactoring is organized into 5 phases, with Phases 1-2 being **mandatory** and Phases 3-4 being **strongly recommended**.

### Key Statistics
- **Total Files**: 55+ components, 18 views, 1 massive store (1,123 lines)
- **Critical Bugs**: 1 (App.vue store initialization)
- **Security Issues**: 5 high-priority vulnerabilities
- **Components Without Props**: 42+ out of 50
- **Estimated Effort**: 3-5 days (critical phases), 7-10 days (full implementation)

### Priorities (User-Selected)
1. ✅ Security fixes (auth, XSS, API hardcoding)
2. ✅ Code quality & maintainability
3. ✅ Maintain API compatibility (no backend changes)
4. ✅ Use environment variables (.env approach)
5. ✅ Moderate refactoring scope

---

## Phase 1: Critical Security Fixes [MUST DO - Day 1]

**Estimated Time**: 4-6 hours
**Risk Level**: Low (pure bug fixes)
**Priority**: CRITICAL

### 1.1 Fix Store Initialization Bug

**File**: `src/App.vue`
**Line**: 14
**Current Code**:
```javascript
const store = useEcommerceStore
```

**Fixed Code**:
```javascript
const store = useEcommerceStore()
```

**Impact**: Without this fix, the entire store is undefined and breaks all functionality.

**Testing**: App should load without "undefined" errors in console.

---

### 1.2 Remove Hardcoded API URLs

#### Files to Modify:

**1. `src/services/api.js`** (Primary API client)
- **Line 23**: Replace `baseURL: 'https://mustardimports.co.ke/api/'`
- **Action**: Use `import.meta.env.VITE_API_BASE_URL`
- **Add validation**: Throw error if env var is missing

```javascript
// Before
const api = axios.create({
  baseURL: 'https://mustardimports.co.ke/api/',
  withCredentials: true,
});

// After
const getBaseURL = () => {
  const url = import.meta.env.VITE_API_BASE_URL;
  if (!url) {
    throw new Error('VITE_API_BASE_URL environment variable is not defined');
  }
  // Normalize: remove trailing slash
  return url.replace(/\/$/, '');
};

const api = axios.create({
  baseURL: getBaseURL(),
  withCredentials: true,
});
```

**2. `src/stores/ecommerce.js`**
- **Line 500**: Remove `https://mustardimports.co.ke//api/` (note double slash bug)
- **Line 913**: Replace direct axios call with `this.apiInstance.get()`
- **Action**: Use centralized API client instead

```javascript
// Before (line 500)
const response = await axios.post('https://mustardimports.co.ke//api/orders/create', payload);

// After
const response = await this.apiInstance.post('/orders/create', payload);
```

**3. `src/components/navigation/SearchBar.vue`**
- **Line 87**: Remove hardcoded search endpoint
- **Action**: Import and use api client

```javascript
// Before
import axios from 'axios';
const response = await axios.get('https://mustardimports.co.ke/api/products/search/', { params });

// After
import { apiClient } from '@/services/api';
const response = await apiClient.get('/products/search/', { params });
```

**4. `src/components/home/recents/HomeCarousel.vue`**
- **Line 72**: Remove hardcoded categories endpoint

```javascript
// Before
const response = await axios.get('https://mustardimports.co.ke/api/categories/');

// After
import { apiClient } from '@/services/api';
const response = await apiClient.get('/categories/');
```

---

### 1.3 Add HTML Sanitization (XSS Protection)

**Step 1**: Install DOMPurify
```bash
npm install dompurify
npm install --save-dev @types/dompurify
```

**Step 2**: Create sanitization utility

**File**: `src/utils/sanitize.js` (NEW FILE)
```javascript
import DOMPurify from 'dompurify';

/**
 * Sanitizes HTML to prevent XSS attacks
 * @param {string} html - Raw HTML string
 * @param {object} options - DOMPurify configuration
 * @returns {string} - Sanitized HTML
 */
export const sanitizeHtml = (html, options = {}) => {
  if (!html || typeof html !== 'string') {
    return '';
  }

  const defaultConfig = {
    ALLOWED_TAGS: [
      'b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 'img'
    ],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'id'],
    ALLOW_DATA_ATTR: false,
  };

  return DOMPurify.sanitize(html, { ...defaultConfig, ...options });
};

/**
 * Strips all HTML tags, leaving only text
 * @param {string} html - Raw HTML string
 * @returns {string} - Plain text
 */
export const stripHtml = (html) => {
  return DOMPurify.sanitize(html, { ALLOWED_TAGS: [] });
};
```

**Step 3**: Apply sanitization to vulnerable components

**File**: `src/views/ProductDetails.vue`
- **Lines to modify**: Where product descriptions are rendered

```vue
<template>
  <!-- Before -->
  <div v-html="product.description"></div>

  <!-- After -->
  <div v-html="sanitizedDescription"></div>
</template>

<script setup>
import { computed } from 'vue';
import { sanitizeHtml } from '@/utils/sanitize';

const sanitizedDescription = computed(() => {
  return sanitizeHtml(product.value?.description || '');
});
</script>
```

**File**: `src/views/Cart.vue`
- **Line 35**: Sanitize `formatAttributes()` output

```javascript
// Before
const formatAttributes = (attributes) => {
  return Object.entries(attributes)
    .map(([key, value]) => `${key}: ${value}`)
    .join(', ');
};

// After
import { stripHtml } from '@/utils/sanitize';

const formatAttributes = (attributes) => {
  return Object.entries(attributes)
    .map(([key, value]) => `${stripHtml(key)}: ${stripHtml(value)}`)
    .join(', ');
};
```

---

### 1.4 Validate CSRF Token

**File**: `src/services/api.js`
**Lines**: 7-18 (CSRF token extraction)

**Current Implementation**:
```javascript
function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === name) return value;
  }
  return null;
}
```

**Enhanced Implementation**:
```javascript
function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');

  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === name) {
      // Validate token format (alphanumeric, 32-64 chars)
      if (value && /^[a-zA-Z0-9]{32,64}$/.test(value)) {
        return value;
      } else {
        console.error('Invalid CSRF token format detected');
        return null;
      }
    }
  }

  console.warn('CSRF token not found in cookies');
  return null;
}
```

---

### 1.5 Document localStorage Security Warning

**File**: `src/stores/ecommerce.js`
**Lines**: 8-10, 104, 285, 328 (localStorage usage)

**Action**: Add security comments

```javascript
// SECURITY WARNING: localStorage is vulnerable to XSS attacks
// TODO: Migrate to httpOnly cookies for auth tokens (requires backend changes)
// Current implementation stores sensitive data:
// - authToken: Authentication JWT
// - currentUser: User profile data
// - cartId: Shopping cart identifier
//
// Mitigation: All user input is sanitized via DOMPurify to prevent XSS
// Future: Move to httpOnly cookies or sessionStorage with server-side sessions

const authToken = localStorage.getItem('authToken');
```

**Note**: Full mitigation requires backend changes (out of current scope).

---

### Phase 1 Testing Checklist

- [ ] App loads without "undefined store" errors
- [ ] All API calls go through centralized client (check Network tab)
- [ ] No hardcoded URLs in Network tab requests
- [ ] XSS test: Enter `<script>alert('XSS')</script>` in product search - should not execute
- [ ] Product descriptions with HTML tags display safely (no script execution)
- [ ] CSRF token validation logs errors for invalid tokens
- [ ] Console shows warning if CSRF token is missing

---

## Phase 2: Environment Configuration [MUST DO - Day 1-2]

**Estimated Time**: 2-3 hours
**Risk Level**: Medium (test all API calls)
**Priority**: CRITICAL

### 2.1 Create Environment Files

**File**: `.env.development` (NEW FILE - Project Root)
```bash
# Development Environment Configuration
# Copy this file to .env.development.local to override

# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_ANALYTICS=false

# Build Configuration
VITE_APP_NAME=Mustard Ecommerce
VITE_APP_VERSION=1.0.0
```

**File**: `.env.production` (NEW FILE - Project Root)
```bash
# Production Environment Configuration

# API Configuration
VITE_API_BASE_URL=https://mustardimports.co.ke/api

# Feature Flags
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true

# Build Configuration
VITE_APP_NAME=Mustard Ecommerce
VITE_APP_VERSION=1.0.0
```

**File**: `.env.example` (NEW FILE - Project Root)
```bash
# Environment Variables Template
# Copy this file to .env.development or .env.production

# Required Variables
VITE_API_BASE_URL=https://your-api-domain.com/api

# Optional Variables
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
VITE_APP_NAME=Mustard Ecommerce
VITE_APP_VERSION=1.0.0
```

**Add to `.gitignore`**:
```
# Environment files
.env.local
.env.*.local
.env.development
.env.production
```

---

### 2.2 Update Vite Configuration

**File**: `vite.config.js`

```javascript
import { fileURLToPath, URL } from 'node:url';
import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';

export default defineConfig(({ mode }) => {
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },

    // Build optimization
    build: {
      // Code splitting
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'vue-router', 'pinia'],
            'axios': ['axios'],
            'charts': ['chart.js', 'vue-chartjs'],
          }
        }
      },

      // Source maps only in development
      sourcemap: mode === 'development',

      // Minification
      minify: mode === 'production' ? 'terser' : false,

      // Performance warnings
      chunkSizeWarningLimit: 1000,
    },

    // Development server
    server: {
      port: 3000,
      strictPort: false,
      proxy: {
        // Proxy API calls to backend during development
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    },

    // Preview server (for production builds)
    preview: {
      port: 4173,
    },
  };
});
```

---

### 2.3 Update API Service

**File**: `src/services/api.js` (ALREADY MODIFIED IN PHASE 1)

Ensure this validation is present:

```javascript
// Validate environment variables
const getBaseURL = () => {
  const url = import.meta.env.VITE_API_BASE_URL;

  if (!url) {
    throw new Error(
      'VITE_API_BASE_URL is not defined. Please check your .env file.'
    );
  }

  // Normalize URL (remove trailing slash)
  return url.replace(/\/$/, '');
};

// Log in development mode
if (import.meta.env.DEV) {
  console.log('[API] Base URL:', getBaseURL());
  console.log('[API] Mode:', import.meta.env.MODE);
}
```

---

### 2.4 Export API Client for Components

**File**: `src/services/api.js`

Add this export at the end of the file:

```javascript
// Export configured axios instance for use in components
export const apiClient = api;

// Export API methods
export default {
  createApiInstance,
  fetchCurrentUserInfo,
  fetchProducts,
  fetchCategories,
  // ... other methods
};
```

---

### Phase 2 Testing Checklist

- [ ] Run `npm run dev` - app starts without errors
- [ ] Check console for API base URL log (development only)
- [ ] Run `npm run build` - build succeeds
- [ ] Built files in `dist/` don't contain hardcoded URLs
- [ ] Change `VITE_API_BASE_URL` in `.env.development` - verify API calls use new URL
- [ ] Remove `VITE_API_BASE_URL` - app throws validation error at startup
- [ ] Production build uses production API URL
- [ ] Network tab shows all requests go to configured base URL

---

## Phase 3: Store Refactoring [RECOMMENDED - Days 2-3]

**Estimated Time**: 8-12 hours
**Risk Level**: High (core state management)
**Priority**: RECOMMENDED

### 3.1 Store Architecture

**Current State**: Single monolithic `ecommerce.js` (1,123 lines)

**Target State**: 5 focused store modules

```
src/stores/
├── index.js              # Store registry
├── ecommerce.js          # DEPRECATED (keep temporarily)
└── modules/
    ├── auth.js           # Authentication & user management (~150 lines)
    ├── cart.js           # Shopping cart operations (~200 lines)
    ├── products.js       # Product browsing & search (~300 lines)
    ├── orders.js         # Order history & tracking (~200 lines)
    └── admin.js          # Admin dashboard & reports (~150 lines)
```

---

### 3.2 Create Store Index

**File**: `src/stores/index.js` (NEW FILE)

```javascript
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

export default pinia;

// Export all store modules
export { useAuthStore } from './modules/auth';
export { useCartStore } from './modules/cart';
export { useProductsStore } from './modules/products';
export { useOrdersStore } from './modules/orders';
export { useAdminStore } from './modules/admin';
```

---

### 3.3 Create Auth Store

**File**: `src/stores/modules/auth.js` (NEW FILE)

```javascript
import { defineStore } from 'pinia';
import { apiClient } from '@/services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    currentUser: null,
    authToken: null,
    loading: false,
    error: null,
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && !!state.currentUser,
    userName: (state) => state.currentUser?.name || 'Guest',
    userEmail: (state) => state.currentUser?.email || '',
    isAdmin: (state) => state.currentUser?.role === 'admin',
  },

  actions: {
    async login(credentials) {
      this.loading = true;
      this.error = null;

      try {
        const response = await apiClient.post('/auth/login', credentials);

        this.authToken = response.data.token;
        this.currentUser = response.data.user;
        this.isAuthenticated = true;

        // Set authorization header for future requests
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${this.authToken}`;

        return { success: true };
      } catch (error) {
        this.error = error.response?.data?.message || 'Login failed';
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        await apiClient.post('/auth/logout');
      } catch (error) {
        console.error('Logout error:', error);
      } finally {
        // Clear state regardless of API response
        this.authToken = null;
        this.currentUser = null;
        this.isAuthenticated = false;
        delete apiClient.defaults.headers.common['Authorization'];
      }
    },

    async register(userData) {
      this.loading = true;
      this.error = null;

      try {
        const response = await apiClient.post('/auth/register', userData);

        // Auto-login after registration
        this.authToken = response.data.token;
        this.currentUser = response.data.user;
        this.isAuthenticated = true;

        return { success: true };
      } catch (error) {
        this.error = error.response?.data?.message || 'Registration failed';
        return { success: false, error: this.error };
      } finally {
        this.loading = false;
      }
    },

    async fetchCurrentUser() {
      if (!this.authToken) return;

      try {
        const response = await apiClient.get('/auth/me');
        this.currentUser = response.data;
        this.isAuthenticated = true;
      } catch (error) {
        // Token invalid or expired
        this.logout();
      }
    },

    // Initialize auth state from persisted storage
    initializeAuth() {
      if (this.authToken) {
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${this.authToken}`;
        this.fetchCurrentUser();
      }
    },
  },

  persist: {
    key: 'auth',
    paths: ['authToken', 'currentUser', 'isAuthenticated'],
  },
});
```

---

### 3.4 Create Cart Store

**File**: `src/stores/modules/cart.js` (NEW FILE)

```javascript
import { defineStore } from 'pinia';
import { apiClient } from '@/services/api';
import { useAuthStore } from './auth';

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    cartId: null,
    loading: false,
    error: null,
  }),

  getters: {
    itemCount: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),

    totalPrice: (state) => state.items.reduce(
      (sum, item) => sum + (item.product.price * item.quantity),
      0
    ),

    hasItems: (state) => state.items.length > 0,
  },

  actions: {
    async addItem(product, quantity = 1, attributes = {}) {
      const authStore = useAuthStore();

      // Check if item already exists
      const existingItem = this.items.find(
        item => item.product.id === product.id &&
                JSON.stringify(item.attributes) === JSON.stringify(attributes)
      );

      if (existingItem) {
        return this.updateQuantity(existingItem.id, existingItem.quantity + quantity);
      }

      try {
        const payload = {
          product_id: product.id,
          quantity,
          attributes,
          cart_id: this.cartId,
        };

        const response = await apiClient.post('/cart/items', payload);

        this.items.push({
          id: response.data.id,
          product,
          quantity,
          attributes,
        });

        if (!this.cartId) {
          this.cartId = response.data.cart_id;
        }

        return { success: true };
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to add item';
        return { success: false, error: this.error };
      }
    },

    async updateQuantity(itemId, newQuantity) {
      if (newQuantity < 1) {
        return this.removeItem(itemId);
      }

      try {
        await apiClient.patch(`/cart/items/${itemId}`, { quantity: newQuantity });

        const item = this.items.find(i => i.id === itemId);
        if (item) {
          item.quantity = newQuantity;
        }

        return { success: true };
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update quantity';
        return { success: false, error: this.error };
      }
    },

    async removeItem(itemId) {
      try {
        await apiClient.delete(`/cart/items/${itemId}`);

        this.items = this.items.filter(item => item.id !== itemId);

        return { success: true };
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to remove item';
        return { success: false, error: this.error };
      }
    },

    async clearCart() {
      try {
        if (this.cartId) {
          await apiClient.delete(`/cart/${this.cartId}`);
        }

        this.items = [];
        this.cartId = null;

        return { success: true };
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to clear cart';
        return { success: false, error: this.error };
      }
    },

    async fetchCart() {
      if (!this.cartId) return;

      this.loading = true;

      try {
        const response = await apiClient.get(`/cart/${this.cartId}`);
        this.items = response.data.items;
      } catch (error) {
        console.error('Failed to fetch cart:', error);
        // Cart might not exist anymore
        this.items = [];
        this.cartId = null;
      } finally {
        this.loading = false;
      }
    },
  },

  persist: {
    key: 'cart',
    paths: ['items', 'cartId'],
  },
});
```

---

### 3.5 Migration Strategy

**Step 1**: Create new store modules (auth.js, cart.js, products.js, orders.js, admin.js)

**Step 2**: Update main.js to initialize stores

```javascript
// src/main.js
import pinia from './stores';
import { useAuthStore } from './stores';

const app = createApp(App);

app.use(pinia);
app.use(router);

// Initialize auth on app start
const authStore = useAuthStore();
authStore.initializeAuth();

app.mount('#app');
```

**Step 3**: Migrate components one-by-one

```vue
<!-- Before -->
<script setup>
import { useEcommerceStore } from '@/stores/ecommerce';
const store = useEcommerceStore();

const login = () => store.login(credentials);
</script>

<!-- After -->
<script setup>
import { useAuthStore } from '@/stores';
const authStore = useAuthStore();

const login = () => authStore.login(credentials);
</script>
```

**Step 4**: Keep old store temporarily, mark as deprecated

```javascript
// src/stores/ecommerce.js
// @deprecated - Use individual store modules instead
// This store will be removed in v2.0
export const useEcommerceStore = defineStore('ecommerce', {
  // ... existing code
});
```

**Step 5**: Remove old store once all components migrated

---

### Phase 3 Testing Checklist

- [ ] Login/logout works (auth store)
- [ ] User profile displays correctly
- [ ] Cart add/remove/update operations work
- [ ] Cart persists after page refresh
- [ ] Product browsing and search work
- [ ] Order history displays
- [ ] Admin dashboard loads (if admin user)
- [ ] Vue DevTools shows separate store modules
- [ ] No "ecommerce store" references in production build
- [ ] localStorage shows separate store keys (auth, cart, etc.)

---

## Phase 4: Component Improvements [RECOMMENDED - Days 3-4]

**Estimated Time**: 6-8 hours
**Risk Level**: Low (additive changes)
**Priority**: RECOMMENDED

### 4.1 Extract MainLayout Modals

**Current**: MainLayout.vue (248 lines)
**Target**: MainLayout.vue (~60 lines)

**Create these new components**:

#### 4.1.1 LoginModal Component

**File**: `src/components/modals/LoginModal.vue` (NEW FILE)

```vue
<template>
  <Modal :show="show" @close="$emit('close')">
    <div class="login-modal">
      <h2>Login to Your Account</h2>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email Address</label>
          <input
            id="email"
            v-model="credentials.email"
            type="email"
            required
            aria-required="true"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            required
            aria-required="true"
          />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <p class="switch-auth">
        Don't have an account?
        <button @click="$emit('switchToRegister')" type="button">
          Register here
        </button>
      </p>
    </div>
  </Modal>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores';
import Modal from '@/components/common/Modal.vue';

defineProps({
  show: {
    type: Boolean,
    required: true,
  }
});

defineEmits(['close', 'switchToRegister']);

const authStore = useAuthStore();
const credentials = ref({ email: '', password: '' });
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  const result = await authStore.login(credentials.value);
  loading.value = false;

  if (result.success) {
    emit('close');
  } else {
    // Show error toast
    console.error(result.error);
  }
};
</script>
```

#### 4.1.2 useModals Composable

**File**: `src/composables/useModals.js` (NEW FILE)

```javascript
import { ref, watch } from 'vue';

const openModals = ref(new Set());

export function useModals() {
  const isModalOpen = (modalId) => openModals.value.has(modalId);

  const openModal = (modalId) => {
    openModals.value.add(modalId);
    updateBodyScroll();
  };

  const closeModal = (modalId) => {
    openModals.value.delete(modalId);
    updateBodyScroll();
  };

  const closeAllModals = () => {
    openModals.value.clear();
    updateBodyScroll();
  };

  const updateBodyScroll = () => {
    if (openModals.value.size > 0) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  };

  return {
    isModalOpen,
    openModal,
    closeModal,
    closeAllModals,
  };
}
```

#### 4.1.3 Updated MainLayout

**File**: `src/components/MainLayout.vue`

```vue
<template>
  <div class="main-layout">
    <TopRow />
    <SearchBar />
    <BottomNavigation />

    <main>
      <router-view />
    </main>

    <Footer />

    <!-- Modals -->
    <LoginModal
      :show="modals.isModalOpen('login')"
      @close="modals.closeModal('login')"
      @switchToRegister="switchToRegister"
    />

    <RegisterModal
      :show="modals.isModalOpen('register')"
      @close="modals.closeModal('register')"
      @switchToLogin="switchToLogin"
    />
  </div>
</template>

<script setup>
import { useModals } from '@/composables/useModals';
import LoginModal from '@/components/modals/LoginModal.vue';
import RegisterModal from '@/components/modals/RegisterModal.vue';
// ... other imports

const modals = useModals();

const switchToRegister = () => {
  modals.closeModal('login');
  modals.openModal('register');
};

const switchToLogin = () => {
  modals.closeModal('register');
  modals.openModal('login');
};
</script>
```

**Reduced from 248 lines to ~60 lines!**

---

### 4.2 Create Reusable SkeletonLoader

**File**: `src/components/common/SkeletonLoader.vue` (NEW FILE)

```vue
<template>
  <div
    class="skeleton-loader"
    :class="{ 'skeleton-animated': animated }"
    :style="loaderStyle"
  ></div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  width: {
    type: [String, Number],
    default: '100%',
  },
  height: {
    type: [String, Number],
    default: '20px',
  },
  variant: {
    type: String,
    default: 'rect',
    validator: (value) => ['rect', 'circle', 'text'].includes(value),
  },
  animated: {
    type: Boolean,
    default: true,
  },
});

const loaderStyle = computed(() => {
  const styles = {
    width: typeof props.width === 'number' ? `${props.width}px` : props.width,
    height: typeof props.height === 'number' ? `${props.height}px` : props.height,
  };

  if (props.variant === 'circle') {
    styles.borderRadius = '50%';
  } else if (props.variant === 'text') {
    styles.borderRadius = '4px';
  }

  return styles;
});
</script>

<style scoped>
.skeleton-loader {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
}

.skeleton-animated {
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
```

**Usage Example**:

```vue
<template>
  <div v-if="loading">
    <SkeletonLoader width="100%" height="40px" />
    <SkeletonLoader width="80%" height="20px" variant="text" />
    <SkeletonLoader width="60px" height="60px" variant="circle" />
  </div>
</template>
```

---

### 4.3 Add Prop Validation to Components

**Files to Update** (20+ components):

- TopRow.vue
- BottomNavigation.vue
- ProductCard.vue
- CategoryCard.vue
- OrderCard.vue
- All icon components (already done)

**Example**: `src/components/navigation/TopRow.vue`

```vue
<script setup>
defineProps({
  showSearchBar: {
    type: Boolean,
    default: true,
  },
  transparent: {
    type: Boolean,
    default: false,
  },
  fixed: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['openCart', 'openLogin']);
</script>
```

---

### 4.4 Create Error Boundary

**File**: `src/components/common/ErrorBoundary.vue` (NEW FILE)

```vue
<template>
  <div v-if="error" class="error-boundary">
    <div class="error-content">
      <h2>Something went wrong</h2>
      <p>{{ userMessage }}</p>

      <div v-if="isDevelopment" class="error-details">
        <h3>Error Details (Development Only)</h3>
        <pre>{{ error.message }}</pre>
        <pre>{{ error.stack }}</pre>
      </div>

      <div class="error-actions">
        <button @click="retry">Try Again</button>
        <button @click="reset">Reset Component</button>
        <button @click="reload">Reload Page</button>
      </div>
    </div>
  </div>

  <slot v-else></slot>
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue';

const props = defineProps({
  fallbackMessage: {
    type: String,
    default: 'An unexpected error occurred. Please try again.',
  },
});

const emit = defineEmits(['error']);

const error = ref(null);
const isDevelopment = import.meta.env.DEV;

onErrorCaptured((err, instance, info) => {
  error.value = err;
  emit('error', { error: err, instance, info });

  // Log in production (without exposing to user)
  if (!isDevelopment) {
    console.error('[ErrorBoundary]', err);
  }

  // Prevent error from propagating
  return false;
});

const userMessage = computed(() => {
  if (isDevelopment) {
    return error.value?.message || 'Unknown error';
  }
  return props.fallbackMessage;
});

const retry = () => {
  error.value = null;
};

const reset = () => {
  window.location.reload();
};

const reload = () => {
  window.location.href = '/';
};
</script>

<style scoped>
.error-boundary {
  padding: 2rem;
  background: #fff5f5;
  border: 2px solid #feb2b2;
  border-radius: 8px;
}

.error-details {
  margin-top: 1rem;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 4px;
  overflow-x: auto;
}

.error-actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
}
</style>
```

**Usage**:

```vue
<template>
  <ErrorBoundary>
    <MyComponent />
  </ErrorBoundary>
</template>
```

---

### Phase 4 Testing Checklist

- [ ] All modals open/close correctly
- [ ] Modal switching works (login ↔ register)
- [ ] No prop validation warnings in console (dev mode)
- [ ] Skeleton loaders display during data fetch
- [ ] Error boundary catches thrown errors (test by throwing in component)
- [ ] Body scroll locked when modal is open
- [ ] Error details only show in development mode
- [ ] Retry/reset/reload buttons work in error boundary

---

## Phase 5: Code Quality Improvements [OPTIONAL - Days 4-5]

**Estimated Time**: 4-6 hours
**Risk Level**: Very Low
**Priority**: NICE TO HAVE

### 5.1 Add Search Debouncing

**File**: `src/composables/useDebounce.js` (NEW FILE)

```javascript
import { ref, watch } from 'vue';

export function useDebounce(value, delay = 500) {
  const debouncedValue = ref(value.value);
  let timeout;

  watch(value, (newValue) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      debouncedValue.value = newValue;
    }, delay);
  });

  return debouncedValue;
}

export function useDebounceFn(fn, delay = 500) {
  let timeout;

  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      fn(...args);
    }, delay);
  };
}
```

**Update SearchBar.vue**:

```vue
<script setup>
import { ref } from 'vue';
import { useDebounce } from '@/composables/useDebounce';

const searchQuery = ref('');
const debouncedQuery = useDebounce(searchQuery, 500);

watch(debouncedQuery, (newQuery) => {
  if (newQuery.length >= 3) {
    performSearch(newQuery);
  }
});
</script>
```

---

### 5.2 Centralize Toast Notifications

**File**: `src/composables/useToast.js` (NEW FILE)

```javascript
import { useToast as useVueToast } from 'vue-toastification';

export function useToast() {
  const toast = useVueToast();

  return {
    success: (message, options = {}) => {
      toast.success(message, { timeout: 3000, ...options });
    },

    error: (message, options = {}) => {
      toast.error(message, { timeout: 5000, ...options });
    },

    warning: (message, options = {}) => {
      toast.warning(message, { timeout: 4000, ...options });
    },

    info: (message, options = {}) => {
      toast.info(message, { timeout: 3000, ...options });
    },

    apiError: (error) => {
      const message = error.response?.data?.message || error.message || 'An error occurred';
      toast.error(message, { timeout: 5000 });
    },
  };
}
```

**Usage**:

```javascript
import { useToast } from '@/composables/useToast';

const toast = useToast();

// Success
toast.success('Item added to cart');

// API error
try {
  await api.post('/cart/items', item);
} catch (error) {
  toast.apiError(error);
}
```

---

### 5.3 Conditional Logging Utility

**File**: `src/utils/logger.js` (NEW FILE)

```javascript
const isDevelopment = import.meta.env.DEV;

class Logger {
  log(...args) {
    if (isDevelopment) {
      console.log(...args);
    }
  }

  warn(...args) {
    if (isDevelopment) {
      console.warn(...args);
    }
  }

  error(...args) {
    // Always log errors, even in production
    console.error(...args);
  }

  info(...args) {
    if (isDevelopment) {
      console.info(...args);
    }
  }

  debug(...args) {
    if (isDevelopment && import.meta.env.VITE_ENABLE_DEBUG) {
      console.debug(...args);
    }
  }
}

export const logger = new Logger();
```

**Replace console.log statements**:

```javascript
// Before
console.log('Fetching products...');

// After
import { logger } from '@/utils/logger';
logger.log('Fetching products...');
```

---

### 5.4 Consolidate Router Files

**Action**: Delete `src/router/admin.js` and merge routes into `src/router/index.js`

**File**: `src/router/index.js`

```javascript
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomePage.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/admin/AdminDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        // Admin subroutes
      ],
    },
    // ... other routes
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    return { top: 0 };
  },
});

// Auth guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'home', query: { redirect: to.fullPath } });
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'home' });
  } else {
    next();
  }
});

export default router;
```

**Delete**: `src/router/admin.js`

---

### Phase 5 Testing Checklist

- [ ] Toast notifications appear on all actions
- [ ] Search doesn't fire on every keystroke (check Network tab)
- [ ] Pagination resets when filters change
- [ ] Page scrolls to top on pagination change
- [ ] No duplicate routes (check Vue Router DevTools)
- [ ] No console.log statements in production build
- [ ] Errors still logged in production

---

## Implementation Timeline

### Day 1: Critical Security & Environment Setup
**Morning** (4 hours):
- Fix App.vue store bug
- Remove hardcoded API URLs
- Add HTML sanitization
- Validate CSRF tokens

**Afternoon** (3 hours):
- Create .env files
- Update vite.config.js
- Test all API calls
- **Deploy to staging**

### Day 2: Store Refactoring Begins
**Morning** (4 hours):
- Create store index
- Build auth store module
- Build cart store module

**Afternoon** (4 hours):
- Build products store module
- Build orders store module
- Build admin store module

### Day 3: Store Migration
**Morning** (4 hours):
- Update App.vue and main.js
- Migrate auth components
- Migrate cart components

**Afternoon** (4 hours):
- Migrate product components
- Migrate order components
- Test all functionality
- **Deploy to staging**

### Day 4: Component Improvements
**Morning** (3 hours):
- Extract MainLayout modals
- Create useModals composable
- Create SkeletonLoader

**Afternoon** (3 hours):
- Add prop validation (20+ components)
- Create ErrorBoundary
- Test modal interactions

### Day 5: Polish & Quality
**Morning** (3 hours):
- Add debounced search
- Centralize toast notifications
- Create logger utility

**Afternoon** (3 hours):
- Consolidate router files
- Final testing
- Documentation updates
- **Deploy to staging, then production**

---

## Risk Management

### High-Risk Areas

#### 1. Store Refactoring (Phase 3)
**Risk**: Breaking all state management
**Mitigation**:
- Keep old ecommerce.js as fallback
- Migrate components incrementally
- Test each store module independently
- Create git tags before starting

**Rollback Plan**: Revert to tagged commit

#### 2. API Client Changes (Phase 2)
**Risk**: Breaking all API communication
**Mitigation**:
- Test locally first
- Verify all endpoints in Network tab
- Check auth headers on every request
- Test with invalid CSRF token

**Rollback Plan**: Revert api.js, restore hardcoded URLs temporarily

---

### Medium-Risk Areas

#### 3. Environment Configuration (Phase 2)
**Risk**: Missing variables in production
**Mitigation**:
- Validate at build time (throw error if missing)
- Document all variables in .env.example
- Test build process before deployment

**Rollback Plan**: Add missing variables to .env files

---

### Low-Risk Areas

#### 4. Security Fixes (Phase 1)
Pure bug fixes, minimal risk. Only risk is if DOMPurify is too aggressive.

**Mitigation**: Configure allowed tags appropriately

#### 5. Component Improvements (Phase 4)
Additive changes only, no breaking modifications.

#### 6. Code Quality (Phase 5)
Optional enhancements, can be skipped entirely.

---

## Testing Strategy

### Manual Testing (No Automated Tests Exist)

#### After Phase 1 (Security):
1. Launch app - no console errors
2. Try XSS injection in search: `<script>alert('XSS')</script>`
3. Try XSS in product description (admin panel)
4. Verify Network tab shows no hardcoded URLs
5. Check CSRF token in request headers

#### After Phase 2 (Environment):
1. Run `npm run dev` - app starts
2. Run `npm run build` - succeeds without errors
3. Change VITE_API_BASE_URL - verify API calls update
4. Remove VITE_API_BASE_URL - app throws error
5. Check dist/ files for hardcoded URLs (should be none)

#### After Phase 3 (Store):
1. Login/logout flow
2. Add/remove cart items
3. Browse products
4. View order history
5. Check admin dashboard (admin user)
6. Refresh page - state persists
7. Check localStorage keys (should show separate stores)
8. Vue DevTools - verify store modules exist

#### After Phase 4 (Components):
1. Open/close all modals
2. Switch between login/register
3. Check for prop warnings (dev mode)
4. Verify skeleton loaders during fetch
5. Throw error in component - error boundary catches it
6. Verify body scroll locks with modal open

#### After Phase 5 (Quality):
1. Search - verify debouncing (Network tab)
2. Toast notifications on actions
3. Pagination resets with filters
4. Page scrolls to top on pagination
5. No duplicate routes (Router DevTools)
6. Build production - no console.logs

---

### User Acceptance Testing (UAT)

Create a testing checklist for QA team:

**Authentication**:
- [ ] Register new account
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Logout
- [ ] Session persists after refresh

**Shopping**:
- [ ] Browse products
- [ ] Search products
- [ ] Filter by category
- [ ] Add to cart
- [ ] Update quantity
- [ ] Remove from cart
- [ ] Cart persists after refresh

**Checkout**:
- [ ] Proceed to checkout
- [ ] Enter shipping info
- [ ] Select payment method
- [ ] Complete order
- [ ] View order confirmation

**Admin** (if applicable):
- [ ] Access admin dashboard
- [ ] View reports
- [ ] Manage products
- [ ] Manage orders

---

## Documentation Requirements

### 1. SECURITY.md (NEW FILE)

```markdown
# Security Documentation

## XSS Protection
All user-generated content is sanitized using DOMPurify before rendering.

## CSRF Protection
CSRF tokens are validated on all state-changing requests.

## Authentication
WARNING: Auth tokens currently stored in localStorage (XSS vulnerable).
Future: Migrate to httpOnly cookies (requires backend changes).

## Environment Variables
Never commit .env files to version control.
```

### 2. ENVIRONMENT_SETUP.md (NEW FILE)

```markdown
# Environment Setup Guide

## Required Environment Variables

### Development (.env.development)
VITE_API_BASE_URL=http://localhost:8000/api

### Production (.env.production)
VITE_API_BASE_URL=https://mustardimports.co.ke/api

## Setup Instructions
1. Copy .env.example to .env.development
2. Update VITE_API_BASE_URL with your API endpoint
3. Run `npm run dev`
```

### 3. Update README.md

Add section:

```markdown
## Environment Configuration

This project uses environment variables for configuration.

1. Copy `.env.example` to `.env.development`
2. Update `VITE_API_BASE_URL` with your API endpoint
3. See [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md) for details

## Security

See [SECURITY.md](./SECURITY.md) for security considerations.
```

---

## Success Metrics

### Must Achieve (Phases 1-2)
- ✅ Zero critical security vulnerabilities
- ✅ Zero hardcoded URLs in codebase
- ✅ 100% API compatibility maintained
- ✅ Environment configuration working
- ✅ All API calls use centralized client

### Should Achieve (Phases 3-4)
- ✅ Store files reduced from 1 (1,123 lines) to 5 modules (avg 200 lines each)
- ✅ MainLayout reduced from 248 to ~60 lines (75% reduction)
- ✅ All 20+ reusable components have prop validation
- ✅ Error handling centralized (ErrorBoundary + useToast)
- ✅ No prop validation warnings in console

### Nice to Have (Phase 5)
- ✅ Toast notifications on all user actions
- ✅ Search API calls reduced by 80%+ (debouncing)
- ✅ Bundle size reduced (code splitting)
- ✅ No console.log in production builds
- ✅ Documentation complete

---

## Migration Rollout Plan

### Step 1: Create Feature Branch
```bash
git checkout -b refactor/security-and-quality
```

### Step 2: Implement Phase 1 + 2
```bash
# Phase 1: Security fixes
git add .
git commit -m "fix: critical security vulnerabilities and store initialization"

# Phase 2: Environment config
git add .
git commit -m "feat: add environment variable configuration"

# Tag for rollback point
git tag v1.0-phase1-2
```

### Step 3: Deploy to Staging
```bash
npm run build
# Deploy dist/ to staging server
# Run full UAT testing
```

### Step 4: Implement Phase 3
```bash
git add .
git commit -m "refactor: split monolithic store into focused modules"
git tag v1.0-phase3
```

### Step 5: Deploy to Staging Again
```bash
npm run build
# Deploy dist/ to staging server
# Run full UAT testing
```

### Step 6: Implement Phase 4 + 5
```bash
git add .
git commit -m "feat: improve component structure and code quality"
git tag v1.0-complete
```

### Step 7: Final Deployment
```bash
# Create pull request
# Code review
# Merge to master
# Deploy to production
```

### Rollback Strategy
```bash
# If Phase 1-2 breaks production:
git reset --hard v1.0-baseline
git push --force

# If Phase 3 breaks production:
git reset --hard v1.0-phase1-2
git push --force

# If everything breaks:
git revert <commit-hash>
```

---

## Next Steps

1. ✅ **Review this plan** with your team
2. ⏳ **Get approval** for phases to implement (recommend minimum: Phases 1-2)
3. ⏳ **Create feature branch**: `refactor/security-and-quality`
4. ⏳ **Start with Phase 1** (security fixes) - highest priority, lowest risk
5. ⏳ **Deploy to staging** after each phase
6. ⏳ **Create pull requests** for code review
7. ⏳ **Full UAT testing** before production deployment

---

## Appendix: Critical Files Reference

### Phase 1 Files
1. `src/App.vue` (line 14)
2. `src/services/api.js`
3. `src/stores/ecommerce.js` (lines 500, 913)
4. `src/components/navigation/SearchBar.vue` (line 87)
5. `src/components/home/recents/HomeCarousel.vue` (line 72)
6. `src/views/ProductDetails.vue`
7. `src/views/Cart.vue` (line 35)
8. `src/utils/sanitize.js` (NEW)

### Phase 2 Files
1. `.env.development` (NEW)
2. `.env.production` (NEW)
3. `.env.example` (NEW)
4. `vite.config.js`
5. `.gitignore`

### Phase 3 Files
1. `src/stores/index.js` (NEW)
2. `src/stores/modules/auth.js` (NEW)
3. `src/stores/modules/cart.js` (NEW)
4. `src/stores/modules/products.js` (NEW)
5. `src/stores/modules/orders.js` (NEW)
6. `src/stores/modules/admin.js` (NEW)

### Phase 4 Files
1. `src/components/MainLayout.vue`
2. `src/components/modals/LoginModal.vue` (NEW)
3. `src/components/modals/RegisterModal.vue` (NEW)
4. `src/composables/useModals.js` (NEW)
5. `src/components/common/SkeletonLoader.vue` (NEW)
6. `src/components/common/ErrorBoundary.vue` (NEW)
7. 20+ components for prop validation

### Phase 5 Files
1. `src/composables/useDebounce.js` (NEW)
2. `src/composables/useToast.js` (NEW)
3. `src/utils/logger.js` (NEW)
4. `src/router/index.js`
5. Delete: `src/router/admin.js`

---

## Questions or Issues?

If you encounter problems during implementation:

1. Check the Testing Checklist for your current phase
2. Review the Risk Management section
3. Refer to the Rollback Strategy
4. Create a git tag before making significant changes

**Good luck with the refactoring!** 🚀
