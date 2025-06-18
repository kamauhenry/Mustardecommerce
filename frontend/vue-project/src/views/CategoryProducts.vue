<template>
  <MainLayout v-if="isStoreReady">
    <div class="container">
      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> /
        <router-link :to="`/category/${categorySlug}/products`">{{
          categoryName || categorySlug || 'Category'
        }}</router-link>
      </div>

      <!-- Category Header -->
      <div v-if="isLoading" class="skeleton-header"></div>
      <div v-else class="category-header" :style="{ backgroundImage: `url(${categoryImage || 'https://via.placeholder.com/1200x400?text=Category+Image'})` }">
        <div class="category-header-content">
          <h1 class="category-title">{{ categoryName || 'Category' }}</h1>
          <p class="category-description">{{ categoryDescription || 'No description available.' }}</p>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters">
        <div class="filter-group search-group">
          <label for="search-filter">Search Products:</label>
          <div class="search-input-wrapper">
            <input
              id="search-filter"
              v-model="searchQuery"
              type="text"
              placeholder="Search by product name..."
              class="search-input"
              @input="applyFilters"
            />
            <span class="search-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
              </svg>
            </span>
          </div>
        </div>
        <div class="filter-group">
          <label for="item-type-filter">Filter by Type:</label>
          <select id="item-type-filter" v-model="selectedFilter" @change="applyFilters" class="filter-select">
            <option value="all">All Items</option>
            <option value="pay-and-pick">Pay & Pick</option>
            <option value="moq">MOQ Items</option>
          </select>
        </div>
        <div class="filter-group price-filter">
          <label>Price Range: KES {{ priceRange[0] }} - KES {{ priceRange[1] }}</label>
          <div class="slider-container">
            <div class="price-inputs">
              <input
                type="number"
                v-model.number="priceRange[0]"
                :min="minPrice"
                :max="maxPrice"
                :step="100"
                @input="applyFilters"
                class="price-input"
              />
              <span>-</span>
              <input
                type="number"
                v-model.number="priceRange[1]"
                :min="minPrice"
                :max="maxPrice"
                :step="100"
                @input="applyFilters"
                class="price-input"
              />
            </div>
            <div class="range-slider">
              <input
                type="range"
                v-model.number="priceRange[0]"
                :min="minPrice"
                :max="maxPrice"
                :step="100"
                @input="applyFilters"
                class="price-slider"
              />
              <input
                type="range"
                v-model.number="priceRange[1]"
                :min="minPrice"
                :max="maxPrice"
                :step="100"
                @input="applyFilters"
                class="price-slider"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Loading state with skeleton -->
      <div v-if="isLoading && !filteredProducts.length" class="skeleton-container">
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
        <div v-if="filteredProducts.length > 0" class="products">
          <div v-for="product in filteredProducts" :key="product.id" class="product-card">
            <router-link
              :to="{
                name: 'product-detail',
                params: { categorySlug: categorySlug, productSlug: product.slug },
                query: { pickup: product.is_pick_and_pay }
              }"
              class="product-link"
            >
              <div class="product-image-wrapper">
                <img
                  :src="product.thumbnail || 'https://yourdomain.com/images/default-product.jpg'"
                  :alt="product.name"
                  class="product-image"
                  loading="lazy"
                />
              </div>
              <h3 class="product-name">{{ product.name }}</h3>
              <div class="product-price">
                <span class="price-highlight">KES {{ product.price }}</span>
                <span v-if="product.moq_status === 'active'" class="below-moq-price">
                  Below MOQ Price: {{ product.below_moq_price ? `KES ${product.below_moq_price}` : 'NA' }}
                </span>
              </div>
              <div v-if="product.moq_status === 'active'" class="moq-info-container">
                <p class="moq-info">MOQ: {{ product.moq || 'N/A' }} items</p>
                <div class="moq-progress-container">
                  <div
                    class="moq-progress-bar"
                    :style="{ width: Math.min(100, product.moq_progress?.percentage || 0) + '%' }"
                  ></div>
                  <span class="moq-progress-text">
                    {{ product.moq_progress?.percentage || 0 }}%
                  </span>
                </div>
              </div>
              <div v-if="product.is_pick_and_pay" class="inventory-info">
                <p class="availability">
                  Available: <span class="stock-count">{{ product.inventory?.quantity || 0 }}</span> units
                </p>
                <p
                  v-if="product.inventory?.quantity && product.inventory?.quantity <= product.inventory?.low_stock_threshold"
                  class="low-stock-warning"
                >
                  Only {{ product.inventory.quantity }} left!
                </p>
              </div>
              <div v-else-if="!product.moq_status || product.moq_status === 'not_applicable'" class="inventory-info">
                <p class="availability">Out of Stock</p>
              </div>
            </router-link>
          </div>
        </div>
        <div v-else class="no-products">
          <p>No products match your filters.</p>
          <button @click="resetFilters" class="cta-button">Reset Filters</button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted, computed, watch, onUnmounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useHead } from '@vueuse/head';
