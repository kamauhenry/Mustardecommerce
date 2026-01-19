<template>
  <div class="page-list">
    <ul>
      <li><router-link class="nav-link" to="/">Home</router-link></li>
      <li><router-link  class="nav-link" to="/pay-and-pick">Pay & Pick</router-link></li>
      <li><router-link class="nav-link" to="/moq-campaigns">MOQ Campaigns</router-link></li>

      <li v-if="authStore.isAuthenticated"><router-link class="nav-link" to="/profile">My Profile</router-link></li>
      <li v-if="authStore.isAuthenticated"><router-link class="nav-link" to="/orders">My Orders</router-link></li>
      <li v-if="authStore.isAuthenticated"><a class="nav-link" @click="openRequestMOQ">Request MOQ Campaign</a></li>
      <li v-else><a class="nav-link" @click="openLoginModal">Request MOQ Campaign</a></li>


      <li><router-link class="nav-link" to="/about">About Us</router-link></li>
      <li><router-link class="nav-link" to="/contact">Contact Us</router-link></li>
    </ul>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/modules/auth';
import { inject } from 'vue';

export default {
  setup() {
    const authStore = useAuthStore();

    // Inject modal functions from the main layout
    const openTrackOrder = inject('openTrackOrder');
    const openRequestMOQ = inject('openRequestMOQ');
    const openLoginModal = inject('openLoginModal');

    return {
      authStore,
      openLoginModal,
      openTrackOrder,
      openRequestMOQ
    };
  },
};
</script>

<style scoped>
.page-list {
  padding: 0 2%;
  background-color: #D4A017; /* Mustard yellow background */
}

.page-list ul {
  display: flex;
  justify-content: space-around;
  list-style: none;
  padding: 0.5rem 0; /* Added padding for better spacing */
  margin: 0;
}

.page-list ul li {
  padding: 0.3rem;
}

.nav-link {
  text-decoration: none;
  font-weight: 700;
  text-transform: uppercase;
  cursor: pointer;
  color: #000; /* Black text for contrast */
  font-size: 0.9rem; /* Consistent font size */
  transition: color 0.3s ease; /* Smooth hover transition */
}

.nav-link:hover,
.nav-link:focus {
  color: #ffd700; /* Brighter mustard yellow for hover/focus, matching footer */
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .page-list ul {
    flex-wrap: wrap; /* Allow wrapping for smaller screens */
    justify-content: center;
    gap: 0.5rem; /* Add spacing between items */
  }

  .nav-link {
    font-size: 0.85rem; /* Slightly smaller for mobile */
  }
}

@media (max-width: 576px) {
  .page-list {
    padding: 0 1%;
  }

  .nav-link {
    font-size: 0.8rem;
  }
}

/* Accessibility */
.nav-link:focus {
  outline: 2px solid #ffd700; /* Mustard yellow outline for focus */
  outline-offset: 2px;
}
</style>