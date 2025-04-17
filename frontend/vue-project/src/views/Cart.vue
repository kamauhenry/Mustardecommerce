<template>
  <MainLayout>
    <div class="cart-container">
      <h2 class="cart-title">Your Cart ({{ cartItemCount }} items)</h2>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your cart...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="retryFetch" class="retry-button">Try Again</button>
      </div>

      <div v-else-if="!isAuthenticated" class="auth-prompt">
        <p>Please login to view and manage your cart</p>
        <button @click="goToLogin" class="login-button">Login</button>
      </div>

      <div v-else-if="cartItems.length === 0" class="empty-cart">
        <p>Your cart is empty</p>
        <button @click="goToProducts" class="shop-button">Start Shopping</button>
      </div>

      <div v-else class="cart-items">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <div class="item-image">
            <img :src="item.variant?.image || item.product?.picture || grey" alt="Item image" />
          </div>
          <div class="item-details">
            <h3>{{ item.product_name }}</h3>
            <p v-if="item.variant">Color: {{ item.variant_info.color }}</p>
            <p v-if="item.variant">Size: {{ item.variant_info.size }}</p>
            <p>Quantity: {{ item.quantity }}</p>
            <p>Price: KES {{ formatPrice(item.price_per_piece || 0) }}</p>
            <p>Total: KES {{ formatPrice(item.line_total) }}</p>
          </div>
          <div class="item-actions">
            <button @click="updateQuantity(item.id, item.quantity - 1)" :disabled="item.quantity <= 1">-</button>
            <span>{{ item.quantity }}</span>
            <button @click="updateQuantity(item.id, item.quantity + 1)">+</button>
            <button @click="removeItem(item.id)" class="remove-button">Remove</button>
          </div>
        </div>
        <div class="cart-summary">
          <p>Subtotal: KES {{ formatPrice(cartSubtotal) }}</p>
          <p class="total">Total: KES {{ formatPrice(cartTotal) }}</p>
          <!-- Updated 'Proceed to Checkout' button -->
          <button @click="proceedToCheckout" class="checkout-button">Proceed to Checkout</button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '../components/navigation/MainLayout.vue';
import grey from '@/assets/images/placeholder.png';

