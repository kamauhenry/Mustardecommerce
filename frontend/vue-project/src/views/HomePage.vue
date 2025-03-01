<template>
  <div class="home-page-container">
    <template v-if="!isMobile">
      <TopRow @toggle-menu="isSidebarOpen = !isSidebarOpen" />
      <PagesRow />
      <CategoriesRow />
    </template>
    <HamburgerMenu v-if="isMobile" :isOpen="isSidebarOpen" @close-menu="isSidebarOpen = false" />
    <div class="handsome">
      <p>I am very handsome</p>
    </div>
    <FooterPage></FooterPage>
    <CookiesConsent />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import TopRow from "../components/navigation/TopRow.vue";
import PagesRow from "../components/navigation/PagesRow.vue";
import CategoriesRow from "../components/navigation/CategoriesRow.vue";
import HamburgerMenu from "../components/navigation/HamburgerMenu.vue";
import FooterPage from "../components/footer/FooterPage.vue";
import CookiesConsent from "../views/CookiesConsent.vue";

export default {
  components: {
    TopRow,
    PagesRow,
    CategoriesRow,
    HamburgerMenu,
    FooterPage,
    CookiesConsent,
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
.handsome {
  flex: 1;
  overflow-y: auto;
  height: 50rem;
}
</style>
