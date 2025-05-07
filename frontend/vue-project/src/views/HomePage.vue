<template>
  <MainLayout>
    <section class="top-row-home" aria-label="Featured Content">
      <RecentCampaigns v-if="!isMobile" />
      <HomeCarousel />
      <RecentSearches v-if="!isMobile" />
    </section>
    <main id="homePage" aria-label="Product Categories">
      <!-- Initial loading skeleton -->
      <div v-if="store.loading.allhomeCategoriesWithProducts && !store.allhomeCategoriesWithProducts.length" class="skeleton-container">
        <div v-for="n in 2" :key="n" class="skeleton-category">
          <div class="skeleton-title"></div>
          <div class="skeleton-products">
            <div v-for="i in 4" :key="i" class="skeleton-product"></div>
          </div>
        </div>
      </div>
      <!-- Error state -->
      <div v-else-if="store.error.allhomeCategoriesWithProducts" class="error">
        {{ store.error.allhomeCategoriesWithProducts }}
        <button @click="retryFetch" class="retry-button">Retry</button>
      </div>
      <!-- Categories and lazy loading -->
      <section v-else class="categories-container" aria-label="Browse Categories">
        <article
          v-for="category in store.allhomeCategoriesWithProducts"
          :key="category.id"
          class="category-card"
        >
          <header class="category-top">
            <h2 class="category-title">{{ category.name }}</h2>
            <router-link
              v-if="category.products && category.products.length > 0"
              :to="`/category/${category.slug}/products`"
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
                  params: { categorySlug: category.slug, productSlug: product.slug }
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
                  <span v-if="product.below_moq_price" class="below-moq-price">
                    Below MOQ Price: KES {{ product.below_moq_price }}
                  </span>
                  <span v-else class="below-moq-price">Below MOQ Price: NA</span>
                </div>
                <p class="moq-info">MOQ: {{ product.moq }} items</p>
                <div v-if="product.moq_progress" class="moq-progress-container">
                  <div
                    class="moq-progress-bar"
                    :style="{ width: Math.min(100, product.moq_progress.percentage) + '%' }"
                  ></div>
                  <span class="moq-progress-text">
                    {{ product.moq_progress.percentage }}%
                  </span>
                </div>
                <div v-else class="moq-progress-container">
                  <div
                    class="moq-progress-bar"
                    :style="{ width: 0 + '%' }"
                  ></div>
                  <span class="moq-progress-text">
                    0%
                  </span>
                </div>
              </router-link>
            </article>
          </div>
          <div v-else class="no-products">
            No products available
          </div>
        </article>
        <!-- Lazy loading skeleton -->
        <div
          v-if="store.loading.allhomeCategoriesWithProducts && store.allhomeCategoriesWithProducts.length"
          class="skeleton-container lazy-loading-skeleton"
        >
          <div v-for="n in 1" :key="'lazy-' + n" class="skeleton-category">
            <div class="skeleton-title"></div>
            <div class="skeleton-products">
              <div v-for="i in 4" :key="'lazy-product-' + i" class="skeleton-product"></div>
            </div>
          </div>
        </div>
        <!-- Sentinel for lazy loading -->
        <div
          v-if="store.homeCategoriesPagination.hasMore"
          ref="loadMoreSentinel"
          class="load-more-sentinel"
          aria-hidden="true"
        ></div>
        <!-- Loading more text (optional, kept for clarity) -->
        <div
          v-if="store.loading.allhomeCategoriesWithProducts && store.allhomeCategoriesWithProducts.length"
          class="loading-more"
        >
          Loading more categories...
        </div>
      </section>
    </main>
  </MainLayout>
</template>

<script>
import { onMounted, ref, onUnmounted, nextTick } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useHead } from '@vueuse/head';
import { computed } from 'vue';
import MainLayout from '@/components/navigation/MainLayout.vue';
import RecentCampaigns from '@/components/home/recents/RecentCampaigns.vue';
import RecentSearches from '@/components/home/recents/RecentSearches.vue';
import HomeCarousel from '@/components/home/recents/HomeCarousel.vue';

