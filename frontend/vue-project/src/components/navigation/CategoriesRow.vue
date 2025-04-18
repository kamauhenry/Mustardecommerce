<template>
  <div class="categories">
    <div class="category category-list">
      <p class="category-p">Categories</p>
    </div>
    <div v-if="store.loading.allCategoriesWithProducts" class="skeleton-container">
      <div v-for="n in 3" :key="n" class="skeleton-category">
        <div v-for="i in 4" :key="i" class="skeleton-category-item"></div>
      </div>
    </div>
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
  font-weight: 700;
  text-transform: uppercase;
  margin: 0;
  color: #f28c38;
}

.category-list-p {
  margin: 0;
}

.category-link {
  font-size: 1rem;
  text-decoration: none;
  transition: color 0.3s ease-in-out;
}

.category-link:hover {
  color: #f28c38;
}

.loading,
.error {
  font-size: 1rem;
  color: #666;
  padding: 0.5rem;
}

.skeleton-container {
  display: flex;
  gap: 2rem;
}

.skeleton-category {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  width: 150px;
}

.skeleton-category-item {
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
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

  .skeleton-container {
    flex-direction: column;
  }

  .skeleton-category {
    width: 100%;
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