export default {
  components: { MainLayout },
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const loading = ref(false);
    const error = ref(null);

    // Computed properties
    const isAuthenticated = computed(() => store.isAuthenticated);
    const cartItems = computed(() => store.cartItems);
    const cartItemCount = computed(() => store.cartItemCount);
    const cartSubtotal = computed(() =>
      cartItems.value.reduce((sum, item) => sum + (item.line_total || 0), 0)
    );
    const cartTotal = computed(() => cartSubtotal.value);

    // Format price to 2 decimal places
    const formatPrice = (price) => (Math.round(price * 100) / 100).toFixed(2);

    // Navigation functions
    const goToLogin = () => router.push('/login');
    const goToProducts = () => router.push('/products');

    // Load cart data on mount
    const loadCart = async () => {
      loading.value = true;
      try {
        await store.fetchCurrentUserInfo();
        await store.fetchCart();
        error.value = null;
      } catch (err) {
        error.value = 'Please login to view your cart';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    // Retry fetching cart
    const retryFetch = () => loadCart();

    // Update item quantity
    const updateQuantity = async (itemId, newQuantity) => {
      if (newQuantity < 1) return;
      try {
        if (!store.apiInstance) store.initializeApiInstance();
        await store.apiInstance.post(`/cart-items/${itemId}/update_cart_item_quantity/`, {
          quantity: newQuantity,
          cart_id: store.cart.id,
        });
        await store.fetchCart();
      } catch (err) {
        console.error('Failed to update quantity:', err);
      }
    };

    // Remove item from cart
    const removeItem = async (itemId) => {
      try {
        if (!store.apiInstance) store.initializeApiInstance();
        await store.apiInstance.post(`/carts/${store.cart.id}/remove_item/`, {
          item_id: itemId,
        });
        await store.fetchCart();
      } catch (err) {
        console.error('Failed to remove item:', err);
      }
    };

    // Proceed to Checkout: Creates an order and redirects
    const proceedToCheckout = async () => {
      if (!cartItems.value.length) return;
      try {
        const order = await store.createOrderFromCart(); // New store method
        router.push({ path: '/checkout', query: { orderId: order.id } });
      } catch (err) {
        console.error('Failed to proceed to checkout:', err);
        console.log('Server response:', err.response?.data); // Log the exact error
        alert('Failed to create order. Please try again.');
      }
    };

    onMounted(loadCart);

    return {
      loading,
      error,
      isAuthenticated,
      cartItems,
      cartItemCount,
      cartSubtotal,
      cartTotal,
      formatPrice,
      goToLogin,
      goToProducts,
      retryFetch,
      updateQuantity,
      removeItem,
      proceedToCheckout,
      grey,
    };
  },
};
</script>
<style scoped>
.cart-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

.cart-title {
  font-size: 1.75rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.cart-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background-color: #f28c38;
  border-radius: 2px;
}

.loading-state, .error-state, .auth-prompt, .empty-cart {
  text-align: center;
  padding: 60px 0;
  color: #666;
  border-radius: 8px;
  background-color: rgba(0, 0, 0, 0.02);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.empty-cart p {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.spinner {
  border: 4px solid rgba(243, 166, 24, 0.1);
  border-top: 4px solid #f28c38;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 25px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.cart-items {
  margin-top: 30px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.cart-item {
  display: grid;
  grid-template-columns: 100px 1fr auto;
  gap: 20px;
  align-items: center;
  padding: 24px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s ease;
}

.cart-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.cart-item:last-child {
  border-bottom: none;
}

.item-image {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.cart-item:hover .item-image img {
  transform: scale(1.05);
}

.item-details {
  flex: 1;
  font-size: 0.95rem;
  line-height: 1.4;
}

.item-details h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.item-details p {
  margin: 5px 0;
  display: flex;
  justify-content: space-between;
}

.item-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.item-actions .quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 20px;
  padding: 5px 12px;
}

.item-actions button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.item-actions button:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.item-actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.item-actions span {
  font-size: 1rem;
  font-weight: 500;
  min-width: 20px;
  text-align: center;
}

.item-actions .remove-button {
  font-size: 0.9rem;
  background-color: #e74c3c;
  color: white;
  padding: 8px 15px;
  border-radius: 20px;
  transition: all 0.2s ease;
  width: auto;
  height: auto;
}

.item-actions .remove-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.cart-summary {
  margin-top: 30px;
  padding: 24px;
  border-radius: 8px;
  background-color: rgba(0, 0, 0, 0.02);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.cart-summary p {
  display: flex;
  justify-content: space-between;
  font-size: 1.1rem;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed rgba(0, 0, 0, 0.1);
}

.cart-summary .total {
  font-size: 1.5rem;
  font-weight: 700;
  border-bottom: none;
  margin-bottom: 25px;
}

.checkout-button {
  background-color: #e74c3c;
  color: white;
  padding: 16px 24px;
  border: none;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
}

.checkout-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 14px rgba(231, 76, 60, 0.4);
}

.checkout-button:active {
  transform: translateY(-1px);
}

.retry-button, .login-button, .shop-button {
  background-color: #e74c3c;
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s ease;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}

.retry-button:hover, .login-button:hover, .shop-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .cart-item {
    grid-template-columns: 80px 1fr;
  }

  .item-actions {
    grid-column: span 2;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
    margin-top: 15px;
  }

  .cart-summary .total {
    font-size: 1.3rem;
  }
}

@media (max-width: 480px) {
  .cart-container {
    padding: 20px 15px;
  }

  .cart-title {
    font-size: 1.5rem;
  }

  .item-image {
    width: 70px;
    height: 70px;
  }

  .item-details h3 {
    font-size: 1rem;
  }

  .item-details p {
    font-size: 0.85rem;
  }
}
</style>
