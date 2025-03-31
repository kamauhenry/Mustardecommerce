<script setup>
// import { ref } from 'vue';
import SearchBar from './SearchBar.vue'
import IconLightMode from '../icons/IconLightMode.vue'
import IconCart from '../icons/IconCart.vue'
import IconLogin from '../icons/IconLogin.vue';
import AuthModals from '../auth/AuthModals.vue';
import CartAuth from '../auth/CartAuth.vue';

</script>

<template>
  <div class="navbar">
    <div class="logo-image">
      <router-link to="/">
        <img
          src="../../assets/images/mustard-imports.png"
          alt="Mustard Imports Logo"
          class="main-logo"
        />
      </router-link>
    </div>
    <SearchBar></SearchBar>
    <div class="nav-icons">
      <div class="icon">
        <IconLightMode></IconLightMode>
      </div>
      <div class="icon">
        <CartAuth>
          <IconCart/>
        </CartAuth>
      </div>
      <div class="icon">
        <AuthModals>
          <IconLogin />
        </AuthModals>
      </div>
    </div>
  </div>
</template>

<style scoped>
.navbar {
  padding: .3rem 1rem;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
}

.logo-image {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
}

.main-logo {
  width: 120px;
  height: 80px;
}

.nav-icons {
  display: flex;
  gap: 1.4rem;
}

.nav-icons .icon {
  border: none;
  border-radius: 30%;
  background-color: var(--background-color-one);
  padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
