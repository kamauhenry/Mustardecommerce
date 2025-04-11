<template>
  <div class="search-container">
    <input
      type="text"
      id="search-input"
      name="search-input"
      v-model="query"
      placeholder="Search..."
      class="search-input"
      @keyup.enter="search"
      @input="showSuggestions = true"
    />
    <img
      src="../../assets/images/211817_search_strong_icon.png"
      alt="Search Icon"
      class="search-icon"
      @click="search"
    />
    <!-- Suggestions Dropdown -->
    <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
      <ul>
        <li
          v-for="suggestion in suggestions"
          :key="suggestion.id"
          @click="selectSuggestion(suggestion)"
          class="suggestion-item"
        >
          {{ suggestion.name }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { useRouter } from 'vue-router';

export default {
  name: 'SearchBar',
  setup() {
    const query = ref('');
    const ecommerceStore = useEcommerceStore();
    const router = useRouter();
    const showSuggestions = ref(false);
    let debounceTimeout = null;
    let hideTimeout = null;

    // Computed property to access search suggestions from the store
    const suggestions = computed(() => {
      console.log('Computed suggestions:', ecommerceStore.searchSuggestions); // Debug
      return ecommerceStore.searchSuggestions;
    });

    // Fetch suggestions with debounce
    watch(query, (newQuery) => {
      if (debounceTimeout) {
        clearTimeout(debounceTimeout);
      }
      if (hideTimeout) {
        clearTimeout(hideTimeout);
      }
      debounceTimeout = setTimeout(() => {
        if (newQuery.trim()) {
          console.log('Fetching suggestions for:', newQuery);
          ecommerceStore.fetchSearchSuggestions(newQuery);
          showSuggestions.value = true;
          hideTimeout = setTimeout(() => {
            showSuggestions.value = false;
            console.log('Suggestions hidden after 3s timeout');
          }, 6000);
        } else {
          ecommerceStore.searchSuggestions = [];
          showSuggestions.value = false;
        }
      }, 200);
    });

    // Perform the full search
    const search = async () => {
      if (!query.value.trim()) return;

      ecommerceStore.setSearchLoading(true);
      try {
        const response = await fetch(
          `http://localhost:8000/api/products/search/?search=${encodeURIComponent(query.value)}`
        );
        if (!response.ok) throw new Error('Failed to fetch products');
        const data = await response.json();

        ecommerceStore.setSearchResults(data.results || []);
        ecommerceStore.setTotalResults(data.count || 0);
        ecommerceStore.addRecentSearch(query.value);

        router.push({
          name: 'search-results',
          query: { q: query.value },
        });

        showSuggestions.value = false;
        if (hideTimeout) {
          clearTimeout(hideTimeout);
        }
      } catch (error) {
        console.error('Error searching products:', error);
        ecommerceStore.setSearchResults([]);
        ecommerceStore.setTotalResults(0);
      } finally {
        ecommerceStore.setSearchLoading(false);
      }
    };

    // Handle suggestion selection
    const selectSuggestion = (suggestion) => {
      query.value = suggestion.name;
      showSuggestions.value = false;
      search();
    };

    return {
      query,
      search,
      suggestions,
      selectSuggestion,
      showSuggestions,
    };
  },
};
</script>

<style scoped>
.search-container {
  display: flex;
  align-items: center;
  min-width: 48vw;
  border-radius: 100px;
  padding: 0.1rem 1.1rem;
  position: relative;
}

.search-input {
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

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 10px 10px 10px 10px;
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.suggestions-dropdown ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  padding: 10px;
  cursor: pointer;
}

.suggestion-item:hover {
  background-color: #f0f0f0;
}

@media screen and (max-width: 480px) {
  .search-container {
    min-width: 90vw;
  }
  .search-input {
    font-size: 14px;
    padding: 0.6rem 0.8rem;
  }
  .search-icon {
    width: 20px;
    height: 20px;
  }
}
</style>