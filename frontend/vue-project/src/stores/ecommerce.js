
import { defineStore, storeToRefs } from 'pinia';
import api from '@/services/api';
console.log('api in ecommerce.js:', api);

console.log('Local storage userId:', localStorage.getItem('userId'));

// Create an API instance to use throughout the store
let apiInstance = null;

export const useEcommerceStore = defineStore('ecommerce', {
  state: () => {
    const state = {
      currentUser: null,
      userId: localStorage.getItem('userId') || null,
      apiInstance: null,
      cart: null,
      userLoading: false,
      userError: null,
      showAuthModal: false,
      searchResults: [],
      totalSearchResults: 0,
      searchLoading: false,
      recentSearches: [],
      searchSuggestions: [],
      categories: [],
      categoryProducts: {},
      allCategoriesWithProducts: [],
      productDetails: {},
      cart: null,
      orders: [],
      completedOrders: [],
      loading: {
        categories: false,
        categoryProducts: false,
        productDetails: false,
        allCategoriesWithProducts: false,
        cart: false,
        orders: false,
        completedOrders: false,
      },
  
      error: {
        categories: null,
        categoryProducts: null,
        productDetails: null,
        allCategoriesWithProducts: null,
        cart: null,
        orders: null,
        completedOrders: null,
      },

    };

    // Initialize API instance with the store
    apiInstance = api.createApiInstance(state);

    return state;
  },

  actions: {

      // Initialize API instance with current store state
      initializeApiInstance() {
        this.apiInstance = api.createApiInstance(this);
      },
  
      async fetchCurrentUserInfo() {
        this.userLoading = true;
        this.userError = null;
        
        try {
          // Ensure API instance is created
          if (!this.apiInstance) {
            this.initializeApiInstance();
          }
  
          const userData = await api.fetchCurrentUserInfo(this.apiInstance);
          
          if (userData.user_id) {
            this.currentUser = {
              id: userData.user_id,
              username: userData.username
            };
            this.setUserId(userData.user_id);
          }
  
          return this.currentUser;
        } catch (error) {
          this.userError = error.message || 'Failed to fetch user information';
          this.currentUser = null;
          this.userId = null;
          
          throw error;
        } finally {
          this.userLoading = false;
        }
      },
  
      async fetchCart() {
        try {
          // Ensure we have a user ID
          if (!this.userId) {
            this.showAuthModal = true;
            throw new Error('Please log in to view your cart');
          }
  
          // Ensure API instance is initialized
          if (!this.apiInstance) {
            this.initializeApiInstance();
          }
  
          const cart = await api.fetchCart(this.apiInstance, this.userId);
          this.cart = cart;
          return cart;
        } catch (error) {
          // If cart doesn't exist, create one
          if (error.response && error.response.status === 404) {
            return this.createCart();
          }
          
          console.error('Cart fetch error:', error);
          return null;
        }
      },
  
      async createCart() {
        try {
          // Ensure we have a user ID and API instance
          if (!this.userId) {
            this.showAuthModal = true;
            throw new Error('No user logged in');
          }
  
          if (!this.apiInstance) {
            this.initializeApiInstance();
          }
  
          const newCart = await api.createCart(this.apiInstance, this.userId);
          this.cart = newCart;
          return newCart;
        } catch (error) {
          console.error('Failed to create cart:', error);
          
          // If cart creation fails due to authentication, show modal
          if (error.response && error.response.status === 403) {
            this.showAuthModal = true;
          }
          
          throw error;
        }
      },
  
      async addToCart(productId, variantId, quantity = 1) {
        try {
          // Ensure user is logged in
          if (!this.userId) {
            this.showAuthModal = true;
            throw new Error('Please log in to add items to cart');
          }
  
          // Ensure cart exists
          if (!this.cart) {
            await this.createCart();
          }
  
          // Ensure API instance is initialized
          if (!this.apiInstance) {
            this.initializeApiInstance();
          }
  
          // Add to cart
          const response = await api.addToCart(
            this.apiInstance, 
            this.cart.id, 
            productId, 
            variantId, 
            quantity
          );
          
          // Update local cart state
          this.cart = response;
          return response;
        } catch (error) {
          console.error('Add to cart error:', error);
          
          // Handle authentication errors
          if (error.response && error.response.status === 403) {
            this.showAuthModal = true;
          }
          
          throw error;
        }
      },
  
      setUserId(userId) {
        this.userId = userId;
        localStorage.setItem('userId', userId);
        // Reinitialize API instance with new user context
        this.initializeApiInstance();
      },
  
      logout() {
        this.userId = null;
        this.currentUser = null;
        this.cart = null;
        localStorage.removeItem('userId');
        // Reinitialize API instance
        this.initializeApiInstance();
      },



    async fetchCategories() {
      this.loading.categories = true;
      this.error.categories = null;
      try {
        const data = await api.fetchCategories(apiInstance);
        this.categories = data;
      } catch (error) {
        this.error.categories = error.message || 'Failed to load categories';
      } finally {
        this.loading.categories = false;
      }
    },
    async fetchAllCategoriesWithProducts() {
      this.loading.allCategoriesWithProducts = true;
      this.error.allCategoriesWithProducts = null;

      try {
        // Ensure API instance is initialized
        if (!this.apiInstance) {
          this.initializeApiInstance();
        }

        const response = await this.apiInstance.get('categories/with-products/');
        this.allCategoriesWithProducts = response.data;
      } catch (error) {
        console.error('Fetch Categories Error:', error);
        this.error.allCategoriesWithProducts = error.message || 'Failed to load categories with products';
      } finally {
        this.loading.allCategoriesWithProducts = false;
      }
    },

    async searchProducts(query, page = 1, perPage = 10) {
      this.setSearchLoading(true);
      try {
        console.log(`Searching for: ${query}`);
        console.log('api in searchProducts:', api);
        console.log('api.createApiInstance:', api.createApiInstance);
        const apiInstance = api.createApiInstance(this);
        console.log('After creating apiInstance', apiInstance);
        const response = await api.searchProducts(apiInstance, query, page, perPage);
        this.searchResults = response.results || [];
        this.totalSearchResults = response.total || 0;
        if (query && !this.recentSearches.includes(query)) {
          this.recentSearches.unshift(query);
          if (this.recentSearches.length > 5) {
            this.recentSearches.pop();
          }
          localStorage.setItem('recentSearches', JSON.stringify(this.recentSearches));
        }
        return response;
      } catch (error) {
        console.error('Error searching products:', error);
        throw error;
      } finally {
        this.setSearchLoading(false);
      }
    },
    setSearchLoading(status) {
      this.searchLoading = status;
    },
    
    async fetchSearchSuggestions(query) {
      if (!query || query.length < 2) {
        this.searchSuggestions = []
        return
      }
      
      try {
        const response = await apiClient.get('/products/', {
          params: {
            search: query,
            page: 1,
            per_page: 5,
            ordering: '-created_at'
          }
        })
        
        // Handle different response structures
        if (Array.isArray(response.data)) {
          this.searchSuggestions = response.data
        } else if (response.data.products) {
          this.searchSuggestions = response.data.products
        } else {
          this.searchSuggestions = response.data.results || []
        }
      } catch (error) {
        console.error('Error fetching suggestions:', error)
        this.searchSuggestions = []
      }
    },
    
    setSearchResults(results) {
      this.searchResults = results
    },
    
    setTotalResults(total) {
      this.totalSearchResults = total
    },
    
    setSearchLoading(status) {
      this.searchLoading = status
    },
    
    addRecentSearch(query) {
      if (!query || !query.trim()) return
      
      // Avoid duplicates
      const trimmedQuery = query.trim()
      if (!this.recentSearches.includes(trimmedQuery)) {
        // Keep only the 5 most recent searches
        if (this.recentSearches.length >= 5) {
          this.recentSearches.pop()
        }
        this.recentSearches.unshift(trimmedQuery)
        
        // Save to localStorage for persistence
        try {
          localStorage.setItem('recentSearches', JSON.stringify(this.recentSearches))
        } catch (e) {
          console.error('Could not save recent searches to localStorage', e)
        }
      }
    },
    
    clearSearchResults() {
      this.searchResults = []
      this.totalSearchResults = 0
    },
    
    clearRecentSearches() {
      this.recentSearches = []
      // Clear from localStorage as well
      try {
        localStorage.removeItem('recentSearches')
      } catch (e) {
        console.error('Could not clear recent searches from localStorage', e)
      }
    },
    async fetchAllCategoriesWithProducts() {
      this.loading.allCategoriesWithProducts = true;
      try {
        const data = await api.fetchAllCategoriesWithProducts(apiInstance);
        this.allCategoriesWithProducts = data;
      } catch (error) {
        this.error.allCategoriesWithProducts = error.message || 'Failed to load categories';
      } finally {
        this.loading.allCategoriesWithProducts = false;
      }
    },

    async fetchCategoryProducts(categorySlug, page = 1) {
      this.loading.categoryProducts = true;
      try {
        const data = await api.fetchCategoryProducts(apiInstance, categorySlug, page);
        if (!this.categoryProducts[categorySlug]) this.categoryProducts[categorySlug] = { products: [], total: data.total };
        this.categoryProducts[categorySlug].products.push(...data.products);
      } catch (error) {
        this.error.categoryProducts = error.message || `Failed to load products for ${categorySlug}`;
      } finally {
        this.loading.categoryProducts = false;
      }
    },

    async fetchProductDetails(categorySlug, productSlug) {
      this.loading.productDetails = true;
      this.error.productDetails = null;
      const key = `${categorySlug}:${productSlug}`;
      try {
        const data = await api.fetchProductDetails(apiInstance, categorySlug, productSlug);
        this.productDetails[key] = data;
      } catch (error) {
        this.error.productDetails = error.message || 'Failed to load product details';
      } finally {
        this.loading.productDetails = false;
      }
    },

    async fetchOrdersData() {
      if (!this.userId) throw new Error('User ID not set');
      this.loading.orders = true;
      this.error.orders = null;
      try {
        const data = await api.fetchOrders(apiInstance, this.userId);
        this.orders = data;
      } catch (error) {
        this.error.orders = error.message || 'Failed to load orders';
      } finally {
        this.loading.orders = false;
      }
    },

    async fetchCompletedOrdersData() {
      if (!this.userId) throw new Error('User ID not set');
      this.loading.completedOrders = true;
      this.error.completedOrders = null;
      try {
        const data = await api.fetchCompletedOrders(apiInstance, this.userId);
        this.completedOrders = data;
      } catch (error) {
        this.error.completedOrders = error.message || 'Failed to load completed orders';
      } finally {
        this.loading.completedOrders = false;
      }
    },

    setUserId(userId) {
      this.userId = userId;
      localStorage.setItem('userId', userId); // Persist user ID
      // Update the API instance with the new userId
      apiInstance = api.createApiInstance(this);
    },

    logout() {
      this.userId = null;
      localStorage.removeItem('userId');
      this.cart = null;
      this.orders = [];
      this.completedOrders = [];
      // Update the API instance after logout
      apiInstance = api.createApiInstance(this);
    },
  },
  persist: {
    // Custom key for localStorage (optional)
    key: 'ecommerce-search-history',
    
    // Only persist these specific parts of your store
    paths: ['recentSearches'],
    
    // Use localStorage (this is the default)
    storage: localStorage,
  },

  getters: {
    isAuthenticated: (state) => !!state.userId,
    isAuthModalVisible: (state) => state.showAuthModal,
    cartItemCount: (state) => state.cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0,
    cartTotal: (state) => state.cart?.items?.reduce((sum, item) => sum + item.line_total, 0) || 0,
    getSearchResults: (state) => state.searchResults,
    isSearchLoading: (state) => state.searchLoading,
    getRecentSearches: (state) => state.recentSearches,
  },
});
