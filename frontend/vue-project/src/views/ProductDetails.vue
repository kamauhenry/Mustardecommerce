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
import { onMounted, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';

export default {
  props: { categorySlug: String, productSlug: String },
  setup(props) {
    const store = useEcommerceStore();
    const productKey = computed(() => `${props.categorySlug}:${props.productSlug}`);
    const product = computed(() => store.productDetails[productKey.value]);

    onMounted(() => {
      if (!store.productDetails[productKey.value]) {
        store.fetchProductDetails(props.categorySlug, props.productSlug);
      }
    });

    const addToCart = async () => {
      if (!product.value || !store.userId) return;
      try {
        const cart = await store.fetchCartData();
        await store.addToCart(cart.id, product.value.id, product.value.variants[0]?.id || null, 1);
        store.fetchCartData();
      } catch (error) {
        console.error('Add to cart failed:', error);
      }
    };

    return { store, product, addToCart };
  },
};
</script>
