<template>
  <MainLayout>
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
            <div
              v-for="product in category.products.slice(0, 4)"
              :key="product.id"
              class="product-card"
            >
              <img :src="product.thumbnail || 'placeholder.jpg'" alt="" class="product-image" />
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-price">KES {{ product.price }}</p>
              <p class="moq-info">MOQ: {{ product.moq }} items</p>
              <p class="moq-status">{{ product.moq_status }}</p>
            </div>
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

export default {
  setup() {
    const store = useEcommerceStore();

    onMounted(() => {
      if (!store.allCategoriesWithProducts.length) store.fetchAllCategoriesWithProducts();
    });

    return { store };
  },
  components: {
    MainLayout,
  }
};
</script>

<style scoped>
/* Container for all categories */
.categories-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem; /* Reduced gap for better spacing */
  padding: 1rem;
  /* background-color: #f5f5f5; */
}

/* Individual category card */
.category-card {
  flex: 1;
  min-width: 300px; /* Ensure cards don't get too narrow */
  max-width: 48%; /* Two cards per row on larger screens */
  border-radius: 8px;
  padding: 1rem; /* Reduced padding for tighter layout */
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
  font-size: .8rem; /* Slightly smaller to match the second page */
  font-weight: 700;
  color: #f28c38; /* Orange color to match the image */
  text-transform: uppercase;
  margin: 0.5rem 0;
}

/* Products grid inside each category */
.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem; /* Reduced gap for tighter layout */
}

/* Individual product card */
.product-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  border-radius: 6px;
  padding: 0.5rem; /* Reduced padding for compact look */
  transition: transform 0.2s ease;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Placeholder image styling */
.product-image {
  width: 100%;
  height: 120px; /* Adjusted height to match the second page */
  background-color: #e0e0e0; /* Light gray placeholder */
  border-radius: 4px;
  margin-bottom: 0.5rem;
  object-fit: cover;
}

.product-name {
  font-size: 0.85rem; /* Smaller font to match the second page */
  font-weight: 600;
  /* color: #333; */
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
  font-size: 0.8rem; /* Smaller font to match the second page */
  font-weight: 700;
  /* color: #333; */
  margin: 0.25rem 0;
}

/* Remove the pseudo-element since the price already includes "KES" in the template */
.product-price::before {
  content: none; /* Remove "KES" prefix since it's in the template */
}

/* MOQ info */
.moq-info {
  font-size: 0.7rem; /* Smaller font to match the second page */
  /* color: #666; */
  margin: 0.25rem 0;
}

/* MOQ status (e.g., "Active: X items") */
.moq-status {
  font-size: 0.7rem; /* Smaller font to match the second page */
  color: #28a745; /* Green for active status */
  background-color: #e6f4ea;
  padding: 0.2rem 0.4rem; /* Reduced padding */
  border-radius: 12px;
  margin: 0.25rem 0;
}

/* "See More" link styling */
.see-more-link {
  display: block; /* Ensure it takes its own line */
  text-align: right; /* Align to the right like in the second page */
  font-size: 0.8rem; /* Smaller font to match the second page */
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  text-decoration: none;
  margin-top: 0.5rem;
}

.see-more-link:hover {
  color: #f28c38; /* Orange on hover */
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
    grid-template-columns: repeat(3, 1fr); /* 3 items per row on medium screens */
  }

  .category-card {
    max-width: 100%; /* Full width on smaller screens */
  }
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 items per row on smaller screens */
  }

  .category-card {
    max-width: 100%; /* Full width */
    min-width: 100%; /* Ensure it takes full width */
  }

  .category-title {
    font-size: 1.1rem; /* Slightly smaller title on mobile */
  }

  .product-image {
    height: 100px; /* Smaller image height on mobile */
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
    grid-template-columns: repeat(1, 1fr); /* 1 item per row on very small screens */
  }

  .category-card {
    padding: 0.75rem; /* Reduced padding on mobile */
  }

  .product-image {
    height: 80px; /* Even smaller image height on very small screens */
  }
}
</style>
