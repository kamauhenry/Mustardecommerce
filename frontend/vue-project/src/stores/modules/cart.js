import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApiCall } from '../composables/useApiCall';
import { useApiInstance } from '../composables/useApiInstance';
import { LocalStorageManager, STORAGE_KEYS } from '../composables/useLocalStorage';
import { toast } from '../composables/useToast';

/**
 * Shopping Cart Store Module
 * Handles cart operations: add, remove, update quantities, checkout
 */
export const useCartStore = defineStore('cart', () => {
  // State
  const cartItems = ref(LocalStorageManager.get(STORAGE_KEYS.CART, []));
  const isLoadingCart = ref(false);
  const checkoutLoading = ref(false);

  // Server-side cart state (for authenticated users)
  const cart = ref(null);
  const isCreatingOrder = ref(false);

  // API instance
  const { api } = useApiInstance();

  // Computed
  const cartItemCount = computed(() => {
    return cartItems.value.reduce((total, item) => total + (item.quantity || 1), 0);
  });

  const cartTotal = computed(() => {
    return cartItems.value.reduce((total, item) => {
      const price = parseFloat(item.price || 0);
      const quantity = parseInt(item.quantity || 1);
      return total + (price * quantity);
    }, 0);
  });

  const hasItems = computed(() => cartItems.value.length > 0);

  /**
   * Sync cart to localStorage
   */
  const syncCart = () => {
    LocalStorageManager.set(STORAGE_KEYS.CART, cartItems.value);
  };

  /**
   * Add item to cart
   * @param {Object} product - Product to add
   * @param {number} quantity - Quantity to add
   * @param {Object} selectedAttributes - Selected product attributes
   */
  const addToCart = async (product, quantity = 1, selectedAttributes = {}) => {
    try {
      // Check if item already exists in cart
      const existingIndex = cartItems.value.findIndex(item => {
        // Match by product ID and attributes
        if (item.id !== product.id) return false;

        // Check if attributes match
        const itemAttrs = JSON.stringify(item.selectedAttributes || {});
        const newAttrs = JSON.stringify(selectedAttributes);
        return itemAttrs === newAttrs;
      });

      if (existingIndex !== -1) {
        // Update quantity if item exists
        cartItems.value[existingIndex].quantity += quantity;
        toast.success('Cart updated');
      } else {
        // Add new item
        cartItems.value.push({
          id: product.id,
          name: product.name,
          price: product.price,
          image: product.image || product.images?.[0]?.image,
          quantity,
          selectedAttributes,
          stock: product.stock_quantity,
        });
        toast.success('Added to cart');
      }

      syncCart();
    } catch (error) {
      toast.error('Failed to add to cart');
      console.error('Add to cart error:', error);
    }
  };

  /**
   * Remove item from cart
   * @param {number} productId - Product ID to remove
   * @param {Object} selectedAttributes - Attributes to match
   */
  const removeFromCart = (productId, selectedAttributes = {}) => {
    const index = cartItems.value.findIndex(item => {
      if (item.id !== productId) return false;
      const itemAttrs = JSON.stringify(item.selectedAttributes || {});
      const matchAttrs = JSON.stringify(selectedAttributes);
      return itemAttrs === matchAttrs;
    });

    if (index !== -1) {
      cartItems.value.splice(index, 1);
      syncCart();
      toast.info('Removed from cart');
    }
  };

  /**
   * Update item quantity
   * @param {number} productId - Product ID
   * @param {number} quantity - New quantity
   * @param {Object} selectedAttributes - Attributes to match
   */
  const updateQuantity = (productId, quantity, selectedAttributes = {}) => {
    const item = cartItems.value.find(item => {
      if (item.id !== productId) return false;
      const itemAttrs = JSON.stringify(item.selectedAttributes || {});
      const matchAttrs = JSON.stringify(selectedAttributes);
      return itemAttrs === matchAttrs;
    });

    if (item) {
      if (quantity <= 0) {
        removeFromCart(productId, selectedAttributes);
      } else {
        item.quantity = quantity;
        syncCart();
      }
    }
  };

  /**
   * Clear entire cart
   */
  const clearCart = () => {
    cartItems.value = [];
    syncCart();
    toast.info('Cart cleared');
  };

  /**
   * Fetch cart from server (if user is authenticated)
   */
  const fetchCart = async () => {
    const { execute } = useApiCall();
    isLoadingCart.value = true;

    try {
      const response = await execute(
        async () => api.get('/carts/current/'),
        { showToast: false }
      );

      cart.value = response;
      if (response?.items) {
        cartItems.value = response.items;
        syncCart();
      }
      return response;
    } catch (error) {
      console.error('Failed to fetch cart:', error);
      // Use local cart if server fetch fails
      return null;
    } finally {
      isLoadingCart.value = false;
    }
  };

  /**
   * Create order from cart
   * @returns {Promise<Object|null>} - Order response or null
   */
  const createOrderFromCart = async () => {
    const { execute } = useApiCall();
    isCreatingOrder.value = true;

    try {
      const response = await execute(
        async () => api.post(`/carts/${cart.value?.id}/create_order/`),
        { showToast: false }
      );

      return response;
    } catch (error) {
      const message = error.response?.data?.error ||
                     error.response?.data?.message ||
                     'Failed to create order';
      toast.error(message);
      throw error;
    } finally {
      isCreatingOrder.value = false;
    }
  };

  /**
   * Sync local cart to server
   */
  const syncCartToServer = async () => {
    if (!hasItems.value) return;

    const { execute } = useApiCall();

    try {
      await execute(
        async () => api.post('/cart/sync/', { items: cartItems.value }),
        { showToast: false }
      );
    } catch (error) {
      console.error('Failed to sync cart to server:', error);
    }
  };

  /**
   * Checkout - create order from cart
   * @param {Object} orderData - Order information (shipping, payment, etc.)
   * @returns {Promise<Object|null>} - Order response or null
   */
  const checkout = async (orderData) => {
    const { execute } = useApiCall();
    checkoutLoading.value = true;

    try {
      const response = await execute(
        async () => api.post('/orders/checkout/', {
          items: cartItems.value,
          ...orderData,
        }),
        {
          successMessage: 'Order placed successfully!',
        }
      );

      // Clear cart after successful checkout
      clearCart();

      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Checkout failed';
      toast.error(message);
      return null;
    } finally {
      checkoutLoading.value = false;
    }
  };

  /**
   * Validate cart items (check stock, prices, etc.)
   * @returns {Promise<boolean>} - Validation result
   */
  const validateCart = async () => {
    if (!hasItems.value) {
      toast.warning('Cart is empty');
      return false;
    }

    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.post('/cart/validate/', { items: cartItems.value }),
        { showToast: false }
      );

      if (response?.valid) {
        return true;
      } else {
        // Update cart with validated items
        if (response?.items) {
          cartItems.value = response.items;
          syncCart();
        }
        toast.warning(response?.message || 'Some items in your cart need attention');
        return false;
      }
    } catch (error) {
      toast.error('Failed to validate cart');
      return false;
    }
  };

  /**
   * Initialize cart from localStorage
   */
  const initCart = () => {
    const savedCart = LocalStorageManager.get(STORAGE_KEYS.CART, []);
    cartItems.value = savedCart;
  };

  // Initialize on store creation
  initCart();

  return {
    // State
    cartItems,
    isLoadingCart,
    checkoutLoading,
    cart,
    isCreatingOrder,

    // Computed
    cartItemCount,
    cartTotal,
    hasItems,

    // Actions
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    fetchCart,
    syncCartToServer,
    checkout,
    validateCart,
    initCart,
    createOrderFromCart,
  };
});
