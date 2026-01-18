import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApiCall } from '../composables/useApiCall';
import { useApiInstance } from '../composables/useApiInstance';
import { LocalStorageManager, STORAGE_KEYS } from '../composables/useLocalStorage';
import { toast } from '../composables/useToast';

/**
 * Search Store Module
 * Handles product search, recent searches, and search suggestions
 */
export const useSearchStore = defineStore('search', () => {
  // State
  const searchQuery = ref('');
  const searchResults = ref([]);
  const recentSearches = ref(LocalStorageManager.get(STORAGE_KEYS.RECENT_SEARCHES, []));
  const searchSuggestions = ref([]);
  const isSearching = ref(false);
  const hasSearched = ref(false);

  // Pagination for search results
  const currentPage = ref(1);
  const totalPages = ref(1);
  const totalResults = ref(0);

  // API instance
  const { api } = useApiInstance();

  // Computed
  const hasResults = computed(() => searchResults.value.length > 0);
  const hasRecentSearches = computed(() => recentSearches.value.length > 0);
  const hasSuggestions = computed(() => searchSuggestions.value.length > 0);

  /**
   * Search for products
   * @param {string} query - Search query
   * @param {number} page - Page number
   */
  const search = async (query, page = 1) => {
    if (!query || query.trim().length === 0) {
      searchResults.value = [];
      hasSearched.value = false;
      return;
    }

    const { execute } = useApiCall();
    isSearching.value = true;
    searchQuery.value = query;

    try {
      const params = {
        search: query,
        page,
        page_size: 12,
      };

      const response = await execute(
        async () => api.get('/products/search/', { params }),
        { showToast: false }
      );

      searchResults.value = response.results || response;
      currentPage.value = page;
      totalPages.value = response.total_pages || 1;
      totalResults.value = response.count || searchResults.value.length;
      hasSearched.value = true;

      // Add to recent searches
      addToRecentSearches(query);

      return searchResults.value;
    } catch (error) {
      toast.error('Search failed');
      console.error('Search error:', error);
      searchResults.value = [];
      return [];
    } finally {
      isSearching.value = false;
    }
  };

  /**
   * Get search suggestions based on query
   * @param {string} query - Partial search query
   */
  const getSuggestions = async (query) => {
    if (!query || query.trim().length < 2) {
      searchSuggestions.value = [];
      return;
    }

    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get('/products/suggestions/', {
          params: { q: query, limit: 5 }
        }),
        { showToast: false }
      );

      searchSuggestions.value = response;
    } catch (error) {
      console.error('Suggestions error:', error);
      searchSuggestions.value = [];
    }
  };

  /**
   * Add query to recent searches
   * @param {string} query - Search query
   */
  const addToRecentSearches = (query) => {
    if (!query || query.trim().length === 0) return;

    const trimmedQuery = query.trim();

    // Remove if already exists
    const index = recentSearches.value.indexOf(trimmedQuery);
    if (index !== -1) {
      recentSearches.value.splice(index, 1);
    }

    // Add to beginning
    recentSearches.value.unshift(trimmedQuery);

    // Keep only last 10 searches
    if (recentSearches.value.length > 10) {
      recentSearches.value = recentSearches.value.slice(0, 10);
    }

    // Save to localStorage
    LocalStorageManager.set(STORAGE_KEYS.RECENT_SEARCHES, recentSearches.value);
  };

  /**
   * Clear recent searches
   */
  const clearRecentSearches = () => {
    recentSearches.value = [];
    LocalStorageManager.remove(STORAGE_KEYS.RECENT_SEARCHES);
  };

  /**
   * Remove specific search from recent searches
   * @param {string} query - Search query to remove
   */
  const removeRecentSearch = (query) => {
    const index = recentSearches.value.indexOf(query);
    if (index !== -1) {
      recentSearches.value.splice(index, 1);
      LocalStorageManager.set(STORAGE_KEYS.RECENT_SEARCHES, recentSearches.value);
    }
  };

  /**
   * Clear search results
   */
  const clearResults = () => {
    searchResults.value = [];
    searchQuery.value = '';
    hasSearched.value = false;
    currentPage.value = 1;
    totalPages.value = 1;
    totalResults.value = 0;
  };

  /**
   * Clear search suggestions
   */
  const clearSuggestions = () => {
    searchSuggestions.value = [];
  };

  /**
   * Go to next page of search results
   */
  const nextPage = async () => {
    if (currentPage.value < totalPages.value && searchQuery.value) {
      await search(searchQuery.value, currentPage.value + 1);
    }
  };

  /**
   * Go to previous page of search results
   */
  const previousPage = async () => {
    if (currentPage.value > 1 && searchQuery.value) {
      await search(searchQuery.value, currentPage.value - 1);
    }
  };

  /**
   * Go to specific page of search results
   * @param {number} page - Page number
   */
  const goToPage = async (page) => {
    if (page >= 1 && page <= totalPages.value && searchQuery.value) {
      await search(searchQuery.value, page);
    }
  };

  /**
   * Initialize search state from localStorage
   */
  const initSearch = () => {
    const savedSearches = LocalStorageManager.get(STORAGE_KEYS.RECENT_SEARCHES, []);
    recentSearches.value = savedSearches;
  };

  // Initialize on store creation
  initSearch();

  return {
    // State
    searchQuery,
    searchResults,
    recentSearches,
    searchSuggestions,
    isSearching,
    hasSearched,
    currentPage,
    totalPages,
    totalResults,

    // Computed
    hasResults,
    hasRecentSearches,
    hasSuggestions,

    // Actions
    search,
    getSuggestions,
    addToRecentSearches,
    clearRecentSearches,
    removeRecentSearch,
    clearResults,
    clearSuggestions,
    nextPage,
    previousPage,
    goToPage,
    initSearch,
  };
});
