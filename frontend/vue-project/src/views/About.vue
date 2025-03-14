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

      <section class="team-section">
        <h2 class="section-title">Meet Our Team</h2>
        <div class="team-grid">
          <div v-for="member in teamMembers" :key="member.id" class="team-card">
            <img :src="member.photo" :alt="member.name" class="team-photo" />
            <h3 class="about-p">{{ member.name }}</h3>
            <p class="about-p">{{ member.role }}</p>
          </div>
        </div>
      </section>

      <section class="testimonials-section">
        <h2 class="section-title">What Our Customers Say</h2>
        <div class="testimonial-carousel-container" @mouseenter="pauseCarousel" @mouseleave="resumeCarousel" role="region"
  aria-label="Customer testimonials carousel">
          <div
            class="testimonial-carousel"
            :style="{ transform: `translateX(-${activeIndex * (100 / cardsInView)}%)`, '--cards-in-view': cardsInView, '--total-cards': testimonials.length }"
          >
            <div
              v-for="testimonial in testimonials"
              :key="testimonial.id"
              class="testimonial-card"
            >
              <img :src="testimonial.photo" alt="Testimonial Profile Image" class="customer-photo" />
              <p class="testimonial-text about-p">"{{ testimonial.feedback }}"</p>
              <h3 class="testimonial-name about-p">- {{ testimonial.name }}</h3>
            </div>
          </div>
        </div>

        <!-- Dots Navigation -->
        <div class="dots-container">
          <span
            v-for="(dot, index) in dotsCount"
            :key="index"
            class="dot"
            :class="{ active: index === activeIndex }"
            @click="goToSlide(index)"
            :aria-label="`Go to slide ${index + 1}`"
          ></span>
        </div>
      </section>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import MainLayout from "@/components/navigation/MainLayout.vue";
import placeholderImg from "@/assets/images/face.jpeg";

const testimonials = ref([
  { id: 1, name: "Sarah Johnson", feedback: "Amazing platform! The shopping experience was seamless.", photo: placeholderImg },
  { id: 2, name: "Michael Lee", feedback: "Top-notch customer service! I felt valued as a customer.", photo: placeholderImg },
  { id: 3, name: "Emily Davis", feedback: "Best quality products with fast delivery. Highly recommend!", photo: placeholderImg },
  { id: 4, name: "Daniel Carter", feedback: "Their commitment to sustainability is impressive.", photo: placeholderImg },
  { id: 5, name: "Sophia Martinez", feedback: "I love the curated product selection. Unique and high-quality!", photo: placeholderImg },
  { id: 6, name: "James Anderson", feedback: "Checkout was super easy, and the order arrived quickly!", photo: placeholderImg },
  { id: 7, name: "Olivia Brown", feedback: "Excellent shopping experience. Will definitely be back!", photo: placeholderImg },
  { id: 8, name: "William Thompson", feedback: "Great customer support. They truly care about their customers!", photo: placeholderImg },
  { id: 9, name: "Jessica Taylor", feedback: "The variety of products is incredible. Found exactly what I needed!", photo: placeholderImg },
  { id: 10, name: "Kevin White", feedback: "Fast shipping and excellent packaging. Highly satisfied!", photo: placeholderImg },
  { id: 11, name: "Ava Patel", feedback: "Their eco-friendly practices align with my values. Love shopping here!", photo: placeholderImg },
  { id: 12, name: "Ethan Hall", feedback: "The website is user-friendly and easy to navigate. Great experience!", photo: placeholderImg },
]);

const teamMembers = ref([
  { id: 1, name: "John Doe", role: "CEO", photo: placeholderImg },
  { id: 2, name: "Jane Smith", role: "CTO", photo: placeholderImg },
  { id: 3, name: "David Wilson", role: "Engineering Lead", photo: placeholderImg },
  { id: 4, name: "Mutheu J", role: "Head of Marketing", photo: placeholderImg },
  { id: 5, name: "Contantinos Alava", role: "Photographer", photo: placeholderImg },
]);

const cardsInView = ref(4); // Default number of cards visible
const activeIndex = ref(0);
let interval = null;

const dotsCount = computed(() => Math.ceil(testimonials.value.length / cardsInView.value));

// Update cardsInView based on screen size
const updateCardsInView = () => {
  if (window.innerWidth <= 480) cardsInView.value = 1;
  else if (window.innerWidth <= 768) cardsInView.value = 2;
  else if (window.innerWidth <= 1024) cardsInView.value = 3;
  else cardsInView.value = 4;
};

// Auto-slide function
const startCarousel = () => {
  interval = setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % dotsCount.value;
  }, 7000); // Slide every 3 seconds
};

// Go to a specific slide
const goToSlide = (index) => {
  activeIndex.value = index;
  resetTimer();
};

// Reset timer on interaction
const resetTimer = () => {
  clearInterval(interval);
  startCarousel();
};

// Pause and resume carousel on hover
const pauseCarousel = () => clearInterval(interval);
const resumeCarousel = () => startCarousel();

onMounted(() => {
  updateCardsInView();
  window.addEventListener("resize", updateCardsInView);
  startCarousel();
});

onUnmounted(() => {
  window.removeEventListener("resize", updateCardsInView);
  clearInterval(interval);
});
</script>

<style scoped>
.about-h2 {
  font-size: 1.2rem;
}

.about-p {
  font-size: 1rem;
}

.about-container {
  max-width: 1200px;
  margin: auto;
  padding: 2rem;
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

.explore-section,
.team-section,
.testimonials-section {
  margin: 3rem 0;
}

.explore-section {
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

/* Meet Our Team Section */
.team-section {
  text-align: center;
  margin: 4rem 0;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  justify-content: center;
  margin-top: 2rem;
}

.team-card {
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.team-photo {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 1rem;
  border: 3px solid #c2c2c2;
}

.customer-photo {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 1rem;
  border: 3px solid #c2c2c2;
}

.team-card h3 {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0.5rem 0;
}

.team-card p {
  font-size: 1rem;
}

/* Testimonials Section */
.testimonials-section {
  text-align: center;
  margin: 4rem 0;
  padding: 3rem 0;
  border-radius: 12px;
}

.section-title {
  text-align: center;
  font-size: 1.4rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 2rem;
}

.testimonial-carousel-container {
  overflow: hidden;
  width: 100%;
  margin: auto;
  position: relative;
}

.testimonial-carousel {
  display: flex;
  width: calc(100% * var(--total-cards) / var(--cards-in-view, 4));
  transition: transform 0.5s ease-in-out;
  width: 100%;
  gap: 20px;
}

.testimonial-card {
  flex: 0 0 calc((100% / var(--cards-in-view, 4)) - 20px); /* Dynamic width with fallback */
  margin: 10px;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease-in-out;
  box-sizing: border-box;
}

.testimonial-card:hover {
  transform: scale(1.05);
}

.testimonial-text {
  font-size: 1rem;
  font-style: italic;
  margin-bottom: 1rem;
}

.testimonial-name {
  font-size: 1rem;
  font-weight: bold;
}

/* Dots Navigation */
.dots-container {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.dot {
  width: 10px;
  height: 10px;
  margin: 0 5px;
  border-radius: 50%;
  background: #ddd;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
}

.dot.active {
  background: #ff6600;
  transform: scale(1.2);
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