import MainLayout from '@/components/navigation/MainLayout.vue';

export default {
  name: 'CategoryProducts',
  components: { MainLayout },
  setup() {
    const route = useRoute();
    const store = useEcommerceStore();
    const selectedFilter = ref('all');
    const minPrice = 1000;
    const maxPrice = 34000;
    const priceRange = ref([minPrice, maxPrice]);
    const isStoreReady = ref(false);
    const searchQuery = ref('');

    // Category slug
    const categorySlug = computed(() => route.params.categorySlug || '');

    // Loading state
    const isLoading = computed(() => store.loading?.categoryProducts ?? false);

    // Initialize store
    onMounted(() => {
      if (!store.apiInstance) store.initializeApiInstance();
      if (!store.loading) {
        store.$patch({ loading: { categoryProducts: false } });
      }
      isStoreReady.value = true; // Mark store as ready after initialization
      if (categorySlug.value) {
        console.log('Store loading state:', store.loading); // Debug
        store.fetchCategoryProducts(categorySlug.value);
      }
    });

    watch(categorySlug, (newSlug) => {
      if (newSlug) store.fetchCategoryProducts(newSlug);
    });

    onUnmounted(() => {
      if (categorySlug.value) store.error.categoryProducts[categorySlug.value] = null;
    });

    // Category details
    const categoryName = computed(() => store.categoryProducts[categorySlug.value]?.category?.name || '');
    const categoryDescription = computed(() => store.categoryProducts[categorySlug.value]?.category?.description || '');
    const categoryImage = computed(() => store.categoryProducts[categorySlug.value]?.category?.image || '');

    // Products
    const products = computed(() => store.categoryProducts[categorySlug.value]?.products || []);

    // Filtered products
    const filteredProducts = computed(() => {
      return products.value.filter(product => {
        const price = parseFloat(product.price);
        const inPriceRange = price >= priceRange.value[0] && price <= priceRange.value[1];
        if (!inPriceRange) return false;

        // Search filter
        const matchesSearch = !searchQuery.value || 
          product.name.toLowerCase().includes(searchQuery.value.toLowerCase());
        if (!matchesSearch) return false;

        switch (selectedFilter.value) {
          case 'pay-and-pick':
            return product.is_pick_and_pay;
          case 'moq':
            return product.moq_status === 'active';
          default:
            return true;
        }
      });
    });

    // Error
    const categoryError = computed(() => store.error.categoryProducts[categorySlug.value] || null);

    // Retry loading
    const retryLoading = () => {
      if (categorySlug.value) store.fetchCategoryProducts(categorySlug.value);
    };

    // Apply filters
    const applyFilters = () => {
      if (priceRange.value[0] > priceRange.value[1]) {
        priceRange.value = [priceRange.value[1], priceRange.value[0]];
      }
    };

    // Reset filters
    const resetFilters = () => {
      selectedFilter.value = 'all';
      priceRange.value = [minPrice, maxPrice];
      searchQuery.value = '';
    };

    // SEO
    const schemaOrg = computed(() => ({
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: `MustardImports ${categoryName.value}`,
      description: categoryDescription.value || 'Browse Bateman products in this category.',
      url: window.location.href,
      publisher: {
        '@type': 'Organization',
        name: 'MustardImports',
        logo: { '@type': 'ImageObject', url: 'https://yourdomain.com/images/logo.png' },
      },
    }));

    useHead({
      title: computed(() => `MustardImports - ${categoryName.value || 'Category'}`),
      meta: [
        { name: 'description', content: categoryDescription.value || 'Browse products in this category at MustardImports.' },
        { name: 'keywords', content: `e-commerce, Kenya, MustardImports, ${categoryName.value}` },
        { property: 'og:title', content: computed(() => `MustardImports - ${categoryName.value}`) },
        { property: 'og:description', content: categoryDescription.value || 'Browse products in this category.' },
        { property: 'og:type', content: 'website' },
        { property: 'og:url', content: window.location.href },
        { property: 'og:image', content: 'https://example.com/images/og-image.jpg' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: computed(() => `MustardImports - ${categoryName.value}`) },
        { name: 'twitter:description', content: categoryDescription.value || 'Browse products in this category.' },
        { name: 'twitter:image', content: 'https://example.com/images/twitter-image.jpg' },
      ],
      link: [{ rel: 'canonical', href: window.location.href }],
      script: [
        {
          type: 'application/ld+json',
          children: JSON.stringify(schemaOrg.value),
        },
      ],
    });

    return {
      store,
      categorySlug,
      categoryName,
      categoryDescription,
      categoryImage,
      filteredProducts,
      categoryError,
      retryLoading,
      selectedFilter,
      priceRange,
      minPrice,
      maxPrice,
      applyFilters,
      resetFilters,
      isStoreReady,
      isLoading,
      searchQuery,
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

/* Filters */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e8e8e8;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 220px;
  flex: 1;
}

.filter-group label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #2d2d2d;
  margin-bottom: 0.25rem;
}

/* Search Input */
.search-group {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  padding: 0.75rem 2.5rem 0.75rem 0.75rem;
  font-size: 0.95rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background-color: #fff;
  width: 100%;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #D4A017;
  box-shadow: 0 0 0 3px rgba(212, 160, 23, 0.1);
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
  pointer-events: none;
}

.search-icon svg {
  width: 18px;
  height: 18px;
}

/* Select Dropdown */
.filter-select {
  padding: 0.75rem;
  font-size: 0.95rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background-color: #fff;
  cursor: pointer;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  appearance: none;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="%236b7280" viewBox="0 0 16 16"><path d="M8 12l-6-6h12l-6 6z"/></svg>');
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 12px;
}

.filter-select:focus {
  outline: none;
  border-color: #D4A017;
  box-shadow: 0 0 0 3px rgba(212, 160, 23, 0.1);
}

/* Price Filter */
.price-filter {
  flex: 1;
  min-width: 250px;
}

.slider-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.price-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.price-input {
  width: 100px;
  padding: 0.5rem;
  font-size: 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  text-align: center;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.price-input:focus {
  outline: none;
  border-color: #D4A017;
  box-shadow: 0 0 0 3px rgba(212, 160, 23, 0.1);
}

.range-slider {
  position: relative;
  width: 100%;
}

.price-slider {
  width: 100%;
  -webkit-appearance: none;
  appearance: none;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  outline: none;
  cursor: pointer;
  position: relative;
  z-index: 1;
}

.price-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: #D4A017;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: background 0.3s ease, transform 0.3s ease;
}

.price-slider::-webkit-slider-thumb:hover {
  background: #e67d21;
  transform: scale(1.1);
}

.price-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: #D4A017;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: background 0.3s ease, transform 0.3s ease;
}

