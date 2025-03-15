<template>
  <div class="recent-campaigns">
    <p class="campaigns-title">Recent Campaigns</p>
    <div class="products-campaigns">
      <div class="product-campaigns" v-for="(item, index) in campaigns" :key="index">
        <img :src="item.image" alt="Product 1" class="product-campaign-img" width="50" height="50">
        <div class="slide-content">
          <p class="campaign-p">{{ item.product }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import placeholder from "../../../assets/images/placeholder.png";

export default {
  data() {
    return {
      campaigns: [
        {
          image: placeholder,
          product: "Product 1",
        },
        {
          image: placeholder,
          product: "Product 2",
        },
        {
          image: placeholder,
          product: "Product 3",
        },
      ],
    };
  },
};
</script>

<style scoped>
.recent-campaigns {
  margin: 1rem;
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
  width: fit-content;
}

.product-campaign-img {
  border-radius: 10px;
}

@media (max-width: 540px) {
  .recent-campaigns {
    margin: 0;
    padding: 0;
  }


  .product-campaigns {
    width: 85vw;
    align-items: center;
  }
}
</style>
