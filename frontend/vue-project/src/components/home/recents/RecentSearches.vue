<template>
  <div class="recent-searches">
    <p class="searches-title">Recent Searches</p>
    <div class="products-searches">
      <div class="product-searches">
        <img src="" alt="Product 1" class="product-search-img" width="50" height="50">
        <p class="search-p">Product 1</p>
      </div>
      <div class="product-searches">
        <img src="" alt="Product 1" class="product-search-img" width="50" height="50">
        <p class="search-p">Product 1</p>
      </div>
      <div class="product-searches">
        <img src="" alt="Product 1" class="product-search-img" width="50" height="50">
        <p class="search-p">Product 1</p>
      </div>
    </div>
  </div>
</template>
<script>
export default {

}
</script>
<style scoped>
  .recent-searches {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
  }

  .searches-title {
    text-transform: uppercase;
    font-weight: 900;
  }

  .products-searches {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .product-searches {
    border-radius: 10px;
    padding: 1rem 2rem;
    display: flex;
    flex-direction: row;
    gap: 1rem;
    justify-content: flex-start;
    align-items: center;
    width: 20vw;
  }
</style>
