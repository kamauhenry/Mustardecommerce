<template>
  <div class="recent-campaigns">
    <p class="campaigns-title">Recent Campaigns</p>
    <div class="products-campaigns">
      <div class="product-campaigns">
        <img src="" alt="Product 1" class="product-campaign-img" width="50" height="50">
        <p class="campaign-p">Product 1</p>
      </div>
      <div class="product-campaigns">
        <img src="" alt="Product 1" class="product-campaign-img" width="50" height="50">
        <p class="campaign-p">Product 1</p>
      </div>
      <div class="product-campaigns">
        <img src="" alt="Product 1" class="product-campaign-img" width="50" height="50">
        <p class="campaign-p">Product 1</p>
      </div>
    </div>
  </div>
</template>
<script>
export default {

}
</script>
<style scoped>
  .recent-campaigns {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
  }

  .campaigns-title {
    text-transform: uppercase;
    font-weight: 700;
  }

  .products-campaigns {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .product-campaigns {
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
