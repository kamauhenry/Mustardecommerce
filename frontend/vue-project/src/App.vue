<script>
import { useAuthStore } from '@/stores/modules/auth';
import { useCartStore } from '@/stores/modules/cart';
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
      const authStore = useAuthStore();
      const cartStore = useCartStore();
      return { authStore, cartStore };
    },
    created() {
    // If authenticated, fetch cart data
    if (this.authStore.isAuthenticated) {
      this.cartStore.fetchCart();
    }
  },

    computed:{
      cartTotalLength() {

      const items = this.cartStore.items || [];

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
  --tabs-bg: #303030;
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

.categories, .product-campaigns, .product-searches {
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

.category-card, .popup-content, .user-info-section, .skeleton-category, .order-item {
  background-color: var(--categories-bg);
}

.product-card, .user-info, .delivery-locations, .product-right, .sidebar, .navbar, .search-group, .search-input, .search-container, .order-item {
  background-color: var(--bg-color-category-card);
}

.quantity-controls, .quantity-button {
  background: var(--bg-color-category-card);
}

.search-group, .search-container {
  border: 1px solid var(--tabs-bg);
}

.search-input, .quantity-button, .quantity-controls span  {
  color: var(--campaigns-bg);
}

.sidebar {
  border-right: 1px solid var(--tabs-bg);
}

.sidebar-nav li:hover {
  background: var(--sidebar-hover);
}

.category-p, .about-h2, .category-title, .search-results-h1, .popup-title, .user-name, .info-label, .product-title, .description h3, .reviews h3, .related-products h3, .cart-title, .policy-section h2, .order-number, .order-section h2, .cart-summary h3 {
  color: var(--text-color-thirteen);
}

.tabs, .locations-list li, .status-tabs, .order-section h2, .cart-summary h3 {
  border-bottom: 1px solid var(--tabs-bg);
}

.cart-summary, .loading-state, .error-state, .auth-prompt, .empty-cart {
  border: 1px solid var(--tabs-bg);
}

.related-products {
  border-top: 1px solid var(--tabs-bg);
}

.summary-row.total{
  border-top: 1px dashed var(--tabs-bg);
}

.tabs button, .tabs button.active {
  color: var(--campaigns-bg);
}

.tabs button.active::after {
  background-color: var(--campaigns-bg);
}

.see-more-link, .show-more {
  background-color:#D4A017;
}

.category-link, .about-p, .moq-info, .product-price, .product-name, .no-products, .loading, .no-products, .product-image, .location-name, .location-address, .map-loading, .set-default-label {
  color: var(--text-color-eleven);

}

.description ul, .description ul li, .description p, .description ul li strong, .quantity label, .attributes label, .shipping label, .promo-code label, .related-products p, .price, .profile-info p, .sidebar-nav li, .policy-section p, .policy-section li, .filter-p, .filter-group, .order-placed, .order-items-count, .order-total, .summary-row {
  color: var(--campaigns-bg);
}

.search-input, .search-button {
  border: 1px solid var(--campaigns-bg);
}

.breadcrumb, .breadcrumb a, .breadcrumb span, .order-count {
  color: var(--breadcrumb-bg);
}

.breadcrumb a {
  color: var(--text-color-thirteen);
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

.info-value, .location-details h3, .location-details p, .no-locations, .item-details h3, .variant, .quantity, .price, .line-total {
  color: var(--campaigns-bg);
}

.page-title, .cart-title {
  font-family:cursive;
  color: var(--text-color-thirteen);
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  position: relative;
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

.add-to-cart, .add-review {
  background-color:#D4A017;
}

#app {
  background-color: var(--main-body-bg);
  transition: background-color 0.3s, color 0.3s;
  display: flex;
  flex-direction: column;
  /* Hide scrollbar while keeping functionality */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

#app::-webkit-scrollbar {
  width: 0;
}
</style>
