<template>
  <section class="recent-searches" aria-labelledby="recent-searches-title">
    <h2 id="recent-searches-title" class="searches-title">Latest Searches</h2>
    <div v-if="isLoading" class="skeleton-container">
      <div v-for="n in 3" :key="n" class="skeleton-search">
        <div class="skeleton-search-img"></div>
        <div class="skeleton-search-text"></div>
      </div>
    </div>
    <div v-else class="products-searches">
      <article
        v-for="(item, index) in displayItems"
        :key="index"
        class="product-searches"
        @click="item.isSearch ? performSearch(item.query) : viewProduct(item)"
        itemscope
        itemtype="http://schema.org/Product"
      >
        <img
          :src="item.image || item.thumbnail || placeholder"
          :alt="item.name"
          class="product-search-img"
          width="50"
          height="50"
          itemprop="image"
          loading="lazy"
        />
        <div class="slide-content">
          <h3 class="search-p" itemprop="name">{{ item.name }}</h3>
          <p class="search-price" itemprop="offers" itemscope itemtype="http://schema.org/Offer">
            KES {{ formatPrice(item.price) }}
            <meta itemprop="priceCurrency" content="KES" />
            <meta itemprop="price" :content="item.price.toString()" />
          </p>
          <div v-if="item.moq_progress && item.moq_progress.percentage != null" class="moq-progress-container">
            <div
              class="moq-progress-bar"
              :style="{ width: Math.min(100, item.moq_progress.percentage) + '%' }"
            ></div>
            <span class="moq-progress-text">
              {{ item.moq_progress.percentage }}%
            </span>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script>
import { computed, onMounted, ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useRouter } from 'vue-router';
import placeholder from '@/assets/images/placeholder.png';

export default {
  setup() {
    const ecommerceStore = useEcommerceStore();
    const router = useRouter();
    const randomProducts = ref([]);
    const searchProducts = ref([]);
    const isLoading = ref(true);

    const recentSearches = computed(() => ecommerceStore.recentSearches.slice(0, 3));

    const fetchRandomProducts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/products/random/?limit=3');
        if (!response.ok) throw new Error('Failed to fetch random products');
        const data = await response.json();
        randomProducts.value = (data.results || []).map((product) => ({
          ...product,
          image: product.image || product.thumbnail,
          moq_progress: product.moq_progress || null, // Fallback to null
        }));
      } catch (error) {
        console.error('Error fetching random products:', error);
        randomProducts.value = [];
      }
    };

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
              image: product.image || product.thumbnail,
              moq_progress: product.moq_progress || null, // Fallback to null
            }
          : null;
      } catch (error) {
        console.error(`Error fetching product for query "${query}":`, error);
        return null;
      }
    };

    const displayItems = computed(() => {
      const items = [];
      for (const query of recentSearches.value) {
        const product = searchProducts.value.find((p) => p.query === query)?.data;
        if (product) {
          console.log('Search Product:', product); // Debug
          items.push({
            isSearch: true,
            query,
            name: product.name,
            image: product.image || product.thumbnail,
            price: product.price,
            moq_progress: product.moq_progress,
            category_slug: product.category_slug,
            slug: product.slug,
          });
        }
      }
      const needed = 3 - items.length;
      const randoms = randomProducts.value
        .filter((rp) => !items.some((item) => !item.isSearch && item.slug === rp.slug))
        .slice(0, needed)
        .map((product) => {
          console.log('Random Product:', product); // Debug
          return {
            isSearch: false,
            name: product.name,
            image: product.image || product.thumbnail,
            price: product.price,
            moq_progress: product.moq_progress,
            category_slug: product.category_slug,
            slug: product.slug,
          };
        });
      console.log('Display Items:', [...items, ...randoms].slice(0, 3)); // Debug
      return [...items, ...randoms].slice(0, 3);
    });

    const formatPrice = (value) => {
      if (value == null) return '0.00';
      return parseFloat(value).toFixed(2);
    };

    onMounted(async () => {
      isLoading.value = true;
      await fetchRandomProducts();
      searchProducts.value = [];
      for (const query of recentSearches.value) {
        if (!searchProducts.value.some((p) => p.query === query)) {
          const product = await fetchProductForSearch(query);
          searchProducts.value.push({ query, data: product });
        }
      }
      isLoading.value = false;
    });

    const performSearch = (query) => {
      ecommerceStore.addRecentSearch(query);
      router.push({ name: 'search-results', query: { q: query } });
    };

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
      isLoading,
      formatPrice,
    };
  },
};
</script>

<style scoped>
.moq-progress-container {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: #e6f4ea;
  border-radius: 20px;
  overflow: hidden;
  margin-top: auto;
}

.moq-progress-bar {
  height: 100%;
  background: linear-gradient(45deg, #28a745, #5fd778);
  transition: width 0.5s ease;
}

.moq-progress-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 0.65rem;
  font-weight: bold;
  text-shadow: 0 0 2px #fff;
}

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
  object-fit: cover;
}

.search-p {
  margin: 0;
  font-size: 1rem;
}

.search-price {
  margin: 0;
  font-size: 0.9rem;
  color: #f28c38;
  font-weight: 600;
}

.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-search {
  display: flex;
  flex-direction: row;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  width: 100%;
}

.skeleton-search-img {
  width: 50px;
  height: 50px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 10px;
}

.skeleton-search-text {
  width: 60%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (max-width: 768px) {
  .recent-searches {
    display: none;
  }
}
</style>