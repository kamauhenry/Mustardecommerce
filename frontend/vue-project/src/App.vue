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
  --text-color-eight: var(--text-color-one); /* #db4619 orange */
  --text-color-nine: var(--vt-c-white); /* #ffffff white */
  --text-color-ten: var(--vt-c-white); /* #ffffff white */
  --text-color-eleven: var(--vt-c-white); /* #ffffff white */
  --text-color-twelve: var(--vt-c-grey); /* grey */
}

[data-theme="light"] {
  --top-row-bg: var(--vt-c-white);
  --categories-bg: var(--background-color-three);
  --main-body-bg: var(--vt-c-white);
  --text-color-eight: var(--text-color-two); /* #838636 darkish green */
  --text-color-nine: var(--text-color-two); /* #838636 darkish green */
  --text-color-ten: var(--vt-c-black-soft); /* #3d3d3d dark grey */
  --text-color-eleven: var(--text-color-two); /* #838636 darkish green */
  --text-color-twelve: var(--text-color-four); /* darker green */
}

.navbar {
  background-color: var(--top-row-bg);
  transition: background-color 0.3s, color 0.3s;
}

.categories {
  background-color: var(--categories-bg);
  transition: background-color 0.3s, color 0.3s;
}

.category-link {
  color: var(--text-color-eleven);

}

.category-link:hover {
  color: var(--text-color-twelve);
}

#app {
  background-color: var(--main-body-bg);
  transition: background-color 0.3s, color 0.3s;
  height: 100vh;
}
</style>
