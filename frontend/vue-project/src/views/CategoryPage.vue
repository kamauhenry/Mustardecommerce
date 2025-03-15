<template>
    <MainLayout>
    <div class="category-products-container">
      <!-- Header with title and filters -->
      <div class="header-section flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold">{{ categoryTitle }}</h1>

        <div class="filters flex gap-4">
          <!-- Category Filter -->
          <div class="filter-group">
            <label for="category-filter" class="block text-sm font-medium mb-1">Category</label>
            <select
              id="category-filter"
              v-model="selectedCategory"
              @change="loadProducts"
              class="border rounded p-2 w-40"
            >
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>

          <!-- Sort Filter -->
          <div class="filter-group">
            <label for="sort-filter" class="block text-sm font-medium mb-1">Sort By</label>
            <select
              id="sort-filter"
              v-model="sortOption"
              @change="applySorting"
              class="border rounded p-2 w-40"
            >
              <option value="name_asc">Name (A-Z)</option>
              <option value="name_desc">Name (Z-A)</option>
              <option value="price_asc">Price (Low to High)</option>
              <option value="price_desc">Price (High to Low)</option>
              <option value="newest">Newest First</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="flex justify-center py-8">
        <div class="loader">Loading...</div>
      </div>

      <!-- Error message -->
      <div v-else-if="error" class="bg-red-100 text-red-700 p-4 rounded mb-4">
        {{ error }}
      </div>

      <!-- Empty state -->
      <div v-else-if="products.length === 0" class="py-8 text-center text-gray-500">
        No products found in this category.
      </div>

      <!-- Products grid -->
      <div v-else class="products-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div v-for="product in products" :key="product.id" class="product-card border rounded overflow-hidden shadow-sm hover:shadow-md transition-shadow">
          <div class="product-image h-48 overflow-hidden bg-gray-100">
            <img
              :src="product.image_url"
              :alt="product.name"
              class="w-full h-full object-cover"
              @error="handleImageError($event, product)"
            />
          </div>

          <div class="product-info p-4">
            <h3 class="font-medium text-lg mb-1">{{ product.name }}</h3>
            <p class="text-gray-500 text-sm mb-2">{{ product.short_description }}</p>
            <div class="flex justify-between items-center">
              <span class="font-bold text-lg">${{ product.price.toFixed(2) }}</span>
              <button
                @click="viewProductDetails(product.id)"
                class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination / Load More -->
      <div v-if="hasMoreProducts" class="flex justify-center mt-8">
        <button
          @click="loadMoreProducts"
          class="bg-gray-200 hover:bg-gray-300 px-6 py-2 rounded font-medium"
          :disabled="loadingMore"
        >
          {{ loadingMore ? 'Loading...' : 'See More' }}
        </button>
      </div>
    </div>
  </MainLayout>
</template>


<script>
  import MainLayout from "@/components/navigation/MainLayout.vue";

  import axios from 'axios';

  export default {
    name: 'CategoryProducts',
    props: {
      initialCategoryId: {
        type: [String, Number],
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
        selectedCategory: '',
        sortOption: 'name_asc',
        loading: true,
        loadingMore: false,
        error: null,
        page: 1,
        hasMoreProducts: false,
        perPage: 12
      };
    },
    created() {
      this.selectedCategory = this.initialCategoryId;
      this.loadCategories();
      this.loadProducts();
    },
    methods: {
      async loadCategories() {
        try {
          const response = await axios.get('/api/categories');
          this.categories = response.data;
        } catch (error) {
          console.error('Error loading categories:', error);
          this.error = 'Failed to load categories. Please try again.';
        }
      },

      async loadProducts() {
        this.loading = true;
        this.error = null;
        this.page = 1;

        try {
          const response = await axios.get('/api/products', {
            params: {
              category_id: this.selectedCategory,
              sort: this.sortOption,
              page: this.page,
              per_page: this.perPage
            }
          });

          this.products = response.data.products;
          this.hasMoreProducts = response.data.total > this.products.length;

        } catch (error) {
          console.error('Error loading products:', error);
          if (error.response && error.response.status === 403) {
            this.error = 'You do not have permission to view these products.';
          } else {
            this.error = 'Failed to load products. Please try again.';
          }
        } finally {
          this.loading = false;
        }
      },

      async loadMoreProducts() {
        this.loadingMore = true;
        this.page += 1;

        try {
          const response = await axios.get('/api/products', {
            params: {
              category_id: this.selectedCategory,
              sort: this.sortOption,
              page: this.page,
              per_page: this.perPage
            }
          });

          this.products = [...this.products, ...response.data.products];
          this.hasMoreProducts = response.data.total > this.products.length;

        } catch (error) {
          console.error('Error loading more products:', error);
          this.error = 'Failed to load more products. Please try again.';
        } finally {
          this.loadingMore = false;
        }
      },

      applySorting() {
        this.loadProducts();
      },

      viewProductDetails(productId) {
        this.$router.push(`/product/${productId}`);
      },

      handleImageError(event, product) {
        // Replace with fallback image
        event.target.src = '/images/placeholder-product.jpg';
        console.warn(`Failed to load image for product: ${product.name}`);
      }
    },
    components: {
      MainLayout,
    }
  };
</script>

<style scoped>
.category-page {
  padding: 20px;
  color: black;
}

.product-card {
  background: #333;
  color: white;
  padding: 15px;
  margin: 10px;
  border-radius: 10px;
  display: inline-block;
  width: 200px;
  text-align: center;
}

.product-card img {
  width: 100%;
  height: auto;
  border-radius: 8px;
}

.price {
  color: #ffcc00;
  font-weight: bold;
}
</style>
