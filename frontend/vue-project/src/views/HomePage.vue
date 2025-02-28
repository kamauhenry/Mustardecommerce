<template>
  <div class="home-page-container">
    <template v-if="!isMobile">
      <TopRow @toggle-menu="isSidebarOpen = !isSidebarOpen" />
      <PagesRow />
      <CategoriesRow />
    </template>
    <HamburgerMenu v-if="isMobile" :isOpen="isSidebarOpen" @close-menu="isSidebarOpen = false" />
    <CookiesConsent />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import TopRow from "../components/navigation/TopRow.vue";
import PagesRow from "../components/navigation/PagesRow.vue";
import CategoriesRow from "../components/navigation/CategoriesRow.vue";
import HamburgerMenu from "../components/navigation/HamburgerMenu.vue";
import CookiesConsent from "../components/CookiesConsent.vue";

export default {
  components: {
    TopRow,
    PagesRow,
    CategoriesRow,
    HamburgerMenu,
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
