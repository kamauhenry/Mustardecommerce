<template>
  <div class="main-layout">
    <!-- Header/Nav -->
    <template v-if="!isMobile">
      <TopRow @toggle-menu="isSidebarOpen = !isSidebarOpen" />
      <PagesRow />
      <CategoriesRow v-if="!isExcludedRoute" />
    </template>
    <HamburgerMenu v-if="isMobile" />

    <!-- Main Content -->
    <main class="main-content">
      <slot></slot>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-container">
        <div class="social-media">
          <h3>Connect with us on social media</h3>
          <div class="icons">
            <a href="https://www.instagram.com/mustard_imports?igsh=d2hqa3FhendhbHA1" target="_blank" aria-label="Instagram">
              <i class="fab fa-instagram"></i>
            </a>
            <a href="https://www.facebook.com/mustardimports" target="_blank" aria-label="Facebook">
              <i class="fab fa-facebook"></i>
            </a>
            <a href="https://www.tiktok.com/@mustard_imports?_t=ZM-8vbZdUKSfIc&_r=1" target="_blank" aria-label="Follow us on TikTok">
              <i class="fa-brands fa-tiktok"></i>
            </a>

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
          <p>Location: Reli-Coop house 1st floor F71</p>
          <p>Email: <a href="mailto:mustardimports@gmail.com">mustardimports@gmail.com</a></p>
          <p>Telephone: <a href="tel:+254724028971">+254 724 028971</a></p>
          <router-link to="/faq" class="faq-link footer-router-link">Frequently Asked Questions</router-link>
        </div>
      </div>

      <div class="copyright">
        <p>
          Created by 
          Henry <a href="https://github.com/kamauhenry" target="_blank" rel="noopener" aria-label="Henry's GitHub"><i class="fab fa-github"></i></a> 
          and 
          Allan <a href="https://github.com/murungiallan" target="_blank" rel="noopener" aria-label="Allan's GitHub"><i class="fab fa-github"></i></a>
        </p>
        <p>Mustard Imports © {{ currentYear }}</p>
      </div>
    </footer>

    <!-- Cookie Consent Modal -->
    <Modal :isOpen="showCookieConsentModal" @close="declineCookies">
      <div class="cookie-consent">
        <h1 class="accept-cookie-h1">Accept Our Cookies</h1>
        <p>
          We use cookies to enhance your experience on our website. By continuing to use our site, you agree to our use of cookies as described in our <router-link to="/cookie-policy">Cookie Policy</router-link>.
        </p>
        <div class="cookie-buttons">
          <button id="accept-cookies" @click="acceptCookies">Accept</button>
          <button id="decline-cookies" @click="declineCookies">Decline</button>
        </div>
      </div>
    </Modal>

    <!-- Other Modals -->
    <Modal :isOpen="showTrackOrder ?? false" @close="showTrackOrder = false">
      <TrackOrder @close="showTrackOrder = false" />
    </Modal>

    <Modal :isOpen="showRequestMOQ ?? false" @close="showRequestMOQ = false">
      <RequestMOQ @close="showRequestMOQ = false" />
    </Modal>

    <Modal :isOpen="showLoginModal ?? false" @close="showLoginModal = false">
      <LoginModal @close="showLoginModal = false" />
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, provide } from 'vue';
import { useRoute } from 'vue-router';
import { toast } from 'vue3-toastify';
import TopRow from '@/components/navigation/TopRow.vue';
import PagesRow from '@/components/navigation/PagesRow.vue';
import CategoriesRow from '@/components/navigation/CategoriesRow.vue';
import HamburgerMenu from '@/components/navigation/HamburgerMenu.vue';
import Modal from '@/components/auth/Modal.vue';
import TrackOrder from '@/components/auth/TrackOrder.vue';
import RequestMOQ from '@/components/auth/RequestMOQ.vue';
import LoginModal from '@/components/auth/AuthModal.vue';

