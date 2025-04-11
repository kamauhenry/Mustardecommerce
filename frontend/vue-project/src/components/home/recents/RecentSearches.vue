<template>
  <div class="recent-searches">
    <p class="searches-title">Latest Searches</p>
    <div class="products-searches">
      <div
        v-for="(item, index) in displayItems"
        :key="index"
        class="product-searches"
        @click="item.isSearch ? performSearch(item.query) : viewProduct(item)"
      >
        <img
          :src="item.image || placeholder"
          :alt="item.name"
          class="product-search-img"
          width="50"
          height="50"
        />
        <div class="slide-content">
          <p class="search-p">{{ item.name }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useRouter } from 'vue-router';
import placeholder from '@/assets/images/placeholder.png'; // Ensure this exists or use a URL

export default {
  setup() {
    const ecommerceStore = useEcommerceStore();
    const router = useRouter();
    const randomProducts = ref([]);
    const searchProducts = ref([]);

    // Access recent searches from the store (up to 3)
    const recentSearches = computed(() => ecommerceStore.recentSearches.slice(0, 3));

    // Fetch random products
    const fetchRandomProducts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/products/random/?limit=3');
        if (!response.ok) throw new Error('Failed to fetch random products');
        const data = await response.json();
        randomProducts.value = (data.results || []).map((product) => ({
          ...product,
          image: product.image || product.thumbnail, // Handle missing image
        }));
        console.log('Random products:', randomProducts.value);
      } catch (error) {
        console.error('Error fetching random products:', error);
        randomProducts.value = [];
      }
    };

    // Fetch product for a search query (first match)
    const fetchProductForSearch = async (query) => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/products/search/?search=${encodeURIComponent(query)}&page=1&per_page=1`
        );
        if (!response.ok) throw new Error(`Failed to fetch product for search: ${query}`);
        const data = await response.json();
        const product = data.results && data.results.length > 0 ? data.results[0] : null;
        return product
          ? {
              ...product,
              image: product.image || product.thumbnail, // Handle missing image
            }
          : null;
      } catch (error) {
        console.error(`Error fetching product for query "${query}":`, error);
        return null;
      }
    };

    // Combine recent searches (as products) and random products
    const displayItems = computed(() => {
      const items = [];
      // Add products for recent searches
      for (const query of recentSearches.value) {
        const product = searchProducts.value.find((p) => p.query === query)?.data;
        if (product) {
          items.push({
            isSearch: true,
            query,
            name: product.name,
            image: product.image,
            category_slug: product.category_slug,
            slug: product.slug,
          });
        }
      }
      // Fill remaining slots with random products
      const needed = 3 - items.length;
      const randoms = randomProducts.value
        .filter((rp) => !items.some((item) => !item.isSearch && item.slug === rp.slug))
        .slice(0, needed)
        .map((product) => ({
          isSearch: false,
          name: product.name,
          image: product.image,
          category_slug: product.category_slug,
          slug: product.slug,
        }));
      const result = [...items, ...randoms].slice(0, 3);
      console.log('Display items:', result);
      return result;
    });

    // Fetch data on mount
    onMounted(async () => {
      await fetchRandomProducts();
      // Fetch products for each recent search
      searchProducts.value = [];
      for (const query of recentSearches.value) {
        if (!searchProducts.value.some((p) => p.query === query)) {
          const product = await fetchProductForSearch(query);
          searchProducts.value.push({ query, data: product });
        }
      }
    });

    // Re-perform a search
    const performSearch = (query) => {
      ecommerceStore.addRecentSearch(query);
      router.push({ name: 'search-results', query: { q: query } });
    };

    // Navigate to product details
    const viewProduct = (product) => {
      router.push({
        name: 'product-detail',
        params: { categorySlug: product.category_slug, productSlug: product.slug },
      });
    };

    return {
      displayItems,
      performSearch,
      viewProduct,
      placeholder,
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
  cursor: pointer;
}

.product-search-img {
  border-radius: 10px;
}

@media (max-width: 768px) {
  .recent-searches {
    display: none;
  }
}
</style>