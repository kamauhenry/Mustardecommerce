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
  display: flex;
  align-items: center;
  justify-content: flex-end;
  transition: transform 0.2s ease;
}

.cart-icon-wrapper:hover {
  transform: scale(1.05);
}

svg {
  display: flex;
  justify-content: flex-end;
  width: 1.6rem;
  height: auto;
  transition: all 0.2s ease;
}

.cart-icon-wrapper:hover svg {
  filter: drop-shadow(0 0 2px rgba(131, 134, 54, 0.3));
}

.cart-count {
  position: absolute;
  top: -10px;
  right: -10px;
  background-color:#D4A017;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 6px;
  border-radius: 12px;
  min-width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  transform-origin: center;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  }
}

.high-count {
  background-color: #e53935;
  animation: highCountPulse 2s infinite;
}

@keyframes highCountPulse {
  0% {
    transform: scale(1);
    box-shadow: 0 2px 4px rgba(229, 57, 53, 0.3);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 3px 8px rgba(229, 57, 53, 0.4);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 2px 4px rgba(229, 57, 53, 0.3);
  }
}

a {
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes cartBump {
  0% { transform: scale(1); }
  40% { transform: scale(1.15); }
  70% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

.cart-bump {
  animation: cartBump 0.5s ease-in-out;
}
</style>
