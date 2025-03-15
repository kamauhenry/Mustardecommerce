<!-- views/MOQCampaigns.vue -->
<template>
  <MainLayout>
    <div class="moq-campaigns-page">
      <h1>MOQ Campaigns</h1>
      <div class="filters">
        <label>Filter:</label>
        <select v-model="selectedCategory" @change="fetchProducts">
          <option value="">ALL CATEGORIES</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <select v-model="sortOrder" @change="fetchProducts">
          <option value="">Default Order</option>
          <option value="price">Price: Low to High</option>
          <option value="-price">Price: High to Low</option>
          <option value="created_at">Newest First</option>
          <option value="-created_at">Oldest First</option>
        </select>
      </div>
      <div v-if="products.length" class="product-list">
        <div v-for="product in products" :key="product.id" class="product-card">
          <router-link :to="`/product/${product.category.slug}/${product.slug}`">
            <img :src="product.thumbnail || 'https://picsum.photos/200/300'" :alt="product.name" class="product-image" />
            <h3>{{ product.name }}</h3>
            <p class="price">KES {{ product.price }}</p>
            <p v-if="product.below_moq_price" class="moq-price">Below MOQ Price: KES {{ product.below_moq_price }}</p>
            <p v-if="product.moq_status === 'active'">MOQ: {{ product.moq }} items</p>
            <p v-if="product.moq_status === 'active'" :class="{ 'active': product.moq_status === 'active' }">
              Status: {{ product.moq_status.toUpperCase() }}
            </p>
            <p v-if="product.moq_status === 'active'">Progress: {{ product.moq_progress_percentage }}% Orders</p>
          </router-link>
        </div>
      </div>
      <p v-else>No MOQ campaigns available.</p>
    </div>
  </MainLayout>
</template>

<script>
import { useProductStore } from '@/stores/products';
import MainLayout from '@/components/navigation/MainLayout.vue';

export default {
  components: { MainLayout },
  setup() {
    const productStore = useProductStore();
    return { productStore };
  },
  data() {
    return {
      selectedCategory: '',
      sortOrder: '',
    };
  },
  computed: {
    categories() {
      return this.productStore.categories;
    },
    products() {
      return this.productStore.products.filter(product => product.moq_status === 'active');
    },
  },
  async created() {
    await this.productStore.fetchCategories();
    await this.fetchProducts();
  },
  methods: {
    async fetchProducts() {
      let url = `/api/products/?moq_status=active`;
      if (this.selectedCategory) {
        url += `&category=${this.selectedCategory}`;
      }
      if (this.sortOrder) {
        url += `&ordering=${this.sortOrder}`;
      }
      try {
        const response = await axios.get(url);
        this.productStore.products = response.data;
      } catch (error) {
        console.error('Error fetching MOQ campaigns:', error);
        this.productStore.products = [];
      }
    },
  },
};
</script>

<style scoped>
.moq-campaigns-page {
  padding: 20px;
  background: #fff;
  color: #333;
  font-family: Arial, sans-serif;
}

.moq-campaigns-page h1 {
  color: #ff6200;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filters label {
  font-weight: bold;
  color: #333;
}

.filters select {
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.product-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.product-card {
  width: 200px;
  text-align: center;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px;
}

.product-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
}

.product-card h3 {
  color: #333;
  margin: 10px 0 5px;
  font-size: 16px;
}

.price {
  color: #ff6200;
  font-weight: bold;
}

.moq-price {
  color: #666;
  font-size: 14px;
}

.product-card p {
  color: #666;
  font-size: 14px;
}

.product-card p.active {
  color: #ff6200;
  font-weight: bold;
}

.product-card a {
  text-decoration: none;
}

.product-card:hover {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
</style>
