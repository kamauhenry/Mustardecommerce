<template>
  <MainLayout>
    <div class="search-results">
      <h1 class="search-results-h1">Search Results for "{{ searchQuery }}"</h1>

      <!-- Skeleton Loader with Shimmer -->
      <div v-if="isLoading" class="products">
        <div v-for="n in 4" :key="'skeleton-' + n" class="product-card skeleton">
          <div class="product-content">
            <div class="product-image skeleton-shimmer"></div>
            <div class="product-details">
              <div class="skeleton-text skeleton-shimmer short"></div>
              <div class="skeleton-text skeleton-shimmer medium"></div>
              <div class="skeleton-text skeleton-shimmer short"></div>
              <div class="skeleton-text skeleton-shimmer long"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-else-if="!searchResults || searchResults.length === 0" class="no-results">
        No results found for "{{ searchQuery }}"
      </div>

      <!-- Search Results -->
      <div v-else class="products">
        <div v-for="product in searchResults" :key="product.id" class="product-card">
          <router-link
            :to="{
              name: 'product-detail',
              params: { categorySlug: product.category_slug, productSlug: product.slug }
            }"
            class="product-link"
          >
            <div class="product-content">
              <img
                v-if="product.thumbnail || product.image"
                :src="product.thumbnail || product.image"
                :alt="`${product.name} - Product Image`"
                class="product-image"
                loading="lazy"
              />
              <div class="product-details">
                <h3 class="product-name">{{ product.name }}</h3>
                <p class="product-price">KES {{ product.price }}</p>
                <p class="moq-info">MOQ: {{ product.moq || 'N/A' }} items</p>
                <div class="moq-progress-container">
                  <div
                    class="moq-progress-bar"
                    :style="{ width: Math.min(100, product.moq_progress?.percentage || 0) + '%' }"
                  ></div>
                  <span class="moq-progress-text">{{ product.moq_progress?.percentage || 0 }}%</span>
                </div>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';

export default {
  name: 'SearchResults',
  components: {
    MainLayout,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const ecommerceStore = useEcommerceStore();

    const searchQuery = computed(() => route.query.q || '');
    const searchResults = computed(() => ecommerceStore.searchResults);
    const isLoading = computed(() => ecommerceStore.searchLoading);
    const totalResults = computed(() => ecommerceStore.totalSearchResults);

    const fetchSearchResults = async (query) => {
      if (!query.trim()) return;

      ecommerceStore.setSearchLoading(true);
      try {
        const response = await fetch(`http://localhost:8000/api/products/search/?search=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Failed to fetch products');
        const data = await response.json();
        ecommerceStore.setSearchResults(data.results || []);
        ecommerceStore.setTotalResults(data.count || 0);
      } catch (error) {
        console.error('Error fetching search results:', error);
        ecommerceStore.setSearchResults([]);
        ecommerceStore.setTotalResults(0);
      } finally {
        ecommerceStore.setSearchLoading(false);
      }
    };

    // Fetch results on mount if no results exist
    onMounted(() => {
      if (searchQuery.value && (!searchResults.value || searchResults.value.length === 0)) {
        fetchSearchResults(searchQuery.value);
      }
    });

    // Watch for changes in searchQuery to fetch new results
    watch(searchQuery, (newQuery) => {
      if (newQuery) {
        fetchSearchResults(newQuery);
      }
    });

    const viewProduct = (slug) => {
      router.push({ name: 'product-detail', params: { slug } });
    };

    return {
      searchQuery,
      searchResults,
      isLoading,
      totalResults,
      viewProduct,
    };
  },
};
</script>

<style scoped>
.search-results {
  padding: 20px;
  margin: 0 auto;
  max-width: 1200px;
}

h1 {
  font-size: 1.25rem;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0.5rem 0 1rem 0;
  color: #333;
}

.no-results {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #666;
}

/* Skeleton Loader */
.products {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.skeleton {
  background-color: #f0f0f0;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.skeleton-shimmer {
  position: relative;
  overflow: hidden;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton .product-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  margin-left: 0.75rem;
  margin-bottom: 1rem;
}

.skeleton .product-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.skeleton-text {
  height: 12px;
  margin: 4px 0;
  border-radius: 4px;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-text.medium {
  width: 80%;
}

.skeleton-text.long {
  width: 100%;
}

/* Individual product card */
.product-card {
  flex: 0 0 calc(25% - 0.75rem);
  max-width: calc(25% - 0.75rem);
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.moq-progress-container {
  position: relative;
  width: 100%;
  height: 24px;
  background-color: #e6f4ea;
  border-radius: 12px;
  overflow: hidden;
  margin: 0.25rem 0;
}

.moq-progress-bar {
  height: 100%;
  padding: 2px;
  background: linear-gradient(45deg, #62c87a, #6dc480);
  transition: width 0.3s ease;
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
  color:#D4A017;
  font-size: 0.7rem;
  font-weight: bold;
}

.product-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  height: 100%;
}

.product-link:hover {
  text-decoration: none;
  color: inherit;
}

.product-content {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: flex-start;
}

.product-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.product-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
  margin-left: 0.75rem;
  background-color: #e0e0e0;
  margin-bottom: 1rem;
}

.product-name {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0.25rem 0;
  text-align: left;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-price {
  font-size: 0.9rem;
  font-weight: 700;
  margin: 0.25rem 0;
}

.moq-info {
  font-size: 0.75rem;
  margin: 0.25rem 0;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .product-card {
    flex: 0 0 calc(33.33% - 0.75rem);
    max-width: calc(33.33% - 0.75rem);
  }

  .skeleton .product-image {
    width: 100px;
    height: 100px;
  }
}

@media (max-width: 768px) {
  .product-card {
    flex: 0 0 calc(50% - 0.75rem);
    max-width: calc(50% - 0.75rem);
  }

  .product-image {
    width: 120px;
    height: 120px;
  }

  .skeleton .product-image {
    width: 120px;
    height: 120px;
  }

  .product-name {
    font-size: 0.85rem;
  }

  .product-price {
    font-size: 0.8rem;
  }

  .moq-info {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .product-card {
    flex: 0 0 calc(100% - 0.75rem);
    max-width: calc(100% - 0.75rem);
  }

  .product-image {
    width: 100%;
    height: 150px;
    margin-left: 0;
    margin-top: 0.75rem;
  }

  .skeleton .product-image {
    width: 100%;
    height: 150px;
    margin-left: 0;
    margin-top: 0.75rem;
  }

  .product-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>