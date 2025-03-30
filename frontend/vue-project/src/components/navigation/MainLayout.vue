<template>
  <div class="main-layout">
    <template v-if="!isMobile">
      <TopRow @toggle-menu="isSidebarOpen = !isSidebarOpen" />
      <PagesRow />
      <CategoriesRow />
    </template>
    <HamburgerMenu v-if="isMobile" :isOpen="isSidebarOpen" @close-menu="isSidebarOpen = false" />

    <main>
      <slot></slot> <!-- This will render the page content -->
    </main>

    <FooterPage />
    <CookiesConsent />

    <Modal :isOpen="showTrackOrderModal" @close="showTrackOrderModal = false">
      <TrackOrderModal @close="showTrackOrderModal = false" />
    </Modal>

    <Modal :isOpen="showRequestMOQModal" @close="showRequestMOQModal = false">
      <RequestMOQModal @close="showRequestMOQModal = false" />
    </Modal>

    <Modal :isOpen="showLoginModal" @close="showLoginModal = false">
      <LoginModal @close="showLoginModal = false" />
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, provide } from "vue";
import TopRow from "@/components/navigation/TopRow.vue";
import PagesRow from "@/components/navigation/PagesRow.vue";
import CategoriesRow from "@/components/navigation/CategoriesRow.vue";
import HamburgerMenu from "@/components/navigation/HamburgerMenu.vue";
import FooterPage from "@/components/footer/FooterPage.vue";
import CookiesConsent from "@/views/CookiesConsent.vue";
import TrackOrderModal from '@/components/auth/TrackOrder.vue';
import RequestMOQModal from '@/components/auth/RequestMOQ.vue';
import LoginModal from '@/components/auth/LoginModal.vue';
import Modal from '@/components/auth/Modal.vue';

export default {
  components: {
    TopRow,
    PagesRow,
    CategoriesRow,
    HamburgerMenu,
    FooterPage,
    CookiesConsent,
    TrackOrderModal,
    RequestMOQModal,
    LoginModal,
    Modal,
  },
  setup() {
    const isMobile = ref(window.innerWidth <= 768);
    const isSidebarOpen = ref(false);
    const showTrackOrderModal = ref(false);
    const showRequestMOQModal = ref(false);
    const showLoginModal = ref(false);
    const showRegisterModal = ref(false);

    const updateScreenSize = () => {
      isMobile.value = window.innerWidth <= 768;
    };

    const openTrackOrderModal = () => {
      showTrackOrderModal.value = true;
    };

    const openRequestMOQModal = () => {
      showRequestMOQModal.value = true;
    };

    const openLoginModal = () => {
      showLoginModal.value = true;
    };

    const closeModals = () => {
      showTrackOrderModal.value = false;
      showRequestMOQModal.value = false;
      showLoginModal.value = false;
      showRegisterModal.value = false;
    };

    // Provide the modal control functions to child components
    provide('openTrackOrderModal', openTrackOrderModal);
    provide('openRequestMOQModal', openRequestMOQModal);
    provide('openLoginModal', openLoginModal);
    provide('closeModals', closeModals);

    onMounted(() => {
      window.addEventListener("resize", updateScreenSize);
    });

    onUnmounted(() => {
      window.removeEventListener("resize", updateScreenSize);
    });

    return {
      isMobile,
      isSidebarOpen,
      showTrackOrderModal,
      showRequestMOQModal,
      showLoginModal,
      showRegisterModal,
    };
  },
};
</script>

<style>
.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
main {
  flex: 1;
  margin: 1% 3%;
}
</style>
