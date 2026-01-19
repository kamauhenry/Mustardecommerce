<template>
  <MainLayout>
    <div class="all-products">
      <h1 class="page-title">MOQ Campaigns</h1>

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
              <div class="product-image-wrapper">
                <img
                  :src="product.images.length > 0 ? product.images[0].image : ''"
                  :alt="`${product.name} - MOQ Campaign Product Image`"
                  class="product-image"
                  loading="lazy"
                />
              </div>
              <h3 class="product-name">{{ product.name }}</h3>
              <div class="product-price">
                <span class="price-highlight">KES {{ product.price }}</span>
                <span class="below-moq-price">
                  Below MOQ Price: {{ product.below_moq_price ? `KES ${product.below_moq_price}` : 'NA' }}
                </span>
              </div>
              <div class="moq-info-container">
                <p class="moq-info">MOQ: {{ product.moq || 1 }} items</p>
                <div class="moq-progress-container">
                  <div
                    class="moq-progress-bar"
                    :style="{ width: Math.min(100, product.moq_progress?.percentage) + '%' }"
                  ></div>
                  <span class="moq-progress-text">
                    {{ product.moq_progress?.percentage }}%
                  </span>
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
import { onMounted, computed } from 'vue';
import MainLayout from '@/components/navigation/MainLayout.vue';
import { useProductsStore } from '@/stores/modules/products';
import { useHead } from '@vueuse/head';

export default {
  name: 'MOQCampaigns',
  components: {
    MainLayout,
  },
  setup() {
    const store = useProductsStore();

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
          content: 'https://yourwebsite.com/path-to-default-image.jpg',
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
          content: 'https://yourwebsite.com/path-to-default-image.jpg',
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
                category.products?.filter(product => product.moq_status !== 'not_applicable').map((product, index) => ({
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
                      "availability": product.moq_status === 'active' ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
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
      this.store.allCategoriesWithProducts.forEach(category => {
        if (category.products && category.products.length > 0) {
          const productsWithCategory = category.products
            .filter(product => product.moq_status !== 'not_applicable') // Filter out products with moq_status 'not_applicable'
            .map(product => ({
              ...product,
              category_slug: category.slug,
            }));
          products = [...products, ...productsWithCategory];
        }
      });

      if (this.selectedCategorySlug) {
        products = products.filter(product => product.category_slug === this.selectedCategorySlug);
      }

      return products;
    },
  },
  methods: {
    sortedProducts(products) {
      const sorted = [...products];
      switch (this.sortOption) {
        case 'price_asc':
          return sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
        case 'price_desc':
          return sorted.sort((a, b) => (b.price || 0) - (b.price || 0));
        case 'moq_status_active':
          return sorted.sort((a, b) => {
            const statusA = (a.moq_status || 'active').toLowerCase();
            const statusB = (b.moq_status || 'active').toLowerCase();
            if (statusA === 'active' && statusB !== 'active') return -1;
            if (statusA !== 'active' && statusB === 'active') return 1;
            return 0;
          });
        case 'default':
        default:
          return sorted;
      }
    },
    onFilterChange() {
      // Client-side filtering and sorting
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
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  height: 100%;
}

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
  .all-products {
    padding-top: 3.8rem;
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
  .product-image-wrapper {
    height: 160px;
  }
}
</style>