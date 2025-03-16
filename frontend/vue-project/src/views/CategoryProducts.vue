<template>
  <div class="container">
    <h1>{{ category?.name }}</h1>

    <div v-if="store.loading.categoryProducts" class="loading">Loading products...</div>
    <div v-else-if="store.error.categoryProducts" class="error">
      Error: {{ store.error.categoryProducts }}
    </div>
    <div v-else class="products">
      <div v-for="product in products" :key="product.id" class="product">
        <img v-if="product.thumbnail" :src="product.thumbnail" :alt="product.name" />
        <h3>{{ product.name }}</h3>
        <p>Price: KES {{ product.price }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';

export default {
  props: { categorySlug: String },
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
