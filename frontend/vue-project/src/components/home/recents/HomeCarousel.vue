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
          <p class="slide-title">{{ item.title }}</p>
          <p class="slide-description">{{ item.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import placeholder from "../../../assets/images/placeholder.jpeg";
export default {
  data() {
    return {
      slides: [
        {
          title: "Slide 1 Title",
          description: "This is the description for slide 1.",
          image: placeholder,
        },
        {
          title: "Slide 2 Title",
          description: "This is the description for slide 2.",
          image: placeholder,
        },
        {
          title: "Slide 3 Title",
          description: "This is the description for slide 3.",
          image: placeholder,
        },
      ],
      currentSlide: 0,
    };
  },
  mounted() {
    this.startAutoSlide();
  },
  methods: {
    startAutoSlide() {
      setInterval(() => {
        this.currentSlide =
          (this.currentSlide + 1) % this.slides.length;
      }, 3000);
    },
  },
};
</script>

<style scoped>
.carousel {
  width: 100%;
  height: auto; /* Define a height, e.g., 25vw */
  overflow: hidden;
  position: relative;
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
  font-size: 1.8rem;
  font-weight: bold;
  color: white;
  padding-bottom: 1rem;
}

.slide-description {
  font-size: 1rem;
  color: white;
  padding-bottom: 5rem;
}
</style>

