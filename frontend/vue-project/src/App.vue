<script>
  import HomePage from "./views/HomePage.vue";

  export default {
    name: "app",
    components: {
      HomePage,
    },
  };
</script>

<template>
  <div id="app">
    <HomePage></HomePage>
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

.category-p {
  color: var(--text-color-thirteen);
}

.category-link {
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

#app {
  background-color: var(--main-body-bg);
  transition: background-color 0.3s, color 0.3s;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
