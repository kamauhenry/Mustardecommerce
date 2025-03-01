<template>
  <div @click="toggleTheme" class="theme-toggle">
    <svg
      v-if="isDarkMode"
      class="feather feather-moon"
      fill="none"
      stroke="#838636"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
    </svg>

    <svg
      v-else
      class="feather feather-sun"
      fill="none"
      stroke="#838636"
      stroke-linecap="round"
      stroke-linejoin="round"
      stroke-width="2"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="12" cy="12" r="5" />
      <line x1="12" x2="12" y1="1" y2="3" />
      <line x1="12" x2="12" y1="21" y2="23" />
      <line x1="4.22" x2="5.64" y1="4.22" y2="5.64" />
      <line x1="18.36" x2="19.78" y1="18.36" y2="19.78" />
      <line x1="1" x2="3" y1="12" y2="12" />
      <line x1="21" x2="23" y1="12" y2="12" />
      <line x1="4.22" x2="5.64" y1="19.78" y2="18.36" />
      <line x1="18.36" x2="19.78" y1="5.64" y2="4.22" />
    </svg>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isDarkMode: false, // Track theme state
    };
  },
  mounted() {
    // Check for saved theme preference
    this.isDarkMode = localStorage.getItem("theme") === "dark";
    this.applyTheme();
  },
  methods: {
    toggleTheme() {
      this.isDarkMode = !this.isDarkMode;
      localStorage.setItem("theme", this.isDarkMode ? "dark" : "light");
      this.applyTheme();
    },
    applyTheme() {
      document.documentElement.setAttribute("data-theme", this.isDarkMode ? "dark" : "light");
    },
  },
};
</script>

<style scoped>
.theme-toggle {
  cursor: pointer;
  display: inline-block;
  transition: transform 0.2s ease-in-out;
}

.theme-toggle:hover {
  transform: scale(1.1);
}

svg {
  display: flex;
  justify-content: center;
  width: 1.5rem;
  height: auto;
}
</style>
