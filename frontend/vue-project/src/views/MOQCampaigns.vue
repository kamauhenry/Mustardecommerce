<template>
  <MainLayout>
    <div class="all-products">
      <h1 class="page-title">MOQ Campaigns</h1>
      <!-- SEO Meta Tags (handled in MainLayout or globally, but noted here for context) -->
      
      <!-- Filters row -->
      <div class="filters-row flex flex-wrap gap-2 mb-6">
        <div class="filter-group flex items-center">
          <label for="category-filter" class="filter-p">Filter:</label>
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
          <label for="sort-filter" class="filter-p">Sort:</label>
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

      <!-- Skeleton Loader with Shimmer -->
      <div v-if="store.loading.allCategoriesWithProducts" class="products-container">
        <div class="products-grid">
          <div v-for="n in 8" :key="'skeleton-' + n" class="product-card skeleton">
            <div class="product-image skeleton-shimmer"></div>
            <div class="product-info">
              <div class="skeleton-text skeleton-shimmer short"></div>
              <div class="skeleton-text skeleton-shimmer medium"></div>
              <div class="skeleton-text skeleton-shimmer short"></div>
              <div class="skeleton-text skeleton-shimmer long"></div>
            </div>
          </div>
        </div>
      </div>

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
                <img
                  :src="product.thumbnail || 'data:image/jpeg;base64,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'"
                  :alt="`${product.name} - MOQ Campaign Product Image`"
                  loading="lazy"
                >
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
                    <div class="progress-bar" :style="{ width: `${product.moq_progress?.percentage || '60'}%` }"></div>
                    <span class="progress-text">{{ product.moq_progress?.percentage || '60' }}% Orders</span>
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>

        <!-- No Products -->
        <div v-else class="no-products">
          No products available for the selected filters.
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted } from 'vue';
import MainLayout from '@/components/navigation/MainLayout.vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useHead } from '@vueuse/head'; // For managing SEO meta tags

export default {
  name: 'AllProducts',
  components: {
    MainLayout,
  },
  setup() {
    const store = useEcommerceStore();

    // SEO Meta Tags
    useHead({
      title: 'MOQ Campaigns - Explore Products with Minimum Order Quantities',
      meta: [
        {
          name: 'description',
          content: 'Discover products with Minimum Order Quantity (MOQ) campaigns. Filter by category, sort by price or status, and join active campaigns to get the best deals.',
        },
        {
          name: 'keywords',
          content: 'MOQ campaigns, minimum order quantity, bulk buying, ecommerce deals, product categories',
        },
        {
          name: 'robots',
          content: 'index, follow',
        },
        {
          name: 'og:title',
          content: 'MOQ Campaigns - Explore Products with Minimum Order Quantities',
        },
        {
          name: 'og:description',
          content: 'Discover products with Minimum Order Quantity (MOQ) campaigns. Filter by category, sort by price or status, and join active campaigns to get the best deals.',
        },
        {
          name: 'og:type',
          content: 'website',
        },
        {
          name: 'og:url',
          content: window.location.href,
        },
        {
          name: 'og:image',
          content: 'https://yourwebsite.com/path-to-default-image.jpg', // Replace with your default image URL
        },
        {
          name: 'twitter:card',
          content: 'summary_large_image',
        },
        {
          name: 'twitter:title',
          content: 'MOQ Campaigns - Explore Products with Minimum Order Quantities',
        },
        {
          name: 'twitter:description',
          content: 'Discover products with Minimum Order Quantity (MOQ) campaigns. Filter by category, sort by price or status, and join active campaigns to get the best deals.',
        },
        {
          name: 'twitter:image',
          content: 'https://yourwebsite.com/path-to-default-image.jpg', // Replace with your default image URL
        },
      ],
      script: [
        {
          type: 'application/ld+json',
          innerHTML: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "MOQ Campaigns",
            "description": "Discover products with Minimum Order Quantity (MOQ) campaigns. Filter by category, sort by price or status, and join active campaigns to get the best deals.",
            "url": window.location.href,
            "mainEntity": {
              "@type": "ItemList",
              "itemListElement": store.allCategoriesWithProducts.flatMap(category =>
                category.products?.map((product, index) => ({
                  "@type": "ListItem",
                  "position": index + 1,
                  "item": {
                    "@type": "Product",
                    "name": product.name,
                    "image": product.thumbnail || 'https://yourwebsite.com/path-to-default-image.jpg',
                    "url": `${window.location.origin}/product/${category.slug || 'uncategorized'}/${product.slug}`,
                    "offers": {
                      "@type": "Offer",
                      "price": product.price,
                      "priceCurrency": "KES",
                      "availability": product.moq_status === 'Active' ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
                    },
                  },
                })) || []
              ),
            },
          }),
        },
      ],
    });

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
  margin: 0 auto;
  max-width: 1200px;
  font-family: 'Roboto', sans-serif;
  padding: 1rem;
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

.filter-p {
  font-weight: 500;
  margin-right: 1rem;
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
.no-products {
  text-align: center;
  padding: 20px;
}

/* Skeleton Loader */
.skeleton {
  background-color: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.skeleton-shimmer {
  position: relative;
  overflow: hidden;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton .product-image {
  height: 120px;
  width: 100%;
}

.skeleton .product-info {
  padding: 8px;
}

.skeleton-text {
  height: 12px;
  margin: 4px 0;
  border-radius: 4px;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-text.medium {
  width: 80%;
}

.skeleton-text.long {
  width: 100%;
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
  line-clamp: 2;
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
  padding: 2px;
  background: linear-gradient(45deg, #62c87a, #6dc480);
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