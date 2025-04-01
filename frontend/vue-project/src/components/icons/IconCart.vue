<template>
  <div class="cart-icon-wrapper">
    <router-link to="/cart">
      <svg
        class="feather feather-shopping-cart"
        viewBox="0 0 256 256"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect fill="none" height="256" width="256" />
        <path
          d="M184,184H69.8L41.9,30.6A8,8,0,0,0,34.1,24H16"
          fill="none"
          stroke="#838636"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="16"
        />
        <circle
          cx="80"
          cy="204"
          fill="none"
          r="20"
          stroke="#838636"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="16"
        />
        <circle
          cx="184"
          cy="204"
          fill="none"
          r="20"
          stroke="#838636"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="16"
        />
        <path
          d="M62.5,144H188.1a15.9,15.9,0,0,0,15.7-13.1L216,64H48"
          fill="none"
          stroke="#838636"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="16"
        />
      </svg>
      <span v-if="cartItemCount > 0" class="cart-count" :class="{ 'high-count': cartItemCount > 99 }">
        {{ cartItemCount > 99 ? '99+' : cartItemCount }}
      </span>
    </router-link>
  </div>
</template>

<script>
import { useEcommerceStore } from '@/stores/ecommerce';

export default {
  name: 'CartIcon',
  setup() {
    const store = useEcommerceStore();
    return {
      cartItemCount: store.cartItemCount,
    };
  },
};
</script>

<style scoped>
.cart-icon-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

svg {
  display: flex;
  justify-content: center;
  width: 1.5rem;
  height: auto;
}

.cart-count {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: #f28c38;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.high-count {
  background-color: #dc3545; /* Red background for counts > 99 */
}

a {
  text-decoration: none;
  color: inherit;
}
</style>
