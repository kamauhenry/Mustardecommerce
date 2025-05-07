<template>
  <section class="recent-campaigns" aria-labelledby="recent-campaigns-title">
    <h2 id="recent-campaigns-title" class="campaigns-title">Recent Campaigns</h2>
    <div v-if="isLoading" class="skeleton-container">
      <div v-for="n in 3" :key="n" class="skeleton-campaign">
        <div class="skeleton-campaign-img"></div>
        <div class="skeleton-campaign-text"></div>
      </div>
    </div>
    <div v-else class="products-campaigns">
      <article
        v-for="(item, index) in latestProducts"
        :key="index"
        class="product-campaigns"
        itemscope
        itemtype="http://schema.org/Product"
      >
        <router-link
          :to="{
            name: 'product-detail',
            params: { categorySlug: item.category?.slug, productSlug: item.slug }
          }"
          class="product-link"
        >
          <img
            :src="item.image || item.thumbnail || placeholder"
            :alt="item.name"
            class="product-campaign-img"
            width="50"
            height="50"
            itemprop="image"
            loading="lazy"
          />
          <div class="slide-content">
            <h3 class="campaign-p" itemprop="name">{{ item.name }}</h3>
            <p class="campaign-price" itemprop="offers" itemscope itemtype="http://schema.org/Offer">
              KES {{ formatPrice(item.price) }}
              <meta itemprop="priceCurrency" content="KES" />
              <meta itemprop="price" :content="item.price.toString()" />
            </p>
            <div v-if="item.moq_progress" class="moq-progress-container">
              <div
                class="moq-progress-bar"
                :style="{ width: Math.min(100, item.moq_progress.percentage) + '%' }"
              ></div>
              <span class="moq-progress-text">
                {{ item.moq_progress.percentage }}%
              </span>
            </div>
          </div>
        </router-link>
      </article>
    </div>
  </section>
</template>

<script>
import { ref, onMounted } from 'vue';
import placeholder from '@/assets/images/placeholder.jpeg';

export default {
  setup() {
    const latestProducts = ref([]);
    const isLoading = ref(true);

    const fetchLatestProducts = async () => {
      try {
        isLoading.value = true;
        const response = await fetch('http://localhost:8000/api/products/latest/?limit=3');
        if (!response.ok) throw new Error('Failed to fetch latest products');
        const data = await response.json();
        latestProducts.value = (data.results || [])
          .map(product => ({
            ...product,
            image: product.image || product.thumbnail,
            moq_progress: product.moq_progress,
          }))
          .filter(product => product.category && product.category.slug); // Ensure valid category
      } catch (error) {
        console.error('Error fetching latest products:', error);
        latestProducts.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    const formatPrice = (value) => {
      if (value == null) return '0.00';
      return parseFloat(value).toFixed(2);
    };

    onMounted(() => {
      fetchLatestProducts();
    });

    return {
      latestProducts,
      isLoading,
      placeholder,
      formatPrice,
    };
  },
};
</script>

<style scoped>
.product-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: row;
  gap: 1rem;
  align-items: center;
  width: 100%;
  height: 100%;
  transition: all 0.3s ease;
}

.product-campaigns {
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: row;
  gap: 1rem;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.product-campaigns:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.product-campaigns:hover .product-campaign-img {
  transform: scale(1.03);
}

.moq-progress-container {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: #e6f4ea;
  border-radius: 20px;
  overflow: hidden;
  margin-top: auto;
}

.moq-progress-bar {
  padding: 2px;
  height: 100%;
  background: linear-gradient(45deg, #62c87a, #6dc480);
  transition: width 0.5s ease;
}

.moq-progress-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 0.65rem;
  font-weight: bold;
  text-shadow: 0 0 2px #fff;
}

.recent-campaigns {
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 250px; /* Fixed width for consistency */
  flex-shrink: 0;
  flex-grow: 0;
}

.campaigns-title {
  text-transform: uppercase;
  font-weight: 700;
  margin: 0;
}

.products-campaigns {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.product-campaign-img {
  border-radius: 10px;
  object-fit: cover;
}

.campaign-p {
  margin: 0;
  font-size: 1rem;
}

.campaign-price {
  margin: 0;
  font-size: 0.9rem;
  color:#D4A017;
  font-weight: 600;
}

.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-campaign {
  display: flex;
  flex-direction: row;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  width: 100%;
  flex-shrink: 0;
  flex-grow: 0;
}

.skeleton-campaign-img {
  width: 50px;
  height: 50px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 10px;
}

.skeleton-campaign-text {
  width: 60%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 768px) {
  .recent-campaigns {
    display: none;
  }
}
</style>