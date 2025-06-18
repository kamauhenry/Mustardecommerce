<template>
  <MainLayout>
    <main id="payAndPickPage" aria-label="Pay & Pick Products">
      <section class="pickup-header" aria-label="Pay & Pick Information">
        <h2 class="pickup-title">Pay & Pick Up at Our Store</h2>
        <p class="pickup-info">Select items, pay online, and pick up at MustardImports Store, Nairobi CBD.</p>
      </section>
      <div v-if="store.loading.pickupCategories && !store.pickupCategories.length" class="skeleton-container">
        <div v-for="n in 2" :key="n" class="skeleton-category">
          <div class="skeleton-title"></div>
          <div class="skeleton-products">
            <div v-for="i in 4" :key="i" class="skeleton-product"></div>
          </div>
        </div>
      </div>
      <div v-else-if="store.error.pickupCategories" class="error">
        {{ store.error?.pickupCategories }}
        <button @click="retryFetch" class="retry-button">Retry</button>
      </div>
      <section class="categories-container" aria-label="Browse Pickup Categories">
        <article
          v-for="category in store.pickupCategories"
          :key="category.id"
          class="category-card"
        >
          <header class="category-top">
            <h2 class="category-title">{{ category.name }}</h2>
            <router-link
              v-if="category.products && category.products.length > 0"
              :to="`/category/${category.slug}/products?pickup=true`"
              class="see-more-link"
            >
              See More
            </router-link>
          </header>
          <div v-if="category.products && category.products.length > 0" class="products-grid">
            <article
              v-for="product in category.products.slice(0, 3)"
              :key="product.id"
              class="product-card"
            >
              <router-link
                :to="{
                  name: 'product-detail',
                  params: { categorySlug: category.slug, productSlug: product.slug },
                  query: { pickup: true }
                }"
                class="product-link"
              >
                <img
                  :src="product.thumbnail || 'https://yourdomain.com/images/default-product.jpg'"
                  :alt="product.name"
                  class="product-image"
                  loading="lazy"
                />
                <h3 class="product-name">{{ product.name }}</h3>
                <div class="product-price">
                  <span class="price-highlight">KES {{ product.price }}</span>
                </div>
                <div v-if="product.inventory" class="inventory-info">
                  <p class="availability">
                    Available: <span class="stock-count">{{ product.inventory.quantity }}</span> units
                  </p>
                  <p
                    v-if="product.inventory.quantity <= product.inventory.low_stock_threshold"
                    class="low-stock-warning"
                  >
                    Only {{ product.inventory.quantity }} left!
                  </p>
                </div>
                <div v-else class="inventory-info">
                  <p class="availability">Out of Stock</p>
                </div>
              </router-link>
            </article>
          </div>
          <div v-else class="no-products">
            No products available for pickup
          </div>
        </article>
        <div
          v-if="store.loading && store.pickupCategories.length"
          class="skeleton-container loading-skeleton"
        >
          <div v-for="n in 1" :key="'lazy-' + n" class="skeleton-category">
            <div class="skeleton"></div>
            <div class="skeleton-products">
              <div v-for="i in 4" :key="'lazy-product-' + i" class="skeleton-product"></div>
            </div>
          </div>
        </div>
        <div
          v-if="store.pickupCategoriesPagination.hasMorePages"
          ref="loadMoreSentinel"
          class="load-more-sentinel"
          aria-hidden="true"
        ></div>
        <div
          v-if="store.loading && store.pickupCategories.length"
          class="loading-more"
        >
          Loading more...
        </div>
      </section>
    </main>
  </MainLayout>
</template>

