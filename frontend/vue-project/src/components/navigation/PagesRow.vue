<template>
  <div class="page-list">
    <ul>
      <li><router-link class="nav-link" to="/">Home</router-link></li>
      <li><router-link class="nav-link" to="/moq-campaigns">MOQ Campaigns</router-link></li>
      <li v-if="store.isAuthenticated"><router-link class="nav-link" to="/profile">My Profile</router-link></li>
      <li v-if="store.isAuthenticated"><router-link class="nav-link" to="/orders">My Orders</router-link></li>
      <li v-if="store.isAuthenticated"><a class="nav-link" @click="openRequestMOQModal">Request MOQ Campaign</a></li>
      <li v-else><a class="nav-link" @click="openLoginModal">Request MOQ Campaign</a></li>
      <li v-if="store.isAuthenticated"><a class="nav-link" @click="openTrackOrderModal">Track Order</a></li>
      <li v-else><a class="nav-link" @click="openLoginModal">Track Order</a></li>
      <li><router-link class="nav-link" to="/about">About Us</router-link></li>
      <li><router-link class="nav-link" to="/contact">Contact Us</router-link></li>
    </ul>
  </div>
</template>

<script>
import { useEcommerceStore } from '@/stores/ecommerce';
import { inject } from 'vue';

export default {
  setup() {
    const store = useEcommerceStore();

    // Inject modal functions from the main layout
    const openTrackOrderModal = inject('openTrackOrderModal');
    const openRequestMOQModal = inject('openRequestMOQModal');
    const openLoginModal = inject('openLoginModal');

    return {
      store,
      openLoginModal,
      openTrackOrderModal,
      openRequestMOQModal
    };
  },
};
</script>

<style scoped>
.page-list {
  padding: 0 2%;
  background-color: #f28c38;
}

.page-list ul {
  display: flex;
  justify-content: space-around;
  list-style: none;
  padding: 0;
  margin: 0;
}

.page-list ul li {
  padding: .3rem;
}

.nav-link {
  text-decoration: none;
  font-weight: 700;
  text-transform: uppercase;
  cursor: pointer;
  color: #000;
}
</style>
