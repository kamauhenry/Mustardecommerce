<template>
  <div class="search-container">
    <input
      type="text"
      v-model="query"
      placeholder="Search..."
      class="search-input"
    />
    <img src="../../assets/images/211817_search_strong_icon.png" alt="Search Icon" class="search-icon"/>
  </div>
</template>

<script>
export default {
  data() {
    return {
      query: ""
    };
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
  padding: .1rem 1.1rem;
  border: 1px solid transparent;
}

.search-input {
  background-color: var(--vt-c-white);
  flex: 1;
  border: none;
  padding: .8rem;
  border-radius: 25px 0 0 25px;
  outline: none;
}

.search-icon {
  width: 30px;
  height: 30px;
}
</style>