<script>
import { onMounted, ref, onUnmounted, nextTick } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useHead } from '@vueuse/head';
import { toast } from 'vue3-toastify';
import MainLayout from '@/components/navigation/MainLayout.vue';
export default {
  name: 'PayAndPick',
  setup() {
    const store = useEcommerceStore();
    const loadMoreSentinel = ref(null);
    let observer = null;
    const maxRetries = 5;

    const debounce = (func, wait) => {
      let timeout;
      return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
      };
    };

    const fetchPickupCategories = async () => {
      store.pickupCategories = [];
      store.pickupCategoriesPagination = { nextPage: 1, hasMorePages: true, totalCount: 0 };
      if (observer && loadMoreSentinel.value) {
        observer.unobserve(loadMoreSentinel.value);
        observer = null;
      }
      await store.fetchPickupCategories(1);
      if (store.pickupCategories.length && store.pickupCategoriesPagination.hasMorePages) {
        await nextTick(() => setupObserver());
      }
    };

    const retryFetch = async () => {
      console.log('Retrying fetch for page 1');
      await fetchPickupCategories();
    };

    const setupObserver = async () => {
      if (!store.pickupCategories.length || !store.pickupCategoriesPagination.hasMorePages) {
        console.log('No categories or no more pages, skipping observer setup');
        return;
      }
      await nextTick();
      let retryCount = 0;
      const trySetup = () => {
        if (loadMoreSentinel.value) {
          console.log('Setting up IntersectionObserver for sentinel');
          observer = new IntersectionObserver(
            debounce((entries) => {
              if (
                entries[0].isIntersecting &&
                store.pickupCategoriesPagination.hasMorePages &&
                !store.loading.pickupCategories
              ) {
                console.log('Fetching next page:', store.pickupCategoriesPagination.nextPage);
                store.fetchPickupCategories(store.pickupCategoriesPagination.nextPage);
              }
            }, 300),
            {
              root: null,
              rootMargin: '100px',
              threshold: 0.1,
            }
          );
          observer.observe(loadMoreSentinel.value);
        } else if (retryCount < maxRetries) {
          console.warn('loadMoreSentinel is null, retrying setup');
          retryCount++;
          setTimeout(trySetup, 500);
        } else {
          console.error('Max retries reached for setting up IntersectionObserver');
        }
      };
      trySetup();
    };

    useHead({
      title: 'MustardImports - Pay & Pick',
      meta: [
        {
          name: 'description',
          content: 'Shop products available for pickup at MustardImports Store, Nairobi CBD. Select items, pay, and collect quickly.',
        },
        {
          name: 'keywords',
          content: 'pay and pick, pickup, e-commerce, Kenya, MustardImports',
        },
        {
          property: 'og:title',
          content: 'MustardImports - Pay & Pick',
        },
        {
          property: 'og:description',
          content: 'Select and pay for products to pick up at MustardImports Store.',
        },
        {
          property: 'og:type',
          content: 'website',
        },
        {
          property: 'og:url',
          content: window.location.href,
        },
        {
          property: 'og:image',
          content: 'https://yourdomain.com/images/og-image.jpg',
        },
        {
          name: 'twitter:card',
          content: 'summary_large_image',
        },
        {
          name: 'twitter:title',
          content: 'MustardImports - Pay & Pick',
        },
        {
          name: 'twitter:description',
          content: 'Shop and pick up products with ease at MustardImports Store.',
        },
        {
          name: 'twitter:image',
          content: 'https://yourdomain.com/images/twitter-image.jpg',
        },
      ],
      link: [
        {
          rel: 'canonical',
          href: window.location.href,
        },
      ],
      script: [
        {
          type: 'application/ld+json',
          children: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'CollectionPage',
            name: 'MustardImports Pay & Pick',
            description: 'Shop products available for pickup at MustardImports Store.',
            url: window.location.href,
            publisher: {
              '@type': 'Organization',
              name: 'MustardImports',
              logo: { '@type': 'ImageObject', url: 'https://yourdomain.com/images/logo.png' },
            },
            hasPart: store.pickupCategories.slice(0, 4).map(category => ({
              '@type': 'Collection',
              name: category.name,
              url: `${window.location.origin}/category/${category.slug}/products?pickup=true`,
            })),
          }),
        },
      ],
    });

    onMounted(async () => {
      await fetchPickupCategories();
    });

    onUnmounted(() => {
      if (observer) {
        observer.disconnect();
        observer = null;
      }
    });

    return {
      store,
      loadMoreSentinel,
      retryFetch,
    };
  },
  components: {
    MainLayout,
  },
};
</script>

<style scoped>
/* Base styles */
.load-more-sentinel {
  height: 50px;
  width: 100%;
  margin-top: 20px;
  background: transparent;
}

.loading-more {
  text-align: center;
  padding: 1.5rem;
  font-size: 1rem;
  color: #D4A017;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #D4A017;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  touch-action: manipulation;
}

.retry-button:hover {
  background-color: #e67d21;
}

.categories-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 2rem;
  padding: 1.5rem 3%;
  align-items: stretch;
  justify-content: space-between;
}

.category-card {
  flex: 1 1 calc(50% - 1rem);
  max-width: calc(50% - 1rem);
  min-width: 300px;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.category-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
}

.category-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #D4A017;
  text-transform: uppercase;
  margin: 0;
  letter-spacing: 0.5px;
  position: relative;
}

.category-title::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 0;
  width: 40px;
  height: 3px;
  background-color: #D4A017;
  border-radius: 3px;
}

.see-more-link {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  background-color: #D4A017;
  padding: 8px 16px;
  border-radius: 20px;
  text-transform: uppercase;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(242, 140, 56, 0.3);
  touch-action: manipulation;
}

