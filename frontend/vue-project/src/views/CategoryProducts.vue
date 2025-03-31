<template>
  <MainLayout>
    <div class="container">
      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> /
        <router-link :to="`/category/${categorySlug}/products`">{{
          categoryName || categorySlug || 'Category'
        }}</router-link>
      </div>

      <!-- Category Header -->
      <div class="category-header" :style="{ backgroundImage: `url(${categoryImage})` }">
        <div class="category-header-content">
          <h1 class="category-title">{{ categoryName || 'Category' }}</h1>
          <p class="category-description">{{ categoryDescription || 'No description available.' }}</p>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="store.loading.categoryProducts" class="loading">Loading products...</div>

      <!-- Error message -->
      <div v-else-if="store.error.categoryProducts" class="error">
        Error: {{ store.error.categoryProducts }}
        <button @click="retryLoading" class="underline ml-2">Retry</button>
      </div>

      <!-- Products Grid -->
      <div v-else class="products-grid">
        <div v-if="products.length > 0" class="products">
          <div v-for="product in products" :key="product.id" class="product-card">
            <router-link
              :to="{
                name: 'product-detail',
                params: { categorySlug: categorySlug, productSlug: product.slug }
              }"
              class="product-link"
            >
              <img
                v-if="product.thumbnail"
                :src="product.thumbnail"
                :alt="product.name"
                class="product-image"
              />
              <div class="product-info">
                <h3 class="product-name">{{ product.name }}</h3>
                <div class="product-price">
                  <span class="price-highlight">KES {{ product.price }}</span>
                  <span v-if="product.below_moq_price" class="below-moq-price"
                    >Below MOQ Price: KES {{ product.below_moq_price }}</span
                  >
                  <span v-else class="below-moq-price">Below MOQ Price: NA</span>
                </div>
                <div class="product-moq-info">
                  <div class="moq-detail">MOQ: {{ product.moq || 'N/A' }} Items</div>
                </div>
                <div class="product-status">
                  <span class="status-text">{{ product.moq_status || 'Active' }}</span>
                  <div class="progress-container">
                    <div
                      class="progress-bar"
                      :style="{ width: `${product.moq_progress?.percentage || '0'}%` }"
                    ></div>
                    <span class="progress-text"
                      >{{ product.moq_progress?.percentage || '0' }}% Orders</span
                    >
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>
        <div v-else class="no-products">No products available</div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';

export default {
  name: 'CategoryProducts',
  components: { MainLayout },
  setup() {
    const route = useRoute();
    const store = useEcommerceStore();

    // Get category slug from route params
    const categorySlug = computed(() => route.params.categorySlug);

    // Fetch category products when the component is mounted or the category slug changes
    onMounted(() => {
      if (!store.apiInstance) {
        store.initializeApiInstance();
      }
      if (categorySlug.value) {
        store.fetchCategoryProducts(categorySlug.value);
      }
    });

    // Watch for changes in categorySlug and refetch products
    watch(categorySlug, (newSlug) => {
      if (newSlug) {
        store.fetchCategoryProducts(newSlug);
      }
    });

    // Compute category details
    const categoryName = computed(() => {
      const categoryData = store.categoryProducts[categorySlug.value]?.category;
      return categoryData?.name || '';
    });

    const categoryDescription = computed(() => {
      const categoryData = store.categoryProducts[categorySlug.value]?.category;
      return categoryData?.description || '';
    });

    const categoryImage = computed(() => {
      const categoryData = store.categoryProducts[categorySlug.value]?.category;
      return categoryData?.image || ''; // Fallback to empty string if no image
    });

    // Compute products for the current category
    const products = computed(() => {
      return store.categoryProducts[categorySlug.value]?.products || [];
    });

    // Retry loading products
    const retryLoading = () => {
      if (categorySlug.value) {
        store.fetchCategoryProducts(categorySlug.value);
      }
    };

    return {
      store,
      categorySlug,
      categoryName,
      categoryDescription,
      categoryImage,
      products,
      retryLoading,
    };
  },
};
</script>

<style scoped>
.container {
  font-family: 'Roboto', sans-serif;
  padding: 12px;
}

/* Breadcrumb styling */
.breadcrumb {
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.breadcrumb a {
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

/* Category Header */
.category-header {
  width: 100%;
  height: 300px; /* Adjust height as needed */
  background-size: cover;
  background-position: center;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.category-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3); /* Dark overlay for better text readability */
}

.category-header-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.category-title {
  font-family: 'Roboto', sans-serif;
  font-size: 2rem;
  font-weight: 900;
  color: #fff;
  margin-bottom: 0.5rem;
}

.category-description {
  font-family: 'Roboto', sans-serif;
  font-size: 1rem;
  font-weight: 500;
  color: #fff;
  margin: 0 1rem;
}

/* Products grid container */
.products-grid {
  display: flex;
  flex-direction: column;
}

/* Products container */
.products {
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
  height: 120px;
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
  padding: 8px;
}

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

.product-price {
  display: flex;
  flex-direction: column;
  margin: 0.25rem 0;
}

.price-highlight {
  font-size: 0.9rem;
  font-weight: 700;
}

.below-moq-price {
  font-size: 0.7rem;
}

.product-moq-info {
  font-size: 0.7rem;
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
  font-size: 0.7rem;
  color: #28a745;
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
  font-size: 0.7rem;
  font-weight: 500;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

/* Loading and error states */
.loading,
.error,
.no-products {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .products {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }

  .category-header {
    height: 250px;
  }

  .category-title {
    font-size: 1.5rem;
  }

  .category-description {
    font-size: 0.9rem;
  }
}

@media (max-width: 768px) {
  .products {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }

  .category-header {
    height: 200px;
  }

  .category-title {
    font-size: 1.25rem;
  }

  .category-description {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .products {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }

  .product-image {
    height: 100px;
  }

  .category-header {
    height: 150px;
  }

  .category-title {
    font-size: 1rem;
  }

  .category-description {
    font-size: 0.7rem;
  }
}
</style>
