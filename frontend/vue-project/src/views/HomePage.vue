<template>
  <MainLayout>
    <div id="homePage">
      <div class="component-row">
        <RecentCampaigns />
        <HomeCarousel />
        <RecentSearches />
      </div>
      <CategoryProducts />
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from "@/components/navigation/MainLayout.vue";
import RecentSearches from "@/components/home/recents/RecentSearches.vue";
import RecentCampaigns from "@/components/home/recents/RecentCampaigns.vue";
import HomeCarousel from "../components/home/recents/HomeCarousel.vue";
import CategoryProducts from "@/components/home/CategoryProducts.vue";

export default {
  components: {
    MainLayout,
    RecentCampaigns,
    RecentSearches,
    HomeCarousel,
    CategoryProducts,
  },
};
</script>

<style scoped>
#homePage {
  padding: 20px; /* Optional padding for the whole page */
}

.component-row {
  display: flex;
  flex-direction: row;
  gap: 20px;
  justify-content: space-between; /* Distributes space evenly */
  align-items: stretch; /* Ensures all components stretch to the same height */
}

/* Ensure each component takes up equal width */
.component-row > * {
  flex: 1; /* Each child takes equal space */
  max-width: 33.33%; /* Cap at 1/3 of the row width */
}

/* Responsive design */
@media (max-width: 768px) {
  .component-row {
    flex-direction: column;
  }
  .component-row > * {
    max-width: 100%; /* Full width on mobile */
  }
}
</style>