.see-more-link:hover {
  background-color: #D4A017;
  box-shadow: 0 4px 15px rgba(242, 140, 56, 0.4);
  transform: translateY(-2px);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.product-card {
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  height: 100%;
  min-height: 400px;
  width: auto;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.product-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  transition: all 0.3s ease;
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
  margin: 0.5rem 0;
  text-align: left;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

.product-price {
  display: flex;
  flex-direction: column;
  margin: 0.25rem 0;
}

.price-highlight {
  font-size: 0.95rem;
  font-weight: 700;
  color: #D4A017;
}

.no-products {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2.5rem;
  font-size: 0.9rem;
  border-radius: 8px;
  text-align: center;
  font-style: italic;
  height: 150px;
}

.loading,
.error {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  border-radius: 8px;
  margin: 1rem 3%;
}

.skeleton-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 2rem;
  padding: 1.5rem 3%;
  justify-content: space-between;
}

.loading-skeleton {
  margin-top: 1rem;
  width: 100%;
}

.skeleton-category {
  flex: 1 1 calc(50% - 1rem);
  max-width: calc(50% - 1rem);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.skeleton-title {
  width: 150px;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 1.5rem;
}

.skeleton-products {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.skeleton-product {
  height: 300px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 10px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Responsive adjustments */
@media (min-width: 1500px) {
  .categories-container {
    gap: 2.5rem;
  }
  .category-card {
    flex: 1 1 calc(33.333% - 1.667rem);
    max-width: calc(33.333% - 1.667rem);
  }
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
  .skeleton-category {
    flex: 1 1 calc(33.333% - 1.667rem);
    max-width: calc(33.333% - 1.667rem);
  }
  .skeleton-products {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
}

@media (min-width: 1200px) and (max-width: 1499px) {
  .category-card {
    flex: 1 1 calc(50% - 1rem);
    max-width: calc(50% - 1rem);
  }
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
  .skeleton-products {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .category-card {
    flex: 1 1 calc(50% - 1rem);
    max-width: calc(50% - 1rem);
  }
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
  .skeleton-products {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  .product-image {
    height: 140px;
  }
  .product-card {
    min-height: 280px;
  }
}

@media (min-width: 651px) and (max-width: 991px) {
  .category-card {
    flex: 1 1 calc(50% - 1rem);
    max-width: calc(50% - 1rem);
  }
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
  .skeleton-products {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

/* Mobile adjustments for <650px */
@media (max-width: 650px) {
  .categories-container {
    padding: 0 2%;
    gap: 1rem;
    flex-direction: column;
  }
  .category-card {
    flex: 1 1 100%;
    max-width: 100%;
    min-width: 0;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  .category-top {
    margin-bottom: 1rem;
  }
  .category-title {
    font-size: 1.1rem;
  }
  .see-more-link {
    font-size: 0.85rem;
    padding: 6px 12px;
  }
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  .skeleton-container {
    padding: 0.5rem 2%;
    gap: 1rem;
    flex-direction: column;
  }
  .skeleton-category {
    flex: 1 1 100%;
    max-width: 100%;
    padding: 1rem;
  }
  .skeleton-products {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  .skeleton-product {
    height: 280px;
  }
  .product-card {
    min-height: 280px;
    padding: 0.75rem;
  }
  .product-image {
    height: 140px;
  }
  .product-name {
    font-size: 0.9rem;
  }
  .product-price {
    font-size: 0.9rem;
  }
  .price-highlight {
    font-size: 0.9rem;
  }
  .retry-button {
    padding: 0.6rem 1.2rem;
    font-size: 0.9rem;
  }
  .loading-more {
    padding: 1rem;
    font-size: 0.9rem;
  }
  .load-more-sentinel {
    height: 40px;
    margin-top: 15px;
  }
}

@media (max-width: 360px) {
  .category-title {
    font-size: 1rem;
  }
  .product-card {
    min-height: 260px;
  }
  .product-image {
    height: 130px;
  }
  .product-name {
    font-size: 0.85rem;
  }
  .product-price {
    font-size: 0.85rem;
  }
  .skeleton-product {
    height: 260px;
  }
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  .skeleton-products {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

.product-link {
  text-decoration: none;
  color: inherit;
  display: block;
  cursor: pointer;
}

.product-link:hover .product-name,
.product-link:hover .price-highlight {
  color: #e67d21;
}

.low-stock-warning {
  color: #d9534f;
  font-size: 0.8rem;
  font-weight: bold;
  margin-top: 0.25rem;
}

.pickup-header {
  padding: 1.5rem 3%;
  text-align: center;
}

.pickup-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #D4A017;
  margin-bottom: 0.5rem;
}

.pickup-info {
  font-size: 1rem;
  color: #666;
  margin-bottom: 1rem;
}

.inventory-info {
  margin-top: 0.5rem;
}

.availability {
  font-size: 0.8rem;
  color: #333;
}

.stock-count {
  font-weight: 600;
  color: #D4A017;
}

@media (max-width: 650px) {
  .pickup-header {
    padding-top: 4.0rem ;

  }
  .pickup-title {
    font-size: 1.25rem;
  }
  .pickup-info {
    font-size: 0.9rem;
  }
}
</style>