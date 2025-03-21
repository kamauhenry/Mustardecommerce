<template>
  <MainLayout>
    <div id="productsPage">
      <!-- Loading and Error States -->
      <div v-if="store.loading.allCategoriesWithProducts" class="loading">Loading...</div>
      <div v-else-if="store.error.allCategoriesWithProducts" class="error">
        {{ store.error.allCategoriesWithProducts }}
      </div>
      <div v-else class="products-page-container">
        <!-- Filter and Sort Controls -->
        <div class="controls-container">
          <!-- Category Filter -->
          <div class="filter-container">
            <label for="category-filter" class="filter-label">Filter:</label>
            <select
              id="category-filter"
              v-model="selectedCategory"
              @change="filterProducts"
              class="category-select"
            >
              <option value="">All Categories</option>
              <option
                v-for="category in store.allCategoriesWithProducts"
                :key="category.id"
                :value="category.slug"
              >
                {{ category.name }}
              </option>
            </select>
          </div>

          <!-- Sort Options -->
          <div class="sort-container">
            <label for="sort-by" class="sort-label">Sort by:</label>
            <select id="sort-by" v-model="sortBy" @change="sortProducts" class="sort-select">
              <option value="name-asc">Alphabetical (A-Z)</option>
              <option value="name-desc">Alphabetical (Z-A)</option>
              <option value="price-asc">Price (Low to High)</option>
              <option value="price-desc">Price (High to Low)</option>
              <option value="status-asc">Status (Active First)</option>
              <option value="status-desc">Status (Inactive First)</option>
            </select>
          </div>

          <!-- Search Input -->
          <div class="search-container">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search products..."
              class="search-input"
            />
          </div>
        </div>

        <!-- Products Grid -->
        <div class="products-grid">
          <router-link
            v-for="product in displayedProducts"
            :key="product.id"
            :to="`/category/${getCategorySlug(product)}/${product.slug}`"
            class="product-card"
            @click="trackProductClick(product)"
          >
            <img :src="product.thumbnail || placeholder" :alt="product.name" class="product-image" />
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-price">KES {{ product.price }}</p>
            <p class="moq-info">MOQ: {{ product.moq }} items</p>
            <p class="moq-status">{{ product.moq_status }}</p>
          </router-link>
        </div>

        <!-- No Products Message -->
        <div v-if="!displayedProducts.length" class="no-products">
          No products available
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted, ref, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';
import { trackProduct } from '@/utils/tracking'; // Import trackProduct
import placeholder from '@/assets/images/placeholder.png';

export default {
  setup() {
    const store = useEcommerceStore();
    const selectedCategory = ref('');
    const sortBy = ref('name-asc'); // Default sort by alphabetical order (A-Z)
    const searchQuery = ref(''); // Search query

    // Fetch all categories with products on mount
    onMounted(() => {
      if (!store.allCategoriesWithProducts.length) {
        store.fetchAllCategoriesWithProducts();
      }
    });

    // Compute filtered products based on selected category
    const filteredProducts = computed(() => {
      const allProducts = [];

      // Collect all products from all categories
      store.allCategoriesWithProducts.forEach(category => {
        if (category.products && category.products.length > 0) {
          allProducts.push(...category.products);
        }
      });

      // Filter by category
      let filtered = allProducts;
      if (selectedCategory.value) {
        filtered = allProducts.filter(product => {
          const category = store.allCategoriesWithProducts.find(cat => cat.slug === selectedCategory.value);
          return category.products.some(p => p.id === product.id);
        });
      }

      // Filter by search query
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.trim().toLowerCase();
        filtered = filtered.filter(product =>
          product.name.toLowerCase().includes(query)
        );
      }

      return filtered;
    });

    // Compute sorted and filtered products for display
    const displayedProducts = computed(() => {
      const products = [...filteredProducts.value];

      // Sort based on sortBy value
      switch (sortBy.value) {
        case 'name-asc':
          return products.sort((a, b) => a.name.localeCompare(b.name));
        case 'name-desc':
          return products.sort((a, b) => b.name.localeCompare(a.name));
        case 'price-asc':
          return products.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
        case 'price-desc':
          return products.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
        case 'status-asc':
          return products.sort((a, b) => {
            const statusA = a.moq_status.toLowerCase() === 'active' ? 1 : 0;
            const statusB = b.moq_status.toLowerCase() === 'active' ? 1 : 0;
            return statusB - statusA;
          });
        case 'status-desc':
          return products.sort((a, b) => {
            const statusA = a.moq_status.toLowerCase() === 'active' ? 1 : 0;
            const statusB = b.moq_status.toLowerCase() === 'active' ? 1 : 0;
            return statusA - statusB;
          });
        default:
          return products;
      }
    });

    // Filter function (handled by computed property)
    const filterProducts = () => {
      // automatically updates
    };

    // Sort function (handled by computed property)
    const sortProducts = () => {
      // automatically updates
    };

    // Get the category slug for a product
    const getCategorySlug = (product) => {
      const category = store.allCategoriesWithProducts.find(cat =>
        cat.products.some(p => p.id === product.id)
      );
      return category ? category.slug : '';
    };

    // Track product click
    const trackProductClick = (product) => {
      const categorySlug = getCategorySlug(product);
      if (categorySlug) {
        trackProduct(product, categorySlug);
      }
    };

    return {
      store,
      selectedCategory,
      sortBy,
      searchQuery,
      displayedProducts,
      filterProducts,
      sortProducts,
      getCategorySlug,
      trackProductClick
    };
  },
  components: {
    MainLayout,
  }
};
</script>

<style scoped>
.top-row-home {
  display: flex;
  flex-direction: row;
  gap: 1rem;
  margin-top: 1rem;
}

.products-page-container {
  padding: 1rem;
}

.controls-container {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.search-container {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.search-input {
  width: 60%;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 0.9rem;
  background-color: #fff;
}

.search-input:focus {
  outline: none;
  border-color: #f28c38;
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.category-select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 0.9rem;
  background-color: #fff;
  cursor: pointer;
}

.category-select:focus {
  outline: none;
  border-color: #f28c38;
}

.sort-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.sort-select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 0.9rem;
  background-color: #fff;
  cursor: pointer;
}

.sort-select:focus {
  outline: none;
  border-color: #f28c38;
}

/* Products grid (reusing the same styling) */
.products-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.75rem;
}

/* Individual product card (reusing the same styling) */
.product-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  border-radius: 6px;
  padding: 0.5rem;
  transition: transform 0.2s ease;
  text-decoration: none; /* Remove underline from router-link */
  color: inherit; /* Inherit text color */
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

/* No products message */
.no-products {
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
}

@media (max-width: 768px) {
  .top-row-home {
    flex-direction: column;
    gap: 1rem;
    justify-content: center;
  }

  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .controls-container {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-container,
  .filter-container,
  .sort-container {
    width: 100%;
  }

  .search-input,
  .category-select,
  .sort-select {
    width: 100%;
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

  .product-image {
    height: 80px;
  }
}
</style>
