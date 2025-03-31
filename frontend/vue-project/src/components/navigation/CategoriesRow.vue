<template>
  <div class="categories">
    <div class="category category-list">
      <p class="category-p">Categories</p>
    </div>
    <div v-if="store.loading.allCategoriesWithProducts" class="loading">Loading categories...</div>
    <div v-else-if="store.error.allCategoriesWithProducts" class="error">
      Error: {{ store.error.allCategoriesWithProducts }}
    </div>
    <div v-else v-for="(group, index) in categoryGroupsComputed" :key="index" class="category-list">
      <p v-for="(category, i) in group" :key="i" class="category-list-p">
        <router-link
          :to="`/category/${category.slug}/products`"
          class="category-link"
        >
          {{ category.name }}
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';

const store = useEcommerceStore();

onMounted(() => {
  if (!store.allCategoriesWithProducts.length) {
    store.fetchAllCategoriesWithProducts();
  }
});

const categories = computed(() => store.allCategoriesWithProducts);

const categoryGroupsComputed = computed(() => {
  const grouped = [];
  for (let i = 0; i < categories.value.length; i += 3) {
    grouped.push(categories.value.slice(i, i + 3));
  }
  return grouped;
});
</script>

<style scoped>
.categories {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  justify-content: space-around;
  padding: 1.3rem 3.3rem;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.category-p {
  font-weight: 700; /* Bolder to match the first code's category title */
  /* font-size: 1.25rem; Matches the first code's category-title */
  text-transform: uppercase;
  margin: 0;
  color: #f28c38;
}

.category-list-p {
  margin: 0;
}

.category-link {
  font-size: 1rem; /* Slightly smaller than the title for hierarchy */
  text-decoration: none;
  transition: color 0.3s ease-in-out;
}

.category-link:hover {
  color: #f28c38; /* Matches the hover color from the first code */
}

.loading,
.error {
  font-size: 1rem;
  color: #666;
  padding: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .categories {
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
  }

  .category-p {
    font-size: 1.1rem;
  }

  .category-link {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .category-p {
    font-size: 1rem;
  }

  .category-link {
    font-size: 0.85rem;
  }
}
</style>
