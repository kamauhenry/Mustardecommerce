<template>
  <MainLayout>
    <div class="category-page">
      <h1>{{ formattedCategory }}</h1>
      <div v-if="filteredProducts.length">
        <div v-for="product in filteredProducts" :key="product.id" class="product-card">
          <img :src="categoryImages[product.categoryFormatted]" :alt="product.name" />
          <h3>{{ product.name }}</h3>
          <p>{{ product.description }}</p>
          <p class="price">${{ product.price }}</p>
        </div>
      </div>
      <p v-else>No products found in this category.</p>
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from "@/components/navigation/MainLayout.vue";
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
  components: {MainLayout},
  computed: {
    categoryName() {
      return this.$route.params.categoryName;
    },
    formattedCategory() {
      return this.categoryName.replace(/-/g, " ");
    },
    filteredProducts() {
      return this.products.filter(product => {
        return product.categoryFormatted === this.categoryName;
      });
    },
  },
  data() {
    return {
      categoryImages: {
        "agriculture-food-drinks": agriculture,
        "baby-kids-games": babies,
        "swag-branded-gift-items": brandedGifts,
        "buy4me": buy4Me,
        "clothes-apparels": clothes,
        "beauty-personal-health": health,
        "ikea": ikea,
        "machine-industrials": industrial,
        "home-kitchen": kitchen,
        "electronics": laptops,
        "office": office,
        "bags-footwear": shoes,
        "sports-hardware-entertainment": sports,
      },
      products: [
        { id: 1, name: "Blender", category: "Home & Kitchen", categoryFormatted: "home-kitchen", price: 49.99, description: "High-speed kitchen blender." },
        { id: 2, name: "Running Shoes", category: "Bags & Footwear",  categoryFormatted: "bags-footwear", price: 89.99, description: "Comfortable and stylish." },
        { id: 3, name: "Laptop", category: "Electronics",  categoryFormatted: "electronics", price: 699.99, description: "Latest model laptop." },
        { id: 4, name: "Office Chair", category: "Office",  categoryFormatted: "office", price: 149.99, description: "Ergonomic office chair." },
        { id: 5, name: "Baby Toy", category: "Baby, Kids & Games",  categoryFormatted: "baby-kids-games", price: 59.99, description: "Fun and educational toy set." },
        { id: 6, name: "Agricultural Tool", category: "Agriculture, Food & Drinks",  categoryFormatted: "agriculture-food-drinks", price: 79.99, description: "Durable agricultural tool." },
        { id: 7, name: "Branded Mug", category: "Swag/Branded Gift Items",  categoryFormatted: "swag-branded-gift-items", price: 19.99, description: "Custom branded mug." },
        { id: 8, name: "Buy4Me Service", category: "Buy4me",  categoryFormatted: "buy4me", price: 99.99, description: "Personal shopping service." },
        { id: 9, name: "Cotton Shirt", category: "Clothes & Apparels",  categoryFormatted: "clothes-apparels", price: 39.99, description: "Comfortable cotton shirt." },
        { id: 10, name: "Health Supplement", category: "Beauty, Personal & Health",  categoryFormatted: "beauty-personal-health", price: 29.99, description: "Essential health supplement." },
        { id: 11, name: "IKEA Furniture", category: "IKEA",  categoryFormatted: "ikea", price: 249.99, description: "Stylish IKEA furniture." },
        { id: 12, name: "Industrial Machine", category: "Machine & Industrials",  categoryFormatted: "machine-industrials", price: 1299.99, description: "Heavy-duty industrial machine." },
        { id: 13, name: "Blender Pro", category: "Home & Kitchen",  categoryFormatted: "home-kitchen", price: 59.99, description: "Professional kitchen blender." },
        { id: 14, name: "Sports Shoes", category: "Sports, Hardware & Entertainment",  categoryFormatted: "sports-hardware-entertainment", price: 99.99, description: "High quality sports shoes." },
        { id: 15, name: "Gaming Laptop", category: "Electronics",  categoryFormatted: "electronics", price: 899.99, description: "High performance gaming laptop." },
        { id: 16, name: "Executive Chair", category: "Office", categoryFormatted: "office", price: 179.99, description: "Premium executive chair." },
        { id: 17, name: "Baby Clothes", category: "Baby, Kids & Games",  categoryFormatted: "baby-kids-games", price: 69.99, description: "Soft baby clothes." },
        { id: 18, name: "Fertilizer", category: "Agriculture, Food & Drinks",  categoryFormatted: "agriculture-food-drinks", price: 49.99, description: "High yield fertilizer." },
         { id: 19, name: "Branded Pen", category: "Swag/Branded Gift Items",  categoryFormatted: "swag-branded-gift-items", price: 9.99, description: "Custom branded pen." },
        { id: 20, name: "Buy4Me Plus", category: "Buy4me",  categoryFormatted: "buy4me", price: 149.99, description: "Enhanced personal shopping service." },
        { id: 21, name: "Leather Jacket", category: "Clothes & Apparels",  categoryFormatted: "clothes-apparels", price: 129.99, description: "Stylish leather jacket." },
        { id: 22, name: "Vitamins", category: "Beauty, Personal & Health",  categoryFormatted: "beauty-personal-health", price: 19.99, description: "Essential vitamins." },
        { id: 23, name: "IKEA Lamp", category: "IKEA",  categoryFormatted: "ikea", price: 79.99, description: "Modern IKEA lamp." },
        { id: 24, name: "Industrial Robot", category: "Machine & Industrials",  categoryFormatted: "machine-industrials", price: 2499.99, description: "Advanced industrial robot." },
        { id: 25, name: "Toaster", category: "Home & Kitchen",  categoryFormatted: "home-kitchen", price: 39.99, description: "Compact kitchen toaster." },
        { id: 26, name: "Sports Equipment", category: "Sports, Hardware & Entertainment",  categoryFormatted: "sports-hardware-entertainment", price: 119.99, description: "Professional grade sports equipment." },
        { id: 27, name: "Ultrabook", category: "Electronics",  categoryFormatted: "electronics", price: 999.99, description: "Ultra lightweight ultrabook." },
        { id: 28, name: "Desk", category: "Office",  categoryFormatted: "office", price: 299.99, description: "Spacious desk." },
        { id: 29, name: "Baby Blanket", category: "Baby, Kids & Games",  categoryFormatted: "baby-kids-games", price: 39.99, description: "Soft baby blanket." },
        { id: 30, name: "Pesticide", category: "Agriculture, Food & Drinks", categoryFormatted: "agriculture-food-drinks", price: 59.99, description: "Effective pesticide." }
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
