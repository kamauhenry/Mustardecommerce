<template>
  <MainLayout>
  <div class="container">
    <h1 class="category-title">{{ category?.name }}</h1>

    <div v-if="store.loading.categoryProducts" class="loading">Loading products...</div>
    <div v-else-if="store.error.categoryProducts" class="error">
      Error: {{ store.error.categoryProducts }}
    </div>
    <div v-else class="products-grid">
      <div v-if="products.length > 0" class="products">
        <div v-for="product in products" :key="product.id" class="product-card">
          <img
            v-if="product.thumbnail"
            :src="product.thumbnail"
            :alt="product.name"
            class="product-image"
          />
          <h3 class="product-name">{{ product.name }}</h3>
          <p class="product-price">KES {{ product.price }}</p>
          <p class="moq-info">MOQ: {{ product.moq || 'N/A' }} items</p>
          <p class="moq-status">{{ product.moq_status || 'N/A' }}</p>
        </div>
      </div>
      <div v-else class="no-products">
        No products available
      </div>
    </div>
  </div>
</MainLayout>
</template>

<script>
import { onMounted, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '../components/navigation/MainLayout.vue';

export default {
  props: { categorySlug: String },
  components: { MainLayout },
  setup(props) {
    const store = useEcommerceStore();

    onMounted(() => {
      store.fetchCategoryProducts(props.categorySlug);
    });

    const category = computed(() => {
      return store.categoryProducts[props.categorySlug]?.category;
    });

    const products = computed(() => {
      return store.categoryProducts[props.categorySlug]?.products || [];
    });

    return {
      store,
      category,
      products,
    };
  },
};
</script>
<style scoped>
/* Container for the entire page */
.container {
  padding: 1rem;
  background-color: #f5f5f5; /* Light grey background to match the screenshot */
}

/* Category title */
.category-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333; /* Darker color for the title, as the screenshot doesn’t use orange */
  text-transform: uppercase;
  margin: 0.5rem 0 1rem 0;
}

/* Products grid container */
.products-grid {
  display: flex;
  flex-direction: column;
}

/* Products container */
.products {
  display: flex;
  flex-wrap: wrap; /* Allows wrapping to the next row */
  gap: 1rem; /* Consistent spacing between cards */
}

/* Individual product card */
.product-card {
  flex: 0 0 calc(25% - 0.75rem); /* 4 cards per row on large screens, adjusted for gap */
  max-width: calc(25% - 0.75rem); /* Ensures consistent width */
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* Subtle shadow to match screenshot */
  transition: transform 0.2s ease;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-image {
  width: 100%;
  height: 150px; /* Fixed height for consistency */
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  background-color: #e0e0e0; /* Placeholder background if no image */
}

.product-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
  margin: 0.25rem 0;
  text-align: left;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* Limit to 2 lines */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-price {
  font-size: 0.9rem;
  font-weight: 700;
  color: #333;
  margin: 0.25rem 0;
}

/* MOQ info */
.moq-info {
  font-size: 0.75rem;
  color: #666;
  margin: 0.25rem 0;
}

/* MOQ status (e.g., active, not_applicable) */
.moq-status {
  font-size: 0.75rem;
  color: #28a745; /* Green for status */
  background-color: #e6f4ea;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  margin: 0.25rem 0;
}

/* No products available message */
.no-products {
  text-align: center;
  padding: 1rem;
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
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
  .product-card {
    flex: 0 0 calc(33.33% - 0.75rem); /* 3 cards per row */
    max-width: calc(33.33% - 0.75rem);
  }
}

@media (max-width: 768px) {
  .product-card {
    flex: 0 0 calc(50% - 0.75rem); /* 2 cards per row */
    max-width: calc(50% - 0.75rem);
  }

  .product-image {
    height: 120px; /* Smaller image height on mobile */
  }

  .product-name {
    font-size: 0.85rem;
  }

  .product-price {
    font-size: 0.8rem;
  }

  .moq-info,
  .moq-status {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .product-card {
    flex: 0 0 calc(100% - 0.75rem); /* 1 card per row */
    max-width: calc(100% - 0.75rem);
  }

  .product-image {
    height: 100px; /* Even smaller image height */
  }
}
</style>
