<template>
  <MainLayout>
    <div class="search-results-page">
      <!-- Loading and Error States -->
      <div v-if="store.loading.allCategoriesWithProducts" class="loading">Loading...</div>
      <div v-else-if="store.error.allCategoriesWithProducts" class="error">
        {{ store.error.allCategoriesWithProducts }}
      </div>
      <div v-else>
        <!-- Search Query Display -->
        <h1 class="search-title">Search Results for "{{ query }}"</h1>

        <!-- Categories Section -->
        <div v-if="matchingCategories.length" class="categories-container">
          <div
            v-for="category in matchingCategories"
            :key="category.id"
            class="category-card"
          >
            <h2 class="category-title">{{ category.name }}</h2>
            <div v-if="category.products && category.products.length > 0" class="products-grid">
              <div
                v-for="product in category.products.slice(0, 4)"
                :key="product.id"
                class="product-card"
              >
                <img :src="product.thumbnail || 'placeholder.jpg'" alt="" class="product-image" />
                <h3 class="product-name">{{ product.name }}</h3>
                <p class="product-price">KES {{ product.price }}</p>
                <p class="moq-info">MOQ: {{ product.moq }} items</p>
                <p class="moq-status">{{ product.moq_status }}</p>
              </div>
            </div>
            <div v-else class="no-products">
              No products available
            </div>
            <router-link
              v-if="category.products && category.products.length > 0"
              :to="`/category/${category.slug}/products`"
              class="see-more-link"
            >
              See More
            </router-link>
          </div>
        </div>

        <!-- Individual Products Section -->
        <div v-if="matchingProducts.length" class="products-section">
          <div class="products-grid">
            <div
              v-for="product in matchingProducts"
              :key="product.id"
              class="product-card"
            >
              <img :src="product.thumbnail || 'placeholder.jpg'" alt="" class="product-image" />
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-price">KES {{ product.price }}</p>
              <p class="moq-info">MOQ: {{ product.moq }} items</p>
              <p class="moq-status">{{ product.moq_status }}</p>
            </div>
          </div>
        </div>

        <!-- No Results Message -->
        <div v-if="!matchingCategories.length && !matchingProducts.length" class="no-results">
          No results found for "{{ query }}".
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';

export default {
  setup() {
    const route = useRoute();
    const store = useEcommerceStore();

    // Get the search query from the URL
    const query = computed(() => route.query.q || '');

    // Fetch all categories with products on mount
    onMounted(() => {
      if (!store.allCategoriesWithProducts.length) {
        store.fetchAllCategoriesWithProducts();
      }
    });

    // Compute matching categories based on the search query
    const matchingCategories = computed(() => {
      if (!query.value) return [];
      const searchQuery = query.value.toLowerCase();
      return store.allCategoriesWithProducts.filter(category =>
        category.name.toLowerCase().includes(searchQuery)
      );
    });

    // Compute matching products based on the search query
    const matchingProducts = computed(() => {
      if (!query.value) return [];
      const searchQuery = query.value.toLowerCase();
      const allProducts = [];

      // Collect all products from all categories
      store.allCategoriesWithProducts.forEach(category => {
        if (category.products && category.products.length > 0) {
          allProducts.push(...category.products);
        }
      });

      // Filter products by name
      return allProducts.filter(product =>
        product.name.toLowerCase().includes(searchQuery) &&
        // Exclude products that are already shown in matching categories
        !matchingCategories.value.some(category =>
          category.products.some(p => p.id === product.id)
        )
      );
    });

    return {
      store,
      query,
      matchingCategories,
      matchingProducts
    };
  },
  components: {
    MainLayout
  }
};
</script>

<style scoped>
.search-results-page {
  padding: 2rem;
}

.search-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #f28c38;
  margin-bottom: 1rem;
  text-transform: uppercase;
}

/* Container for all categories */
.categories-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem 0;
}

/* Individual category card */
.category-card {
  flex: 1;
  min-width: 300px;
  max-width: 48%;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Category title */
.category-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #f28c38;
  text-transform: uppercase;
  margin: 0.5rem 0;
}

/* Products grid inside each category */
.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

/* Individual product card */
.product-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  border-radius: 6px;
  padding: 0.5rem;
  transition: transform 0.2s ease;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Product image */
.product-image {
  width: 100%;
  height: 120px;
  background-color: #e0e0e0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  object-fit: cover;
}

/* Product name */
.product-name {
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0.25rem 0;
  text-align: left;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Product price */
.product-price {
  font-size: 0.8rem;
  font-weight: 700;
  margin: 0.25rem 0;
}

/* MOQ info */
.moq-info {
  font-size: 0.7rem;
  margin: 0.25rem 0;
}

/* MOQ status */
.moq-status {
  font-size: 0.7rem;
  color: #28a745;
  background-color: #e6f4ea;
  padding: 0.2rem 0.4rem;
  border-radius: 12px;
  margin: 0.25rem 0;
}

/* "See More" link styling */
.see-more-link {
  display: block;
  text-align: right;
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  text-decoration: none;
  margin-top: 0.5rem;
}

.see-more-link:hover {
  color: #f28c38;
}

/* Products section for individual products */
.products-section {
  margin-top: 2rem;
}

/* No results message */
.no-results {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #666;
}

/* Loading and error states */
.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #666;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .category-card {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .category-card {
    max-width: 100%;
    min-width: 100%;
  }

  .category-title {
    font-size: 1.1rem;
  }

  .product-image {
    height: 100px;
  }

  .product-name {
    font-size: 0.8rem;
  }

  .product-price {
    font-size: 0.75rem;
  }

  .moq-info,
  .moq-status {
    font-size: 0.65rem;
  }
}

@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: repeat(1, 1fr);
  }

  .category-card {
    padding: 0.75rem;
  }

  .product-image {
    height: 80px;
  }
}
</style>
