<template>
  <div class="main-layout">
    <!-- Header/Nav -->
    <template v-if="!isMobile">
      <TopRow @toggle-menu="isSidebarOpen = !isSidebarOpen" />
      <PagesRow />
      <CategoriesRow />
    </template>
    <HamburgerMenu v-if="isMobile" :isOpen="isSidebarOpen" @close-menu="isSidebarOpen = false" />

    <!-- Main Content -->
    <main>
      <slot></slot> <!-- This will render the page content -->
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-container">
        <div class="social-media">
          <h3>Connect with us on social media</h3>
          <div class="icons">
            <i class="fab fa-instagram"></i>
            <i class="fab fa-facebook"></i>
            <i class="fab fa-tiktok"></i>
            <i class="fab fa-twitter"></i>
          </div>
        </div>

        <div class="quick-links">
          <h3>Quick Links</h3>
          <ul class="footer-links">
            <li><router-link to="/about" class="footer-router-link">About Us</router-link></li>
            <li><router-link to="/contact" class="footer-router-link">Contact Us</router-link></li>
            <li><router-link to="/terms" class="footer-router-link">Terms of Service</router-link></li>
            <li><router-link to="/privacy-policy" class="footer-router-link">Privacy Policy</router-link></li>
            <li><router-link to="/cookie-policy" class="footer-router-link">Cookie Policy</router-link></li>
            <li><a href="#" @click.prevent="manageCookies" class="footer-router-link">Manage Cookies</a></li>
          </ul>
        </div>

        <div class="contact-info">
          <h3>Contact Us</h3>
          <p>Location: XYZ</p>
          <p>Email: <a href="mailto:email@email.com">email@email.com</a></p>
          <p>Telephone: <a href="tel:+2541233455677889">+2541233455677889</a></p>
          <router-link to="/faq" class="faq-link footer-router-link">Frequently Asked Questions</router-link>
        </div>
      </div>

      <div class="copyright">
        Mustard Imports © {{ currentYear }}
      </div>
    </footer>

    <!-- Modals -->
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
import { ref, onMounted, onUnmounted, provide, inject } from 'vue';
import TopRow from '@/components/navigation/TopRow.vue';
import PagesRow from '@/components/navigation/PagesRow.vue';
import CategoriesRow from '@/components/navigation/CategoriesRow.vue';
import HamburgerMenu from '@/components/navigation/HamburgerMenu.vue';
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
    const currentYear = ref(new Date().getFullYear());
    let toastId = null; // Store the toast ID to dismiss it later

    // Inject the $toast instance
    const $toast = inject('$toast');
    if (!$toast) {
      console.error('Toast instance not found! Ensure vue-toast-notification is properly set up in main.js.');
    }

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

    const showCookieConsent = () => {
      // Check if the user has already made a choice
      const consent = localStorage.getItem('cookieConsent');
      if (consent) {
        console.log('Cookie consent already given:', consent);
        return; // If consent exists, don't show the popup
      }

      console.log('Showing cookie consent popup...');

      // Show the cookie consent popup using vue-toast-notification
      toastId = $toast.open({
        message: `
          <div class="cookie-consent">
            <p>We use cookies to enhance your experience on our website. By continuing to use our site, you agree to our use of cookies as described in our <a href="/cookie-policy" target="_blank">Cookie Policy</a>.</p>
            <div class="cookie-buttons">
              <button id="accept-cookies" tabindex="0" aria-label="Accept cookies">Accept</button>
              <button id="decline-cookies" tabindex="0" aria-label="Decline cookies">Decline</button>
            </div>
          </div>
        `,
        type: 'info', // Use 'info' type for a neutral style
        position: 'bottom-center', // Position at the bottom center
        duration: 0, // Keep the popup open until the user makes a choice (0 = infinite)
        dismissible: false, // Prevent closing by clicking outside
        onOpen: () => {
          console.log('Toast opened, adding event listeners...');
          // Add event listeners to the buttons after the toast is rendered
          const acceptButton = document.getElementById('accept-cookies');
          const declineButton = document.getElementById('decline-cookies');

          if (acceptButton) {
            acceptButton.addEventListener('click', () => {
              console.log('Accept button clicked');
              localStorage.setItem('cookieConsent', 'accepted');
              $toast.dismiss(toastId); // Close the popup
              $toast.success('Cookies accepted!', { duration: 3000 });
              window.location.reload(); // Reload to apply changes (e.g., load GA)
            });
          } else {
            console.error('Accept button not found in toast');
          }

          if (declineButton) {
            declineButton.addEventListener('click', () => {
              console.log('Decline button clicked');
              localStorage.setItem('cookieConsent', 'declined');
              $toast.dismiss(toastId); // Close the popup
              $toast.info('Cookies declined. Some features may be limited.', { duration: 3000 });
              window.location.reload(); // Reload to apply changes
            });
          } else {
            console.error('Decline button not found in toast');
          }
        },
      });
    };

    const manageCookies = () => {
      console.log('Managing cookies...');
      // Clear the existing consent and show the popup again
      localStorage.removeItem('cookieConsent');
      showCookieConsent();
    };

    // Provide the modal control functions to child components
    provide('openTrackOrderModal', openTrackOrderModal);
    provide('openRequestMOQModal', openRequestMOQModal);
    provide('openLoginModal', openLoginModal);
    provide('closeModals', closeModals);

    onMounted(() => {
      console.log('MainLayout mounted, setting up resize listener and showing cookie consent...');
      window.addEventListener('resize', updateScreenSize);
      showCookieConsent();
    });

    onUnmounted(() => {
      console.log('MainLayout unmounted, removing resize listener...');
      window.removeEventListener('resize', updateScreenSize);
    });

    return {
      isMobile,
      isSidebarOpen,
      showTrackOrderModal,
      showRequestMOQModal,
      showLoginModal,
      showRegisterModal,
      currentYear,
      manageCookies,
    };
  },
};
</script>

