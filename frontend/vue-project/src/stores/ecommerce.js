import { defineStore } from 'pinia';
import api from '@/services/api';

export const useEcommerceStore = defineStore('ecommerce', {
  state: () => {
    const state = {
      authToken: localStorage.getItem('authToken') || null,
      currentUser: null,
      userId: null,
      apiInstance: null,
      cart: null,
      isLoggingOut: false,
      cartItems: [], 
      userLoading: false,
      userError: null,
      showAuthModal: false,
      searchResults: [],
      totalSearchResults: 0,
      searchLoading: false,
      recentSearches: JSON.parse(localStorage.getItem("recentSearches")) || [],
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
        auth: false,
        profile: false,
        dashboard: false,
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
        auth: null,
        profile: null,
        dashboard: null,
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
    isAuthenticated: (state) => !!state.authToken,
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

    async adminLogin(credentials) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.auth = true;
      this.error.auth = null;
      try {
        const response = await api.adminLogin(this.apiInstance, credentials);
        if (!response.token) {
          throw new Error('No token received from server');
        }
        this.authToken = response.token;
        this.userId = response.user_id;
        this.currentUser = {
          id: response.user_id,
          username: response.username,
          user_type: response.user_type,
        };
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
        this.apiInstance = api.createApiInstance(this);
        return response;
      } catch (error) {
        this.error.auth = error.response?.data?.error || error.message || 'Admin login failed';
        throw error;
      } finally {
        this.loading.auth = false;
      }
    },
    async adminRegister(userData) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.auth = true;
      this.error.auth = null;
      try {
        const response = await api.adminRegister(this.apiInstance, userData);
        this.authToken = response.token;
        this.userId = response.user_id;
        this.currentUser = {
          id: response.user_id,
          username: response.username,
          email: response.email,
          user_type: response.user_type,
        };
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
        this.apiInstance = api.createApiInstance(this);
        return response;
      } catch (error) {
        this.error.auth = error.response?.data?.error || error.message || 'Admin registration failed';
        throw error;
      } finally {
        this.loading.auth = false;
      }
    },

    async fetchProfile() {
      this.loading.profile = true;
      this.error.profile = null;
      try {
        const response = await api.fetchProfile(this.apiInstance);
        this.currentUser = response;
        localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
        return response;
      } catch (error) {
        this.error.profile = error.response?.data?.error || error.message || 'Failed to load profile';
        throw error;
      } finally {
        this.loading.profile = false;
      }
    },
    async updateProfile(userData) {
      this.loading.profile = true;
      this.error.profile = null;
      try {
        const response = await api.updateProfile(this.apiInstance, userData);
        this.currentUser = response;
        localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
        return response;
      } catch (error) {
        this.error.profile = error.response?.data?.error || error.message || 'Failed to update profile';
        throw error;
      } finally {
        this.loading.profile = false;
      }
    },
    async fetchDashboardData() {
      this.loading.dashboard = true;
      this.error.dashboard = null;
      try {
        const response = await api.fetchDashboardData(this.apiInstance);
        this.dashboardData = response;
        return response;
      } catch (error) {
        this.error.dashboard = error.response?.data?.error || error.message || 'Failed to load dashboard data';
        throw error;
      } finally {
        this.loading.dashboard = false;
      }
    },
    isAdmin() {
      return this.currentUser && this.currentUser.user_type === 'admin';
    },


    async login(username, password) {
      try {
        if (!this.apiInstance) {
          this.initializeApiInstance();
        }
        const response = await api.login(this.apiInstance, username, password);
        this.authToken = response.token; // Set authToken (assumes response includes token)
        localStorage.setItem('authToken', response.token); // Sync with localStorage
        this.userId = response.user_id;
        this.currentUser = {
          id: response.user_id,
          username: response.username,
        };
        await this.fetchCurrentUserInfo();
        await this.syncCartWithBackend();
        return response;
      } catch (error) {
        console.error('Login failed:', error);
        this.showAuthModal = true;
        throw error;
      }
    },

    async googleLogin(idToken) {
      try {
        if (!this.apiInstance) {
          this.initializeApiInstance();
        }
        const response = await api.googleAuth(this.apiInstance, idToken); // Assumes api.googleAuth exists
        this.authToken = response.token; // Set authToken from Google auth response
        localStorage.setItem('authToken', response.token); // Sync with localStorage
        this.userId = response.user_id;
        this.currentUser = {
          id: response.user_id,
          username: response.username,
        };
        await this.fetchCurrentUserInfo();
        await this.syncCartWithBackend();
        return response;
      } catch (error) {
        console.error('Google login failed:', error);
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
        if (this.currentUser) return this.currentUser;
        if (!this.apiInstance) {
          this.initializeApiInstance();
        }
        const userData = await api.fetchCurrentUserInfo(this.apiInstance);
        this.userId = userData.id;
        this.currentUser = {
          id: userData.id,
          username: userData.username,
          email: userData.email,
          first_name: userData.first_name,
          last_name: userData.last_name,
          phone_number: userData.phone_number || '',
        };
        await this.fetchCart();
        return userData;
      } catch (error) {
        console.error('Authentication check failed:', error);
        this.showAuthModal = true;
        throw error;
      }
    },

    async changePassword(currentPassword, newPassword, confirmPassword) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const response = await this.apiInstance.post('auth/change-password/', {
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        });
        return response.data;
      } catch (error) {
        throw new Error(error.response?.data?.error || 'Failed to change password');
      }
    },
    async logout() {
      if (this.isLoggingOut) return;
      this.isLoggingOut = true;
      try {
        if (this.apiInstance && this.isAuthenticated) {
          await api.logout(this.apiInstance);
        }
      } catch (error) {
        console.error('Logout error:', error.response?.data || error.message);
      } finally {
        this.authToken = null; // Clear authToken from state
        this.userId = null;
        this.currentUser = null;
        this.cart = null;
        this.orders = [];
        this.completedOrders = [];
        this.deliveryLocations = [];
        localStorage.removeItem('authToken');
        this.cartItems = this.loadCartFromLocalStorage();
        this.initializeApiInstance();
        this.isLoggingOut = false;
      }
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

    async createOrderFromCart() {
      try {
        if (!this.cart || !this.cart.id) {
          throw new Error('No active cart found');
        }
        const response = await this.apiInstance.post(`/carts/${this.cart.id}/create-order/`);
        const order = response.data;
        this.cart = null;
        this.cartItems = [];
        localStorage.removeItem('cartItems');
        return order;
      } catch (error) {
        console.error('Create order error:', error);
        throw error;
      }
    },

    // New method: Fetch order details
    async fetchOrder(orderId) {
      try {
        const response = await this.apiInstance.get(`/orders/${orderId}/`);
        return response.data;
      } catch (error) {
        console.error('Fetch order error:', error);
        throw error;
      }
    },

    // New method: Update order shipping details
    async updateOrderShipping(orderId, shippingMethod, deliveryLocationId) {
      try {
        const response = await this.apiInstance.put(`/orders/${orderId}/update-shipping/`, {
          shipping_method: shippingMethod,
          delivery_location_id: deliveryLocationId,
        });
        return response.data;
      } catch (error) {
        console.error('Update order shipping error:', error);
        throw error;
      }
    },

    // New method: Initiate M-Pesa payment
    async initiatePayment(orderId, phoneNumber) {
      try {
        const response = await this.apiInstance.post(`/process-payment/`, {
          order_id: orderId,
          phone_number: phoneNumber,
        });
        return response.data;
      } catch (error) {
        console.error('Initiate payment error:', error);
        throw error;
      }
    },

    // New method: Verify payment status
    async verifyPayment(orderId) {
      try {
        const response = await this.apiInstance.get(`/payment-details/${orderId}/`);
        return response.data;
      } catch (error) {
        console.error('Verify payment error:', error);
        throw error;
      }
    },

    // Updated checkout method (renamed from checkout)
    async checkoutCart(checkoutData) {
      try {
        if (!this.cart || !this.cart.id) {
          throw new Error('No active cart found');
        }
        const response = await this.apiInstance.post(`/carts/${this.cart.id}/checkout/`, checkoutData);
        this.cart = null;
        this.cartItems = [];
        localStorage.removeItem('cartItems');
        await this.fetchOrdersData();
        return response.data;
      } catch (err) {
        console.error('Checkout error:', err);
        throw err;
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
        this.addRecentSearch(query); 
        return response;
      } catch (error) {
        console.error('Error searching products:', error);
        throw error;
      } finally {
        this.setSearchLoading(false);
      }
    },

    async fetchSearchSuggestions(query) {
      try {
        const response = await fetch(
          `http://localhost:8000/api/products/search/?search=${encodeURIComponent(query)}&page=1&per_page=5&ordering=-created_at`
        );
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        this.searchSuggestions = data.results || [];
        console.log('Suggestions fetched:', this.searchSuggestions); // Debugging
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
        this.recentSearches.unshift(trimmedQuery);
        if (this.recentSearches.length > 3) {
          this.recentSearches.pop();
        }
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



    async fetchUserProfile() {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        this.loading.userProfile = true;
        const userData = await api.getUserProfile(this.apiInstance);
        this.userId = userData.id; // Set userId
        this.currentUser = {
          id: userData.id, // Set currentUser.id
          username: userData.username,
          email: userData.email,
          first_name: userData.first_name,
          last_name: userData.last_name,
          phone_number: userData.phone_number || '',
        };
        return userData;
      } catch (error) {
        this.error.userProfile = error.message || 'Failed to fetch user profile';
        throw error;
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
        this.currentUser = {
          ...this.currentUser,
          ...response, 
        };
        return response;
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
        return response;
      } catch (error) {
        this.error.deliveryLocations = error.message || 'Failed to fetch delivery locations';
        return [];
      } finally {
        this.loading.deliveryLocations = false;
      }
    },

    async addDeliveryLocation(location) {
      try {
        const response = await api.addDeliveryLocation(this.apiInstance, location);
        this.deliveryLocations.push(response);
        return response; 
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
