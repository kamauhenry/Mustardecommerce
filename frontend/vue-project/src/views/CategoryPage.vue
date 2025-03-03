<template>
  <div class="category-page">
    <h1>{{ formattedCategory }}</h1>
    <div v-if="filteredProducts.length">
      <div v-for="product in filteredProducts" :key="product.id" class="product-card">
        <img :src="categoryImages[product.category]" :alt="product.name" />
        <h3>{{ product.name }}</h3>
        <p>{{ product.description }}</p>
        <p class="price">${{ product.price }}</p>
      </div>
    </div>
    <p v-else>No products found in this category.</p>
  </div>
</template>

<script>
import agriculture from "../assets/images/agriculture.jpeg";
import babies from "../assets/images/babies.jpeg";
import brandedGifts from "../assets/images/branded-gifts.jpeg";
import buy4Me from "../assets/images/buy-4-me.jpeg";
import clothes from "../assets/images/clothes.jpeg";
import health from "../assets/images/health.jpeg";
import ikea from "../assets/images/ikea.jpeg";
import industrial from "../assets/images/industrial.jpeg";
import kitchen from "../assets/images/kitchen.jpeg";
import laptops from "../assets/images/laptops.jpeg";
import office from "../assets/images/office.jpeg";
import shoes from "../assets/images/shoes.jpeg";
import sports from "../assets/images/sports.jpeg";

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
      categoryImages: {
        "agriculture": agriculture,
        "babies": babies,
        "branded-gifts": brandedGifts,
        "buy-4-me": buy4Me,
        "clothes": clothes,
        "health": health,
        "ikea": ikea,
        "industrial": industrial,
        "home-kitchen": kitchen,
        "laptops": laptops,
        "office": office,
        "bags-footwear": shoes,
        "sports": sports
      },
      products: [
        { id: 1, name: "Blender", category: "home-kitchen", price: 49.99, description: "High-speed kitchen blender." },
        { id: 2, name: "Running Shoes", category: "bags-footwear", price: 89.99, description: "Comfortable and stylish." },
        { id: 3, name: "Laptop", category: "laptops", price: 699.99, description: "Latest model laptop." },
        { id: 4, name: "Office Chair", category: "office", price: 149.99, description: "Ergonomic office chair." },
        { id: 5, name: "Baby Toy", category: "babies", price: 59.99, description: "Fun and educational toy set." },
        { id: 6, name: "Agricultural Tool", category: "agriculture", price: 79.99, description: "Durable agricultural tool." },
        { id: 7, name: "Branded Mug", category: "branded-gifts", price: 19.99, description: "Custom branded mug." },
        { id: 8, name: "Buy4Me Service", category: "buy-4-me", price: 99.99, description: "Personal shopping service." },
        { id: 9, name: "Cotton Shirt", category: "clothes", price: 39.99, description: "Comfortable cotton shirt." },
        { id: 10, name: "Health Supplement", category: "health", price: 29.99, description: "Essential health supplement." },
        { id: 11, name: "IKEA Furniture", category: "ikea", price: 249.99, description: "Stylish IKEA furniture." },
        { id: 12, name: "Industrial Machine", category: "industrial", price: 1299.99, description: "Heavy-duty industrial machine." },
        { id: 13, name: "Blender Pro", category: "home-kitchen", price: 59.99, description: "Professional kitchen blender." },
        { id: 14, name: "Sports Shoes", category: "sports", price: 99.99, description: "High quality sports shoes." },
        { id: 15, name: "Gaming Laptop", category: "laptops", price: 899.99, description: "High performance gaming laptop." },
        { id: 16, name: "Executive Chair", category: "office", price: 179.99, description: "Premium executive chair." },
        { id: 17, name: "Baby Clothes", category: "babies", price: 69.99, description: "Soft baby clothes." },
        { id: 18, name: "Fertilizer", category: "agriculture", price: 49.99, description: "High yield fertilizer." },
        { id: 19, name: "Branded Pen", category: "branded-gifts", price: 9.99, description: "Custom branded pen." },
        { id: 20, name: "Buy4Me Plus", category: "buy-4-me", price: 149.99, description: "Enhanced personal shopping service." },
        { id: 21, name: "Leather Jacket", category: "clothes", price: 129.99, description: "Stylish leather jacket." },
        { id: 22, name: "Vitamins", category: "health", price: 19.99, description: "Essential vitamins." },
        { id: 23, name: "IKEA Lamp", category: "ikea", price: 79.99, description: "Modern IKEA lamp." },
        { id: 24, name: "Industrial Robot", category: "industrial", price: 2499.99, description: "Advanced industrial robot." },
        { id: 25, name: "Toaster", category: "home-kitchen", price: 39.99, description: "Compact kitchen toaster." },
        { id: 26, name: "Sports Equipment", category: "sports", price: 119.99, description: "Professional grade sports equipment." },
        { id: 27, name: "Ultrabook", category: "laptops", price: 999.99, description: "Ultra lightweight ultrabook." },
        { id: 28, name: "Desk", category: "office", price: 299.99, description: "Spacious desk." },
        { id: 29, name: "Baby Blanket", category: "babies", price: 39.99, description: "Soft baby blanket." },
        { id: 30, name: "Pesticide", category: "agriculture", price: 59.99, description: "Effective pesticide." }
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
