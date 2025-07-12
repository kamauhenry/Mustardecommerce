<template>
  <div class="carousel">
    <div v-if="loading" class="skeleton-container">
      <div class="skeleton-slides">
        <div v-for="n in 3" :key="n" class="skeleton-slide">
          <div class="skeleton-image"></div>
          <div class="skeleton-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-description"></div>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button @click="fetchCategories" class="retry-button">Retry</button>
    </div>
    <div
      v-else-if="slides.length"
      class="carousel-slides"
      :style="{ transform: `translateX(-${currentSlide * 100}%)` }"
    >
      <div
        class="slide"
        v-for="(item, index) in slides"
        :key="index"
        :style="{ backgroundImage: `url(${item.image})` }"
        @click="goToCategory(item.slug)"
      >
        <div class="slide-overlay"></div>
        <div class="slide-content">
          <h2 class="slide-title">{{ item.name }}</h2>
          <p class="slide-description">{{ item.description }}</p>
          <div class="slide-cta">
            <span class="cta-text">Explore Category</span>
            <span class="cta-arrow">→</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="no-slides">
      No active categories available.
    </div>
    
    <!-- Navigation dots -->
    <div v-if="slides.length > 1" class="carousel-dots">
      <button
        v-for="(slide, index) in slides"
        :key="index"
        class="dot"
        :class="{ active: currentSlide === index }"
        @click="goToSlide(index)"
      ></button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const slides = ref([]);
const currentSlide = ref(0);
const loading = ref(false);
const error = ref(null);
let autoSlideInterval = null;

const fetchCategories = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await axios.get('https://mustardimports.co.ke/api/categories/');
    console.log('API response:', response.data);
    slides.value = response.data
      .map(category => ({
        name: category.name,
        slug: category.slug,
        image: category.primary_image,
        description: category.description || 'Explore our range of products in this category.',
      }));
    if (!slides.value.length) {
      error.value = 'No active categories available.';
    }
  } catch (err) {
    console.error('Error fetching categories:', err);
    error.value = 'Failed to load categories. Please try again later.';
  } finally {
    loading.value = false;
  }
};

const startAutoSlide = () => {
  if (autoSlideInterval) {
    clearInterval(autoSlideInterval);
  }
  autoSlideInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % slides.value.length;
  }, 5000);
};

const goToSlide = (index) => {
  currentSlide.value = index;
  startAutoSlide(); // Restart auto-slide timer
};

const goToCategory = (slug) => {
  window.location.href = `/category/${slug}/products`;
};

onMounted(() => {
  fetchCategories().then(() => {
    console.log('Slides after fetch:', slides.value);
    if (slides.value.length > 1) {
      startAutoSlide();
    }
  });
});

onUnmounted(() => {
  if (autoSlideInterval) {
    clearInterval(autoSlideInterval);
  }
});
</script>

<style scoped>
.carousel {
  flex: 1;
  height: 100%;
  min-height: 400px;
  max-height: 500px;
  overflow: hidden;
  position: relative;
  width: 100%;
  box-sizing: border-box;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.carousel-slides {
  display: flex;
  transition: transform 0.5s ease-in-out;
  height: 100%;
  width: 100%;
}

.slide {
  flex: 0 0 100%;
  height: 100%;
  width: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  cursor: pointer;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  position: relative;
  transition: transform 0.3s ease;
}

.slide:hover {
  transform: scale(1.02);
}

.slide-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.4) 0%,
    rgba(0, 0, 0, 0.2) 50%,
    rgba(0, 0, 0, 0.6) 100%
  );
  z-index: 1;
}

.slide-content {
  text-align: center;
  position: relative;
  z-index: 2;
  max-width: 80%;
  width: 100%;
  padding: 2rem;
  color: white;
}

.slide-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
  letter-spacing: 1px;
  text-transform: uppercase;
  line-height: 1.2;
}

.slide-description {
  font-size: 1.2rem;
  margin: 0 0 1.5rem 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
  opacity: 0.95;
  line-height: 1.4;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.slide-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(212, 160, 23, 0.9);
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.slide:hover .slide-cta {
  background: rgba(212, 160, 23, 1);
  border-color: white;
  transform: translateY(-2px);
}

.cta-arrow {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.slide:hover .cta-arrow {
  transform: translateX(5px);
}

.carousel-dots {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 3;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dot.active {
  background: white;
  transform: scale(1.2);
}

.dot:hover {
  background: rgba(255, 255, 255, 0.8);
}

.skeleton-container {
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}

.skeleton-slides {
  display: flex;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}

.skeleton-slide {
  flex: 0 0 100%;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  box-sizing: border-box;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
}

.skeleton-image {
  width: 80%;
  height: 60%;
  background: linear-gradient(90deg, #e0e0e0 25%, #d0d0d0 50%, #e0e0e0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

.skeleton-content {
  text-align: center;
  padding: 1rem;
  max-width: 80%;
}

.skeleton-title {
  width: 200px;
  height: 24px;
  background: linear-gradient(90deg, #e0e0e0 25%, #d0d0d0 50%, #e0e0e0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin: 0 auto 1rem;
  border-radius: 4px;
}

.skeleton-description {
  width: 300px;
  height: 18px;
  background: linear-gradient(90deg, #e0e0e0 25%, #d0d0d0 50%, #e0e0e0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin: 0 auto;
  border-radius: 4px;
}

.error-message {
  color: #e74c3c;
  text-align: center;
  padding: 2rem;
  background-color: #ffe6e6;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.no-slides {
  text-align: center;
  padding: 2rem;
  color: #666;
  background-color: #f8f9fa;
  border-radius: 8px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #D4A017;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background-color: #e67d21;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Tablet adjustments */
@media (max-width: 1024px) {
  .carousel {
    min-height: 350px;
    max-height: 400px;
  }
  
  .slide-title {
    font-size: 2rem;
  }
  
  .slide-description {
    font-size: 1.1rem;
  }
  
  .slide-content {
    padding: 1.5rem;
    max-width: 90%;
  }
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .carousel {
    min-height: 280px;
    max-height: 320px;
    border-radius: 8px;
  }
  
  .slide-title {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }
  
  .slide-description {
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }
  
  .slide-content {
    padding: 1rem;
    max-width: 95%;
  }
  
  .slide-cta {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .carousel-dots {
    bottom: 15px;
  }
  
  .dot {
    width: 10px;
    height: 10px;
  }
}

/* Small mobile adjustments */
@media (max-width: 480px) {
  .carousel {
    min-height: 250px;
    max-height: 280px;
  }
  
  .slide-title {
    font-size: 1.3rem;
    margin-bottom: 0.4rem;
  }
  
  .slide-description {
    font-size: 0.8rem;
    margin-bottom: 0.8rem;
  }
  
  .slide-content {
    padding: 0.8rem;
  }
  
  .slide-cta {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
  
  .carousel-dots {
    bottom: 10px;
  }
  
  .dot {
    width: 8px;
    height: 8px;
  }
}
</style>