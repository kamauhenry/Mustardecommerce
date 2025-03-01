<template>
  <div class="categories">
    <div class="category category-list">
      <p class="category-p">Categories</p>
    </div>
    <div v-for="(group, index) in categoryGroups" :key="index" class="category-list">
      <p v-for="(category, i) in group" :key="i" class="category-list-p">
        <router-link :to="getCategoryRoute(category)" class="category-link">
          {{ category }}
        </router-link>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "CategoryGroups",
  data() {
    return {
      categoryGroups: [
        ["Home & Kitchen", "Clothes & Apparels", "Buy4me"],
        ["Bags & Footwear", "Sports, Hardware & Entertainment", "Swag/Branded Gift Items"],
        ["Electronics", "Ikea", "Agriculture, Food & Drinks"],
        ["Beauty, Personal & Health", "Baby, Kids & Games"],
        ["Machine & Industrials", "Office"],
      ],
    };
  },
  methods: {
    getCategoryRoute(category) {
      return `/category/${category.toLowerCase().replace(/[\s,&]+/g, "-")}`;
    },
  },
};
</script>

<style scoped>
.categories {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  justify-content: space-around;
  padding: .7rem 1rem;
  font-weight: 700;
}

.category-title {
  font-weight: bold;
  color: var(--text-color-one);
  margin-right: 20px;
  min-width: 120px;
}

.category-container {
  display: flex;
  gap: 40px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: .4rem;
}

.category-p {
  color: var(--text-color-one);
  font-weight: 700;
  font-size: 1.1rem;
}

.category-link {
  font-size: 1.1rem;
  text-decoration: none;
  font-weight: 700;
  transition: color 0.3s ease-in-out;
}
</style>
