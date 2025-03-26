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
        <button @click="continueAsGuest" class="guest-button">Continue as Guest</button>
      </div>
      
      <div v-else-if="cartItems.length === 0" class="empty-cart">
        <p>Your cart is empty</p>
        <button @click="goToProducts" class="shop-button">Start Shopping</button>
      </div>
      
      <div v-else class="cart-items">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <div class="item-image">
            <img :src="item.variant?.image || item.product?.image || '/default-product.jpg'" :alt="item.product?.name">
          </div>
          
          <div class="item-details">
            <h3>{{ item.product?.name }}</h3>
            <p v-if="item.variant">Variant: {{ item.variant.name }}</p>
            <p>Quantity: {{ item.quantity }}</p>
            <p>Price: ${{ formatPrice(item.variant?.price || 0) }}</p>
            <p>Total: ${{ formatPrice(item.line_total) }}</p>
          </div>
          
          <div class="item-actions">
            <button @click="updateQuantity(item.id, item.quantity - 1)" 
                    :disabled="item.quantity <= 1">-</button>
            <span>{{ item.quantity }}</span>
            <button @click="updateQuantity(item.id, item.quantity + 1)">+</button>
            <button @click="removeItem(item.id)" class="remove-button">Remove</button>
          </div>
        </div>
        
        <div class="cart-summary">
          <p>Subtotal: ${{ formatPrice(cartSubtotal) }}</p>
          <p>Tax: ${{ formatPrice(cartTax) }}</p>
          <p class="total">Total: ${{ formatPrice(cartTotal) }}</p>
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
import axios from 'axios';
import MainLayout from '../components/navigation/MainLayout.vue';

export default {
  components: {
    MainLayout
  },
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const loading = ref(false);
    const error = ref(null);
    
    // Computed properties
    const isAuthenticated = computed(() => store.isAuthenticated);
    const cartItems = computed(() => store.cart?.items || []);
    const cartItemCount = computed(() => 
      cartItems.value.reduce((total, item) => total + item.quantity, 0));
    const cartSubtotal = computed(() => 
      cartItems.value.reduce((sum, item) => sum + (item.line_total || 0), 0));
    const cartTax = computed(() => cartSubtotal.value * 0.1); // 10% tax
    const cartTotal = computed(() => cartSubtotal.value + cartTax.value);
    
    // Format price to have 2 decimal places
    const formatPrice = (price) => (Math.round(price * 100) / 100).toFixed(2);
    
    // Navigation
    const goToLogin = () => router.push('/login');
    const goToProducts = () => router.push('/products');
    
    // Continue as guest
    const continueAsGuest = async () => {
      await fetchCartAsGuest();
    };
    
    // Fetch cart data
    const fetchCart = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        await store.fetchCartData();
      } catch (err) {
        error.value = 'Could not load your cart. Please try again.';
        console.error('Error loading cart:', err);
      } finally {
        loading.value = false;
      }
    };
    
    // Fetch cart as guest
    const fetchCartAsGuest = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // Get or create session-based cart
        const response = await axios.get('/api/carts/current/');
        store.cart = response.data;
        // Save cart ID to localStorage for future requests
        if (response.data && response.data.id) {
          localStorage.setItem('cartId', response.data.id);
        }
      } catch (err) {
        error.value = 'Could not create guest cart. Please try again.';
        console.error('Error creating guest cart:', err);
      } finally {
        loading.value = false;
      }
    };
    
    // Retry fetch if it failed
    const retryFetch = () => {
      isAuthenticated.value ? fetchCart() : fetchCartAsGuest();
    };
    
    // Update item quantity
    const updateQuantity = async (itemId, newQuantity) => {
      if (newQuantity < 1) return;
      
      try {
        await axios.post(`/api/cart-items/${itemId}/update-quantity/`, {
          quantity: newQuantity
        });
        fetchCart();
      } catch (err) {
        console.error('Failed to update quantity:', err);
      }
    };
    
    // Remove item from cart
    const removeItem = async (itemId) => {
      try {
        await axios.post(`/api/carts/${store.cart.id}/remove_item/`, { 
          item_id: itemId 
        });
        fetchCart();
      } catch (err) {
        console.error('Failed to remove item:', err);
      }
    };
    
    // Checkout
    const checkout = async () => {
      if (!cartItems.value.length) return;
      
      try {
        await axios.post(`/api/carts/${store.cart.id}/checkout/`, {
          shipping_method: 'standard',
          shipping_address: store.user?.location || 'Please enter your address',
          payment_method: 'Credit Card', // This would come from a form
        });
        await fetchCart();
        await store.fetchOrdersData();
        router.push('/checkout/success');
      } catch (err) {
        console.error('Checkout failed:', err);
      }
    };
    
    // On component mount
    onMounted(() => {
      if (isAuthenticated.value) {
        fetchCart();
      } else {
        // Check if we have a cart ID in localStorage
        const cartId = localStorage.getItem('cartId');
        if (cartId) {
          fetchCartAsGuest();
        }
      }
    });
    
    return {
      loading,
      error,
      isAuthenticated,
      cartItems,
      cartItemCount,
      cartSubtotal,
      cartTax,
      cartTotal,
      formatPrice,
      goToLogin,
      goToProducts,
      continueAsGuest,
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