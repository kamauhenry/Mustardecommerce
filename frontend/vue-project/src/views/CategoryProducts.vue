<template>
  <MainLayout>
    <div class="container">
      <!-- Show loading if allCategoriesWithProducts is still loading -->
      <div v-if="store.loading.allCategoriesWithProducts" class="loading">
        Loading products...
      </div>
      <!-- Show loading if categoryProducts is loading and no products are available yet -->
      <div v-else-if="store.loading.categoryProducts && !products.length" class="loading">
        Loading products...
      </div>
      <!-- Show error if there's an error -->
      <div v-else-if="store.error.categoryProducts" class="error">
        Error: {{ store.error.categoryProducts }}
      </div>
      <div v-else>
        <!-- Display Category Name -->
        <h1 class="category-title">{{ category?.name || 'Category' }}</h1>

        <div class="products-grid">
          <div v-if="products.length > 0" class="products">
            <router-link
              v-for="product in products"
              :key="product.id"
              :to="`/products/${categorySlug}/${product.slug}`"
              class="product-card"
              @click="trackProductClick(product)"
            >
              <img
                :src="product.thumbnail"
                :alt="product.name"
                class="product-image"
              />
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-price">KES {{ product.price }}</p>
              <p class="moq-info">MOQ: {{ product.moq || 'N/A' }} items</p>
              <p class="moq-status">{{ product.moq_status || 'N/A' }}</p>
            </router-link>
          </div>
          <!-- Show "No products available" only if the category is confirmed to have no products -->
          <div v-else-if="isCategoryLoaded" class="no-products">
            No products available
          </div>
          <!-- Show loading if the category is still being fetched -->
          <div v-else class="loading">
            Loading products...
          </div>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMoreProducts" class="load-more">
          <button @click="loadMoreProducts" :disabled="store.loading.categoryProducts">
            {{ store.loading.categoryProducts ? 'Loading...' : 'Load More' }}
          </button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted, computed, ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '../components/navigation/MainLayout.vue';
import { trackCategory, trackProduct } from '@/utils/tracking';

export default {
  props: { categorySlug: String },
  components: { MainLayout },
  setup(props) {
    const store = useEcommerceStore();
    const currentPage = ref(1);
    const isCategoryLoaded = ref(false); // Track if the category data is fully loaded

    // Fetch products on mount
    onMounted(async () => {
      console.log(`CategoryProducts mounted with categorySlug: ${props.categorySlug}`);
      // Ensure allCategoriesWithProducts is loaded
      if (!store.allCategoriesWithProducts.length) {
        console.log('allCategoriesWithProducts is empty, fetching...');
        await store.fetchAllCategoriesWithProducts();
      } else {
        console.log('allCategoriesWithProducts already loaded:', store.allCategoriesWithProducts);
      }
      initializeProducts();
    });

    // Initialize products using pre-fetched data
    const initializeProducts = () => {
      // Find the category in allCategoriesWithProducts
      const categoryData = store.allCategoriesWithProducts.find(
        cat => cat.slug === props.categorySlug
      );
      console.log(`Category data for ${props.categorySlug}:`, categoryData);

      if (categoryData) {
        // Initialize categoryProducts with pre-fetched data
        if (!store.categoryProducts[props.categorySlug]) {
          store.categoryProducts[props.categorySlug] = {
            category: { slug: categoryData.slug, name: categoryData.name },
            products: categoryData.products || [],
            total: categoryData.products?.length || 0, // Initial total based on pre-fetched data
          };
        }
        // Track the category
        trackCategory(categoryData);
        isCategoryLoaded.value = true; // Mark the category as loaded
      } else {
        console.warn(`Category ${props.categorySlug} not found in allCategoriesWithProducts`);
        // If the category isn't found, fetch it
        fetchProducts();
      }
    };

    // Fetch products for the current page using fetchCategoryProducts
    const fetchProducts = async () => {
      await store.fetchCategoryProducts(props.categorySlug, currentPage.value);
      const categoryData = store.categoryProducts[props.categorySlug]?.category;
      if (categoryData) {
        trackCategory(categoryData);
      }
      isCategoryLoaded.value = true; // Mark the category as loaded after fetching
    };

    // Load more products (for pagination)
    const loadMoreProducts = () => {
      currentPage.value += 1;
      fetchProducts();
    };

    const category = computed(() => {
      return store.categoryProducts[props.categorySlug]?.category;
    });

    const products = computed(() => {
      return store.categoryProducts[props.categorySlug]?.products || [];
    });

    const totalProducts = computed(() => {
      return store.categoryProducts[props.categorySlug]?.total || 0;
    });

    const hasMoreProducts = computed(() => {
      return products.value.length < totalProducts.value;
    });

    // Track product click
    const trackProductClick = (product) => {
      trackProduct(product, props.categorySlug);
    };

    return {
      store,
      category,
      products,
      hasMoreProducts,
      loadMoreProducts,
      trackProductClick,
      isCategoryLoaded,
    };
  },
};
</script>

<style scoped>
/* Category title */
.category-title {
  font-size: 1.25rem;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0.5rem 0 1rem 0;
  color: #f28c38;
}

/* Products grid container */
.products-grid {
  display: flex;
  flex-direction: column;
}

/* Products container */
.products {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Individual product card */
.product-card {
  flex: 0 0 calc(25% - 0.75rem);
  max-width: calc(25% - 0.75rem);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
  text-decoration: none;
  color: inherit;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  background-color: #e0e0e0;
}

.product-name {
  font-size: 0.95rem;
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

.product-price {
  font-size: 0.9rem;
  font-weight: 700;
  margin: 0.25rem 0;
}

/* MOQ info */
.moq-info {
  font-size: 0.75rem;
  margin: 0.25rem 0;
}

/* MOQ status (e.g., active, not_applicable) */
.moq-status {
  font-size: 0.75rem;
  color: #28a745;
  background-color: #e6f4ea;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  margin: 0.25rem 0;
}

/* No products available message */
.no-products {
  text-align: center;
  padding: 1rem;
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
}

/* Loading and error states */
.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #666;
}

/* Load More Button */
.load-more {
  text-align: center;
  margin-top: 1rem;
}

.load-more button {
  padding: 0.75rem 1.5rem;
  background-color: #f28c38;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.load-more button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .product-card {
    flex: 0 0 calc(33.33% - 0.75rem);
    max-width: calc(33.33% - 0.75rem);
  }
}

@media (max-width: 768px) {
  .product-card {
    flex: 0 0 calc(50% - 0.75rem);
    max-width: calc(50% - 0.75rem);
  }

  .product-image {
    height: 120px;
  }

  .product-name {
    font-size: 0.85rem;
  }

  .product-price {
    font-size: 0.8rem;
  }

  .moq-info,
  .moq-status {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .product-card {
    flex: 0 0 calc(50% - 0.75rem);
    max-width: calc(50% - 0.75rem);
  }

  .product-image {
    height: 100px;
    width: auto;
  }
}
</style>