<style scoped>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css";

.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
  margin: 1% 3%;
}

/* Footer Styles */
.footer {
  width: 100%;
  background-color: var(--background-color-five);
  color: white;
  padding: 1.5rem 0;
  text-align: center;
  position: relative;
}

.footer-container {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  align-items: start;
  padding: 0 2rem;
  max-width: 90rem;
  margin: 0 auto;
  gap: 1rem;
}

/* Footer Sections */
.social-media,
.quick-links,
.contact-info {
  padding: 1rem;
  min-width: 12.5rem;
  text-align: left;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%;
}

.social-media {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* Add vertical dividers */
.social-media,
.quick-links {
  border-right: 1px solid rgba(255, 255, 255, 0.5);
  padding-right: 1rem;
}

/* Ensure the last div (contact-info) doesn't have a border */
.contact-info {
  border-right: none;
}

/* Typography & Icons */
h3 {
  font-size: 1.125rem;
  margin-bottom: 0.625rem;
}

.icons {
  font-size: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.quick-links ul {
  list-style: none;
  padding: 0;
}

.quick-links li {
  margin-bottom: 0.3125rem;
}

.footer-router-link,
.contact-info a {
  color: white;
  text-decoration: none;
}

.footer-router-link:hover {
  text-decoration: underline;
}

/* Copyright */
.copyright {
  margin-top: 1rem;
  font-size: 0.875rem;
}

/* Style the cookie consent popup */
.cookie-consent {
  text-align: center;
  padding: 1rem;
}

.cookie-consent p {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.cookie-consent a {
  color: #007bff;
  text-decoration: underline;
}

.cookie-consent a:hover {
  color: #0056b3;
}

.cookie-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.cookie-buttons button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

#accept-cookies {
  background-color: #28a745;
  color: #fff;
}

#accept-cookies:hover {
  background-color: #218838;
}

#decline-cookies {
  background-color: #dc3545;
  color: #fff;
}

#decline-cookies:hover {
  background-color: #c82333;
}

/* Responsive Design */
@media (max-width: 540px) {
  .footer-container {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 1rem;
  }

  .social-media,
  .quick-links,
  .contact-info {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    flex-direction: column;
    border-right: none;
  }
}
</style>
