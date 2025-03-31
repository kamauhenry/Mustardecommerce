<script>
import { useEcommerceStore } from '@/stores/ecommerce';
  export default {
    name: "app",
    data(){
      return{

        cart:{
          items:[]
        }
      }
    },
    setup(){
      const store = useEcommerceStore
      return {store};
    },
    created() {
    // If authenticated, fetch cart data
    if (this.store.isAuthenticated) {
      this.store.fetchCartData();
    }
  },

    computed:{
      cartTotalLength() {

      const items = this.store.cart.items || [];

      //sum up quantities
      return items.reduce((total, item) => total + (item.quantity || 0), 0);
    }
    }
  };
</script>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
[data-theme="dark"] {
  --top-row-bg: var(--vt-c-black-mute);
  --categories-bg: var(--vt-c-black-mute);
  --main-body-bg: var(--vt-c-black-soft);
  --sidebar-text-color: var(--vt-c-white); /* #ffffff white */
  --text-color-eight: var(--text-color-one); /* #db4619 orange */
  --text-color-nine: var(--vt-c-white); /* #ffffff white */
  --text-color-ten: var(--vt-c-white); /* #ffffff white */
  --text-color-eleven: var(--vt-c-white); /* #ffffff white */
  --text-color-twelve: var(--vt-c-grey); /* grey */
  --text-color-thirteen: var(--text-color-category-hover);
  --text-color-fourteen: var(--vt-c-white);
  --text-color-page-title: var(--text-color-one);
  --bg-color-about-section: var(--bg-color-about-section-2);
  --bg-color-about-section-card: var(--vt-c-black-mute);
  --bg-color-category-card: var(--vt-c-black-soft);
  --faq-bg: var(--vt-c-black-soft);
  --faq-question-bg: var(--vt-c-black);
  --faq-answer-bg: var(--vt-c-black-mute);
  --campaigns-bg: var(--vt-c-white-soft);
  --tabs-bg: #3a3a3a;
  --breadcrumb-bg: #bdbdbd;
  --sidebar-hover: #363636;
}

[data-theme="light"] {
  --top-row-bg: var(--vt-c-white);
  --categories-bg: var(--background-color-three);
  --main-body-bg: var(--vt-c-white);
  --sidebar-text-color: var(--vt-c-black); /* #ffffff white */
  --text-color-eight: var(--text-color-two); /* #838636 darkish green */
  --text-color-nine: var(--text-color-two); /* #838636 darkish green */
  --text-color-ten: var(--vt-c-black-soft); /* #3d3d3d dark grey */
  --text-color-eleven: #787a30; /* #838636 darkish green */
  --text-color-twelve: var(--text-color-four); /* darker green */
  --text-color-thirteen: var(--text-color-one);
  --text-color-fourteen: var(--vt-c-black-soft);
  --text-color-page-title: var(--text-color-two);
  --bg-color-about-section: var(--bg-color-about-section-1);
  --bg-color-about-section-card: var(--vt-c-white);
  --bg-color-category-card: var(); /* light grey */
  --faq-bg: var(--vt-c-white);
  --faq-question-bg: var(--background-color-three);
  --faq-answer-bg: var(--vt-c-white-soft);
  --campaigns-bg: var(--vt-c-black-soft);
  --tabs-bg: #e6e6e6;
  --breadcrumb-bg: #414141;
  --sidebar-hover: #dddddd;
}

.navbar, .categories, .product-campaigns, .product-searches {
  background-color: var(--categories-bg);
  transition: background-color 0.3s, color 0.3s;
}

.sidebar {
  background-color: var(--main-body-bg);
  transition: background-color 0.3s, color 0.3s;
}
@media (max-width: 768px) {
  .page-list a, .category-list a {
    color: var(--sidebar-text-color);
  }
}

.category-card, .popup-content, .user-info-section {
  background-color: var(--categories-bg);
}

.product-card, .user-info, .delivery-locations, .product-right, .sidebar {
  background-color: var(--bg-color-category-card);
}

.sidebar {
  border-right: 1px solid var(--tabs-bg);
}

.sidebar-nav li:hover {
  background: var(--sidebar-hover);
}

.category-p, .about-h2, .category-title, .search-results-h1, .popup-title, .user-name, .info-label, .product-title, .description h3, .reviews h3, .related-products h3, .cart-title {
  color: var(--text-color-thirteen);
}

.tabs, .locations-list li {
  border-bottom: 1px solid var(--tabs-bg);
}

.related-products {
  border-top: 1px solid var(--tabs-bg);
}

.tabs button, .tabs button.active {
  color: var(--campaigns-bg);
}

.tabs button.active::after {
  background-color: var(--campaigns-bg);
}

.see-more-link, .show-more {
  background-color: #f28c38;
}

.category-link, .about-p, .moq-info, .product-price, .product-name, .no-products, .loading, .no-products, .product-image, .location-name, .location-address, .map-loading, .set-default-label {
  color: var(--text-color-eleven);

}

.description ul, .description ul li, .description p, .description ul li strong, .quantity label, .attributes label, .shipping label, .promo-code label, .related-products p, .price, .profile-info p, .sidebar-nav li {
  color: var(--campaigns-bg);
}

.breadcrumb, .breadcrumb a, .breadcrumb span {
  color: var(--breadcrumb-bg);
}


.category-link:hover {
  color: var(--text-color-twelve);
}

.campaigns-title, .searches-title {
  color: var(--text-color-eleven);
}

.campaign-p, .search-p {
  color: var(--campaigns-bg);
  font-weight: 700;
}

.info-value, .location-details h3, .location-details p, .no-locations {
  color: var(--campaigns-bg);
}

.page-title {
  font-family:cursive;
  color: var(--text-color-page-title);
  font-size: 1.4rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 2rem;
  text-align: left;
}

.section-title {
  color: var(--text-color-page-title);
}

.about-text {
  background-image: var(--bg-color-about-section);
}

.team-card, .testimonial-card {
  background-color: var(--bg-color-about-section-card);
}

.faq-section {
  background-color: var(--faq-bg);
}

.faq-question {
  background-color: var(--faq-question-bg);
  color: var(--text-color-fourteen);
}

.faq-answer {
  background-color: var(--faq-answer-bg);
  color: var(--text-color-fourteen);
}

.faq-question:hover, .faq-question.active {
  background-color: var(--faq-question-bg);
}

#app {
  background-color: var(--main-body-bg);
  transition: background-color 0.3s, color 0.3s;
  display: flex;
  flex-direction: column;
}
</style>
