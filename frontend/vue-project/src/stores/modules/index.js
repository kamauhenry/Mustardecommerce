/**
 * Module Stores Index
 * Central export point for all Pinia module stores
 *
 * Usage:
 * import { useAuthStore, useCartStore, useProductsStore } from '@/stores/modules';
 *
 * Or individually:
 * import { useAuthStore } from '@/stores/modules/auth';
 */

export { useAuthStore } from './auth';
export { useCartStore } from './cart';
export { useProductsStore } from './products';
export { useSearchStore } from './search';
export { useOrdersStore } from './orders';
export { useUserStore } from './user';
export { useAdminStore } from './admin';

/**
 * Initialize all stores
 * Call this function in your main.js or App.vue to ensure all stores are ready
 * This is particularly useful for stores that need to initialize from localStorage
 */
export function initializeStores() {
  // Import stores
  const { useAuthStore } = require('./auth');
  const { useCartStore } = require('./cart');
  const { useUserStore } = require('./user');
  const { useSearchStore } = require('./search');

  // Initialize stores that need setup
  const authStore = useAuthStore();
  const cartStore = useCartStore();
  const userStore = useUserStore();
  const searchStore = useSearchStore();

  // Initialize auth
  authStore.initAuth();

  // Initialize cart
  cartStore.initCart();

  // Initialize user
  userStore.initUser();

  // Initialize search
  searchStore.initSearch();

  console.log('[Stores] All module stores initialized');
}
