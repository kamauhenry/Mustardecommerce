<template>
  <MainLayout>
    <div class="moq-campaigns">
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
            :disabled="loading || !categories.length"
          >
            <option value="">All categories</option>
            <option v-for="category in categories" :key="category.id" :value="category.slug">
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
            :disabled="loading || !categories.length"
          >
            <option value="name_asc">Default order</option>
            <option value="name_desc">Name (Z-A)</option>
            <option value="price_asc">Price (Low to High)</option>
            <option value="price_desc">Price (High to Low)</option>
            <option value="newest">Newest First</option>
          </select>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="loading">Loading products...</div>

      <!-- Error message -->
      <div v-else-if="error" class="bg-red-100 text-red-700 p-4 rounded mb-4" role="alert">
        <strong>Error:</strong> {{ error }}
        <button @click="retryLoading" class="underline ml-2">Retry</button>
      </div>

      <!-- Empty state -->
      <div v-else-if="!products || products.length === 0" class="no-products">
        No products available.
      </div>

      <!-- Products grid -->
      <div v-else class="products-grid">
        <div v-for="(product, index) in products" :key="product.id" class="product-card">
          <router-link :to="`/product/${product.category_slug || 'uncategorized'}/${product.slug}`" class="product-link">
            <div class="product-image">
              <img :src="product.thumbnail || '/path/to/placeholder.jpg'" :alt="product.name">
            </div>
            <div class="product-info">
              <h3 class="product-name">{{ product.name }}</h3>
              <div class="product-price">
                <span class="price-highlight">KES {{ product.price }}</span>
              </div>
              <div class="product-moq-info">
                <div class="below-moq">Below MOQ Price: KES {{ product.below_moq_price || product.price }}</div>
                <div class="moq-detail">MOQ: {{ product.moq || 1 }} Items</div>
              </div>
              <div class="product-status">
                <span class="status-text">{{ product.moq_status || 'Active' }}</span>
                <div class="progress-container">
                  <div class="progress-bar" :style="{ width: `${product.moq_progress?.percentage || '100'}%` }"></div>
                  <span class="progress-text">{{ product.moq_progress?.percentage || '100' }}% Orders</span>
                </div>
              </div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMoreProducts" class="flex justify-center mt-8">
        <button
          @click="loadMoreProducts"
          class="bg-gray-200 hover:bg-gray-300 px-6 py-2 rounded font-medium"
          :disabled="loadingMore"
          aria-label="Load more products"
        >
          <span v-if="loadingMore">Loading...</span>
          <span v-else>See More</span>
        </button>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import axios from 'axios';
import MainLayout from '@/components/navigation/MainLayout.vue'; // Import MainLayout

