<template>
  <div class="recent-campaigns">
    <p class="campaigns-title">Recent Campaigns</p>
    <div v-if="displayCategories.length" class="products-campaigns">
      <router-link
        v-for="(item, index) in displayCategories"
        :key="index"
        :to="`/category/${item.slug}/products`"
        class="product-campaigns"
      >
        <img :src="item.image" :alt="item.name" class="product-campaign-img" width="50" height="50">
        <div class="slide-content">
          <p class="campaign-p">{{ item.name }}</p>
        </div>
      </router-link>
    </div>
    <div v-else class="no-campaigns">
      No recent campaigns
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import placeholderImage from '@/assets/images/ikea.jpeg';
import { getRecentCategories } from '@/utils/tracking';

export default {
  setup() {
    const store = useEcommerceStore();

    // Fetch recent categories from localStorage
    const recentCategories = computed(() => getRecentCategories());

    // Fetch all categories from the store
    const allCategories = computed(() => store.allCategoriesWithProducts);

    // Function to get 3 random categories
    const getRandomCategories = (categories, count) => {
      if (!categories || categories.length === 0) return [];
      const shuffled = [...categories].sort(() => 0.5 - Math.random());
      return shuffled.slice(0, count).map(category => ({
        id: category.id,
        name: category.name,
        slug: category.slug,
        image: category.image || placeholderImage
      }));
    };

    // Display categories: use recent ones if available, otherwise use random ones
    const displayCategories = computed(() => {
      let categories = recentCategories.value;
      if (categories.length === 0) {
        // If no recent categories, pick 3 random ones
        categories = getRandomCategories(allCategories.value, 3);
      }
      // Ensure we always display 3 items, using placeholders if necessary
      const placeholder = {
        name: 'No Category',
        slug: '',
        image: placeholderImage
      };
      while (categories.length < 3) {
        categories.push({ ...placeholder, id: `placeholder-${categories.length}` });
      }
      return categories;
    });

    return {
      displayCategories
    };
  }
};
</script>

<style scoped>
.recent-campaigns {
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 35%;
  min-width: 20vw;
}

.campaigns-title {
  text-transform: uppercase;
  font-weight: 700;
}

.products-campaigns {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  text-decoration: none;
  color: inherit;
}

.product-campaign-img {
  border-radius: 10px;
}

.no-campaigns {
  padding: 1rem;
  color: #666;
  font-style: italic;
}

@media (max-width: 768px) {
  .recent-campaigns {
    display: none;
  }
}
</style>
