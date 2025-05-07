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
      <div v-if="store.loading.categoryProducts" class="skeleton-header"></div>
      <div v-else class="category-header" :style="{ backgroundImage: `url(${categoryImage || 'https://via.placeholder.com/1200x400?text=Category+Image'})` }">
        <div class="category-header-content">
          <h1 class="category-title">{{ categoryName || 'Category' }}</h1>
          <p class="category-description">{{ categoryDescription || 'No description available.' }}</p>
        </div>
      </div>

      <!-- Loading state with skeleton -->
      <div v-if="store.loading.categoryProducts" class="skeleton-container">
        <div class="skeleton-products">
          <div v-for="n in 6" :key="n" class="skeleton-product"></div>
        </div>
      </div>

      <!-- Error message -->
      <div v-else-if="categoryError" class="error">
        Error: {{ categoryError }}
        <button @click="retryLoading" class="retry-button" tabindex="0">Retry</button>
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
              <div class="product-image-wrapper">
                <img
                  :src="product.thumbnail || 'data:image/jpeg;base64,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'"
                  :alt="product.name"
                  class="product-image"
                  loading="lazy"
                />
              </div>
              <div class="product-info">
                <h3 class="product-name">{{ product.name }}</h3>
                <div class="product-price">
                  <span class="price-highlight">KES {{ product.price }}</span>
                  <span v-if="product.below_moq_price" class="below-moq-price">
                    Below MOQ Price: KES {{ product.below_moq_price }}
                  </span>
                  <span v-else class="below-moq-price">Below MOQ Price: NA</span>
                </div>
                <div class="product-moq-info">
                  <span class="moq-detail">MOQ: {{ product.moq || 'N/A' }} Items</span>
                </div>
                <div class="product-status">
                  <span class="status-text">{{ product.moq_status || 'Active' }}</span>
                  <div class="progress-container">
                    <div
                      class="progress-bar"
                      :style="{ width: `${product.moq_progress?.percentage || '0'}%` }"
                    ></div>
                    <span class="progress-text">
                      {{ product.moq_progress?.percentage || '0' }}% Orders
                    </span>
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>
        <div v-else class="no-products">
          <p>No products available in this category.</p>
          <router-link to="/" class="cta-button">Explore Other Categories</router-link>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted, computed, watch, onUnmounted } from 'vue';
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
    const categorySlug = computed(() => {
      const slug = route.params.categorySlug || '';
      console.log('Category Slug:', slug);
      return slug;
    });

    // Fetch category products when the component is mounted or the category slug changes
    onMounted(() => {
      if (!store.apiInstance) {
        store.initializeApiInstance();
      }
      if (categorySlug.value) {
        console.log('Fetching data for category:', categorySlug.value);
        store.fetchCategoryProducts(categorySlug.value);
      }
    });

    // Watch for changes in categorySlug and refetch products
    watch(categorySlug, (newSlug) => {
      if (newSlug) {
        console.log('Category slug changed, refetching data for:', newSlug);
        store.fetchCategoryProducts(newSlug);
      }
    });

    // Clean up error state when the component is unmounted
    onUnmounted(() => {
      if (categorySlug.value) {
        store.error.categoryProducts[categorySlug.value] = null;
        console.log(`Cleared error for category: ${categorySlug.value}`);
      }
    });

    // Compute category details
    const categoryName = computed(() => {
      const name = store.categoryProducts[categorySlug.value]?.category?.name || '';
      console.log('Computed categoryName:', name);
      return name;
    });

    const categoryDescription = computed(() => {
      const description = store.categoryProducts[categorySlug.value]?.category?.description || '';
      console.log('Computed categoryDescription:', description);
      return description;
    });

    const categoryImage = computed(() => {
      const image = store.categoryProducts[categorySlug.value]?.category?.image || '';
      console.log('Computed categoryImage:', image);
      return image;
    });

    // Compute products for the current category
    const products = computed(() => {
      const products = store.categoryProducts[categorySlug.value]?.products || [];
      console.log('Computed products:', products);
      return products;
    });

    // Compute category-specific error
    const categoryError = computed(() => {
      const error = store.error.categoryProducts[categorySlug.value] || null;
      console.log('Computed categoryError:', error);
      return error;
    });

    // Retry loading products
    const retryLoading = () => {
      if (categorySlug.value) {
        console.log('Retrying fetch for category:', categorySlug.value);
        store.fetchCategoryProducts(categorySlug.value);
      }
    };

    // Debug the store state
    watch(() => store.categoryProducts, (newValue) => {
      console.log('Store categoryProducts updated:', newValue);
    }, { deep: true });

    watch(() => store.error.categoryProducts, (newError) => {
      console.log('Store error.categoryProducts updated:', newError);
    }, { deep: true });

    return {
      store,
      categorySlug,
      categoryName,
      categoryDescription,
      categoryImage,
      products,
      categoryError,
      retryLoading,
    };
  },
};
</script>

