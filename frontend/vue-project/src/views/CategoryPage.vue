<template>
  <div class="category-page">
    <h1>{{ formattedCategory }}</h1>
    <div v-if="filteredProducts.length">
      <div v-for="product in filteredProducts" :key="product.id" class="product-card">
        <img :src="product.image" :alt="product.name" />
        <h3>{{ product.name }}</h3>
        <p>{{ product.description }}</p>
        <p class="price">${{ product.price }}</p>
      </div>
    </div>
    <p v-else>No products found in this category.</p>
  </div>
</template>

<script>
export default {
  computed: {
    categoryName() {
      return this.$route.params.categoryName; // Get category from route
    },
    formattedCategory() {
      return this.categoryName.replace(/-/g, " "); // Convert URL format back to readable text
    },
    filteredProducts() {
      return this.products.filter(product => product.category === this.categoryName);
    },
  },
  data() {
    return {
      products: [
        { id: 1, name: "Blender", category: "home-kitchen", price: 49.99, image: "https://via.placeholder.com/150", description: "High-speed kitchen blender." },
        { id: 2, name: "Running Shoes", category: "bags-footwear", price: 89.99, image: "https://via.placeholder.com/150", description: "Comfortable and stylish." },
        { id: 3, name: "Smartphone", category: "electronics", price: 699.99, image: "https://via.placeholder.com/150", description: "Latest model smartphone." },
        { id: 4, name: "Office Chair", category: "office", price: 149.99, image: "https://via.placeholder.com/150", description: "Ergonomic office chair." },
        { id: 5, name: "Lego Set", category: "baby-kids-games", price: 59.99, image: "https://via.placeholder.com/150", description: "Fun and educational toy set." },
      ],
    };
  },
};
</script>

<style scoped>
.category-page {
  padding: 20px;
  color: black;
}

.product-card {
  background: #333;
  color: white;
  padding: 15px;
  margin: 10px;
  border-radius: 10px;
  display: inline-block;
  width: 200px;
  text-align: center;
}

.product-card img {
  width: 100%;
  height: auto;
  border-radius: 8px;
}

.price {
  color: #ffcc00;
  font-weight: bold;
}
</style>