.price-slider::-moz-range-thumb:hover {
  background: #e67d21;
  transform: scale(1.1);
}

.price-slider::-webkit-slider-runnable-track {
  background: #e5e7eb;
  height: 8px;
  border-radius: 4px;
}

.price-slider::-moz-range-track {
  background: #e5e7eb;
  height: 8px;
  border-radius: 4px;
}

/* Product card */
.product-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 250px;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.product-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  height: 100%;

}

.product-image {
  width: 100%;
  height: 160px;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image {
  transform: scale(1.03);
}

.product-name {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0.1rem 0;
  text-align: left;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 1rem;
}

.product-price {
  display: flex;
  flex-direction: column;
  margin: 0.1rem 0;
  padding: 0 1rem;
}

.price-highlight {
  font-size: 0.95rem;
  font-weight: 700;
  color: #D4A017;
}

.below-moq-price {
  font-size: 0.75rem;
  margin-top: 0.1rem;
}

.moq-info-container {
  padding: 0 1rem;
}

.moq-info {
  font-size: 0.8rem;
  margin: 0.5rem 0;
  padding: 3px 8px;
  border-radius: 4px;
  display: inline-block;
}

.moq-progress-container {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: #e6f4ea;
  border-radius: 20px;
  overflow: hidden;
  margin-top: auto;
}

.moq-progress-bar {
  height: 100%;
  padding: 2px;
  background: linear-gradient(45deg, #62c87a, #6dc480);
  transition: width 0.5s ease;
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
  color: #333;
  font-size: 0.65rem;
  font-weight: bold;
  text-shadow: 0 0 2px #fff;
}

.inventory-info {
  margin-top: 0.5rem;
  padding: 0 1rem;
}

.availability {
  font-size: 0.8rem;
  color: #333;
}

.stock-count {
  font-weight: 600;
  color: #D4A017;
}

.low-stock-warning {
  color: #d9534f;
  font-size: 0.8rem;
  font-weight: bold;
  margin-top: 0.25rem;
}

/* No products */
.no-products {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  border-radius: 8px;
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.cta-button {
  padding: 0.5rem 1rem;
  background-color: #D4A017;
  color: #fff;
  text-decoration: none;
  border-radius: 20px;
  font-weight: 500;
  transition: background-color 0.3s ease;
  border: none;
  cursor: pointer;
}

.cta-button:hover {
  background-color: #e67d21;
}

/* Breadcrumb styling */
.breadcrumb {
  font-size: 0.9rem;
  margin-bottom: 1rem;

  color: #666;
}

.breadcrumb a {
  color: #D4A017;
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
  margin-bottom: 0.25rem;
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
  height: 400px;
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
  gap: 0.5rem 1.0rem; /* Row gap reduced to 0.5rem (8px), column gap remains 1.5rem */
}

/* Individual product card */
.product-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 250px;
  display: flex;
  flex-direction: column;
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

/* Shimmer animation for skeleton */
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Error state */
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  border-radius: 8px;
  margin: 1rem 0;
  color: #dc3545;
}

.retry-button {
  background: none;
  border: none;
  color: #D4A017;
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

  .skeleton-header {
    height: 300px;
  }
}

@media (max-width: 768px) {
  .breadcrumb {
    padding-top: 3.1rem;
  }
  .filters {
    flex-direction: column;
    padding: 1rem;
  }

  .filter-group {
    min-width: 100%;
  }

  .price-input {
    width: 80px;
  }

  .products {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.333rem 1rem;
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
    min-height: 250px;
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

  .moq-info {
    font-size: 0.75rem;
  }

  .moq-progress-container {
    height: 16px;
  }

  .moq-progress-text {
    font-size: 0.6rem;
  }

  .skeleton-header {
    height: 250px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 1rem 2%;
  }

  .products {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 0.333rem 1rem; /* Row gap reduced to 0.333rem (5.3px), column gap remains 1rem */
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
    min-height: 250px;
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

  .moq-info {
    font-size: 0.75rem;
  }

  .skeleton-header {
    height: 200px;
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
    min-height: 250px;
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
</style>