<template>
  <MainLayout>
    <div class="about-container">
      <section class="hero">
        <div class="hero-content">
          <h1 class="page-title">About Mustard Imports</h1>
        </div>
      </section>

      <section class="about-content">
        <div class="content-wrapper">
          <div class="about-text">
            <h2 class="about-h2">Our Story</h2>
            <p class="about-p">
              At Mustard Imports, we believe in building trust through transparency. Our journey began with a passion for delivering high-quality products while ensuring ethical sourcing practices. We're committed to creating a positive impact on the environment and our community.
            </p>
          </div>
          <div class="about-text">
            <h2 class="about-h2">Our Mission</h2>
            <p class="about-p">
              We aim to redefine online shopping by offering curated products, seamless transactions, and an unmatched customer experience. Our mission is to be a leader in sustainable e-commerce practices.
            </p>
          </div>
        </div>

        <div class="content-wrapper">
          <div class="about-text">
            <h2 class="about-h2">Our Vision</h2>
            <p class="about-p">
              To be the most trusted and innovative e-commerce marketplace, creating connections that inspire and products that elevate lifestyles while promoting environmental responsibility.
            </p>
          </div>
          <div class="about-text">
            <h2 class="about-h2">Our Values</h2>
            <ul class="about-p">
              <li>Innovation - Always pushing boundaries.</li>
              <li>Customer-First - Every decision revolves around you.</li>
              <li>Sustainability - Ethical sourcing and environmental responsibility.</li>
              <li>Integrity - Transparent, trustworthy, and dedicated.</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="explore-section">
        <h2 class="page-title">More to Explore</h2>
        <div class="explore-grid">
          <router-link to="/" class="explore-item explore-item-1">
            <span>Latest Collections</span>
          </router-link>
          <router-link to="/orders" class="explore-item explore-item-2">
            <span>My Orders</span>
          </router-link>
          <router-link to="/moq-campaigns" class="explore-item explore-item-4">
            <span>MOQ Campaigns</span>
          </router-link>
          <router-link to="/contact" class="explore-item explore-item-3">
            <span>Contact Us</span>
          </router-link>
        </div>
      </section>
    </div>
  </MainLayout>
</template>

<script setup>
import MainLayout from "@/components/navigation/MainLayout.vue";
</script>

<style>
.about-h2 {
  font-size: 1.2rem;
  text-transform: uppercase;
}

.about-p,
.about-p li {
  font-size: 1rem;
}

.about-p li {
  list-style: none;
}

.about-container {
  max-width: 1200px;
  margin: auto;
  padding: 2rem;
  text-align: left;
}

.hero-content {
  text-align: center;
  margin-bottom: 2rem;
}

.about-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.content-wrapper {
  display: flex;
  justify-content: space-between;
  gap: 2rem;
}

.about-text {
  flex: 1;
  text-align: left;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.explore-section {
  margin: 3rem 0;
  text-align: center;
}

.explore-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.explore-item {
  height: 150px;
  border-radius: 20px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  color: #fff;
  text-decoration: none;
  background-size: cover;
  background-position: center;
  transition: transform 0.3s ease-in-out;
}

.explore-item span {
  margin-bottom: 1rem;
  font-size: 1rem;
  font-weight: bold;
  background-color: rgba(0, 0, 0, 0.534);
  padding: 5px 10px;
  border-radius: 10px;
}

.explore-item:hover {
  transform: scale(1.05);
}

.explore-item-1 {
  background-image: url("@/assets/images/babies.jpeg");
}

.explore-item-2 {
  background-image: url("@/assets/images/health.jpeg");
}

.explore-item-3 {
  background-image: url("@/assets/images/contact.jpeg");
}

.explore-item-4 {
  background-image: url("@/assets/images/ikea.jpeg");
}

/* Responsive Design */
@media (max-width: 1024px) {
  .explore-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .content-wrapper {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .explore-grid {
    grid-template-columns: 1fr;
  }
}
</style>