<template>
  <MainLayout>
    <div class="container">
      <h1 class="page-title">Privacy Policy</h1>
      <p class="last-updated">Last Updated: April 1, 2025</p>

      <section class="policy-section">
        <h2>1. Introduction</h2>
        <p>
          Welcome to Mustardecommerce ("we," "us," or "our"). We are committed to protecting your privacy and ensuring that your personal information is handled in a safe and responsible manner. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website, <a href="https://mustardecommerce.com">mustardecommerce.com</a>, or use our services.
        </p>
      </section>

      <section class="policy-section">
        <h2>2. Information We Collect</h2>
        <p>We may collect the following types of information:</p>
        <ul>
          <li><strong>Personal Information:</strong> Name, email address, phone number, shipping address, billing information, and payment details when you create an account, place an order, or contact us.</li>
          <li><strong>Usage Data:</strong> Information about how you interact with our website, such as your IP address, browser type, pages visited, and time spent on the site.</li>
          <li><strong>Cookies and Tracking Data:</strong> We use cookies and similar technologies to track your activity on our site. See our <router-link to="/cookie-policy">Cookie Policy</router-link> for more details.</li>
        </ul>
      </section>

      <section class="policy-section">
        <h2>3. How We Use Your Information</h2>
        <p>We use your information to:</p>
        <ul>
          <li>Process and fulfill your orders, including shipping and payment processing.</li>
          <li>Communicate with you about your account, orders, or customer service inquiries.</li>
          <li>Improve our website, products, and services based on usage data.</li>
          <li>Send you promotional emails or newsletters (you can opt out at any time).</li>
          <li>Comply with legal obligations and protect against fraudulent activities.</li>
        </ul>
      </section>

      <section class="policy-section">
        <h2>4. Sharing Your Information</h2>
        <p>We may share your information with:</p>
        <ul>
          <li><strong>Service Providers:</strong> Third-party vendors who help us with payment processing, shipping, email marketing, and website analytics (e.g., Stripe, Google Analytics).</li>
          <li><strong>Legal Authorities:</strong> If required by law or to protect our rights, we may disclose your information to law enforcement or regulatory bodies.</li>
        </ul>
        <p>We do not sell your personal information to third parties.</p>
      </section>

      <section class="policy-section">
        <h2>5. Your Rights</h2>
        <p>You have the right to:</p>
        <ul>
          <li>Access, update, or delete your personal information by contacting us.</li>
          <li>Opt out of marketing communications.</li>
          <li>Request a copy of the data we have collected about you.</li>
        </ul>
        <p>To exercise these rights, please contact us at <a href="mailto:privacy@mustardecommerce.com">privacy@mustardecommerce.com</a>.</p>
      </section>

      <section class="policy-section">
        <h2>6. Data Security</h2>
        <p>We implement industry-standard security measures to protect your information, including encryption and secure servers. However, no method of transmission over the internet is 100% secure, and we cannot guarantee absolute security.</p>
      </section>

      <section class="policy-section">
        <h2>7. Changes to This Privacy Policy</h2>
        <p>We may update this Privacy Policy from time to time. Any changes will be posted on this page with an updated "Last Updated" date. We encourage you to review this policy periodically.</p>
      </section>

      <section class="policy-section">
        <h2>8. Contact Us</h2>
        <p>If you have any questions about this Privacy Policy, please contact us:</p>
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
  name: 'PrivacyPolicy',
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
  color: #333;
}

.page-title {
  color: #f58930;
}

.last-updated {
  font-size: 0.9rem;
  color: #777;
  margin-bottom: 2rem;
}

.policy-section {
  margin-bottom: 2rem;
}

.policy-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
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
  color: #f77847;
  text-decoration: none;
}

.policy-section a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .policy-section h2 {
    font-size: 1.25rem;
  }

  .policy-section p,
  .policy-section li {
    font-size: 0.9rem;
  }
}
</style>
