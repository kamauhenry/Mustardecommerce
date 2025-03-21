<script setup>
import SearchBar from './SearchBar.vue';
import IconLightMode from '@/components/icons/IconLightMode.vue';
import IconCart from '@/components/icons/IconCart.vue';
import IconLogin from '@/components/icons/IconLogin.vue';
import IconAdmin from '@/components/icons/IconAdmin.vue'; // New admin icon
import AuthModals from '@/components/auth/AuthModals.vue';
</script>

<template>
  <div class="navbar">
    <div class="logo-image">
      <router-link to="/">
        <img
          src="@/assets/images/mustard-imports.png"
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
        <AuthModals>
          <IconLogin />
        </AuthModals>
      </div>
      <div class="icon admin-icon">
        <div class="admin-links">
          <IconAdmin />
          <div class="admin-dropdown">
            <router-link to="/admin-page/login">Admin Login</router-link>
            <router-link to="/admin-page/register">Admin Register</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.navbar {
  padding: 0.3rem 1rem;
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
  position: relative; /* For positioning the dropdown */
}

.nav-icons .admin-icon {
  cursor: pointer;
}

.admin-links {
  position: relative;
}

.admin-dropdown {
  display: none;
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--background-color-one);
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.admin-links:hover .admin-dropdown {
  display: block;
}

.admin-dropdown a {
  display: block;
  padding: 8px 12px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
}

.admin-dropdown a:hover {
  background-color: #f0f0f0;
}
</style>
