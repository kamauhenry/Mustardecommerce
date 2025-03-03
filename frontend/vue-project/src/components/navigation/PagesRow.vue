<template>
  <div class="page-list">
    <ul>
      <li><router-link class="nav-link" to="/">Home</router-link></li>
      <li><router-link class="nav-link" to="/moq-campaigns">MOQ Campaigns</router-link></li>
      <li><router-link class="nav-link" to="/profile">My Profile</router-link></li>
      <li><router-link class="nav-link" to="/orders">My Orders</router-link></li>
      <li><router-link class="nav-link" to="/request-moq">Request MOQ Campaign</router-link></li>
      <li><router-link class="nav-link" to="/track-order">Track Order</router-link></li>
      <li><router-link class="nav-link" to="/about">About Us</router-link></li>
      <li><router-link class="nav-link" to="/contact">Contact Us</router-link></li>
    </ul>
  </div>
</template>

<script>
  export default {};
</script>

<style scoped>
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
  }

  .nav-link :hover {
    color: var(--background-color-three);
  }
</style>