<style scoped>
.container {
  font-family: 'Roboto', sans-serif;
  padding: 1rem 3%;
  max-width: 1400px;
  margin: 0 auto;
}

/* Breadcrumb styling */
.breadcrumb {
  font-size: 0.9rem;
  margin-bottom: 1rem;
  color: #666;
}

.breadcrumb a {
  color:#D4A017;
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb a:hover {
  color: #e67d21;
  text-decoration: underline;
}

/* Category Header */
.category-header {
  width: 100%;
  height: 350px;
  background-size: cover;
  background-position: center;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.category-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6));
}

.category-header-content {
  text-align: center;
  position: relative;
  z-index: 1;
  padding: 1rem;
}

.category-title {
  font-family: 'Roboto', sans-serif;
  font-size: 2.5rem;
  font-weight: 900;
  color: #fff;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.category-description {
  font-family: 'Roboto', sans-serif;
  font-size: 1.1rem;
  font-weight: 400;
  color: #fff;
  margin: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

/* Skeleton Loader */
.skeleton-container {
  padding: 1rem 0;
}

.skeleton-products {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
}

.skeleton-product {
  height: 350px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* Products grid container */
.products-grid {
  display: flex;
  flex-direction: column;
}

/* Products container */
.products {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
}

/* Individual product card */
.product-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 350px;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.product-link {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  height: 100%;
}

/* Product image wrapper */
.product-image-wrapper {
  width: 100%;
  height: 200px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

/* Product info */
.product-info {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.product-name {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
  text-align: left;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-price {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
}

.price-highlight {
  font-size: 1rem;
  font-weight: 700;
  color:#D4A017;
}

.below-moq-price {
  font-size: 0.8rem;
}

/* MOQ info */
.product-moq-info {
  margin-bottom: 0.5rem;
}

.moq-detail {
  font-size: 0.85rem;
  background-color: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

/* Product status */
.product-status {
  margin-top: auto; /* Push to bottom of card */
}

.status-text {
  font-size: 0.8rem;
  color: #28a745;
  background-color: #e6f4ea;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  margin-bottom: 0.5rem;
  display: inline-block;
}

.progress-container {
  position: relative;
  height: 16px;
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  padding: 2px;
  background: linear-gradient(45deg, #62c87a, #6dc480);
  border-radius: 5px;
  transition: width 0.5s ease;
}

.progress-text {
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

/* Loading, error, and no-products states */
.loading,
.error,
.no-products {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.error {
  color: #dc3545;
}

.retry-button {
  background: none;
  border: none;
  color:#D4A017;
  font-size: 1rem;
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
  margin-left: 0.5rem;
  transition: color 0.3s ease;
}

.retry-button:hover {
  color: #e67d21;
}

.no-products {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.cta-button {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color:#D4A017;
  color: #fff;
  text-decoration: none;
  border-radius: 20px;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.cta-button:hover {
  background-color: #e67d21;
}

/* Shimmer animation for skeleton */
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Responsive adjustments */
@media (min-width: 1200px) {
  .products {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 1024px) {
  .products {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }

  .category-header {
    height: 300px;
  }

  .category-title {
    font-size: 2rem;
  }

  .category-description {
    font-size: 1rem;
  }

  .product-image-wrapper {
    height: 180px;
  }
}

@media (max-width: 768px) {
  .products {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  .skeleton-products {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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

  .product-image-wrapper {
    height: 160px;
  }

  .product-card {
    min-height: 320px;
  }

  .product-name {
    font-size: 0.95rem;
  }

  .price-highlight {
    font-size: 0.95rem;
  }

  .below-moq-price {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 1rem 2%;
  }

  .products {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
  }

  .skeleton-products {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
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

  .product-image-wrapper {
    height: 140px;
  }

  .product-card {
    min-height: 300px;
  }

  .product-name {
    font-size: 0.9rem;
  }

  .price-highlight {
    font-size: 0.9rem;
  }

  .below-moq-price {
    font-size: 0.7rem;
  }

  .moq-detail {
    font-size: 0.8rem;
  }

  .status-text {
    font-size: 0.75rem;
  }
}

@media (max-width: 360px) {
  .products {
    grid-template-columns: 1fr;
  }

  .skeleton-products {
    grid-template-columns: 1fr;
  }

  .product-image-wrapper {
    height: 130px;
  }

  .product-card {
    min-height: 280px;
  }
}

.skeleton-header {
  width: 100%;
  height: 350px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
  margin-bottom: 2rem;
}

@media (max-width: 1024px) {
  .skeleton-header {
    height: 300px;
  }
}

@media (max-width: 768px) {
  .skeleton-header {
    height: 250px;
  }
}

@media (max-width: 480px) {
  .skeleton-header {
    height: 200px;
  }
}
</style>
