<script setup>
import SearchBar from './SearchBar.vue';
import IconLightMode from '../icons/IconLightMode.vue';
import IconCart from '../icons/IconCart.vue';
import IconLogin from '../icons/IconLogin.vue';
import IconAdmin from '@/components/icons/IconAdmin.vue';
import AuthModals from '../auth/AuthModals.vue';
import CartAuth from '../auth/CartAuth.vue';
</script>

<template>
  <div class="navbar">
    <div class="logo-image">
      <router-link to="/" class="logo-link">
        <img src="../../assets/images/mustard-imports.png" alt="Icon" class="logo-icon" />
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
  padding: 1rem;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
}

.logo-image {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.logo-icon {
  width: 90px;
  height: auto;
  margin-right: 8px;
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

.admin-links {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.admin-dropdown {
  display: none;
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background-color: var(--background-color-one);
  border-radius: 8px;
  width: 160px;
  padding: 8px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.admin-links:hover .admin-dropdown {
  display: block;
  opacity: 1;
  transform: translateY(0);
}

.admin-dropdown a {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  color: var(--text-color, #333);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.admin-dropdown a:first-child {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.admin-dropdown a:last-child {
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.admin-dropdown a:hover {
  background-color: rgba(243, 166, 24, 0.15);
  color: rgba(243, 166, 24, 1);
}

.admin-dropdown::before {
  content: '';
  position: absolute;
  top: -6px;
  right: 10px;
  width: 12px;
  height: 12px;
  background-color: var(--background-color-one);
  transform: rotate(45deg);
  box-shadow: -2px -2px 5px rgba(0, 0, 0, 0.04);
}

/* Responsive Styles */
@media (max-width: 767px) {
  .navbar {
    padding: .3rem .5rem;
    justify-content: space-between;
  }

  .logo-text {
    font-size: 1rem;
  }

  .logo-icon {
    width: 20px;
    height: 20px;
    margin-right: 6px;
  }

  .nav-icons {
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .logo-text {
    font-size: 0.9rem;
  }

  .logo-icon {
    width: 18px;
    height: 18px;
    margin-right: 5px;
  }

  .nav-icons {
    gap: 0.8rem;
  }
}

@media (max-width: 360px) {
  .logo-text {
    font-size: 0.85rem;
  }

  .logo-icon {
    width: 16px;
    height: 16px;
    margin-right: 4px;
  }

  .nav-icons {
    gap: 0.6rem;
  }
}
</style>
