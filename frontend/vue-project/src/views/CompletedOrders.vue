<template>
  <div>
    <h1>All Categories</h1>
    <div v-if="store.loading.allCategoriesWithProducts">Loading...</div>
    <div v-else-if="store.error.allCategoriesWithProducts">{{ store.error.allCategoriesWithProducts }}</div>
    <ul v-else>
      <li v-for="category in store.allCategoriesWithProducts" :key="category.id">
        <router-link :to="`/category/${category.slug}`">{{ category.name }}</router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useProductsStore } from '@/stores/modules/products';

export default {
  setup() {
    const store = useProductsStore();

    onMounted(() => {
      if (!store.allCategoriesWithProducts.length) store.fetchAllCategoriesWithProducts();
    });

    return { store };
  },
};
</script>
