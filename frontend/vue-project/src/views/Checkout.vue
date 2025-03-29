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
