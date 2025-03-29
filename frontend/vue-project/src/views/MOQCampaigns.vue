<template>
  <MainLayout>
    <div class="all-products">
      <!-- Filters row -->
      <div class="filters-row flex flex-wrap gap-2 mb-6">
        <div class="filter-group flex items-center">
          <span class="mr-2">Filter:</span>
          <select
            id="category-filter"
            v-model="selectedCategorySlug"
            @change="onFilterChange"
            class="border px-2 py-1 w-64"
            aria-label="Filter by category"
            :disabled="store.loading.allCategoriesWithProducts || !store.allCategoriesWithProducts.length"
          >
            <option value="">All categories</option>
            <option v-for="category in store.allCategoriesWithProducts" :key="category.id" :value="category.slug">
              {{ category.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <select
            id="sort-filter"
            v-model="sortOption"
            @change="onFilterChange"
            class="border px-2 py-1 w-48"
            aria-label="Sort products"
            :disabled="store.loading.allCategoriesWithProducts || !store.allCategoriesWithProducts.length"
          >
            <option value="default">Default order</option>
            <option value="price_asc">Price (Low to High)</option>
            <option value="price_desc">Price (High to Low)</option>
            <option value="moq_status_active">MOQ Status (Active First)</option>
          </select>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="store.loading.allCategoriesWithProducts" class="loading">Loading products...</div>

      <!-- Error message -->
      <div v-else-if="store.error.allCategoriesWithProducts" class="bg-red-100 text-red-700 p-4 rounded mb-4" role="alert">
        <strong>Error:</strong> {{ store.error.allCategoriesWithProducts }}
        <button @click="retryLoading" class="underline ml-2">Retry</button>
      </div>

      <!-- Products Grid -->
      <div v-else class="products-container">
        <div v-if="allFilteredProducts.length > 0" class="products-grid">
          <div v-for="product in sortedProducts(allFilteredProducts)" :key="product.id" class="product-card">
            <router-link :to="`/product/${product.category_slug || 'uncategorized'}/${product.slug}`" class="product-link">
              <div class="product-image">
                <img :src="product.thumbnail || '/path/to/placeholder.jpg'" :alt="product.name">
              </div>
              <div class="product-info">
                <h3 class="product-name">{{ product.name }}</h3>
                <div class="product-price">
                  <span class="price-highlight">KES {{ product.price }}</span>
                  <span v-if="product.below_moq_price" class="below-moq-price">Below MOQ Price: KES {{ product.below_moq_price }}</span>
                  <span v-else class="below-moq-price">Below MOQ Price: NA</span>
                </div>
                <div class="product-moq-info">
                  <div class="moq-info">MOQ: {{ product.moq || 1 }} Items</div>
                </div>
                <div class="product-status">
                  <span class="status-text">{{ product.moq_status || 'Active' }}</span>
                  <div class="progress-container">
                    <div class="progress-bar" :style="{ width: `${product.moq_progress?.percentage || '40'}%` }"></div> <!-- Development-->
                    <span class="progress-text">{{ product.moq_progress?.percentage || '40' }}% Orders</span>
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>

        <!-- No Products -->
        <div v-else class="no-products">
          No products available.
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted } from 'vue';
import MainLayout from '@/components/navigation/MainLayout.vue';
import { useEcommerceStore } from '@/stores/ecommerce';

export default {
  name: 'AllProducts',
  components: {
    MainLayout,
  },
  setup() {
    const store = useEcommerceStore();

    onMounted(() => {
      // Initialize the API instance if not already done
      if (!store.apiInstance) {
        store.initializeApiInstance();
      }
      // Fetch all categories with products if not already loaded
      if (!store.allCategoriesWithProducts.length) {
        store.fetchAllCategoriesWithProducts();
      }
    });

    return { store };
  },
  data() {
    return {
      selectedCategorySlug: '',
      sortOption: 'default',
    };
  },
  computed: {
    allFilteredProducts() {
      let products = [];
      // Collect all products from all categories
      this.store.allCategoriesWithProducts.forEach(category => {
        if (category.products && category.products.length > 0) {
          // Add category_slug to each product for routing
          const productsWithCategory = category.products.map(product => ({
            ...product,
            category_slug: category.slug,
          }));
          products = [...products, ...productsWithCategory];
        }
      });

      // Filter by selected category if applicable
      if (this.selectedCategorySlug) {
        products = products.filter(product => product.category_slug === this.selectedCategorySlug);
      }

      return products;
    },
  },
  methods: {
    sortedProducts(products) {
      const sorted = [...products]; // Create a copy to avoid mutating the original array
      switch (this.sortOption) {
        case 'price_asc':
          return sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
        case 'price_desc':
          return sorted.sort((a, b) => (b.price || 0) - (a.price || 0));
        case 'moq_status_active':
          return sorted.sort((a, b) => {
            const statusA = (a.moq_status || 'Active').toLowerCase();
            const statusB = (b.moq_status || 'Active').toLowerCase();
            if (statusA === 'active' && statusB !== 'active') return -1;
            if (statusA !== 'active' && statusB === 'active') return 1;
            return 0;
          });
        case 'default':
        default:
          return sorted; // Return original order
      }
    },
    onFilterChange() {
      // No need to reload data since filtering and sorting are done on the client side
    },
    retryLoading() {
      this.store.fetchAllCategoriesWithProducts();
    },
  },
};
</script>

<style scoped>
.all-products {
  font-family: 'Roboto', sans-serif;
  padding: 12px;
}

/* Filters row */
.filters-row {
  display: flex;
  gap: 20px;
  margin-bottom: 1.5rem;
}

.filter-group {
  display: flex;
  align-items: center;
}

.filter-group span {
  color: #333;
  font-weight: 500;
}

.filter-group select {
  border: 1px solid #ddd;
  padding: 0.5rem;
  border-radius: 4px;
  background-color: #fff;
  cursor: pointer;
  font-size: 0.875rem;
}

.filter-group select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

/* Container for all products */
.products-container {
  padding: 1rem;
}

/* Loading and no-products states */
.loading,
.no-products {
  text-align: center;
  padding: 20px;
}

/* Products grid */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

/* Individual product card */
.product-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.product-link {
  display: block;
  text-decoration: none;
  color: inherit;
}

.product-image {
  height: 120px; /* Adjusted to match the image */
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #666;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  padding: 8px; /* Reduced padding to match the compact look */
}

.product-name {
  font-size: 0.85rem; /* Smaller font to match the image */
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
  display: flex;
  flex-direction: column;
  margin: 0.25rem 0;
}

.price-highlight {
  font-size: 0.9rem; /* Slightly smaller to match the image */
  font-weight: 700;
}

.below-moq-price {
  font-size: 0.7rem;
}

.product-moq-info {
  font-size: 0.7rem; /* Smaller font to match the image */
  margin: 0.25rem 0;
}

.moq-detail {
  color: #777;
}

.product-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-text {
  font-size: 0.7rem; /* Smaller font to match the image */
  color: #28a745; /* Green for active status */
  background-color: #e6f4ea;
  padding: 0.2rem 0.4rem;
  border-radius: 12px;
  margin: 0.25rem 0;
  width: fit-content;
}

.progress-container {
  position: relative;
  height: 20px;
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #8BC34A;
  border-radius: 10px;
}

.progress-text {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  font-size: 0.7rem; /* Smaller font to match the image */
  font-weight: 500;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
  .filters-row {
    flex-direction: column;
    gap: 10px;
  }
  .filter-group select {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
  .product-image {
    height: 100px;
  }
}
</style>
