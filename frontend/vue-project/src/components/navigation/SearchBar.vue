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
    />
    <img
      src="../../assets/images/211817_search_strong_icon.png"
      alt="Search Icon"
      class="search-icon"
      @click="search"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import { useEcommerceStore } from '@/stores/ecommerce'
import { useRouter } from 'vue-router'

export default {
  name: 'SearchBar',
  setup() {
    const query = ref('')
    const ecommerceStore = useEcommerceStore()
    const router = useRouter()

    const search = async () => {
      if (!query.value.trim()) return  // Skip empty searches

      ecommerceStore.setSearchLoading(true)

      try {
        const response = await fetch(`http://localhost:8000/api/products/search/?search=${encodeURIComponent(query.value)}`)
        if (!response.ok) throw new Error('Failed to fetch products')
        const data = await response.json()

        // Store results and total in Pinia store
        ecommerceStore.setSearchResults(data.results || [])
        ecommerceStore.setTotalResults(data.count || 0) // Assuming API returns a count
        ecommerceStore.addRecentSearch(query.value)

        // Navigate to results page
        router.push({
          name: 'search-results',
          query: { q: query.value }
        })
      } catch (error) {
        console.error('Error searching products:', error)
        ecommerceStore.setSearchResults([])  // Clear results on error
        ecommerceStore.setTotalResults(0)
      } finally {
        ecommerceStore.setSearchLoading(false)
      }
    }

    return {
      query,
      search
    }
  }
}
</script>

<!-- Style remains unchanged -->
<style scoped>
.search-container {
  display: flex;
  align-items: center;
  min-width: 48vw;
  /* background-color: var(--vt-c-white); */
  border-radius: 100px;
  padding: .1rem 1.1rem;
  /* border: 1px solid transparent; */
}

.search-input {
  /* background-color: var(--vt-c-white); */
  flex: 1;
  border: none;
  padding: .8rem;
  border-radius: 25px 0 0 25px;
  outline: none;
}

.search-icon {
  width: 30px;
  height: 30px;
  cursor: pointer;
}
/* Media query for smaller phones */
@media screen and (max-width: 480px) {
  .search-container {
    min-width: 90vw; /* Use more screen width on small devices */
  }
}

.search-input {
  flex: 1;
  padding: .8rem 1rem;
  border-radius: 25px 0 0 25px;
  outline: none;
  font-size: 16px;
}

/* Adjust font size for smaller screens */
@media screen and (max-width: 480px) {
  .search-input {
    font-size: 14px;
    padding: .6rem .8rem;
  }
}

.search-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--vt-c-white);
  border: none;
  border-radius: 0 25px 25px 0;
  padding: .7rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

/* Make button slightly smaller on mobile */
@media screen and (max-width: 480px) {
  .search-button {
    padding: .6rem .8rem;
  }
}

/* .search-button:hover {
  background-color: #f0f0f0;
}

.search-button:active {
  background-color: #e0e0e0;
} */

.search-icon {
  width: 24px;
  height: 24px;
}

/* Make icon slightly smaller on mobile */
@media screen and (max-width: 480px) {
  .search-icon {
    width: 20px;
    height: 20px;
  }
}
</style>
