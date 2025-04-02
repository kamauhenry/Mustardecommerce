<template>
    <div class="search-page">
      <div class="search-container">
        <input
          type="text"
          v-model="query"
          placeholder="Search..."
          class="search-input"
          @keyup.enter="search"
          @blur="handleBlur"
        />
        <img
          :src="searchIcon"
          alt="Search Icon"
          class="search-icon"
          @click="search"
        />
      </div>
    </div>
</template>

<script>
import searchIcon from '@/assets/images/211817_search_strong_icon.png';

export default {
  data() {
    return {
      query: '',
      searchIcon
    };
  },
  methods: {
    async search() {
      if (this.query.trim()) {
        try {
          this.$router.push({ path: '/search-results', query: { q: this.query.trim() } });
        } catch (error) {
          console.error('Navigation error:', error);
        }
      }
    },
    handleBlur() {
      this.$forceUpdate();
    }
  }
};
</script>

<style scoped>

.search-container {
  display: flex;
  align-items: center;
  min-width: 60vw;
  background-color: var(--vt-c-white);
  border-radius: 100px;
  padding: 0.1rem 1.1rem;
  border: 1px solid transparent;
}

.search-input {
  background-color: var(--vt-c-white);
  flex: 1;
  border: none;
  padding: 0.8rem;
  border-radius: 25px 0 0 25px;
  outline: none;
}

.search-icon {
  width: 30px;
  height: 30px;
  cursor: pointer;
}
</style>