export default {
  name: 'MainLayout',
  components: {
    TopRow,
    PagesRow,
    CategoriesRow,
    HamburgerMenu,
    Modal,
    TrackOrder,
    RequestMOQ,
    LoginModal,
  },
  setup() {
    const isMobile = ref(window.innerWidth <= 500);
    const showTrackOrder = ref(false);
    const showRequestMOQ = ref(false);
    const showLoginModal = ref(false);
    const showCookieConsentModal = ref(false);
    const currentYear = ref(new Date().getFullYear());

    const route = useRoute();
    const excludedRoutes = ['/checkout', '/checkout/confirmation'];

    const isExcludedRoute = computed(() => {
      const currentPath = route.path;
      console.log('Current route.path:', currentPath);
      const isExcluded = excludedRoutes.some((excludedPath) => currentPath.startsWith(excludedPath));
      console.log('isExcludedRoute result:', isExcluded);
      return isExcluded;
    });

    const updateScreenSize = () => {
      isMobile.value = window.innerWidth <= 500;
    };

    const openTrackOrder = () => {
      showTrackOrder.value = true;
    };

    const openRequestMOQ = () => {
      showRequestMOQ.value = true;
    };

    const openLoginModal = () => {
      showLoginModal.value = true;
    };

    const closeModals = () => {
      showTrackOrder.value = false;
      showRequestMOQ.value = false;
      showLoginModal.value = false;
      showCookieConsentModal.value = false;
    };

    const acceptCookies = () => {
      console.log('Accept button clicked');
      localStorage.setItem('cookieConsent', 'accepted');
      showCookieConsentModal.value = false;
      toast.success('Cookies accepted!', { autoClose: 3000 });

    };

    const declineCookies = () => {
      console.log('Decline button clicked');
      localStorage.setItem('cookieConsent', 'declined');
      showCookieConsentModal.value = false;
      toast.info('Cookies declined.', { autoClose: 3000 });
    };

    const showCookieConsent = () => {
      try {
        const consent = localStorage.getItem('cookieConsent');
        if (consent) {
          console.log('Cookie consent already given:', consent);
          if (consent === 'accepted') {
            loadGoogleAnalytics();
          }
          return;
        }
        console.log('Showing cookie consent modal...');
        showCookieConsentModal.value = true;
      } catch (error) {
        console.error('Error in showCookieConsent:', error);
      }
    };

    const manageCookies = () => {
      console.log('Managing cookies...');
      localStorage.removeItem('cookieConsent');
      showCookieConsent();
    };

    const loadGoogleAnalytics = () => {
      if (localStorage.getItem('cookieConsent') === 'accepted') {
        console.log('Loading Google Analytics...');
        const script = document.createElement('script');
        script.async = true;
        script.src = 'https://www.googletagmanager.com/gtag/js?id=G-4HWLRPEN7Y';
        document.head.appendChild(script);

        window.dataLayer = window.dataLayer || [];
        function gtag() {
          window.dataLayer.push(arguments);
        }
        gtag('js', new Date());
        gtag('config', 'G-4HWLRPEN7Y');
      }
    };

    onMounted(() => {
      console.log('MainLayout mounted, setting up resize listener and showing cookie consent...');
      window.addEventListener('resize', updateScreenSize);
      showCookieConsent();
    });

    onUnmounted(() => {
      console.log('MainLayout unmounted, removing resize listener...');
      window.removeEventListener('resize', updateScreenSize);
    });

    provide('openTrackOrder', openTrackOrder);
    provide('openRequestMOQ', openRequestMOQ);
    provide('openLoginModal', openLoginModal);
    provide('closeModals', closeModals);

    return {
      isMobile,
      showTrackOrder,
      showRequestMOQ,
      showLoginModal,
      showCookieConsentModal,
      currentYear,
      manageCookies,
      isExcludedRoute,
      acceptCookies,
      declineCookies,
    };
  },
};
</script>

<style scoped>

.header, .navbar {
  position: relative;
  z-index: 2;
}
.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main.main-content {
  flex: 1;
  margin: 1% 3%;
}

/* Footer Styles */
.footer {
  width: 100%;
  background-color: #1E2A44; /* Dark blue to match homepage */
  color: #E6E6E6; /* Light gray for text */
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
  justify-content: space-between; /* Center icons vertically */
  align-items: center; /* Center icons horizontally */
}

/* Add vertical dividers */
.social-media,
.quick-links {
  border-right: 1px solid rgba(255, 255, 255, 0.3); /* Slightly transparent divider */
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
  color: #E6E6E6;
}

.icons {
  font-size: 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  flex-grow: 1; /* Allow icons to take available space for centering */
}

.icons a {
  color: #E6E6E6;
  text-decoration: none;
}

.icons a:hover {
  color: #F2C94C; /* Mustard yellow hover to match homepage */
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
  color: #E6E6E6;
  text-decoration: none;
}

.footer-router-link:hover,
.contact-info a:hover {
  color: #F2C94C; /* Mustard yellow hover */
}

/* Copyright */
.copyright {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #E6E6E6;
}

.copyright a:hover {
  color: #F2C94C; /* Mustard yellow hover to match theme */
}

.copyright .fab.fa-github {
  font-size: 1rem; /* Adjust icon size */
  vertical-align: middle;
  margin-left: 0.25rem;
}

/* Cookie Consent Modal */
.cookie-consent {
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  padding: 2rem;
  max-width: 500px;
  margin: 0 auto;
  text-align: justify;
  font-family: 'Inter', sans-serif;
  animation: slideIn 0.3s ease-out;
}

.accept-cookie-h1 {
  font-weight: 700;
  margin-bottom: 1rem;
}

.cookie-consent p {
  color: #333;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.cookie-consent a {
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.cookie-consent a:hover {
  text-decoration: underline;
}

.cookie-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.cookie-buttons button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

#accept-cookies {
  background-color: #28a745;
  color: white;
}

#accept-cookies:hover {
  background-color: #218838;
  transform: translateY(-2px);
}

#decline-cookies {
  background-color: #6c757d;
  color: white;
}

#decline-cookies:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
}

/* Animation for modal entrance */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 540px) {
  .cookie-consent {
    padding: 1.5rem;
    max-width: 90%;
  }

  .cookie-consent p {
    font-size: 0.9rem;
  }

  .cookie-buttons button {
    padding: 0.6rem 1.2rem;
    font-size: 0.9rem;
  }

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
    align-items: center; /* Center content horizontally on mobile */
    flex-direction: column;
    border-right: none;
  }

  .social-media {
    justify-content: center; /* Center icons vertically on mobile */
  }
}
</style>