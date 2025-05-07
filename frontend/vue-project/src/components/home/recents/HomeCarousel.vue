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
      v-else
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
        <div class="slide-content">
          <p class="slide-title">{{ item.name }}</p>
          <p class="slide-description">{{ item.description || 'Explore our range of products in this category.' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import placeholder from '@/assets/images/placeholder.jpeg';

const slides = ref([]);
const currentSlide = ref(0);
const loading = ref(false);
const error = ref(null);

const fetchCategories = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await axios.get('http://localhost:8000/api/categories/');
    slides.value = response.data
      .filter(category => category.is_active)
      .map(category => ({
        name: category.name,
        slug: category.slug,
        image: category.image || placeholder,
        description: category.description,
      }));
  } catch (err) {
    console.error('Error fetching categories:', err);
    error.value = 'Failed to load categories.';
  } finally {
    loading.value = false;
  }
};

const startAutoSlide = () => {
  setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % slides.value.length;
  }, 5000);
};

const goToCategory = (slug) => {
  window.location.href = `/category/${slug}/products`;
};

onMounted(() => {
  fetchCategories().then(() => {
    if (slides.value.length) {
      startAutoSlide();
    }
  });
});
</script>

<style scoped>
.carousel {
  flex: 1;
  height: 100%;
  overflow: hidden;
  position: relative;
  min-width: 300px;
  max-width: 100%;
  box-sizing: border-box;
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
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  cursor: pointer;
  margin: 0;
  padding: 0;
}

.slide-content {
  text-align: center;
  background: rgba(0, 0, 0, 0.5);
  padding: 1rem;
  border-radius: 8px;
  max-width: 80%;
}

.slide-title {
  font-family: "Roboto", sans-serif;
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--vt-c-category-carousel, #fff);
  padding-bottom: 0.1rem;
  margin: 0;
}

.slide-description {
  font-family: "Roboto", sans-serif;
  margin: 0.5rem 1rem 0;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--vt-c-category-carousel, #fff);
}

.skeleton-container {
  height: 100%;
  width: 100%;
}

.skeleton-slides {
  display: flex;
  height: 100%;
  width: 100%;
}

.skeleton-slide {
  flex: 0 0 100%;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.skeleton-image {
  width: 100%;
  height: 70%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
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
  width: 150px;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin: 0 auto 0.5rem;
  border-radius: 4px;
}

.skeleton-description {
  width: 200px;
  height: 15px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin: 0 auto;
  border-radius: 4px;
}

.error-message {
  color: #e74c3c;
  text-align: center;
  padding: 1rem;
  background-color: #ffe6e6;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.retry-button {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f28c38;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .carousel {
    margin-top: 0;
    width: 100%;
    min-height: 200px;
  }

  .slide-title {
    font-size: 1.2rem;
  }

  .slide-description {
    font-size: 0.8rem;
    margin: 0.3rem 0.5rem 0;
  }

  .slide-content {
    padding: 0.75rem;
    max-width: 90%;
  }

  .skeleton-title {
    width: 120px;
    height: 18px;
  }

  .skeleton-description {
    width: 160px;
    height: 12px;
  }
}

@media (max-width: 650px) {
  .carousel {
    height: 250px;
  }

  .slide {
    background-size: contain;
  }

  .slide-title {
    font-size: 1rem;
  }

  .slide-description {
    font-size: 0.75rem;
  }

  .skeleton-title {
    width: 100px;
    height: 16px;
  }

  .skeleton-description {
    width: 140px;
    height: 10px;
  }
}
</style>