<template>
    <MainLayout>
      <div class="checkout-container">
        <h1>Checkout</h1>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Processing your order...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button @click="retryCheckout" class="retry-button">Try Again</button>
        </div>

        <form v-else @submit.prevent="processCheckout" class="checkout-form">
          <div class="shipping-section">
            <h2>Shipping Information</h2>
            <div class="form-group">
              <label for="fullName">Full Name</label>
              <input
                id="fullName"
                v-model="shippingDetails.fullName"
                type="text"
                required
              />
            </div>

            <div class="form-group">
              <label for="address">Shipping Address</label>
              <input
                id="address"
                v-model="shippingDetails.address"
                type="text"
                required
              />
            </div>

            <div class="form-group">
              <label for="shippingMethod">Shipping Method</label>
              <select
                id="shippingMethod"
                v-model="shippingDetails.shippingMethod"
              >
                <option value="standard">Standard Shipping (KES 0)</option>
                <option value="express">Express Shipping (KES 500)</option>
                <option value="pickup">Local Pickup (Free)</option>
              </select>
            </div>
          </div>

          <div class="payment-section">
            <h2>Payment Method</h2>
            <div class="form-group">
              <label for="paymentMethod">Payment Method</label>
              <select
                id="paymentMethod"
                v-model="paymentMethod"
              >
                <option value="mpesa">M-Pesa</option>
                <option value="creditCard">Credit Card</option>
                <option value="bankTransfer">Bank Transfer</option>
              </select>
            </div>
          </div>

          <div class="order-summary">
            <h2>Order Summary</h2>
            <div v-for="item in cartItems" :key="item.id" class="cart-item">
              <p>
                {{ item.product.name }} -
                Quantity: {{ item.quantity }} -
                KES {{ (item.price * item.quantity).toFixed(2) }}
              </p>
            </div>

            <div class="totals">
              <p>Subtotal: KES {{ subtotal.toFixed(2) }}</p>
              <p>Tax (10%): KES {{ tax.toFixed(2) }}</p>
              <p>Total: KES {{ total.toFixed(2) }}</p>
            </div>
          </div>

          <button
            type="submit"
            class="checkout-button"
            :disabled="!isFormValid"
          >
            Complete Order
          </button>
        </form>
      </div>
    </MainLayout>
  </template>

  <script>
  import { ref, computed, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { useEcommerceStore } from '@/stores/ecommerce';
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

      const shippingDetails = ref({
        fullName: '',
        address: '',
        shippingMethod: 'standard'
      });

      const paymentMethod = ref('mpesa');

      const cartItems = computed(() => store.cart?.items || []);

      const subtotal = computed(() =>
        cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
      );

      const tax = computed(() => subtotal.value * 0.1);

      const total = computed(() => subtotal.value + tax.value);

      const isFormValid = computed(() =>
        shippingDetails.value.fullName &&
        shippingDetails.value.address
      );

      const processCheckout = async () => {
        loading.value = true;
        error.value = null;

        try {
          const checkoutData = {
            cart_id: store.cart.id,
            shipping_method: shippingDetails.value.shippingMethod,
            shipping_address: `${shippingDetails.value.fullName}, ${shippingDetails.value.address}`,
            payment_method: paymentMethod.value
          };

          const response = await store.checkoutCart(checkoutData);

          // Navigate to order confirmation
          router.push({
            path: '/checkout/confirmation',
            query: { orderId: response.data[0].id }
          });
        } catch (err) {
          error.value = 'Checkout failed. Please try again.';
          console.error('Checkout error:', err);
        } finally {
          loading.value = false;
        }
      };

      const retryCheckout = () => {
        error.value = null;
      };

      return {
        loading,
        error,
        shippingDetails,
        paymentMethod,
        cartItems,
        subtotal,
        tax,
        total,
        isFormValid,
        processCheckout,
        retryCheckout
      };
    }
  };
  </script>

<style scoped>
.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

h1 {
  font-size: 1.8rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 30px;
  color: #333;
}

h2 {
  font-size: 1.2rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 20px;
  color: #333;
}

.checkout-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

.shipping-section,
.payment-section {
  padding: 20px;
}

.shipping-method-toggle {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.shipping-method-toggle button {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.shipping-method-toggle button.active {
  background-color: #1a3c5e;
  color: white;
  border-color: #1a3c5e;
}

.shipping-method-toggle .icon {
  font-size: 1rem;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 5px;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #1a3c5e;
  box-shadow: 0 0 0 2px rgba(26, 60, 94, 0.2);
}

.terms {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #666;
}

.order-summary {
  padding: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #e5e5e5;
}

.cart-item:last-child {
  border-bottom: none;
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

.item-details p {
  margin: 3px 0;
  font-size: 0.9rem;
  color: #333;
}

.discount-code {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.discount-code input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.discount-code button {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
}

.totals {
  font-size: 1rem;
  color: #666;
}

.totals p {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.totals .total {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
}

.checkout-button {
  grid-column: 1 / -1;
  background-color: #1a3c5e;
  color: white;
  padding: 15px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
  margin-top: 20px;
}

.checkout-button:hover {
  background-color: #153048;
}

.checkout-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.security-note {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 0.8rem;
  color: #666;
  margin-top: 20px;
}

.security-note p:first-child {
  font-weight: 500;
}

/* Responsiveness */
@media (max-width: 768px) {
  .checkout-form {
    grid-template-columns: 1fr;
  }

  .shipping-section,
  .payment-section,
  .order-summary {
    padding: 15px;
  }

  .cart-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .item-image {
    margin-right: 0;
    margin-bottom: 10px;
  }

  .checkout-button {
    margin-top: 10px;
  }
}

@media (max-width: 480px) {
  .checkout-container {
    padding: 20px 10px;
  }

  h1 {
    font-size: 1.5rem;
  }

  h2 {
    font-size: 1rem;
  }

  .form-group input,
  .form-group select {
    font-size: 0.85rem;
  }

  .discount-code {
    flex-direction: column;
  }

  .discount-code button {
    width: 100%;
  }
}
</style>
