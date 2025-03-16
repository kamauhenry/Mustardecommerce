<template>
  <div class="carousel">
    <div
      class="carousel-slides"
      :style="{ transform: `translateX(-${currentSlide * 100}%)` }"
    >
      <div
        class="slide"
        v-for="(item, index) in slides"
        :key="index"
        :style="{ backgroundImage: `url(${item.image})` }"
        @click="goToCategory(item.name)"
      >
        <div class="slide-content">
          <p class="slide-title">{{ item.name }}</p>
          <p class="slide-description">{{ item.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import agriculture from "../../../assets/images/agriculture.jpeg";
import babies from "../../../assets/images/babies.jpeg";
import brandedGifts from "../../../assets/images/branded-gifts.jpeg";
import buy4Me from "../../../assets/images/buy-4-me.jpeg";
import clothes from "../../../assets/images/clothes.jpeg";
import health from "../../../assets/images/health.jpeg";
import ikea from "../../../assets/images/ikea.jpeg";
import industrial from "../../../assets/images/industrial.jpeg";
import kitchen from "../../../assets/images/kitchen.jpeg";
import laptops from "../../../assets/images/laptops.jpeg";
import office from "../../../assets/images/office.jpeg";
import shoes from "../../../assets/images/shoes.jpeg";
import sports from "../../../assets/images/sports.jpeg";

export default {
  data() {
    return {
      categories: [
        {
          name: "Agriculture, Food & Drinks",
          description: "Explore a diverse range of products and tools tailored for modern farming and agriculture.",
          image: agriculture,
        },
        {
          name: "Baby, Kids & Games",
          description: "Discover a delightful selection of products designed for babies, children, and engaging play.",
          image: babies,
        },
        {
          name: "Swag/Branded Gift Items",
          description: "Elevate your brand with our customizable swag and branded gift items, perfect for any occasion.",
          image: brandedGifts,
        },
        {
          name: "Buy4me",
          description: "Let us handle your shopping with our convenient Buy4me service, making online purchases a breeze.",
          image: buy4Me,
        },
        {
          name: "Clothes & Apparels",
          description: "Find fashionable clothing and apparel for all ages and styles.",
          image: clothes,
        },
        {
          name: "Beauty, Personal & Health",
          description: "Enhance your well-being with our range of beauty, personal care, and health products.",
          image: health,
        },
        {
          name: "IKEA",
          description: "Transform your home with the latest furniture and stylish home goods from IKEA.",
          image: ikea,
        },
        {
          name: "Machine & Industrials",
          description: "Create your dream space with our extensive collection of home and kitchen appliances and essentials.",
          image: industrial,
        },
        {
          name: "Home & Kitchen",
          description: "Discover innovative home appliances designed to simplify your daily routines and enhance your living space.",
          image: kitchen,
        },
        {
          name: "Electronics",
          description: "Explore the latest electronics and gadgets designed to make your life easier, more productive, and more enjoyable.",
          image: laptops,
        },
        {
          name: "Office",
          description: "Optimize your workspace with our range of office supplies and ergonomic furniture solutions.",
          image: office,
        },
        {
          name: "Bags & Footwear",
          description: "Step out in style with our fashionable bags and footwear for every occasion.",
          image: shoes,
        },
        {
          name: "Sports, Hardware & Entertainment",
          description: "Gear up for your next adventure with our sports, hardware, and entertainment products.",
          image: sports,
        },
      ],
      slides: [],
      currentSlide: 0,
    };
  },
  mounted() {
    this.selectRandomCategories();
    this.startAutoSlide();
  },
  methods: {
    selectRandomCategories() {
      const shuffled = [...this.categories].sort(() => 0.5 - Math.random()); // Shuffle array

      this.slides = shuffled.slice(0, 3); // Get first 3 elements

    },
    startAutoSlide() {
      setInterval(() => {
        this.currentSlide = (this.currentSlide + 1) % this.slides.length;
      }, 5000);
    },
    goToCategory(categoryName) {
      const urlFriendlyName = categoryName.toLowerCase().replace(/[^a-z0-9]+/g, "-");
      this.$router.push(`/category/${urlFriendlyName}`);
    },
  },
};
</script>

<style scoped>
.carousel {
  width: 100%;
  height: 45vh;
  overflow: hidden;
  position: relative;
  border-radius: 20px;
}

.carousel-slides {
  display: flex;
  transition: transform 0.5s ease-in-out;
}

.slide {
  min-width: 100%;
  height: 45vh;
  background-size: cover;
  background-position: center;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.slide-content {
  text-align: center;
}

.slide-title {
  font-family: "Roboto", sans-serif;
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--vt-c-category-carousel);
  padding-bottom: .1rem;
}

.slide-description {
  font-family: "Roboto", sans-serif;
  margin: 0 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--vt-c-category-carousel);
}
</style>
