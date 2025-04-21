<!-- eslint-disable vue/multi-word-component-names -->
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
        <button @click="retryFetch" class="action-button retry-button">Try Again</button>
      </div>

      <div v-else-if="!isAuthenticated" class="auth-prompt">
        <p>Please login to view and manage your cart</p>
        <button @click="goToLogin" class="action-button login-button">Login</button>
      </div>

      <div v-else-if="cartItems.length === 0" class="empty-cart">
        <p>Your cart is empty</p>
        <button @click="goToProducts" class="action-button shop-button">Start Shopping</button>
      </div>

      <div v-else class="cart-content">
        <div class="cart-items">
          <div v-for="item in cartItems" :key="item.id" class="cart-item">
            <div class="item-image">
              <img :src="item.product?.thumbnail || grey" alt="Item image" />
            </div>
            <div class="item-details">
              <h3>{{ item.product_name }}</h3>
              <div v-for="attr in item.variant_attributes" :key="attr.attribute_name">
                <p class="variant">{{ attr.attribute_name }}: {{ attr.value }}</p>
              </div>
              <p class="quantity">Qty: {{ item.quantity }}</p>
              <p class="price">
                KES {{ formatPrice(item.price_per_piece || 0) }} each
                <span v-if="item.quantity < item.product.moq_per_person && item.product.moq_status === 'active'" class="moq-warning">
                  (Below MOQ)
                </span>
              </p>
              <p class="line-total">Total: KES {{ formatPrice(item.line_total) }}</p>
            </div>
            <div class="item-actions">
              <div class="quantity-controls">
                <button @click="updateQuantity(item.id, item.quantity - 1)" :disabled="item.quantity <= 1" class="quantity-button">-</button>
                <span>{{ item.quantity }}</span>
                <button @click="updateQuantity(item.id, item.quantity + 1)" class="quantity-button">+</button>
              </div>
              <button @click="removeItem(item.id)" class="remove-button">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                  <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div class="cart-summary">
          <h3>Order Summary</h3>
          <div class="summary-row">
            <span>Subtotal</span>
            <span>KES {{ formatPrice(cartSubtotal) }}</span>
          </div>
          <div class="summary-row">
            <span>Shipping</span>
            <span>KES {{ formatPrice(shippingCost) }}</span>
          </div>
          <div class="summary-row total">
            <span>Total</span>
            <span>KES {{ formatPrice(cartTotal) }}</span>
          </div>
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
import { toast } from 'vue3-toastify';
import MainLayout from '../components/navigation/MainLayout.vue';
import grey from '@/assets/images/placeholder.png';

export default {
  components: { MainLayout },
  setup() {
    const store = useEcommerceStore();
    const router = useRouter();
    const loading = ref(false);
    const error = ref(null);
    const shippingCost = ref(0); // Placeholder for shipping cost

    // Computed properties
    const isAuthenticated = computed(() => store.isAuthenticated);
    const cartItems = computed(() => store.cartItems);
    const cartItemCount = computed(() => store.cartItemCount);
    const cartSubtotal = computed(() =>
      cartItems.value.reduce((sum, item) => sum + (item.line_total || 0), 0)
    );
    const cartTotal = computed(() => cartSubtotal.value + shippingCost.value);

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
        toast.success('Quantity updated successfully!', { autoClose: 3000 });
      } catch (err) {
        console.error('Failed to update quantity:', err);
        toast.error('Failed to update quantity.', { autoClose: 3000 });
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
        toast.success('Item removed from cart!', { autoClose: 3000 });
      } catch (err) {
        console.error('Failed to remove item:', err);
        toast.error('Failed to remove item.', { autoClose: 3000 });
      }
    };

    // Proceed to Checkout
    const proceedToCheckout = async () => {
      if (!cartItems.value.length) {
        toast.error('Your cart is empty.', { autoClose: 3000 });
        return;
      }
      try {
        const order = await store.createOrderFromCart();
        router.push({ path: '/checkout', query: { orderId: order.id } });
      } catch (err) {
        console.error('Failed to proceed to checkout:', err);
        console.log('Server response:', err.response?.data);
        toast.error('Failed to create order. Please try again.', { autoClose: 3000 });
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
      shippingCost,
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
/* Modern Cart Styling */
.cart-container {
    margin: 0 auto;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Loading, Error, Auth, and Empty States */
.loading-state, .error-state, .auth-prompt, .empty-cart {
  padding: 2rem;
  text-align: center;
  margin: 1rem 0;
  border: none;
}

.spinner {
  border: 4px solid #edf2f7;
  border-top: 4px solid #f6ad55;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p, .error-state p, .auth-prompt p, .empty-cart p {
  font-size: 1rem;
  color: #4a5568;
  margin-bottom: 1.5rem;
}

.action-button {
  background: linear-gradient(135deg, #f6ad55, #ed8936);
  color: #fff;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-button:hover {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Cart Content Layout */
.cart-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  align-items: start;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cart-item {
  display: flex;
  align-items: center;
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.cart-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  margin-right: 1rem;
  border: 1px solid #e2e8f0;
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
  font-size: 0.875rem;
  line-height: 1.4;
}

.item-details h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-transform: capitalize;
}

.variant, .quantity, .price, .line-total {
  margin: 0.25rem 0;
}

.moq-warning {
  color: #e53e3e;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.line-total {
  font-weight: 600;
}

.item-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 20px;
  padding: 0.25rem;
  border: 1px solid var(--tabs-bg);
}

.quantity-button {
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.quantity-button:hover {
  background: #edf2f7;
  color: #2d3748;
}

.quantity-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-controls span {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 20px;
  text-align: center;
}

.remove-button {
  background: none;
  border: none;
  color: #e53e3e;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.5rem;
  transition: all 0.2s ease;
}

.remove-button:hover {
  color: #c53030;
  transform: scale(1.1);
}

.remove-button svg {
  width: 16px;
  height: 16px;
}

/* Cart Summary */
.cart-summary {
  background: var(--bg-color-category-card);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 1rem;
}

.cart-summary h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.summary-row.total {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 1rem;
  padding-top: 1rem;
}

.checkout-button {
  background: linear-gradient(135deg, #f6ad55, #ed8936);
  color: #fff;
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.checkout-button:hover {
  background: linear-gradient(135deg, #ed8936, #dd6b20);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.checkout-button:active {
  transform: translateY(0);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .cart-content {
    grid-template-columns: 1fr;
  }

  .cart-summary {
    position: static;
  }
}

@media (max-width: 768px) {
  .cart-container {
    padding: 15px;
  }

  .cart-title {
    font-size: 1.5rem;
  }

  .cart-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .item-image {
    width: 60px;
    height: 60px;
    margin-right: 0;
  }

  .item-details h3 {
    font-size: 0.875rem;
  }

  .item-details p {
    font-size: 0.75rem;
  }

  .item-actions {
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }

  .cart-summary {
    padding: 1rem;
  }

  .summary-row {
    font-size: 0.75rem;
  }

  .summary-row.total {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .cart-container {
    padding: 10px;
  }

  .cart-title {
    font-size: 1.25rem;
  }

  .cart-item {
    padding: 0.75rem;
  }

  .item-image {
    width: 50px;
    height: 50px;
  }

  .quantity-button {
    width: 24px;
    height: 24px;
    font-size: 0.875rem;
  }

  .checkout-button {
    padding: 0.5rem;
    font-size: 0.875rem;
  }
}
</style>
