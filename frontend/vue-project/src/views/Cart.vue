<template>
  <MainLayout>
    <div class="cart-container">
      <h1 class="cart-title">Your Cart ({{ cartItemCount }} items)</h1>

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
            <img :src="item.variant?.image || item.product?.picture || grey" :alt="item.product_name">
          </div>
          <div class="item-details">
            <h3>PRODUCT: {{ item.product_name }}</h3>
            <p v-if="item.variant">color: {{ item.variant_info.color }}</p>
            <p v-if="item.variant">size: {{ item.variant_info.size }}</p>
            <p>Quantity: {{ item.quantity }}</p>
            <p>Price: KES{{ formatPrice(item.price_per_piece || 0) }}</p>
            <p>Total: KES{{ formatPrice(item.line_total) }}</p>
          </div>
          <div class="item-actions">
            <button @click="updateQuantity(item.id, item.quantity - 1)" :disabled="item.quantity <= 1">-</button>
            <span>{{ item.quantity }}</span>
            <button @click="updateQuantity(item.id, item.quantity + 1)">+</button>
            <button @click="removeItem(item.id)" class="remove-button">Remove</button>
          </div>
        </div>
        <div class="cart-summary">
          <p>Subtotal: KES{{ formatPrice(cartSubtotal) }}</p>
          <p class="total">Total: KES{{ formatPrice(cartTotal) }}</p>
          <button @click="checkout" class="checkout-button">Proceed to Checkout</button>
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
    const cartItems = ref([]);
    const cartItemCount = computed(() =>
      cartItems.value.reduce((total, item) => total + item.quantity, 0)
    );
    const cartSubtotal = computed(() =>
      cartItems.value.reduce((sum, item) => sum + (item.line_total || 0), 0)
    );
    const cartTotal = computed(() => cartSubtotal.value);

    // Format price to 2 decimal places
    const formatPrice = (price) => (Math.round(price * 100) / 100).toFixed(2);

    // Navigation
    const goToLogin = () => router.push('/login');
    const goToProducts = () => router.push('/products');

    // Fetch cart using store.apiInstance
    const fetchCart = async () => {
      if (!store.userId) {
        console.error('User ID is not set');
        return { error: 'User ID is not set' };
      }
      try {
        const response = await store.apiInstance.get(`/users/${store.userId}/cart/`);
        console.log('Cart data:', response.data);
        return { data: response.data };
      } catch (err) {
        if (err.response && err.response.status === 401) {
          return { error: 'Authentication failed. Please log in again.' };
        } else {
          return { error: 'Failed to fetch cart' };
        }
      }
    };

    // Load cart data, ensuring user info is fetched first
    const loadCart = async () => {
      loading.value = true;
      try {
        // Fetch user info to ensure userId and apiInstance are set
        await store.fetchCurrentUserInfo();
        const result = await fetchCart();
        if (result.error) {
          error.value = result.error;
        } else {
          store.cart = result.data;
          cartItems.value = result.data.items || [];
          error.value = null;
        }
      } catch (err) {
        error.value = 'Please login to view your cart';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    // Retry fetch by reusing loadCart
    const retryFetch = () => loadCart();

    // Update item quantity
    const updateQuantity = async (itemId, newQuantity) => {
      if (newQuantity < 1) return;
      try {
        if (!store.apiInstance) store.initializeApiInstance();
        await store.apiInstance.post(`/cart-items/${itemId}/update_cart_item_quantity/`, {
          quantity: newQuantity,
          cart_id: store.cart.id
        });
        await fetchCart();
      } catch (err) {
        console.error('Failed to update quantity:', err);
      }
    };

    // Remove item
    const removeItem = async (itemId) => {
      try {
        if (!store.apiInstance) store.initializeApiInstance();
        await store.apiInstance.post(`/carts/${store.cart.id}/remove_item/`, {
          item_id: itemId
        });
        await fetchCart();
      } catch (err) {
        console.error('Failed to remove item:', err);
      }
    };

    // Checkout
    const checkout = async () => {
      if (!cartItems.value.length) return;
      try {
        const checkoutData = {
          shipping_method: 'standard',
          shipping_address: store.user?.location || 'shop pick uo',
          payment_method: 'mpesa'
        };
        const orderResponse = await store.checkout(checkoutData);
        router.push({
          name: 'Checkout',
          query: { orderId: orderResponse.id }
        });
      } catch (err) {
        console.error('Checkout process failed:', err.message);
        alert(err.message);
      }
    };

    // Load cart when component mounts
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
      fetchCart,
      loadCart,
      retryFetch,
      updateQuantity,
      removeItem,
      checkout
    };
  },
  data: function() {
    return {
      image: grey
    }
  }
};
</script>


<style scoped>
.cart-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.cart-title {
  font-size: 1.5rem;
  font-weight: 600;
  text-transform: uppercase;
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.loading-state, .error-state, .auth-prompt, .empty-cart {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1a3c5e;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.cart-items {
  margin-top: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #e5e5e5;
}

.item-image {
  width: 80px;
  height: 80px;
  margin-right: 20px;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.item-details {
  flex: 1;
  font-size: 0.9rem;
  color: #333;
}

.item-details h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.item-details p {
  margin: 3px 0;
  color: #666;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-actions button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #666;
}

.item-actions .remove-button {
  font-size: 1rem;
  color: #999;
}

.item-actions .quantity-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-actions .quantity-controls button {
  width: 30px;
  height: 30px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1.2rem;
}

.item-actions .quantity-controls span {
  font-size: 1rem;
  color: #333;
}

.cart-summary {
  margin-top: 30px;
  padding: 20px;
  text-align: right;
}

.cart-summary p {
  font-size: 1rem;
  margin-bottom: 10px;
  color: #666;
}

.cart-summary .total {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
}

.checkout-button {
  background-color: #1a3c5e;
  color: white;
  padding: 15px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  text-transform: uppercase;
  width: 100%;
  cursor: pointer;
  margin-top: 20px;
}

.checkout-button:hover {
  background-color: #153048;
}

button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button, .login-button, .shop-button {
  background-color: #1a3c5e;
  color: white;
}

.remove-button:hover {
  color: #e74c3c;
}

</style>
