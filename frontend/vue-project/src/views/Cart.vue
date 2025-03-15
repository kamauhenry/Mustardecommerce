<!-- views/CartPage.vue -->
<template>
  <MainLayout>
    <div class="cart-page">
      <h1>Shopping Cart</h1>
      <div v-if="cartItems.length" class="cart-items">
        <div v-for="item in cartItems" :key="item.id" class="cart-item">
          <img :src="item.product.thumbnail || 'https://picsum.photos/80/80'" :alt="item.product.name" class="item-image" />
          <div class="item-details">
            <h3>{{ item.product.name }}</h3>
            <p><strong>Variant:</strong> {{ item.variant.color }} / {{ item.variant.size }}</p>
            <p><strong>Quantity:</strong> {{ item.quantity }}</p>
            <p><strong>Line Total:</strong> KES {{ item.line_total }}</p>
          </div>
          <button @click="removeItem(item.id)" class="remove-btn">Remove</button>
        </div>
        <div class="cart-summary">
          <h3>Cart Summary</h3>
          <p><strong>Total Items:</strong> {{ totalItems }}</p>
          <p><strong>Subtotal:</strong> KES {{ subtotal }}</p>

          <h3>Checkout Options</h3>
          <div class="checkout-options">
            <div class="attribute-field">
              <label>Shipping Method</label>
              <select v-model="shippingMethod" class="select-field">
                <option value="standard">Standard (KES 150 each)</option>
                <option value="express">Express (KES 600 each)</option>
                <option value="pickup">Local Pickup</option>
              </select>
            </div>
            <div class="attribute-field">
              <label>Shipping Address</label>
              <input v-model="shippingAddress" type="text" placeholder="Enter shipping address" class="quantity-input" />
            </div>
            <div class="attribute-field">
              <label>Payment Method</label>
              <select v-model="paymentMethod" class="select-field">
                <option value="credit_card">Credit Card</option>
                <option value="paypal">PayPal</option>
                <option value="mobile_money">Mobile Money</option>
              </select>
            </div>
          </div>
          <button @click="checkout" class="checkout-btn">Checkout</button>
        </div>
      </div>
      <p v-else>Your cart is empty.</p>
    </div>
  </MainLayout>
</template>

<script>
import { useCartStore } from '@/stores/cart';
import MainLayout from "@/components/navigation/MainLayout.vue";

export default {
  components: { MainLayout },
  setup() {
    const cartStore = useCartStore();
    return { cartStore };
  },
  data() {
    return {
      shippingMethod: 'standard',
      shippingAddress: '',
      paymentMethod: 'credit_card',
    };
  },
  computed: {
    cartItems() {
      return this.cartStore.cartItems;
    },
    totalItems() {
      return this.cartStore.totalItems;
    },
    subtotal() {
      return this.cartStore.subtotal;
    },
  },
  async created() {
    await this.cartStore.fetchCart();
  },
  methods: {
    async removeItem(itemId) {
      try {
        await this.cartStore.removeItem(itemId);
        alert('Item removed from cart!');
      } catch (error) {
        alert('Failed to remove item. Please try again.');
      }
    },
    async checkout() {
      try {
        const orders = await this.cartStore.checkout({
          shippingMethod: this.shippingMethod,
          shippingAddress: this.shippingAddress,
          paymentMethod: this.paymentMethod,
        });
        alert('Checkout successful! Your orders have been placed.');
        this.$router.push('/my-orders');
      } catch (error) {
        alert(error.response?.data?.error || 'Checkout failed. Please try again.');
      }
    },
  },
};
</script>

<style scoped>
.cart-page {
  padding: 20px;
  background: #1a1a1a;
  color: #fff;
  font-family: Arial, sans-serif;
}

.cart-page h1 {
  color: #ff6200;
  margin-bottom: 20px;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.cart-item {
  display: flex;
  align-items: center;
  background: #333;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #444;
  gap: 20px;
}

.item-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
}

.item-details {
  flex: 1;
}

.item-details h3 {
  color: #fff;
  margin-bottom: 10px;
}

.item-details p {
  color: #ccc;
  margin: 5px 0;
}

.remove-btn {
  padding: 8px 15px;
  background: #ff4444;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.remove-btn:hover {
  background: #cc3333;
}

.cart-summary {
  margin-top: 20px;
  padding: 20px;
  background: #333;
  border-radius: 8px;
}

.cart-summary h3 {
  color: #ff6200;
  margin-bottom: 15px;
}

.cart-summary p {
  color: #ccc;
  margin: 5px 0;
}

.checkout-options {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.attribute-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.quantity-input,
.select-field {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #555;
  background: #222;
  color: #fff;
}

.checkout-btn {
  margin-top: 20px;
  padding: 10px 20px;
  background: #ff6200;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.checkout-btn:hover {
  background: #e55b00;
}
</style>
