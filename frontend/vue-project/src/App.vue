<script>
  export default {
    name: "app",
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
  --text-color-thirteen: var(--text-color-one);
  --text-color-fourteen: var(--vt-c-white);
  --text-color-page-title: var(--text-color-one);
  --bg-color-about-section: var(--bg-color-about-section-2);
  --bg-color-about-section-card: var(--vt-c-black-mute);
}

[data-theme="light"] {
  --top-row-bg: var(--vt-c-white);
  --categories-bg: var(--background-color-three);
  --main-body-bg: var(--vt-c-white);
  --sidebar-text-color: var(--vt-c-black-mute); /* #ffffff white */
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

/* Categories */
.category-p, .about-h2 {
  color: var(--text-color-thirteen);
}

.category-link, .about-p {
  color: var(--text-color-eleven);

}

.category-link:hover {
  color: var(--text-color-twelve);
}

.campaigns-title, .searches-title {
  color: var(--text-color-eleven);
}

.campaign-p, .search-p {
  color: var(--text-color-fourteen);
  font-weight: 700;
}

/* About */
.page-title {
  font-family:cursive;
  color: var(--text-color-eleven);
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

/* Products */
.product-card {
  background-color: var(--categories-bg);
}

.product-header,.moq, .moq-details, .progress-text {
  color: var(--sidebar-text-color);
}

.price {
  color: var(--text-color-page-title);
}

#app {
  background-color: var(--main-body-bg);
  transition: background-color 0.3s, color 0.3s;
  display: flex;
  flex-direction: column;
  font-weight: 700;
}
</style>
