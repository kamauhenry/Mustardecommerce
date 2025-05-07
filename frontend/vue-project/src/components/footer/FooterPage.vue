<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="social-media">
        <h3>Connect with us</h3>
        <div class="icons">
          <a href="https://www.instagram.com/mustard_imports?igsh=d2hqa3FhendhbHA1" title="Instagram" aria-label="Follow us on Instagram">
            <i class="fa-brands fa-instagram"></i>
          </a>
          <a href="https://www.tiktok.com/@mustard_imports?_t=ZM-8vbZdUKSfIc&_r=1" title="TikTok" aria-label="Follow us on TikTok">
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
        </ul>
      </div>

      <div class="contact-info">
        <h3>Contact Us</h3>
        <p>Location: XYZ</p>
        <p>Email: <a href="mailto:mustardimports@email.com" aria-label="Email Mustard Imports">mustardimports@email.com</a></p>
        <p>Telephone: <a href="tel:+254724028971" aria-label="Call Mustard Imports">+254724028971</a></p>
        <router-link to="/faq" class="faq-link footer-router-link" aria-label="View Frequently Asked Questions">Frequently Asked Questions</router-link>
      </div>
    </div>

    <div class="copyright">
      Mustard Imports © {{ currentYear }}
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  data() {
    return {
      currentYear: new Date().getFullYear(),
    };
  },
};
</script>

<style scoped>
.footer {
  width: 100%;
  background-color: #1e3a8a; /* Dark blue background */
  color: #ffffff;
  padding: 2rem 0;
  font-family: 'Arial', sans-serif;
  position: relative;
}

.footer-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  align-items: flex-start;
}

.social-media,
.quick-links,
.contact-info {
  display: flex;
  flex-direction: column;
  min-width: 200px;
  text-align: left;
}

.social-media {
  justify-content: flex-start;
}

h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #f0f0f0; /* Light gray for headings to soften contrast */
}

.icons {
  display: flex;
  gap: 1.5rem;
}

.icons a {
  color: #ffffff; /* Fixed typo: removed invalid 'Membrane' */
  font-size: 1.75rem;
  transition: transform 0.3s ease, color 0.3s ease;
}

.icons a:hover {
  color: #f28c38; /* Mustard orange for hover to match homepage */
  transform: scale(1.2);
}

.quick-links ul {
  list-style: none;
  padding: 0;
}

.quick-links li {
  margin-bottom: 0.5rem;
}

.footer-router-link,
.contact-info a {
  color: #d0d0d0; /* Light gray for links */
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.footer-router-link:hover,
.contact-info a:hover {
  color: #f28c38; /* Mustard orange for hover */
  text-decoration: underline;
}

.contact-info p {
  margin: 0.5rem 0;
  font-size: 1rem;
}

.copyright {
  margin-top: 2rem;
  font-size: 0.875rem;
  text-align: center;
  padding: 1rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.2); /* Slightly lighter border for contrast */
}

/* Responsive Design */

/* Large screens (above 1024px) */
@media (max-width: 1024px) {
  .footer-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }

  .contact-info {
    grid-column: span 2; /* Contact info takes full width */
    text-align: center;
  }

  .social-media,
  .quick-links {
    border-right: none;
  }
}

/* Tablets (768px - 1024px) */
@media (max-width: 768px) {
  .footer-container {
    grid-template-columns: 1fr;
    gap: 1rem;
    text-align: center;
  }

  .social-media,
  .quick-links,
  .contact-info {
    align-items: center;
    border-right: none;
  }

  .icons {
    justify-content: center;
  }

  h3 {
    font-size: 1.125rem;
  }

  .footer-router-link,
  .contact-info a {
    font-size: 0.9375rem;
  }
}

/* Mobile phones (below 576px) */
@media (max-width: 576px) {
  .footer {
    padding: 1.5rem 0;
  }

  .footer-container {
    padding: 0 1rem;
  }

  h3 {
    font-size: 1rem;
  }

  .icons a {
    font-size: 1.5rem;
  }

  .footer-router-link,
  .contact-info a {
    font-size: 0.875rem;
  }

  .contact-info p {
    font-size: 0.875rem;
  }

  .copyright {
    font-size: 0.75rem;
  }
}

/* Accessibility */
a:focus,
.footer-router-link:focus {
  outline: 2px solid #f28c38; /* Mustard orange for focus to match hover */
  outline-offset: 2px;
}
</style>