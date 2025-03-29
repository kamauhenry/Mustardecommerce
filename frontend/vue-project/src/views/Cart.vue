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
            <img :src="item.variant?.image || item.product?.picture || '/default-product.jpg'" :alt="item.product_name">
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
  }
};
</script>


<style scoped>
.cart-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.cart-title {
  margin-bottom: 20px;
}

.loading-state, .error-state, .auth-prompt, .empty-cart {
  text-align: center;
  padding: 40px 0;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
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
  border-bottom: 1px solid #eee;
  padding: 20px 0;
}

.item-image {
  width: 100px;
  height: 100px;
  margin-right: 20px;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  flex: 1;
}

.item-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.item-actions button {
  margin: 5px;
  padding: 5px 10px;
}

.cart-summary {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 5px;
}

.total {
  font-size: 1.2em;
  font-weight: bold;
}

button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button, .login-button, .shop-button {
  background-color: #3498db;
  color: white;
}

.guest-button {
  background-color: #95a5a6;
  color: white;
  margin-left: 10px;
}

.remove-button {
  background-color: #e74c3c;
  color: white;
}

.checkout-button {
  background-color: #2ecc71;
  color: white;
  padding: 15px 20px;
  font-size: 1.1em;
  width: 100%;
  margin-top: 20px;
}
</style>