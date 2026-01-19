# Phase 3: Store Refactoring Migration Guide

## Overview

This guide explains how to migrate from the old monolithic `ecommerce.js` store to the new modular store architecture.

## What Was Created

### Composables (DRY Utilities)

Located in `src/stores/composables/`:

1. **useApiCall.js** - Standardized API calls with loading/error handling
2. **useLocalStorage.js** - Safe localStorage operations with reactivity
3. **useToast.js** - Centralized toast notifications
4. **useApiInstance.js** - API instance management with token handling

### Module Stores

Located in `src/stores/modules/`:

1. **auth.js** (~150 lines) - Authentication & user session
2. **cart.js** (~200 lines) - Shopping cart operations
3. **products.js** (~300 lines) - Product catalog & filtering
4. **search.js** (~150 lines) - Search functionality
5. **orders.js** (~250 lines) - Order management
6. **user.js** (~150 lines) - User profile & preferences
7. **admin.js** (~100 lines) - Admin operations
8. **index.js** - Central export point

## Migration Strategy

### Phase 3A: ✅ COMPLETED
- ✅ Created all composables
- ✅ Created all module stores
- ✅ Build verified successfully
- ✅ Dev server tested

### Phase 3B: Component Migration (Next Steps)

Components can now be migrated **one at a time** without breaking existing functionality. Both old and new stores can coexist during migration.

## How to Use the New Stores

### 1. Import Stores

```javascript
// Import individual stores
import { useAuthStore } from '@/stores/modules/auth';
import { useCartStore } from '@/stores/modules/cart';
import { useProductsStore } from '@/stores/modules/products';

// Or import multiple at once
import { useAuthStore, useCartStore, useProductsStore } from '@/stores/modules';
```

### 2. Use Stores in Components

**Old Way (ecommerce.js):**
```javascript
import { useEcommerceStore } from '@/stores/ecommerce';

export default {
  setup() {
    const store = useEcommerceStore();

    const login = async () => {
      await store.login(email.value, password.value);
      if (store.loginMessage) {
        alert(store.loginMessage);
      }
    };

    return { login };
  }
}
```

**New Way (auth.js module):**
```javascript
import { useAuthStore } from '@/stores/modules/auth';

export default {
  setup() {
    const authStore = useAuthStore();

    const login = async () => {
      const success = await authStore.login(email.value, password.value);
      // Toast notifications are automatic!
    };

    return { login, isLoggingIn: authStore.isLoggingIn };
  }
}
```

### 3. Using Composables

**Example: API Call with Loading State**

```javascript
import { useApiCall } from '@/stores/composables/useApiCall';
import { useApiInstance } from '@/stores/composables/useApiInstance';

export default {
  setup() {
    const { execute, loading, error, data } = useApiCall();
    const { api } = useApiInstance();

    const fetchData = async () => {
      await execute(async () => {
        return await api.get('/some-endpoint');
      });

      // data.value now contains the response
      console.log(data.value);
    };

    return { fetchData, loading, error };
  }
}
```

**Example: LocalStorage Management**

```javascript
import { useLocalStorage, STORAGE_KEYS } from '@/stores/composables/useLocalStorage';

export default {
  setup() {
    const { value: theme, remove } = useLocalStorage(STORAGE_KEYS.THEME, 'light');

    // Reactive - automatically syncs to localStorage
    const toggleTheme = () => {
      theme.value = theme.value === 'light' ? 'dark' : 'light';
    };

    return { theme, toggleTheme };
  }
}
```

**Example: Toast Notifications**

```javascript
import { toast } from '@/stores/composables/useToast';

export default {
  setup() {
    const saveData = async () => {
      try {
        // ... save logic
        toast.success('Data saved successfully');
      } catch (error) {
        toast.error('Failed to save data');
      }
    };

    return { saveData };
  }
}
```

## Component Migration Examples

### Example 1: Login Component

**File: src/components/LoginForm.vue**

**Before:**
```javascript
import { useEcommerceStore } from '@/stores/ecommerce';

export default {
  setup() {
    const store = useEcommerceStore();
    const email = ref('');
    const password = ref('');

    const handleLogin = async () => {
      await store.login(email.value, password.value);
    };

    return {
      email,
      password,
      handleLogin,
      loginMessage: store.loginMessage,
    };
  }
}
```

**After:**
```javascript
import { useAuthStore } from '@/stores/modules/auth';

export default {
  setup() {
    const authStore = useAuthStore();
    const email = ref('');
    const password = ref('');

    const handleLogin = async () => {
      await authStore.login(email.value, password.value);
    };

    return {
      email,
      password,
      handleLogin,
      isLoggingIn: authStore.isLoggingIn,
      // loginMessage removed - toast handles notifications
    };
  }
}
```

### Example 2: Cart Component

**File: src/views/Cart.vue**

**Before:**
```javascript
import { useEcommerceStore } from '@/stores/ecommerce';

export default {
  setup() {
    const store = useEcommerceStore();

    const addToCart = (product) => {
      store.cart.push(product);
      localStorage.setItem('cart', JSON.stringify(store.cart));
      alert('Added to cart');
    };

    return {
      cart: store.cart,
      addToCart,
    };
  }
}
```

**After:**
```javascript
import { useCartStore } from '@/stores/modules/cart';

export default {
  setup() {
    const cartStore = useCartStore();

    const addToCart = (product) => {
      cartStore.addToCart(product, 1);
      // localStorage sync is automatic
      // toast notification is automatic
    };

    return {
      cart: cartStore.cartItems,
      cartTotal: cartStore.cartTotal,
      cartItemCount: cartStore.cartItemCount,
      addToCart,
    };
  }
}
```

### Example 3: Product List Component

