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

<style>
.checkout-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  color: #333;
}

h2 {
  font-size: 1.4rem;
  margin-bottom: 1rem;
  color: #555;
}

.loading-state {
  text-align: center;
  padding: 2rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  background-color: #ffebee;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #d32f2f;
}

.retry-button {
  background-color: #d32f2f;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  margin-top: 0.5rem;
}

.retry-button:hover {
  background-color: #b71c1c;
}

.checkout-form {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 768px) {
  .checkout-form {
    grid-template-columns: 1fr 1fr;
  }
  
  .order-summary {
    grid-column: 1 / -1;
  }
}

.shipping-section,
.payment-section {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

input, select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus, select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.order-summary {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.cart-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid #eee;
}

.cart-item:last-child {
  border-bottom: none;
}

.totals {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid #ddd;
}

.totals p {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.totals p:last-child {
  font-weight: bold;
  font-size: 1.1rem;
  color: #333;
}

.checkout-button {
  grid-column: 1 / -1;
  background-color: #2ecc71;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 4px;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.checkout-button:hover {
  background-color: #27ae60;
}

.checkout-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}
</style>