<template>
  <div class="home-page-container">
    <template v-if="!isMobile">
      <TopRow @toggle-menu="isSidebarOpen = !isSidebarOpen" />
      <PagesRow />
      <CategoriesRow />
    </template>
    <HamburgerMenu v-if="isMobile" :isOpen="isSidebarOpen" @close-menu="isSidebarOpen = false" />
    <div id="homePage">
      <RecentCampaigns></RecentCampaigns>
      <HomeCarousel></HomeCarousel>
      <RecentSearches></RecentSearches>
    </div>
    <FooterPage></FooterPage>
    <CookiesConsent />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import TopRow from "@/components/navigation/TopRow.vue";
import PagesRow from "@/components/navigation/PagesRow.vue";
import CategoriesRow from "@/components/navigation/CategoriesRow.vue";
import HamburgerMenu from "@/components/navigation/HamburgerMenu.vue";
import FooterPage from "@/components/footer/FooterPage.vue";
import CookiesConsent from "@/views/CookiesConsent.vue";
import RecentSearches from "@/components/home/recents/RecentSearches.vue";
import RecentCampaigns from "@/components/home/recents/RecentCampaigns.vue";
import HomeCarousel from "../components/home/recents/HomeCarousel.vue";

export default {
  components: {
    TopRow,
    PagesRow,
    CategoriesRow,
    HamburgerMenu,
    FooterPage,
    CookiesConsent,
    RecentCampaigns,
    RecentSearches,
    HomeCarousel,
  },
  setup() {
    const isMobile = ref(window.innerWidth <= 768);
    const isSidebarOpen = ref(false);

    const updateScreenSize = () => {
      isMobile.value = window.innerWidth <= 768;
    };

    onMounted(() => {
      window.addEventListener("resize", updateScreenSize);
    });

    onUnmounted(() => {
      window.removeEventListener("resize", updateScreenSize);
    });

    return { isMobile, isSidebarOpen };
  },
};
</script>

<style>
#homePage {
  margin: 1% 3%;
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: center;
}
</style>
