<template>
  <MainLayout>
    <div class="container">
      <h1 class="page-title">Cookie Policy</h1>
      <p class="last-updated">Last Updated: April 1, 2025</p>

      <section class="policy-section">
        <h2>1. Introduction</h2>
        <p>
          This Cookie Policy explains how Mustardecommerce ("we," "us," or "our") uses cookies and similar technologies on our website, <a href="https://mustardecommerce.com">mustardecommerce.com</a>. By using our website, you consent to the use of cookies as described in this policy.
        </p>
      </section>

      <section class="policy-section">
        <h2>2. What Are Cookies?</h2>
        <p>
          Cookies are small text files that are stored on your device (computer, tablet, or mobile) when you visit a website. They help us enhance your user experience, understand how you use our site, and provide personalized content.
        </p>
      </section>

      <section class="policy-section">
        <h2>3. Types of Cookies We Use</h2>
        <p>We use the following types of cookies:</p>
        <ul>
          <li><strong>Essential Cookies:</strong> These cookies are necessary for the website to function properly, such as maintaining your session, enabling secure login, and processing payments.</li>
          <li><strong>Performance Cookies:</strong> These cookies collect information about how you use our website (e.g., pages visited, time spent). We use this data to improve our site’s performance (e.g., Google Analytics).</li>
          <li><strong>Functionality Cookies:</strong> These cookies allow us to remember your preferences, such as language settings or items in your cart.</li>
          <li><strong>Advertising Cookies:</strong> These cookies are used to deliver personalized ads based on your browsing behavior. We may share this data with third-party advertising partners.</li>
        </ul>
      </section>

      <section class="policy-section">
        <h2>4. How We Use Cookies</h2>
        <p>We use cookies to:</p>
        <ul>
          <li>Ensure the website functions correctly and securely.</li>
          <li>Analyze website traffic and user behavior to improve our services.</li>
          <li>Remember your preferences and provide a personalized experience.</li>
          <li>Deliver relevant advertisements and measure their effectiveness.</li>
        </ul>
      </section>

      <section class="policy-section">
        <h2>5. Managing Cookies</h2>
        <p>
          You can manage or disable cookies through your browser settings. However, disabling essential cookies may affect the functionality of our website. Here’s how to manage cookies in popular browsers:
        </p>
        <ul>
          <li><a href="https://support.google.com/chrome/answer/95647" target="_blank">Google Chrome</a></li>
          <li><a href="https://support.mozilla.org/en-US/kb/enable-and-disable-cookies-website-preferences" target="_blank">Mozilla Firefox</a></li>
          <li><a href="https://support.apple.com/en-us/HT201265" target="_blank">Safari</a></li>
          <li><a href="https://support.microsoft.com/en-us/microsoft-edge/manage-cookies-in-microsoft-edge-view-allow-block-delete-and-use-168dab11-0753-043d-7c16-ede5947fc64d" target="_blank">Microsoft Edge</a></li>
        </ul>
        <p>
          Additionally, you can opt out of personalized ads by visiting <a href="https://www.youronlinechoices.com/" target="_blank">Your Online Choices</a> or <a href="https://optout.aboutads.info/" target="_blank">About Ads</a>.
        </p>
      </section>

      <section class="policy-section">
        <h2>6. Third-Party Cookies</h2>
        <p>
          We use third-party services like Google Analytics and advertising networks that may place cookies on your device. These third parties have their own privacy policies, and we recommend reviewing them for more information.
        </p>
      </section>

      <section class="policy-section">
        <h2>7. Changes to This Cookie Policy</h2>
        <p>
          We may update this Cookie Policy from time to time. Any changes will be posted on this page with an updated "Last Updated" date. We encourage you to review this policy periodically.
        </p>
      </section>

      <section class="policy-section">
        <h2>8. Contact Us</h2>
        <p>If you have any questions about this Cookie Policy, please contact us:</p>
        <ul>
          <li>Email: <a href="mailto:privacy@mustardecommerce.com">privacy@mustardecommerce.com</a></li>
          <li>Phone: +254 123 456 789</li>
          <li>Address: Mustardecommerce, 123 Commerce Street, Nairobi, Kenya</li>
        </ul>
      </section>
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from '@/components/navigation/MainLayout.vue';

export default {
  name: 'CookiePolicy',
  components: {
    MainLayout,
  },
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Roboto', sans-serif;
}

.page-title {
  color: #f58930;
}

.last-updated {
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.policy-section {
  margin-bottom: 2rem;
}

.policy-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #f58930;
}

.policy-section p {
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.policy-section ul {
  list-style-type: disc;
  padding-left: 2rem;
  margin-bottom: 1rem;
}

.policy-section li {
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.policy-section a {
  color: #f58930;
  text-decoration: none;
}

.policy-section a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  /* .page-title {
    font-size: 2rem;
  } */

  .policy-section h2 {
    font-size: 1.25rem;
  }

  .policy-section p,
  .policy-section li {
    font-size: 0.9rem;
  }
}
</style>
