<template>
  <div class="recent-searches">
    <p class="searches-title">Recent Searches</p>
    <div class="products-searches">
      <div class="product-searches" v-for="(item, index) in searches" :key="index">
        <img :src="item.image" alt="Product 1" class="product-search-img" width="30" height="30">
        <div class="slide-content">
          <p class="search-p">{{ item.product }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import placeholder from "@/assets/images/office.jpeg";

export default {
  data() {
    return {
      searches: [
        {
          image: placeholder,
          product: "Product 4",
        },
        {
          image: placeholder,
          product: "Product 5",
        },
        {
          image: placeholder,
          product: "Product 6",
        },
      ],
    };
  },
};
</script>

<style scoped>
  .recent-searches {
    padding: 0 1rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 35%;
    min-width: 20vw;
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

  .product-search-img {
    border-radius: 10px;
  }

  .product-searches {
    border-radius: 10px;
    padding: 0.5rem 1rem;
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
    justify-content: flex-start;
    align-items: center;
  }
</style>
