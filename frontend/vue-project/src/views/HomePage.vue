<template>
  <MainLayout>
    <div class="top-row-home">
      <RecentCampaigns />
      <HomeCarousel />
      <RecentSearches />
    </div>
    <div id="homePage">
      <div v-if="store.loading.allCategoriesWithProducts" class="loading">Loading...</div>
      <div v-else-if="store.error.allCategoriesWithProducts" class="error">
        {{ store.error.allCategoriesWithProducts }}
      </div>
      <div v-else class="categories-container">
        <div
          v-for="category in store.allCategoriesWithProducts"
          :key="category.id"
          class="category-card"
        >
          <h2 class="category-title">{{ category.name }}</h2>
          <div v-if="category.products && category.products.length > 0" class="products-grid">
            <router-link
              v-for="product in category.products.slice(0, 4)"
              :key="product.id"
              :to="`/products/${category.slug}/${product.slug}`"
              class="product-card"
              @click="trackProductClick(product, category.slug)"
            >
              <img :src="product.thumbnail || placeholder" alt="" class="product-image" />
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-price">KES {{ product.price }}</p>
              <p class="moq-info">MOQ: {{ product.moq }} items</p>
              <p class="moq-status">{{ product.moq_status }}</p>
            </router-link>
          </div>
          <div v-else class="no-products">
            No products available
          </div>
          <router-link
            v-if="category.products && category.products.length > 0"
            :to="`/category/${category.slug}/products`"
            class="see-more-link"
          >
            See More
          </router-link>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';
import RecentCampaigns from '@/components/home/recents/RecentCampaigns.vue';
import RecentSearches from '@/components/home/recents/RecentSearches.vue';
import HomeCarousel from '@/components/home/recents/HomeCarousel.vue';
import { trackProduct } from '@/utils/tracking';
import placeholder from '@/assets/images/grey.jpg';

export default {
  setup() {
    const store = useEcommerceStore();

    onMounted(() => {
      if (!store.allCategoriesWithProducts.length) store.fetchAllCategoriesWithProducts();
    });

    // Track product click
    const trackProductClick = (product, categorySlug) => {
      trackProduct(product, categorySlug);
    };

    return { store, trackProductClick };
  },
  components: {
    MainLayout,
    RecentCampaigns,
    RecentSearches,
    HomeCarousel,
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

/* Container for all categories */
.categories-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
}

/* Individual category card */
.category-card {
  flex: 1;
  min-width: 300px;
  max-width: 48%;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Category header (title and "See More" link container) */
.category-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  min-width: 100%;
}

/* Category title */
.category-title {
  font-size: .8rem;
  font-weight: 700;
  color: #f28c38;
  text-transform: uppercase;
  margin: 0.5rem 0;
}

/* Products grid inside each category */
.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

/* Individual product card */
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

/* Placeholder image styling */
.product-image {
  width: 100%;
  height: 120px;
  background-color: #e0e0e0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  object-fit: cover;
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
  font-size: 0.8rem;
  font-weight: 700;
  margin: 0.25rem 0;
}

/* Remove the pseudo-element since the price already includes "KES" in the template */
.product-price::before {
  content: none;
}

/* MOQ info */
.moq-info {
  font-size: 0.7rem;
  margin: 0.25rem 0;
}

/* MOQ status (e.g., "Active: X items") */
.moq-status {
  font-size: 0.7rem;
  color: #28a745;
  background-color: #e6f4ea;
  padding: 0.2rem 0.4rem;
  border-radius: 12px;
  margin: 0.25rem 0;
}

/* "See More" link styling */
.see-more-link {
  display: block;
  text-align: right;
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  text-decoration: none;
  margin-top: 0.5rem;
}

.see-more-link:hover {
  color: #f28c38;
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

  .category-card {
    max-width: 100%;
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

  .category-card {
    max-width: 100%;
    min-width: 100%;
  }

  .category-title {
    font-size: 1.1rem;
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

  .category-card {
    padding: 0.75rem;
  }

  .product-image {
    height: 80px;
  }
}
</style>
