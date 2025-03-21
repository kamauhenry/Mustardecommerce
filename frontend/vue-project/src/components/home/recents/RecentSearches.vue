<template>
  <div class="recent-searches">
    <p class="searches-title">Recent Searches</p>
    <div v-if="displayProducts.length" class="products-searches">
      <router-link
        v-for="(item, index) in displayProducts"
        :key="index"
        :to="item.categorySlug && item.slug ? `/category/${item.categorySlug}/${item.slug}` : '#'"
        class="product-searches"
      >
        <img :src="item.image" :alt="item.name" class="product-search-img" width="50" height="50">
        <div class="slide-content">
          <p class="search-p">{{ item.name }}</p>
        </div>
      </router-link>
    </div>
    <div v-else class="no-searches">
      No recent searches
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import placeholderImage from '@/assets/images/office.jpeg';
import { getRecentProducts } from '@/utils/tracking';

export default {
  setup() {
    const store = useEcommerceStore();

    // Fetch recent products from localStorage
    const recentProducts = computed(() => getRecentProducts());

    // Fetch all products from the store
    const allProducts = computed(() => {
      const products = [];
      store.allCategoriesWithProducts.forEach(category => {
        if (category.products && category.products.length > 0) {
          products.push(
            ...category.products.map(product => ({
              ...product,
              categorySlug: category.slug
            }))
          );
        }
      });
      return products;
    });

    // Function to get 3 random products
    const getRandomProducts = (products, count) => {
      if (!products || products.length === 0) return [];
      const shuffled = [...products].sort(() => 0.5 - Math.random());
      return shuffled.slice(0, count).map(product => ({
        id: product.id,
        name: product.name,
        slug: product.slug, // Include the slug for random products
        image: product.thumbnail || placeholderImage,
        categorySlug: product.categorySlug
      }));
    };

    // Display products: use recent ones if available, otherwise use random ones
    const displayProducts = computed(() => {
      let products = recentProducts.value;
      if (products.length === 0) {
        // If no recent products, pick 3 random ones
        products = getRandomProducts(allProducts.value, 3);
      }
      // Ensure we always display 3 items, using placeholders if necessary
      const placeholder = {
        name: 'No Product',
        id: '',
        slug: '',
        categorySlug: '',
        image: placeholderImage
      };
      while (products.length < 3) {
        products.push({ ...placeholder, id: `placeholder-${products.length}` });
      }
      return products;
    });

    return {
      displayProducts
    };
  }
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
  font-weight: 700;
}

.products-searches {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.product-searches {
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: row;
  gap: 1rem;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  text-decoration: none;
  color: inherit;
}

.product-search-img {
  border-radius: 10px;
}

.no-searches {
  padding: 1rem;
  color: #666;
  font-style: italic;
}

@media (max-width: 768px) {
  .recent-searches {
    width: 100%;
  }
}
</style>
