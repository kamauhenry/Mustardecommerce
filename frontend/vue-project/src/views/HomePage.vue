<template>
  <MainLayout>
    <div id="homePage">
      <div class="top-part-home">
        <RecentCampaigns></RecentCampaigns>
        <HomeCarousel></HomeCarousel>
        <RecentSearches></RecentSearches>
      </div>
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

<style>

.top-part-home {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  gap: 20px;
}

@media (max-width: 540px) {
  .top-part-home {
    margin: 1rem;
    flex-wrap: wrap-reverse;
  }
}
</style>
