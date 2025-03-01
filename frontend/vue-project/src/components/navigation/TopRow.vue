<script setup>
import SearchBar from './SearchBar.vue'
import IconLightMode from '../icons/IconLightMode.vue'
import IconCart from '../icons/IconCart.vue'
import IconLogin from '../icons/IconLogin.vue'
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
        <IconCart></IconCart>
      </div>
      <div class="icon">
        <IconLogin></IconLogin>
      </div>
    </div>
  </div>
</template>

<style scoped>
.navbar {
  padding: 0.1rem;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
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
