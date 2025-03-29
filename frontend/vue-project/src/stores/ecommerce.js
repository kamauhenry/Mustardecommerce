import { defineStore, storeToRefs } from 'pinia';
import api from '@/services/api';
import { fetchCurrentUserInfo } from '@/services/api';


export const useEcommerceStore = defineStore('ecommerce', {
  state: () => {
    const state = {
      currentUser: null,
      userId: null,
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

    return state;
  },
  getters: {
    isAuthenticated: (state) => !!localStorage.getItem('authToken'),
    isAuthModalVisible: (state) => state.showAuthModal,
    cartItemCount: (state) => state.cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0,
    cartTotal: (state) => state.cart?.items?.reduce((sum, item) => sum + item.line_total, 0) || 0,
    getSearchResults: (state) => state.searchResults,
    isSearchLoading: (state) => state.searchLoading,
    getRecentSearches: (state) => state.recentSearches,
  },
  actions: {
    initializeApiInstance() {
      // Pass the store reference to createApiInstance
      this.apiInstance = api.createApiInstance(this);
    },
  
    async login(username, password) {
      try {
        if (!this.apiInstance) {
          this.initializeApiInstance();
        }
        const response = await api.login(this.apiInstance, username, password);
        console.log('Login response:', response);
        // Set user details based on backend response
        this.userId = response.user_id;
        this.currentUser = {
          id: response.user_id,
          username: response.username,
        };
      
        return response;
      } catch (error) {
        console.error('Login failed:', error);
        this.showAuthModal = true;
        throw error;
      }
    },

    async fetchCurrentUserInfo() {
      try {
        // If no token, show auth modal
        if (!this.isAuthenticated) {
          this.showAuthModal = true;
          return null;
        }

        // Ensure apiInstance is initialized
        if (!this.apiInstance) {
          this.initializeApiInstance();
        }
        
        // Use the imported fetchCurrentUserInfo function
        const userData = await fetchCurrentUserInfo(this.apiInstance);
        
        this.userId = userData.id;
        this.currentUser = {
          id: userData.id,
          username: userData.username,
        };
        
        return userData;
      } catch (error) {
        console.error('Authentication check failed:', error);
        this.showAuthModal = true;
        this.logout(); // Clear any invalid token
        throw error;
      }
    },


    logout() {
      // Optional: Call backend logout if needed
      if (this.apiInstance) {
        logout(this.apiInstance);
      }
      
      // Clear local state
      this.userId = null;
      this.currentUser = null;
      this.cart = null;
      this.orders = [];
      this.completedOrders = [];
      
      // Remove token from storage
      localStorage.removeItem('authToken');
      
      // Reinitialize API instance
      this.initializeApiInstance();
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
      async checkout(checkoutData) {
        try {
          // 1. Validate cart existence
          if (!this.cart || !this.cart.id) {
            throw new Error('No active cart found');
          }
      
          // 2. Ensure API instance is initialized
          if (!this.apiInstance) {
            this.initializeApiInstance();
          }
      
          // 3. Prepare default checkout data with fallback values
          const defaultCheckoutData = {
            cart_id: this.cart.id,
            shipping_method: 'standard',
            shipping_address: this.currentUser?.location || 'shop pick up',
            payment_method: 'default'  // Add a default payment method
          };
      
          // 4. Merge default data with provided checkout data
          const finalCheckoutData = { 
            ...defaultCheckoutData, 
            ...checkoutData 
          };
          console.log('Checkout Data:', finalCheckoutData);
      
          // 5. Perform checkout API call
          const response = await this.apiInstance.post(
            `/carts/${this.cart.id}/checkout/`, 
            finalCheckoutData,
            { timeout: 15000 } 
          );
          
          // 6. Post-checkout cleanup and data refresh
          this.cart = null;  // Clear cart
          localStorage.removeItem('cartId');
          
          // 7. Fetch updated orders data
          await this.fetchOrdersData();
      
          // 8. Return the response for further handling
          return response.data;
        } catch (err) {
          // 9. Enhanced error handling
          console.error('Full Checkout Error:', err);
          console.error('Error Response:', err.response?.data);
          console.error('Error Status:', err.response?.status);
          // 10. Provide more informative error
          const errorMessage = err.response?.data?.error || 
                               err.message || 
                               'Checkout failed. Please try again.';
          
          // Optionally, you could add a toast or error notification here
          throw new Error(errorMessage);
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
  

  
      logout() {
        this.userId = null;
        this.currentUser = null;
        this.cart = null;
        localStorage.removeItem('userId');
        // Reinitialize API instance
        this.initializeApiInstance();
      },

    async fetchAllCategoriesWithProducts() {
      this.loading.allCategoriesWithProducts = true;
      this.error.allCategoriesWithProducts = null;
      try {
        if (!this.apiInstance) {
          console.log('apiInstance is null, initializing...');
          this.initializeApiInstance();
        }
        console.log('apiInstance after init:', this.apiInstance);
        if (!this.apiInstance) {
          throw new Error('apiInstance failed to initialize');
        }
        const data = await api.fetchAllCategoriesWithProducts(this.apiInstance);
        this.allCategoriesWithProducts = data;
      } catch (error) {
        console.error('Fetch Categories Error:', error);
        this.error.allCategoriesWithProducts = error.message || 'Failed to load categories with products';
      } finally {
        this.loading.allCategoriesWithProducts = false;
      }
    },
    
    async fetchCategories() {
      this.loading.categories = true;
      this.error.categories = null;
      try {
        if (!this.apiInstance) {
          console.log('apiInstance is null, initializing...');
          this.initializeApiInstance();
        }
        console.log('apiInstance after init:', this.apiInstance);
        if (!this.apiInstance) {
          throw new Error('apiInstance failed to initialize');
        }
        const data = await api.fetchCategories(this.apiInstance);
        this.categories = data;
      } catch (error) {
        this.error.categories = error.message || 'Failed to load categories';
      } finally {
        this.loading.categories = false;
      }
    },

    async fetchCategoryProducts(categorySlug, page = 1) {
      // Optional: Ensure apiInstance is initialized
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.categoryProducts = true;
      try {
        // Use this.apiInstance instead of apiInstance
        const data = await api.fetchCategoryProducts(this.apiInstance, categorySlug, page);
        if (!this.categoryProducts[categorySlug]) this.categoryProducts[categorySlug] = { products: [], total: data.total };
        this.categoryProducts[categorySlug].products.push(...data.products);
      } catch (error) {
        this.error.categoryProducts = error.message || `Failed to load products for ${categorySlug}`;
      } finally {
        this.loading.categoryProducts = false;
      }
    },

    async searchProducts(query, page = 1, perPage = 10) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.setSearchLoading(true);
      try {
        // Use this.apiInstance directly instead of creating a new instance
        const response = await api.searchProducts(this.apiInstance, query, page, perPage);
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
        this.searchSuggestions = [];
        return;
      }
      
      try {
        // Replace apiClient with this.apiInstance
        const response = await this.apiInstance.get('/products/', {
          params: {
            search: query,
            page: 1,
            per_page: 5,
            ordering: '-created_at'
          }
        });
        
        // Handle different response structures
        if (Array.isArray(response.data)) {
          this.searchSuggestions = response.data;
        } else if (response.data.products) {
          this.searchSuggestions = response.data.products;
        } else {
          this.searchSuggestions = response.data.results || [];
        }
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        this.searchSuggestions = [];
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
 
    async fetchProductDetails(categorySlug, productSlug) {
      // Ensure apiInstance is initialized
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.productDetails = true;
      this.error.productDetails = null;
      const key = `${categorySlug}:${productSlug}`;
      try {
        // Use this.apiInstance instead of apiInstance
        const data = await api.fetchProductDetails(this.apiInstance, categorySlug, productSlug);
        this.productDetails[key] = data;
      } catch (error) {
        this.error.productDetails = error.message || 'Failed to load product details';
      } finally {
        this.loading.productDetails = false;
      }
    },


    // Fetch Orders Data
    async fetchOrdersData() {
      try {
        this.loading.orders = true;
        this.error.orders = null;

        const response = await this.apiInstance.get('orders/');
        this.orders = response.data;
        
        // Separate completed orders
        this.completedOrders = this.orders.filter(order => order.status === 'Completed');
      } catch (err) {
        this.error.orders = 'Could not load orders. Please try again.';
        console.error('Error loading orders:', err);
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


});
