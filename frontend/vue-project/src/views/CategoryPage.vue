<!-- views/CategoryPage.vue -->
<template>
  <MainLayout>
    <div class="category-page">
      <h1>Categories</h1>
      <div v-if="categories.length" class="category-list">
        <div v-for="category in categories" :key="category.id" class="category-card">
          <h2>{{ category.name }}</h2>
          <div class="product-list">
            <div v-for="product in category.products" :key="product.id" class="product-card">
              <router-link :to="`/product/${category.slug}/${product.slug}`">
                <img :src="product.thumbnail || 'https://picsum.photos/200/300'" :alt="product.name" class="product-image" />
                <h3>{{ product.name }}</h3>
                <p class="price">KES {{ product.price }}</p>
                <p v-if="product.moq_status === 'active'">MOQ Progress: {{ product.moq_progress_percentage }}%</p>
              </router-link>
            </div>
          </div>
          <router-link :to="`/category/${category.id}`" class="view-more">View More in {{ category.name }}</router-link>
        </div>
      </div>
      <p v-else>No categories available.</p>
    </div>
  </MainLayout>
</template>

<script>
import { useProductStore } from '@/stores/products';
import MainLayout from "@/components/navigation/MainLayout.vue";

export default {
  components: { MainLayout },
  setup() {
    const productStore = useProductStore();
    return { productStore };
  },
  computed: {
    categories() {
      return this.productStore.categories;
    },
  },
  async created() {
    await this.productStore.fetchCategories();
  },
};
</script>

<style scoped>
.category-page {
  padding: 20px;
  background: #1a1a1a;
  color: #fff;
  font-family: Arial, sans-serif;
}

.category-page h1 {
  color: #ff6200;
  margin-bottom: 20px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.category-card {
  background: #333;
  padding: 20px;
  border-radius: 8px;
}

.category-card h2 {
  color: #ffcc00;
  margin-bottom: 15px;
}

.product-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.product-card {
  width: 200px;
  text-align: center;
}

.product-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #444;
}

.product-card h3 {
  color: #fff;
  margin: 10px 0 5px;
  font-size: 16px;
}

.price {
  color: #ffcc00;
  font-weight: bold;
}

.product-card p {
  color: #ccc;
  font-size: 14px;
}

.view-more {
  display: inline-block;
  margin-top: 15px;
  color: #ff6200;
  text-decoration: none;
}

.view-more:hover {
  text-decoration: underline;
}
</style>
