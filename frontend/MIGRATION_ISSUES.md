# Store Migration - UI Issues & Mismatches Report

## Critical Issues Found

### 1. **Checkout.vue - Missing retryFetch method**
- **Location**: [Checkout.vue:13](src/views/Checkout.vue#L13)
- **Issue**: Template uses `@click="retryFetch"` but the method is not defined in setup() return
- **Fix**: Add `retryFetch: fetchOrder` to the return statement
```javascript
return {
  // ... existing returns
  retryFetch: fetchOrder,  // Add this line
  grey,
};
```

### 2. **IconCart.vue - Non-reactive cart count**
- **Location**: [IconCart.vue:55-64](src/components/icons/IconCart.vue#L55-L64)
- **Issue**: Using old ecommerce store, accessing `cartItemCount` directly (not reactive)
- **Current Code**:
```javascript
import { useEcommerceStore } from '@/stores/ecommerce';
export default {
  setup() {
    const store = useEcommerceStore();
    return {
      cartItemCount: store.cartItemCount,  // Not reactive!
    };
  },
};
```
- **Fix**: Migrate to use new cart store with computed
```javascript
import { computed } from 'vue';
import { useCartStore } from '@/stores/modules/cart';
export default {
  setup() {
    const cartStore = useCartStore();
    return {
      cartItemCount: computed(() => cartStore.cartItemCount),
    };
  },
};
```

### 3. **HamburgerMenu.vue - Using old ecommerce store**
- **Location**: [HamburgerMenu.vue:134-145](src/components/navigation/HamburgerMenu.vue#L134-L145)
- **Issue**: Still using old ecommerce store for categories and search
- **Current Dependencies**:
  - Categories: `store.categories`, `store.loading.categories`, `store.error.categories`, `store.fetchCategories()`
  - Search: `store.searchSuggestions`, `store.fetchSearchSuggestions()`, `store.setSearchResults()`, etc.
- **Fix**: Migrate to use `useProductsStore` for categories and `useSearchStore` for search functionality

## Files Still Using Old Store (Not Yet Migrated)

### Views
1. **ProductDetails.vue** - Intentionally hybrid (uses old store for cart operations)
2. **Confirmation.vue** - Not migrated
3. **CompletedOrders.vue** - Not migrated

### Components
1. **HamburgerMenu.vue** - Categories & Search (CRITICAL - used in main navigation)
2. **IconCart.vue** - Cart count display (CRITICAL - visible on every page)
3. **admin/Products.vue** - Admin product management
4. **admin/Categories.vue** - Admin category management
5. **admin/Orders.vue** - Admin order management
6. **admin/Settings.vue** - Admin settings
7. **admin/RegisterAdmin.vue** - Admin registration

## Verified Working Files

### Successfully Migrated Views ✅
- HomePage.vue
- CategoryProducts.vue
- MOQCampaigns.vue
- payandpick.vue
- Cart.vue
- Orders.vue
- Checkout.vue (needs retryFetch fix)
- Profile.vue
- OrderDetails.vue

### Successfully Migrated Components ✅
- PagesRow.vue
- Dashboard.vue (admin)
- AdminLayout.vue (admin)

## Recommendations

### Priority 1 (Critical - Affects All Pages)
1. **Fix Checkout.vue** - Add missing `retryFetch` method
2. **Migrate IconCart.vue** - Cart icon visible on every page
3. **Migrate HamburgerMenu.vue** - Main navigation component

### Priority 2 (Important - User-Facing)
4. **Migrate Confirmation.vue** - Post-checkout page
5. **Migrate CompletedOrders.vue** - User order history

### Priority 3 (Admin Only)
6. Admin components can be migrated last as they're only used by admin users

## Store Methods Availability Check

All migrated stores properly expose their methods:
- ✅ `productsStore` - Has categories, loading states, error states
- ✅ `cartStore` - Has cartItemCount computed property
- ✅ `searchStore` - Has search suggestions and methods
- ✅ `authStore` - Has authentication state
- ✅ `ordersStore` - Has order fetching methods
- ✅ `userStore` - Has profile and address methods

## Testing Recommendations

After fixes are applied:
1. Test cart icon updates when adding/removing items
2. Test category navigation from hamburger menu
3. Test search functionality in hamburger menu
4. Test checkout retry functionality
5. Verify all page transitions work correctly
