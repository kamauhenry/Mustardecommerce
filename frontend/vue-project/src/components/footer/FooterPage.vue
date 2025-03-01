<template>
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
          <li><router-link to="/privacy" class="footer-router-link">Privacy Policy</router-link></li>
          <li><router-link to="/cookies" class="footer-router-link">Cookie Policy</router-link></li>
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
</template>

<script setup>
import { ref } from 'vue';

const currentYear = ref(new Date().getFullYear());
</script>

<style scoped>
@import "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css";

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
  align-items:start;
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
  justify-content: flex-start;
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

/* Responsive Design */
@media (max-width: 768px) {
  .footer-container {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 1rem;
  }

  .social-media,
  .quick-links,
  .contact-info {
    border-right: none;
    text-align: center;
  }
}
</style>
