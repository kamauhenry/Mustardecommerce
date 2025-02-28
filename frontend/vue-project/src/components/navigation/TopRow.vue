<script setup>
  import SearchBar from "./SearchBar.vue";
  import IconDarkMode from "../icons/IconDarkMode.vue";
  import IconCart from "../icons/IconCart.vue";
  import IconLogin from "../icons/IconLogin.vue";

</script>

<template>
  <div class="navbar">
    <div class="logo-image">
      <img src="../../assets/images/mustard-imports.jpg" alt="Mustard Imports Logo" class="main-logo">
    </div>
    <SearchBar></SearchBar>
    <div class="nav-icons">
      <div class="icon">
        <IconDarkMode></IconDarkMode>
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
  background-color: var(--vt-c-white);
  padding: 1.1rem;
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
  border-radius: 10%;
  background-color: var(--background-color-one);
  padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
