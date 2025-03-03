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
          description: "Products and tools for farming and agriculture.",
          image: agriculture,
        },
        {
          name: "Baby, Kids & Games",
          description: "Products for babies and infants.",
          image: babies,
        },
        {
          name: "Swag/Branded Gift Items",
          description: "Customized gifts for marketing and branding.",
          image: brandedGifts,
        },
        {
          name: "Buy4me",
          description: "Service for purchasing products on your behalf.",
          image: buy4Me,
        },
        {
          name: "Clothes & Apparels",
          description: "Fashionable clothing for all ages.",
          image: clothes,
        },
        {
          name: "Beauty, Personal & Health",
          description: "Health and wellness products.",
          image: health,
        },
        {
          name: "IKEA",
          description: "Furniture and home goods from IKEA.",
          image: ikea,
        },
        {
          name: "Machine & Industrials",
          description: "Industrial machinery and equipment.",
          image: industrial,
        },
        {
          name: "Home & Kitchen",
          description: "Kitchen appliances and cookware.",
          image: kitchen,
        },
        {
          name: "Electronics",
          description: "High-performance laptops for all needs.",
          image: laptops,
        },
        {
          name: "Office",
          description: "Office supplies and furniture.",
          image: office,
        },
        {
          name: "Bags & Footwear",
          description: "Footwear for all occasions.",
          image: shoes,
        },
        {
          name: "Sports, Hardware & Entertainment",
          description: "Sports equipment and apparel.",
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
      }, 3000);
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
  justify-content: flex-end;
  align-items: center;
  flex-direction: column;
}

.slide-content {
  text-align: center;
}

.slide-title {
  font-family: "Roboto", sans-serif;
  font-size: 2rem;
  font-weight: 900;
  color: var(--vt-c-white-soft);
  padding-bottom: .1rem;
}

.slide-description {
  font-size: 1.2rem;
  font-weight: 700;
  color: white;
  padding-bottom: 2rem;
}
</style>
