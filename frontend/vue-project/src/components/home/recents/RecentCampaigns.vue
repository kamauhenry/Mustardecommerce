<template>
  <div class="recent-campaigns">
    <p class="campaigns-title">Recent Campaigns</p>
    <div class="products-campaigns">
      <div
        v-for="(item, index) in latestProducts"
        :key="index"
        class="product-campaigns"
        @click="viewProduct(item)"
      >
        <img
          :src="item.image"
          :alt="item.name"
          class="product-campaign-img"
          width="50"
          height="50"
        />
        <div class="slide-content">
          <p class="campaign-p">{{ item.name }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const router = useRouter();
    const latestProducts = ref([]);

    // Fetch the 3 latest products from the backend
    const fetchLatestProducts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/products/latest/?limit=3');
        if (!response.ok) throw new Error('Failed to fetch latest products');
        const data = await response.json();
        latestProducts.value = data.results || [];
      } catch (error) {
        console.error('Error fetching latest products:', error);
        latestProducts.value = [];
      }
    };

    // Navigate to product detail page
    const viewProduct = (product) => {
      router.push({
        name: 'product-detail',
        params: { categorySlug: product.category_slug, productSlug: product.slug },
      });
    };

    // Fetch products on component mount
    onMounted(() => {
      fetchLatestProducts();
    });

    return {
      latestProducts,
      viewProduct,
    };
  },
};
</script>

<style scoped>
.recent-campaigns {
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 35%;
  min-width: 20vw;
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
  padding: 1rem;
  display: flex;
  flex-direction: row;
  gap: 1rem;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  cursor: pointer;
}

.product-campaign-img {
  border-radius: 10px;
}

@media (max-width: 768px) {
  .recent-campaigns {
    display: none;
  }
}
</style>