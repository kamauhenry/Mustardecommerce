<!-- eslint-disable vue/multi-word-component-names -->
<script>
import api from "@/api.js";

export default {
  data() {
    return {
      products: [],
      loading: true,
      error: null,
    };
  },
  async created() {
    try {
      const response = await api.get("products/");
      this.products = response.data;
    } catch (error) {
      this.error = "Error fetching products";
      console.error(error);
    } finally {
      this.loading = false;
    }
  },
};
</script>

<template>
  <div>
    <h1>Product List</h1>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <ul v-else>
      <li v-for="product in products" :key="product.id">
        {{ product.name }} - ${{ product.price }}
      </li>
    </ul>
  </div>
</template>