**File: src/views/ProductList.vue**

**Before:**
```javascript
import { useEcommerceStore } from '@/stores/ecommerce';

export default {
  setup() {
    const store = useEcommerceStore();
    const loading = ref(false);

    const fetchProducts = async () => {
      loading.value = true;
      try {
        await store.fetchProducts();
      } catch (error) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchProducts);

    return {
      products: store.products,
      loading,
    };
  }
}
```

**After:**
```javascript
import { useProductsStore } from '@/stores/modules/products';

export default {
  setup() {
    const productsStore = useProductsStore();

    onMounted(() => {
      productsStore.fetchProducts();
    });

    return {
      products: productsStore.products,
      loading: productsStore.isLoadingProducts,
      // Bonus: pagination built-in
      currentPage: productsStore.currentPage,
      totalPages: productsStore.totalPages,
      nextPage: productsStore.nextPage,
      previousPage: productsStore.previousPage,
    };
  }
}
```

## Store API Reference

### Auth Store (useAuthStore)

**State:**
- `currentUser` - Current user object
- `isAuthenticated` - Boolean authentication status
- `isLoggingIn` - Login loading state

**Actions:**
- `login(email, password)` - Login user
- `logout()` - Logout user
- `register(userData)` - Register new user
- `verifyToken()` - Verify auth token
- `refreshUser()` - Refresh user data

### Cart Store (useCartStore)

**State:**
- `cartItems` - Array of cart items
- `cartItemCount` - Total items in cart
- `cartTotal` - Total cart value

**Actions:**
- `addToCart(product, quantity, attributes)` - Add item
- `removeFromCart(productId, attributes)` - Remove item
- `updateQuantity(productId, quantity, attributes)` - Update quantity
- `clearCart()` - Clear entire cart
- `checkout(orderData)` - Checkout

### Products Store (useProductsStore)

**State:**
- `products` - Product list
- `categories` - Category list
- `currentProduct` - Selected product
- `isLoadingProducts` - Loading state

**Actions:**
- `fetchProducts(page, filters)` - Fetch products with filters
- `fetchProduct(id)` - Fetch single product
- `fetchCategories()` - Fetch categories
- `fetchLatestProducts(limit)` - Fetch latest products
- `applyFilters(filters)` - Apply filters
- `nextPage()` / `previousPage()` - Pagination

### Search Store (useSearchStore)

**State:**
- `searchQuery` - Current search query
- `searchResults` - Search results
- `recentSearches` - Recent searches
- `isSearching` - Loading state

**Actions:**
- `search(query, page)` - Search products
- `getSuggestions(query)` - Get search suggestions
- `clearResults()` - Clear search results
- `clearRecentSearches()` - Clear history

### Orders Store (useOrdersStore)

**State:**
- `orders` - Order list
- `currentOrder` - Selected order
- `pendingOrders` - Pending orders
- `completedOrders` - Completed orders

**Actions:**
- `fetchOrders(page)` - Fetch order history
- `fetchOrder(id)` - Fetch single order
- `createOrder(orderData)` - Create order
- `cancelOrder(id)` - Cancel order
- `trackOrder(trackingNumber)` - Track order

### User Store (useUserStore)

**State:**
- `profile` - User profile
- `addresses` - User addresses
- `wishlist` - Wishlist items

**Actions:**
- `fetchProfile()` - Fetch user profile
- `updateProfile(data)` - Update profile
- `changePassword(current, new)` - Change password
- `fetchAddresses()` - Fetch addresses
- `addAddress(data)` - Add address
- `addToWishlist(product)` - Add to wishlist
- `removeFromWishlist(id)` - Remove from wishlist

### Admin Store (useAdminStore)

**State:**
- `dashboardStats` - Dashboard statistics

**Actions:**
- `fetchDashboardStats()` - Fetch stats
- `manageProduct(action, data, id)` - Manage products
- `manageCategory(action, data, id)` - Manage categories
- `updateOrderStatus(id, status)` - Update order status
- `fetchUsers(page)` - Fetch users
- `exportData(type, filters)` - Export data

## Benefits of New Architecture

### 1. DRY Principle
- **Before:** 40+ duplicate try/catch blocks
- **After:** Single `useApiCall` composable

### 2. Clear Boundaries
- **Before:** 1,123-line monolithic store
- **After:** 7 focused modules (~150 lines each)

### 3. Better Testing
- Each module can be tested independently
- Composables are pure functions

### 4. Easier Maintenance
- Changes isolated to specific modules
- Clear single responsibility

### 5. Automatic Features
- Toast notifications (no manual alerts)
- Loading states (built into every action)
- Error handling (standardized)
- localStorage sync (automatic)

## Next Steps

1. **Test Current Implementation**
   - Run `npm run dev`
   - Verify no console errors
   - Check that old store still works

2. **Migrate Components (One at a Time)**
   - Start with small components (e.g., LoginForm)
   - Test thoroughly after each migration
   - Both stores can coexist during migration

3. **Remove Old Store**
   - After all components migrated
   - Delete `src/stores/ecommerce.js`
   - Update imports

4. **Run npm audit fix**
   - Address remaining vulnerabilities
   - Per your preference to do this after Phase 2/3 testing

## Rollback Plan

If issues occur during migration:

1. **Immediate Rollback:**
   - Components still using old store work fine
   - Simply revert component changes

2. **Full Rollback:**
   - Delete `src/stores/composables/` directory
   - Delete `src/stores/modules/` directory
   - All components still using old store continue to work

## Support

For issues or questions:
- Check console for error messages
- Review store API reference above
- Compare migration examples
- Test in development mode first

---

**Status:** Phase 3A Complete ✅
**Next:** Begin component migration (Phase 3B)
