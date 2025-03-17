<template>
  <div class="page-list">
    <ul>
      <li><router-link class="nav-link" to="/">Home</router-link></li>
      <li><router-link class="nav-link" to="/moq-campaigns">MOQ Campaigns</router-link></li>
      <li v-if="store.isAuthenticated"><router-link class="nav-link" to="/profile">My Profile</router-link></li>
      <li v-if="store.isAuthenticated"><router-link class="nav-link" to="/orders">My Orders</router-link></li>
      <li v-if="store.isAuthenticated"><a class="nav-link" @click="showRequestMOQModal = true">Request MOQ Campaign</a></li>
      <li v-else><a class="nav-link" @click="openLoginModal">Request MOQ Campaign</a></li>
      <li v-if="store.isAuthenticated"><a class="nav-link" @click="showTrackOrderModal = true">Track Order</a></li>
      <li v-else><a class="nav-link" @click="openLoginModal">Track Order</a></li>
      <li><router-link class="nav-link" to="/about">About Us</router-link></li>
      <li><router-link class="nav-link" to="/contact">Contact Us</router-link></li>
    </ul>
  </div>
</template>

<script>
import { useEcommerceStore } from '@/stores/ecommerce';
import { ref, inject } from 'vue';

export default {
  setup() {
    const store = useEcommerceStore();
    const openTrackOrderModal = inject('openTrackOrderModal');
    const openRequestMOQModal = inject('openRequestMOQModal');
    const openLoginModal = inject('openLoginModal');

    return {
      store,
      openLoginModal,
    };
  },
};
</script>

<style scoped>

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent background */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* Ensure it's on top */
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  width: 80%;
  max-width: 600px; /* Adjust as necessary */
}

  .page-list {
    padding: 0 2%;
    background-color: var(--background-color-two);
  }

  .page-list ul {
    display: flex;
    justify-content: space-around;
    list-style: none;
  }

  .page-list ul li {
    padding: .3rem;
  }

  .nav-link {
    color: var(--vt-c-black);
    text-decoration: none;
    font-weight: 700;
    text-transform: uppercase;
    cursor: pointer;
  }

  .nav-link :hover {
    color: var(--background-color-three);
  }
</style>
