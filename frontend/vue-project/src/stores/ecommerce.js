import { defineStore } from 'pinia';
import api from '@/services/api';

export const useEcommerceStore = defineStore('ecommerce', {
  state: () => {
    const state = {
      currentUser: null,
      userId: null,
      apiInstance: null,
      cart: null,
      cartItems: [], // Add cartItems to store
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
      deliveryLocations: [],
      productDetails: {},
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
        userProfile: false,
        deliveryLocations: false,
      },
      error: {
        categories: null,
        categoryProducts: {},
        productDetails: null,
        allCategoriesWithProducts: null,
        cart: null,
        orders: null,
        completedOrders: null,
        userProfile: null,
        deliveryLocations: null,
      },
    };

    // Load cartItems from localStorage for unauthenticated users
    const storedCart = localStorage.getItem('cartItems');
    if (storedCart) {
      state.cartItems = JSON.parse(storedCart);
    }

    return state;
  },
  getters: {
    isAuthenticated: (state) => !!localStorage.getItem('authToken'),
    isAuthModalVisible: (state) => state.showAuthModal,
    cartItemCount: (state) => {
      return state.cartItems.reduce((sum, item) => sum + (item.quantity || 0), 0) || 0;
    },
    cartTotal: (state) => state.cartItems.reduce((sum, item) => sum + (item.line_total || 0), 0) || 0,
    getSearchResults: (state) => state.searchResults,
    isSearchLoading: (state) => state.searchLoading,
    getRecentSearches: (state) => state.recentSearches,
  },
  actions: {
    initializeApiInstance() {
      this.apiInstance = api.createApiInstance(this);
    },
    setUserId(userId) {
      this.userId = userId;
      localStorage.setItem('userId', userId);
      this.apiInstance = api.createApiInstance(this);
    },

    async login(username, password) {
      try {
        if (!this.apiInstance) {
          this.initializeApiInstance();
        }
        const response = await api.login(this.apiInstance, username, password);
        this.userId = response.user_id;
        this.currentUser = {
          id: response.user_id,
          username: response.username,
        };
        await this.fetchCurrentUserInfo();
        await this.syncCartWithBackend(); // Sync local cart after login
        return response;
      } catch (error) {
        console.error('Login failed:', error);
        this.showAuthModal = true;
        throw error;
      }
    },

    async fetchCurrentUserInfo() {
      try {
        if (!this.isAuthenticated) {
          this.showAuthModal = true;
          this.cartItems = this.loadCartFromLocalStorage(); // Load from localStorage if not authenticated
          return null;
        }

        if (!this.apiInstance) {
          this.initializeApiInstance();
        }

        const userData = await api.fetchCurrentUserInfo(this.apiInstance);

        this.userId = userData.id;
        this.currentUser = {
          id: userData.id,
          username: userData.username,
          email: userData.email,
        };

        await this.fetchCart(); // Fetch cart after user info
        return userData;
      } catch (error) {
        console.error('Authentication check failed:', error);
        this.showAuthModal = true;
        this.logout();
        throw error;
      }
    },

    async logout() {
      if (this.apiInstance) {
        await api.logout(this.apiInstance);
      }

      this.userId = null;
      this.currentUser = null;
      this.cart = null;
      this.orders = [];
      this.completedOrders = [];
      this.deliveryLocations = [];
      localStorage.removeItem('authToken');
      this.cartItems = this.loadCartFromLocalStorage(); // Persist cart in localStorage
      this.initializeApiInstance();
    },

    async createCart() {
      try {
        if (!this.userId) {
          this.showAuthModal = true;
          throw new Error('No user logged in');
        }

        if (!this.apiInstance) {
          this.initializeApiInstance();
        }

        const newCart = await api.createCart(this.apiInstance, this.userId);
        this.cart = newCart;
        this.cartItems = newCart.items || [];
        localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
        return newCart;
      } catch (error) {
        console.error('Failed to create cart:', error);
        if (error.response && error.response.status === 403) {
          this.showAuthModal = true;
        }
        throw error;
      }
    },

    async fetchCart() {
      if (!this.userId) {
        this.cartItems = this.loadCartFromLocalStorage();
        return;
      }
      try {
        const response = await this.apiInstance.get(`/users/${this.userId}/cart/`);
        this.cart = response.data;
        this.cartItems = response.data.items || [];
        localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
      } catch (error) {
        console.error('Failed to fetch cart:', error);
        this.cartItems = this.loadCartFromLocalStorage();
      }
    },

    loadCartFromLocalStorage() {
      const storedCart = localStorage.getItem('cartItems');
      return storedCart ? JSON.parse(storedCart) : [];
    },

    async syncCartWithBackend() {
      if (!this.isAuthenticated || !this.cartItems.length) return;

      try {
        if (!this.cart) {
          await this.createCart();
        }
        for (const item of this.cartItems) {
          await this.apiInstance.post(`/carts/${this.cart.id}/add_item/`, {
            product_id: item.product_id,
            variant_id: item.variant_id,
            quantity: item.quantity,
          });
        }
        await this.fetchCart();
        localStorage.removeItem('cartItems'); // Clear localStorage after sync
      } catch (error) {
        console.error('Failed to sync cart with backend:', error);
      }
    },

    async checkout(checkoutData) {
      try {
        if (!this.cart || !this.cart.id) {
          throw new Error('No active cart found');
        }

        if (!this.apiInstance) {
          this.initializeApiInstance();
        }

        const defaultCheckoutData = {
          cart_id: this.cart.id,
          shipping_method: 'standard',
          shipping_address: this.currentUser?.location || 'shop pick up',
          payment_method: 'default',
        };

        const finalCheckoutData = {
          ...defaultCheckoutData,
          ...checkoutData,
        };

        const response = await this.apiInstance.post(
          `/carts/${this.cart.id}/checkout/`,
          finalCheckoutData,
          { timeout: 15000 }
        );

        this.cart = null;
        this.cartItems = [];
        localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
        localStorage.removeItem('cartId');
        await this.fetchOrdersData();
        return response.data;
      } catch (err) {
        console.error('Full Checkout Error:', err);
        const errorMessage = err.response?.data?.error || err.message || 'Checkout failed. Please try again.';
        throw new Error(errorMessage);
      }
    },

    async addToCart(productId, variantId, quantity = 1) {
      try {
        if (!this.isAuthenticated) {
          // For unauthenticated users, store in localStorage
          const newItem = { product_id: productId, variant_id: variantId, quantity };
          this.cartItems.push(newItem);
          localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
          return;
        }

        if (!this.apiInstance) {
          this.initializeApiInstance();
        }

        if (!this.cart) {
          try {
            this.cart = await api.fetchCart(this.apiInstance, this.userId);
          } catch (error) {
            await this.createCart();
            if (!this.cart) this.cart = { id: null, items: [] };
          }
        }

        const response = await api.addToCart(
          this.apiInstance,
          this.cart.id,
          productId,
          variantId,
          quantity
        );

        this.cart = response || { id: this.cart.id, items: [] };
        this.cartItems = this.cart.items || [];
        localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
        return response;
      } catch (error) {
        console.error('Add to cart error:', error);
        if (error.response && error.response.status === 403) {
          this.showAuthModal = true;
        }
        throw error;
      }
    },

    async fetchAllCategoriesWithProducts() {
      this.loading.allCategoriesWithProducts = true;
      this.error.allCategoriesWithProducts = null;
      try {
        if (!this.apiInstance) {
          this.initializeApiInstance();
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
          this.initializeApiInstance();
        }
        const data = await api.fetchCategories(this.apiInstance);
        this.categories = data;
      } catch (error) {
        this.error.categories = error.message || 'Failed to load categories';
      } finally {
        this.loading.categories = false;
      }
    },

    async fetchCategoryProducts(categorySlug) {
      this.loading.categoryProducts = true;
      this.error.categoryProducts[categorySlug] = null;
      try {
        const response = await api.fetchCategoryProducts(this.apiInstance, categorySlug);
        this.categoryProducts[categorySlug] = response;
      } catch (error) {
        if (error.response?.status === 404) {
          this.error.categoryProducts[categorySlug] = `Category "${categorySlug}" not found or inactive.`;
        } else {
          this.error.categoryProducts[categorySlug] = error.response?.data?.error || error.message || 'Failed to fetch category products';
        }
        console.error(`Error fetching category products for ${categorySlug}:`, error);
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

    async fetchSearchSuggestions(query) {
      if (!query || query.length < 2) {
        this.searchSuggestions = [];
        return;
      }

      try {
        const response = await this.apiInstance.get('/products/', {
          params: {
            search: query,
            page: 1,
            per_page: 5,
            ordering: '-created_at',
          },
        });

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
      this.searchResults = results;
    },

    setTotalResults(total) {
      this.totalSearchResults = total;
    },

    setSearchLoading(status) {
      this.searchLoading = status;
    },

    addRecentSearch(query) {
      if (!query || !query.trim()) return;

      const trimmedQuery = query.trim();
      if (!this.recentSearches.includes(trimmedQuery)) {
        if (this.recentSearches.length >= 5) {
          this.recentSearches.pop();
        }
        this.recentSearches.unshift(trimmedQuery);

        try {
          localStorage.setItem('recentSearches', JSON.stringify(this.recentSearches));
        } catch (e) {
          console.error('Could not save recent searches to localStorage', e);
        }
      }
    },

    clearSearchResults() {
      this.searchResults = [];
      this.totalSearchResults = 0;
    },

    clearRecentSearches() {
      this.recentSearches = [];
      try {
        localStorage.removeItem('recentSearches');
      } catch (e) {
        console.error('Could not clear recent searches from localStorage', e);
      }
    },

    async fetchProductDetails(categorySlug, productSlug) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.productDetails = true;
      this.error.productDetails = null;
      const key = `${categorySlug}:${productSlug}`;
      try {
        const data = await api.fetchProductDetails(this.apiInstance, categorySlug, productSlug);
        this.productDetails[key] = data;
      } catch (error) {
        this.error.productDetails = error.message || 'Failed to load product details';
      } finally {
        this.loading.productDetails = false;
      }
    },

    async fetchOrdersData() {
      try {
        this.loading.orders = true;
        this.error.orders = null;

        const response = await this.apiInstance.get('orders/');
        this.orders = response.data;

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
        const data = await api.fetchCompletedOrders(this.apiInstance, this.userId);
        this.completedOrders = data;
      } catch (error) {
        this.error.completedOrders = error.message || 'Failed to load completed orders';
      } finally {
        this.loading.completedOrders = false;
      }
    },



    async fetchUserProfile() {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.userProfile = true;
      this.error.userProfile = null;
      try {
        const response = await api.getUserProfile(this.apiInstance);
        this.currentUser = response;
      } catch (error) {
        this.error.userProfile = error.message || 'Failed to fetch user profile';
      } finally {
        this.loading.userProfile = false;
      }
    },

    async updateUserProfile(profileData) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const response = await api.updateUserProfile(this.apiInstance, profileData);
        this.currentUser = response;
      } catch (error) {
        throw new Error(error.message || 'Failed to update user profile');
      }
    },

    async fetchDeliveryLocations() {
      this.loading.deliveryLocations = true;
      this.error.deliveryLocations = null;
      try {
        const response = await api.getDeliveryLocations(this.apiInstance);
        this.deliveryLocations = response;
      } catch (error) {
        this.error.deliveryLocations = error.message || 'Failed to fetch delivery locations';
      } finally {
        this.loading.deliveryLocations = false;
      }
    },

    async addDeliveryLocation(location) {
      try {
        const response = await api.addDeliveryLocation(this.apiInstance, location);
        this.deliveryLocations.push(response);
      } catch (error) {
        throw new Error(error.message || 'Failed to add delivery location');
      }
    },

    async setDefaultDeliveryLocation(locationId) {
      try {
        await api.setDefaultDeliveryLocation(this.apiInstance, locationId);
        await this.fetchDeliveryLocations();
      } catch (error) {
        throw new Error(error.message || 'Failed to set default delivery location');
      }
    },

    async deleteDeliveryLocation(locationId) {
      try {
        await api.deleteDeliveryLocation(this.apiInstance, locationId);
        this.deliveryLocations = this.deliveryLocations.filter(loc => loc.id !== locationId);
      } catch (error) {
        throw new Error(error.message || 'Failed to delete delivery location');
      }
    },
  },
  persist: {
    key: 'ecommerce-search-history',
    paths: ['recentSearches'],
    storage: localStorage,
  },
});
