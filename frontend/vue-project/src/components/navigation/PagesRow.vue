<template>
  <div class="page-list">
    <ul>
      <li><a href="">Home</a></li>
      <li><a href="">MOQ Campaigns</a></li>
      <li><a href="">My Profile</a></li>
      <li><a href="">My Orders</a></li>
      <li><a href="">Request MOQ Campaign</a></li>
      <li><a href="">Track Order</a></li>
      <li><a href="">About Us</a></li>
      <li><a href="">Contact Us</a></li>
    </ul>
  </div>
</template>

<script>
  export default {};
</script>

<style scoped>
  .page-list {
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

  .page-list ul li a {
    color: var(--vt-c-black);
    text-decoration: none;
    font-weight: 700;
    text-transform: uppercase;
  }
</style>