export default {
  name: 'CategoryProducts',
  components: {
    MainLayout, // Register MainLayout as a component
  },
  data() {
    return {
      products: [],
      categories: [],
      selectedCategorySlug: '',
      sortOption: 'name_asc',
      loading: true,
      loadingMore: false,
      error: null,
      page: 1,
      hasMoreProducts: false,
      perPage: 5,
      retryAttempts: 0,
      maxRetries: 3,
    };
  },
  mounted() {
    this.loadCategories().then(() => this.loadProducts());
  },
  methods: {
    async loadCategories() {
      this.error = null;
      try {
        const response = await axios.get('/api/categories/', {
          // timeout: 15000,
        });
        console.log('Categories response:', response.data); // Debugging
        this.categories = Array.isArray(response.data) ? response.data : [];
        if (!this.categories.length) {
          console.warn('No categories loaded from API');
          this.error = 'No categories available.';
        }
      } catch (error) {
        console.error('Error loading categories:', error.response ? error.response.data : error);
        if (error.code === 'ECONNABORTED' && this.retryAttempts < this.maxRetries) {
          this.retryAttempts += 1;
          console.log(`Retrying loadCategories (attempt ${this.retryAttempts}/${this.maxRetries})...`);
          await new Promise(resolve => setTimeout(resolve, 20000));
          return this.loadCategories();
        }
        this.error = `Failed to load categories: ${error.message}. ${error.code === 'ECONNABORTED' ? '(Request timed out)' : ''}`;
      }
    },
    async loadProducts() {
      this.loading = true;
      this.error = null;
      this.page = 1;
      this.retryAttempts = 0;

      try {
        const response = await axios.get('/api/products/', {
          params: {
            category: this.selectedCategorySlug || undefined,
            sort: this.sortOption,
            page: this.page,
            per_page: this.perPage,
          },
          // timeout: 15000,
        });
        console.log('Products response:', response.data); // Debugging
        if (response.data && Array.isArray(response.data.products)) {
          this.products = this.processProducts(response.data.products);
          this.hasMoreProducts = response.data.total > this.products.length;
        } else {
          this.products = [];
          this.hasMoreProducts = false;
          this.error = 'No products available.';
        }
      } catch (error) {
        console.error('Error loading products:', error.response || error);
        if (error.code === 'ECONNABORTED' && this.retryAttempts < this.maxRetries) {
          this.retryAttempts += 1;
          console.log(`Retrying loadProducts (attempt ${this.retryAttempts}/${this.maxRetries})...`);
          await new Promise(resolve => setTimeout(resolve, 20000));
          return this.loadProducts();
        }
        this.error = `Failed to load products: ${error.message}. ${error.code === 'ECONNABORTED' ? '(Request timed out)' : ''}`;
      } finally {
        this.loading = false;
      }
    },
    async loadMoreProducts() {
      if (!this.hasMoreProducts) return;

      this.loadingMore = true;
      this.page += 1;
      this.retryAttempts = 0;

      try {
        const response = await axios.get('/api/products/', {
          params: {
            category: this.selectedCategorySlug || undefined,
            sort: this.sortOption,
            page: this.page,
            per_page: this.perPage,
          },
          // timeout: 15000,
        });
        console.log('Load more products response:', response.data); // Debugging
        let newProducts = [];
        if (response.data && Array.isArray(response.data.products)) {
          newProducts = this.processProducts(response.data.products);
          this.hasMoreProducts = response.data.total > (this.products.length + newProducts.length);
        } else {
          this.hasMoreProducts = false;
        }

        this.products = [...this.products, ...newProducts];
      } catch (error) {
        console.error('Error loading more products:', error.response || error);
        if (error.code === 'ECONNABORTED' && this.retryAttempts < this.maxRetries) {
          this.retryAttempts += 1;
          console.log(`Retrying loadMoreProducts (attempt ${this.retryAttempts}/${this.maxRetries})...`);
          await new Promise(resolve => setTimeout(resolve, 2000));
          return this.loadMoreProducts();
        }
        this.error = `Failed to load more products: ${error.message}. ${error.code === 'ECONNABORTED' ? '(Request timed out)' : ''}`;
      } finally {
        this.loadingMore = false;
      }
    },
    processProducts(products) {
      return products.map(product => ({
        ...product,
        category_slug: product.category_slug || this.selectedCategorySlug || 'uncategorized',
      }));
    },
    onFilterChange() {
      this.loadProducts();
    },
    retryLoading() {
      this.retryAttempts = 0;
      this.loadCategories().then(() => this.loadProducts());
    },
  },
};
</script>

<style scoped>
.moq-campaigns {
  font-family: 'Roboto', sans-serif;
  padding: 12px;
}

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

.loading,
.no-products {
  text-align: center;
  padding: 20px;
  color: #666;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.product-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.product-link {
  display: block;
  text-decoration: none;
  color: inherit;
}

.product-image {
  height: 160px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f8f8;
  border-bottom: 1px solid #eee;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  padding: 12px;
}

.product-name {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-price .price-highlight {
  color: #FF6B35;
  font-size: 18px;
  font-weight: 600;
}

.product-moq-info {
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.below-moq {
  margin-bottom: 2px;
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
  color: #555;
  font-size: 13px;
  font-weight: 500;
}

.progress-container {
  position: relative;
  height: 20px;
  width: 100px;
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
  font-size: 11px;
  font-weight: 500;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

@media (max-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
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
    grid-template-columns: 1fr;
  }
  .product-image {
    height: 120px;
  }
}
</style>