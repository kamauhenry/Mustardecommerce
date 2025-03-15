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
.component-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  margin: 1rem 0;
  gap: 1rem;
  align-items: stretch;
}

/* Responsive design */
@media (max-width: 768px) {
  .component-row {
    flex-direction: column-reverse;
    gap: 1rem;
    align-items: center;

  }
  .component-row > * {
    width: 100%;
  }

  .recent-campaigns {
    display: none;
  }
}

@media (min-width: 769px) {
  .component-row {
    align-items: stretch;
  }
}
</style>