export default {
  setup() {
    const store = useEcommerceStore();
    const loadMoreSentinel = ref(null);
    const isMobile = ref(window.innerWidth <= 650);
    let observer = null;
    const maxRetries = 5;
    let retryCount = 0;

    const initialCategories = computed(() => store.allhomeCategoriesWithProducts.slice(0, 4));
    useHead({
      title: 'MustardImports - Buy Quality Products Online',
      meta: [
        {
          name: 'description',
          content: 'Shop a wide range of quality products at MustardImports. Discover top categories, exclusive deals, and fast delivery across Kenya.',
        },
        {
          name: 'keywords',
          content: 'e-commerce, online shopping, Kenya, electronics, home appliances, clothing, footwear',
        },
        {
          property: 'og:title',
          content: 'MustardImports - Buy Quality Products Online',
        },
        {
          property: 'og:description',
          content: 'Explore top categories and exclusive deals at MustardImports. Shop now for fast delivery across Kenya!',
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
          content: 'MustardImports - Buy Quality Products Online',
        },
        {
          name: 'twitter:description',
          content: 'Shop quality products with fast delivery at MustardImports. Explore now!',
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
          innerHTML: computed(() => JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'CollectionPage',
            name: 'MustardImports Home',
            description: 'Shop a wide range of quality products at MustardImports.',
            url: window.location.href,
            publisher: {
              '@type': 'Organization',
              name: 'MustardImports',
              logo: { '@type': 'ImageObject', url: 'https://yourdomain.com/images/logo.png' },
            },
            hasPart: initialCategories.value.map(category => ({
              '@type': 'Collection',
              name: category.name,
              url: `${window.location.origin}/category/${category.slug}/products`,
            })),
          })),
        },
      ],
    });

    const debounce = (func, wait) => {
      let timeout;
      return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
      };
    };

    const retryFetch = () => {
      console.log('Retrying fetch for page 1');
      store.allhomeCategoriesWithProducts = [];
      store.homeCategoriesPagination = { nextPage: 1, hasMore: true, totalCount: 0 };
      store.fetchHomeCategories(1).then(() => {
        if (store.homeCategoriesPagination.hasMore) {
          nextTick(() => setupObserver());
        }
      });
    };

    const setupObserver = async () => {
      await nextTick();
      retryCount = 0;
      const trySetup = () => {
        if (loadMoreSentinel.value) {
          console.log('Setting up IntersectionObserver for sentinel');
          observer = new IntersectionObserver(
            debounce((entries) => {
              if (
                entries[0].isIntersecting &&
                store.homeCategoriesPagination.hasMore &&
                !store.loading.allhomeCategoriesWithProducts
              ) {
                console.log('Fetching next page:', store.homeCategoriesPagination.nextPage);
                store.fetchHomeCategories(store.homeCategoriesPagination.nextPage);
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

    onMounted(() => {
      store.allhomeCategoriesWithProducts = [];
      store.homeCategoriesPagination = { nextPage: 1, hasMore: true, totalCount: 0 };
      store.fetchHomeCategories(1).then(() => {
        if (store.homeCategoriesPagination.hasMore) {
          nextTick(() => setupObserver());
        }
      });
      window.addEventListener('resize', updateScreenSize);
    });

    onUnmounted(() => {
      if (observer && loadMoreSentinel.value) {
        console.log('Cleaning up IntersectionObserver');
        observer.unobserve(loadMoreSentinel.value);
        observer = null;
      }
      window.removeEventListener('resize', updateScreenSize);
    });

    const updateScreenSize = () => {
      isMobile.value = window.innerWidth <= 650;
    };

    return { store, loadMoreSentinel, retryFetch, isMobile };
  },
  components: {
    MainLayout,
    RecentCampaigns,
    RecentSearches,
    HomeCarousel,
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

.below-moq-price {
  font-size: 0.75rem;
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

.lazy-loading-skeleton {
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
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.skeleton-product {
  height: 300px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 10px;
}

/* In HomePage.vue or a shared stylesheet */
.top-row-home {
  display: flex;
  flex-direction: row;
  gap: 1rem;
  margin: 1rem 2%;
  align-items: stretch;
  max-width: 100%;
  box-sizing: border-box;
  flex-wrap: nowrap;
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
  .top-row-home {
    flex-direction: column;
    gap: 0.5rem;
    margin: 0.5rem 2%;
    margin-bottom: 0.5rem; /* Reduced to minimize gap */
  }
  .categories-container {
    padding: 0.5rem 2%; /* Reduced padding-top */
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
  .below-moq-price {
    font-size: 0.7rem;
  }
  .moq-info {
    font-size: 0.75rem;
    padding: 2px 6px;
  }
  .moq-progress-container {
    height: 16px;
  }
  .moq-progress-text {
    font-size: 0.6rem;
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
  .moq-info {
    font-size: 0.7rem;
  }
  .skeleton-product {
    height: 260px;
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
</style>