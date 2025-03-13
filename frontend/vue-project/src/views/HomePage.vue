<template>
  <MainLayout>
    <div id="homePage">
      <RecentCampaigns></RecentCampaigns>
      <HomeCarousel></HomeCarousel>
      <RecentSearches></RecentSearches>
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from "@/components/navigation/MainLayout.vue";
import RecentSearches from "@/components/home/recents/RecentSearches.vue";
import RecentCampaigns from "@/components/home/recents/RecentCampaigns.vue";
import HomeCarousel from "../components/home/recents/HomeCarousel.vue";

export default {
  components: {
    MainLayout,
    RecentCampaigns,
    RecentSearches,
    HomeCarousel,
  },
};
</script>
