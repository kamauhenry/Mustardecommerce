<template>
  <MainLayout>
    <div class="category-products-container">
      <!-- Header with title -->
      <div class="mb-4">
        <h2 class="text-lg font-medium text-green-800">MOD CAMPAIGNS</h2>
      </div>
      
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
      <div v-if="loading" class="flex justify-center py-8" role="status" aria-live="polite">
        <div class="loader" aria-label="Loading products">Loading...</div>
      </div>
      
      <!-- Error message -->
      <div v-else-if="error" class="bg-red-100 text-red-700 p-4 rounded mb-4" role="alert">
        <strong>Error:</strong> {{ error }}
        <button @click="retryLoading" class="underline ml-2">Retry</button>
      </div>
      
      <!-- Empty state -->
      <div v-else-if="!products || products.length === 0" class="py-8 text-center text-gray-500">
        No products found in this category. Try selecting a different category.
      </div>
      
      <!-- Products list view -->
      <div v-else class="products-list">
        <div 
          v-for="(product, index) in products" 
          :key="product.id" 
          class="product-item py-4"
          :class="{ 'border-t': index > 0 }"
          :aria-label="`Product: ${product.name}`"
        >
          <div class="text-gray-700">{{ currentYear }} Item{{ product.id }}</div>
          <div class="text-red-500 font-bold text-lg">KES 499</div>
          <div class="text-gray-700">Below MOD price: KES 499</div>
          <div class="text-gray-700">MOD: {{ 11 + index }} Items</div>
          <div class="text-gray-700">Active</div>
          <div class="flex items-center gap-2 mt-1">
            <span class="font-semibold">199%</span>
            <button 
              @click="viewProductDetails(product.category_slug, product.slug)"
              class="border border-gray-300 bg-gray-100 hover:bg-gray-200 px-3 py-1 text-sm"
              :aria-label="`Orders for ${product.name}`"
            >
              Orders
            </button>
          </div>
        </div>
      </div>
      
      <!-- Pagination / Load More -->
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
  import MainLayout from "@/components/navigation/MainLayout.vue";
  import axios from 'axios';
  import { debounce } from 'lodash';

  export default {
    name: 'CategoryProducts',
    components: {
      MainLayout
    },
    props: {
      initialCategorySlug: {
        type: String,
        default: ''
      },
      categoryTitle: {
        type: String,
        default: 'Products'
      }
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
        perPage: 10,
        category: {},
        currentYear: new Date().getFullYear()
      };
    },
    created() {
      this.selectedCategorySlug = this.initialCategorySlug;
      this.loadCategories();
      if (this.selectedCategorySlug) {
        this.loadProductsByCategory();
      } else {
        this.loadProducts();
      }
      
      // Create debounced version of loadProducts
      this.debouncedLoadProducts = debounce(this.onFilterChange, 300);
    },
    methods: {
      async loadCategories() {
        try {
          const response = await axios.get('/api/categories/');
          if (response.data && Array.isArray(response.data)) {
            this.categories = response.data;
          } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
            // Handle paginated response format
            this.categories = response.data.results;
          } else {
            console.warn('Categories response is not in expected format:', response.data);
            this.categories = [];
          }
        } catch (error) {
          console.error('Error loading categories:', error);
          this.error = 'Failed to load categories. Please check your network connection.';
        }
      },
      
      async loadProducts() {
        this.loading = true;
        this.error = null;
        this.page = 1;
        
        try {
          const response = await axios.get('/api/products/', {
            params: {
              sort: this.sortOption,
              page: this.page,
              per_page: this.perPage
            }
          });
          
          if (response.data && response.data.products) {
            this.products = this.processProducts(response.data.products);
            this.hasMoreProducts = response.data.total > this.products.length;
          } else if (Array.isArray(response.data)) {
            // Handle if API returns array directly
            this.products = this.processProducts(response.data);
            this.hasMoreProducts = false;
          } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
            // Handle paginated response
            this.products = this.processProducts(response.data.results);
            this.hasMoreProducts = response.data.next !== null;
          } else {
            console.warn('Products response is not in expected format:', response.data);
            this.products = [];
            this.hasMoreProducts = false;
          }
          
        } catch (error) {
          this.handleApiError(error, 'products');
        } finally {
          this.loading = false;
        }
      },
      
      processProducts(products) {
        // Ensure each product has a category_slug for routing
        return products.map(product => {
          // If category_slug is missing, use the current selected category or a default
          if (!product.category_slug) {
            product.category_slug = this.selectedCategorySlug || 'uncategorized';
          }
          return product;
        });
      },
      
      async loadProductsByCategory() {
        this.loading = true;
        this.error = null;
        this.page = 1;
        
        if (!this.selectedCategorySlug) {
          this.loadProducts();
          return;
        }
        
        try {
          // Using the correct URL from your API routes
          const response = await axios.get(`/api/category/${this.selectedCategorySlug}/products/`, {
            params: {
              sort: this.sortOption,
              page: this.page,
              per_page: this.perPage
            }
          });
          
          if (response.data && response.data.category && response.data.products) {
            // Handle the format from your CategoryProductsView
            this.category = response.data.category;
            // Add category_slug to each product for routing
            this.products = response.data.products.map(product => {
              product.category_slug = this.selectedCategorySlug;
              return product;
            });
            this.hasMoreProducts = false; // API doesn't support pagination for category products yet
          } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
            // Handle paginated response if that's what's coming back
            this.products = response.data.results.map(product => {
              product.category_slug = this.selectedCategorySlug;
              return product;
            });
            this.hasMoreProducts = response.data.next !== null;
          } else if (Array.isArray(response.data)) {
            // Handle direct array response
            this.products = response.data.map(product => {
              product.category_slug = this.selectedCategorySlug;
              return product;
            });
            this.hasMoreProducts = false;
          } else {
            console.warn('Category products response is not in expected format:', response.data);
            this.products = [];
            this.hasMoreProducts = false;
          }
          
        } catch (error) {
          this.handleApiError(error, 'category products');
        } finally {
          this.loading = false;
        }
      },
      
      async loadMoreProducts() {
        if (!this.hasMoreProducts || this.selectedCategorySlug) return;
        
        this.loadingMore = true;
        this.page += 1;
        
        try {
          const response = await axios.get('/api/products/', {
            params: {
              sort: this.sortOption,
              page: this.page,
              per_page: this.perPage
            }
          });
          
          let newProducts = [];
          
          if (response.data && response.data.products) {
            newProducts = this.processProducts(response.data.products);
            this.hasMoreProducts = response.data.total > (this.products.length + newProducts.length);
          } else if (Array.isArray(response.data)) {
            newProducts = this.processProducts(response.data);
            this.hasMoreProducts = response.data.length === this.perPage;
          } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
            newProducts = this.processProducts(response.data.results);
            this.hasMoreProducts = response.data.next !== null;
          } else {
            console.warn('Products response is not in expected format:', response.data);
          }
          
          this.products = [...this.products, ...newProducts];
          
        } catch (error) {
          console.error('Error loading more products:', error);
          this.error = 'Failed to load more products. Please try again.';
        } finally {
          this.loadingMore = false;
        }
      },
      
      onFilterChange() {
        if (this.selectedCategorySlug) {
          this.loadProductsByCategory();
        } else {
          this.loadProducts();
        }
      },
      
      retryLoading() {
        if (this.selectedCategorySlug) {
          this.loadProductsByCategory();
        } else {
          this.loadProducts();
        }
      },
      
      viewProductDetails(categorySlug, productSlug) {
        // Navigate to product detail using the URL pattern you provided
        this.$router.push(`/products/${categorySlug}/${productSlug}/`);
      },
      
      handleImageError(event, product) {
        // Replace with fallback image
        event.target.src = '/images/placeholder-product.jpg';
        console.warn(`Failed to load image for product: ${product.name}`);
      },
      
      handleApiError(error, resourceType) {
        console.error(`Error loading ${resourceType}:`, error);
        
        if (error.response) {
          switch (error.response.status) {
            case 403:
              this.error = `You do not have permission to view these ${resourceType}.`;
              break;
            case 404:
              this.error = `The requested ${resourceType} were not found.`;
              break;
            case 500:
              this.error = 'Server error. Please try again later.';
              break;
            default:
              this.error = `Error (${error.response.status}): Failed to load ${resourceType}.`;
          }
        } else if (error.request) {
          this.error = 'Network error. Please check your connection.';
        } else {
          this.error = `Failed to load ${resourceType}. Please try again.`;
        }
      }
    }
  };
</script>

<style scoped>
.loader {
  display: inline-block;
  width: 50px;
  height: 50px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.product-item {
  position: relative;
}

.product-item:not(:first-child) {
  border-top: 1px solid #eee;
}
</style>