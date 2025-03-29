<template>
  <MainLayout>
    <div class="search-results">
      <h1>Search Results for "{{ searchQuery }}"</h1>
      
      <div v-if="isLoading" class="loading">
        Loading results...
      </div>
      
      <div v-else-if="!searchResults || searchResults.length === 0" class="no-results">
        No results found for "{{ searchQuery }}"
      </div>
      
      <div v-else class="products">
        <div v-for="product in searchResults" :key="product.id" class="product-card">
          <router-link 
            :to="{ 
              name: 'product-detail',
              params: { categorySlug: product.category_slug, productSlug: product.slug }
            }" 
            class="product-link"
          >
            <div class="product-content">
              <div class="product-details">
                <h3 class="product-name">{{ product.name }}</h3>
                <p class="product-price">KES {{ product.price }}</p>
                <p class="moq-info">MOQ: {{ product.moq || 'N/A' }} items</p>
                <!-- Progress bar container -->
                <div class="moq-progress-container">
                    <div 
                      class="moq-progress-bar" 
                      :style="{ width: Math.min(100, product.moq_progress?.percentage || 0) + '%' }"
                    ></div>
                    <span class="moq-progress-text">{{ product.moq_progress?.percentage || 0 }}%</span>
                </div>
              </div>
              <img
                v-if="product.thumbnail || product.image"
                :src="product.thumbnail || product.image"
                :alt="product.name"
                class="product-image"
              />
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEcommerceStore } from '@/stores/ecommerce'
import MainLayout from '@/components/navigation/MainLayout.vue'

export default {
  name: 'SearchResults',
  components: {
    MainLayout,
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const ecommerceStore = useEcommerceStore()
    
    const searchQuery = computed(() => route.query.q || '')
    const searchResults = computed(() => ecommerceStore.searchResults)
    const isLoading = computed(() => ecommerceStore.searchLoading)
    const totalResults = computed(() => ecommerceStore.totalSearchResults)

    const fetchSearchResults = async (query) => {
      ecommerceStore.setSearchLoading(true)
      try {
        const response = await fetch(`http://localhost:8000/api/products/search/?search=${encodeURIComponent(query)}`)
        if (!response.ok) throw new Error('Failed to fetch products')
        const data = await response.json()
        ecommerceStore.setSearchResults(data.results || [])
        ecommerceStore.setTotalResults(data.count || 0)
      } catch (error) {
        console.error('Error fetching search results:', error)
        ecommerceStore.setSearchResults([])
        ecommerceStore.setTotalResults(0)
      } finally {
        ecommerceStore.setSearchLoading(false)
      }
    }

    onMounted(() => {
      if (searchQuery.value && (!searchResults.value || searchResults.value.length === 0)) {
        fetchSearchResults(searchQuery.value)
      }
    })

    const viewProduct = (slug) => {
      router.push({ name: 'product-detail', params: { slug } })
    }
    
    return {
      searchQuery,
      searchResults,
      isLoading,
      totalResults,
      viewProduct
    }
  }
}
</script>

<style scoped>
.search-results {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  font-size: 1.25rem;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0.5rem 0 1rem 0;
  color: #333;
}

.loading,
.no-results {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #666;
}

/* Products container */
.products {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Individual product card */
.product-card {
  flex: 0 0 calc(25% - 0.75rem);
  max-width: calc(25% - 0.75rem);
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
  background-color: white;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
/* MOQ status (e.g., "Active: X items") */
.moq-status {
  font-size: 0.7rem; /* Smaller font to match the second page */
  color: #28a745; /* Green for active status */
  background-color: #e6f4ea;
  padding: 0.2rem 0.4rem; /* Reduced padding */
  border-radius: 12px;
  margin: 0.25rem 0;
}
.moq-progress-container {
  position: relative;
  width: 100%;
  height: 24px;
  background-color: #e6f4ea;
  border-radius: 12px;
  overflow: hidden;
  margin: 0.25rem 0;
}

.moq-progress-bar {
  height: 100%;
  background-color: #28a745;
  transition: width 0.3s ease;
}

.moq-progress-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f28c38;
  font-size: 0.7rem;
  font-weight: bold;
}

.product-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  height: 100%;
}

.product-link:hover {
  text-decoration: none;
  color: inherit;
}

.product-content {
  display: flex;
  flex-direction: row;
  width: 100%;
  align-items: center;
}

.product-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.product-image {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  margin-left: 0.75rem;
  background-color: #e0e0e0;
}

.product-name {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0.25rem 0;
  text-align: left;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-price {
  font-size: 0.9rem;
  font-weight: 700;
  margin: 0.25rem 0;
}

.moq-info {
  font-size: 0.75rem;
  margin: 0.25rem 0;
}

.moq-status {
  font-size: 0.75rem;
  color: #28a745;
  background-color: #e6f4ea;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  margin: 0.25rem 0;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .product-card {
    flex: 0 0 calc(33.33% - 0.75rem);
    max-width: calc(33.33% - 0.75rem);
  }
}

@media (max-width: 768px) {
  .product-card {
    flex: 0 0 calc(50% - 0.75rem);
    max-width: calc(50% - 0.75rem);
  }

  .product-image {
    width: 120px;
    height: 120px;
  }

  .product-name {
    font-size: 0.85rem;
  }

  .product-price {
    font-size: 0.8rem;
  }

  .moq-info,
  .moq-status {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .product-card {
    flex: 0 0 calc(100% - 0.75rem);
    max-width: calc(100% - 0.75rem);
  }

  .product-image {
    width: 100px;
    height: 100px;
  }

  .product-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .product-image {
    margin-left: 0;
    margin-top: 0.75rem;
    width: 100%;
    height: 150px;
  }
}
</style>