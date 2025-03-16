<template>
  <div>
    <h1>Your Cart ({{ store.cartItemCount }} items)</h1>
    <div v-if="!store.isAuthenticated">Please login to view your cart</div>
    <div v-else>
      <div v-if="store.loading.cart">Loading...</div>
      <div v-else-if="store.error.cart">{{ store.error.cart }}</div>
      <div v-else-if="store.cart?.items?.length">
        <div v-for="item in store.cart.items" :key="item.id">
          <p>{{ item.product_name }} - {{ item.quantity }} x {{ item.line_total }}</p>
          <button @click="removeItem(item.id)">Remove</button>
        </div>
        <p>Total: {{ store.cartTotal }}</p>
        <button @click="checkout">Checkout</button>
      </div>
      <div v-else>Cart is empty</div>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import axios from 'axios';

export default {
  setup() {
    const store = useEcommerceStore();

    const removeItem = async (itemId) => {
      try {
        await axios.post(`/api/carts/${store.cart.id}/remove_item/`, { item_id: itemId });
        store.fetchCartData();
      } catch (error) {
        console.error('Remove from cart failed:', error);
      }
    };

    const checkout = async () => {
      if (!store.cart?.items?.length) return;
      try {
        await axios.post(`/api/carts/${store.cart.id}/checkout/`, {
          shipping_method: 'standard',
          shipping_address: 'User Address',
          payment_method: 'Credit Card',
        });
        store.fetchCartData();
        store.fetchOrdersData();
      } catch (error) {
        console.error('Checkout failed:', error);
      }
    };

    onMounted(() => {
      if (store.isAuthenticated && !store.cart) store.fetchCartData();
    });

    return {
      store,
      removeItem,
      checkout,
    };
  },
};
</script>
