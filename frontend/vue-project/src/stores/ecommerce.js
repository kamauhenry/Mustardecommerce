import { defineStore } from 'pinia';
import api from '@/services/api';
import { toast } from 'vue3-toastify';

export const useEcommerceStore = defineStore('ecommerce', {
  state: () => {
    const state = {
      authToken: localStorage.getItem('authToken') || null,
      currentUser: JSON.parse(localStorage.getItem('currentUser')) || null,
      userId: localStorage.getItem('userId') || null,
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
      orderSearchSuggestions: [],
      orderSearchResults: [],
      orderSearchLoading: false,
      pickupCategories: JSON.parse(localStorage.getItem('pickupCategories')) || [],
      pickupCategoriesPagination: { nextPage: 1, hasMore: false, totalCount: 0 },
      recentSearches: JSON.parse(localStorage.getItem("recentSearches")) || [],
      searchSuggestions: [],
      categories: [],
      relatedProducts: {},
      categoryProducts: {},
      allCategoriesWithProducts: [],
      allhomeCategoriesWithProducts: [],
      homeCategoriesPagination: {
        nextPage: 1,
        hasMore: true,
        totalCount: 0,
      },
      deliveryLocations: [],
      productDetails: {},
      orders: [],
      completedOrders: [],
      dashboardData: null,
      payAndPickCart: JSON.parse(localStorage.getItem('payAndPickCart')) || [],
      loading: {
        categories: false,
        categoryProducts: false,
        productDetails: false,
        relatedProducts: false,
        allCategoriesWithProducts: false,
        allhomeCategoriesWithProducts: false,
        cart: false,
        orders: false,
        completedOrders: false,
        userProfile: false,
        deliveryLocations: false,
        auth: false,
        profile: false,
        dashboard: false,
        pickupCategories: false,
      },
      error: {
        categories: null,
        categoryProducts: {},
        relatedProducts: {},
        productDetails: null,
        allCategoriesWithProducts: null,
        allhomeCategoriesWithProducts: null,
        cart: null,
        orders: null,
        completedOrders: null,
        userProfile: null,
        deliveryLocations: null,
        auth: null,
        profile: null,
        dashboard: null,
        pickupCategories: null,
      },
    };

    // Load cartItems from localStorage for unauthenticated users
    const storedCart = localStorage.getItem('cartItems');
    if (storedCart) {
      state.cartItems = JSON.parse(storedCart);
    }

    // Initialize apiInstance if authToken exists
    if (state.authToken && !state.apiInstance) {
      console.log('Initializing apiInstance on store creation due to existing authToken');
      state.apiInstance = api.createApiInstance(state);
      if (!state.userId) {
        setTimeout(async () => {
          try {
            const userData = await api.fetchCurrentUserInfo(state.apiInstance);
            state.userId = userData.id;
            state.currentUser = {
              id: userData.id,
              username: userData.username,
              email: userData.email,
              first_name: userData.first_name,
              last_name: userData.last_name,
              phone_number: userData.phone_number || '',
            };
            localStorage.setItem('userId', userData.id);
            localStorage.setItem('currentUser', JSON.stringify(state.currentUser));
            console.log('User info fetched on store init:', userData);
          } catch (error) {
            console.error('Failed to fetch user info on store init:', error);
            localStorage.removeItem('authToken');
            localStorage.removeItem('userId');
            localStorage.removeItem('currentUser');
            state.authToken = null;
            state.userId = null;
            state.currentUser = null;
          }
        }, 0);
      }
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
    isAdmin: (state) => {
      return state.currentUser && state.currentUser.user_type === 'admin';
    },
  },
  actions: {
    initializeApiInstance() {
      console.log('Initializing apiInstance');
      this.apiInstance = api.createApiInstance(this);
      console.log('apiInstance initialized:', this.apiInstance);
    },
    setUserId(userId) {
      this.userId = userId;
      localStorage.setItem('userId', userId);
      this.initializeApiInstance();
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
        this.initializeApiInstance();
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
        this.initializeApiInstance();
        return response;
      } catch (error) {
        this.error.auth = error.response?.data?.error || error.message || 'Admin registration failed';
        throw error;
      } finally {
        this.loading.auth = false;
      }
    },

    async fetchProfile() {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
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
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
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
      if (!this.apiInstance) {
        console.log('apiInstance is null, initializing...');
        this.initializeApiInstance();
      }
      if (!this.apiInstance) {
        throw new Error('Failed to initialize apiInstance');
      }
      this.loading.dashboard = true;
      this.error.dashboard = null;
      try {
        console.log('Fetching dashboard data for user:', this.currentUser);
        const response = await api.fetchDashboardData(this.apiInstance);
        this.dashboardData = response;
        console.log('Dashboard data loaded:', this.dashboardData);
        return response;
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message || 'Failed to load dashboard data';
        this.error.dashboard = errorMessage;
        console.error('Fetch dashboard data error:', {
          status: error.response?.status,
          message: errorMessage,
          user: this.currentUser,
        });
        if (error.response?.status === 403 && errorMessage.includes('Only admins can access this endpoint')) {
          console.log('User is not an admin, logging out...');
          await this.logout();
        }
        throw new Error(errorMessage);
      } finally {
        this.loading.dashboard = false;
      }
    },

    async login(username, password) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const response = await api.login(this.apiInstance, username, password);
        console.log('Login response:', response);
        this.authToken = response.token;
        localStorage.setItem('authToken', response.token);
        this.userId = response.user_id;
        this.currentUser = {
          id: response.user_id,
          username: response.username,
        };
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('currentUser', JSON.stringify(this.currentUser));

        // Attempt to fetch user info
        try {
          console.log('Fetching user info...');
          await this.fetchCurrentUserInfo();

        } catch (userInfoError) {
          console.error('Failed to fetch user info after login:', userInfoError.response?.data || userInfoError.message);
          console.log('done')
        }

        // Attempt to sync cart
        try {
          console.log('Syncing cart...');
          await this.syncCartWithBackend();
           console.log('done2')
        } catch (cartError) {
          console.error('Failed to sync cart after login:', cartError.response?.data || cartError.message);
        }

        return response;
      } catch (error) {
        console.error('Login failed:', error.response?.data || error.message);
        this.showAuthModal = true;
        throw error;
      }
    },

    async googleLogin(idToken) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const response = await api.googleAuth(this.apiInstance, idToken);
        this.authToken = response.token;
        localStorage.setItem('authToken', response.token);
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
      if (!this.isAuthenticated) {
        this.showAuthModal = true;
        this.cartItems = this.loadCartFromLocalStorage();
        return null;
      }
      if (this.currentUser && this.userId) {
        return this.currentUser;
      }
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const userData = await api.fetchCurrentUserInfo(this.apiInstance);
        console.log('fetchCurrentUserInfo response:', userData);
        if (!userData.id) {
          throw new Error('User info response does not include id');
        }
        this.userId = userData.id;
        this.currentUser = {
          id: userData.id,
          username: userData.username,
          email: userData.email,
          first_name: userData.first_name,
          last_name: userData.last_name,
          phone_number: userData.phone_number || '',
        };
        localStorage.setItem('userId', userData.id);
        localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
        await this.fetchCart();
        return userData;
      } catch (error) {
        console.error('Authentication check failed:', error);
        this.showAuthModal = true;
        this.cartItems = this.loadCartFromLocalStorage();
        localStorage.removeItem('authToken');
        localStorage.removeItem('userId');
        localStorage.removeItem('currentUser');
        this.authToken = null;
        this.userId = null;
        this.currentUser = null;
        return null;
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
        this.authToken = null;
        this.userId = null;
        this.currentUser = null;
        this.cart = null;
        this.orders = [];
        this.completedOrders = [];
        this.deliveryLocations = [];
        this.dashboardData = null;
        localStorage.removeItem('authToken');
        this.cartItems = this.loadCartFromLocalStorage();
        this.apiInstance = null;
        this.isLoggingOut = false;
      }
    },
    async createCart() {
      if (!this.isAuthenticated || !this.userId) {
        console.warn('Cannot create cart: User is not authenticated or userId is missing');
        this.showAuthModal = true;
        throw new Error('No user logged in');
      }
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        console.log(`Creating cart for userId: ${this.userId}`);
        const newCart = await api.createCart(this.apiInstance, this.userId);
        console.log('Cart created:', newCart);
        this.cart = newCart;
        this.cartItems = newCart.items || [];
        localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
        return newCart;
      } catch (error) {
        console.error('Failed to create cart:', error.response?.data || error.message);
        if (error.response && error.response.status === 403) {
          this.showAuthModal = true;
        }
        throw error;
      }
    },

    async addToCart(productId, attributes, quantity = 1, affiliateCode, shippingMethodId) {
      if (!this.isAuthenticated || !this.userId) {
        console.warn('Adding to local cart: User is not authenticated or userId is missing');
        const newItem = { product_id: productId, attributes, quantity };
        this.cartItems.push(newItem);
        localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
        toast.success('Item added to your local cart. Please log in to sync with your account.', { autoClose: 3000 });
        return;
      }
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        if (!this.cart) {
          try {
            this.cart = await api.fetchCart(this.apiInstance, this.userId);
            console.log('Fetched existing cart:', this.cart);
          } catch (error) {
            console.log('No existing cart found, creating new cart');
            await this.createCart();
            if (!this.cart) this.cart = { id: null, items: [] };
          }
        }
        const response = await api.addToCart(
          this.apiInstance,
          this.cart.id,
          productId,
          attributes,
          quantity,
          shippingMethodId
        );
        console.log('Add to cart response:', response);
        this.cart = response || { id: this.cart.id, items: [] };
        this.cartItems = this.cart.items || [];
        localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
        toast.success('Item added to cart!', { autoClose: 2000 });
        return response;
      } catch (error) {
        console.error('Add to cart error:', error.response?.data || error.message);
        if (error.response && error.response.status === 403) {
          this.showAuthModal = true;
        }
        throw error;
      }
    },
    async fetchLatestProducts(limit) {
      const response = await axios.get(`http://127.0.0.1:8000//api/products/latest/?limit=${limit}`, {
        headers: {

        },
      });
      return response.data;
    },

    async fetchCart() {
      if (!this.isAuthenticated || !this.userId) {
        console.warn('Skipping fetchCart: User is not authenticated or userId is missing');
        this.cartItems = this.loadCartFromLocalStorage();
        this.cart = null;
        return;
      }
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.cart = true;
      this.error.cart = null;
      try {
        console.log(`Fetching cart for userId: ${this.userId}`);
        const response = await api.fetchCart(this.apiInstance, this.userId);
        console.log('Fetch cart response:', response);
        this.cart = response || { id: null, items: [] };
        this.cartItems = response.items || [];
        localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
      } catch (error) {
        console.error('Failed to fetch cart:', error.response?.data || error.message);
        this.error.cart = error.response?.data?.error || 'Failed to fetch cart';
        this.cartItems = this.loadCartFromLocalStorage();
        this.cart = null;
        if (error.response?.status === 404) {
          console.log('Cart not found, attempting to create new cart');
          await this.createCart();
        }
      } finally {
        this.loading.cart = false;
      }
    },

    loadCartFromLocalStorage() {
      const storedCart = localStorage.getItem('cartItems');
      return storedCart ? JSON.parse(storedCart) : [];
    },

    async syncCartWithBackend() {
      if (!this.isAuthenticated || !this.cartItems.length) return;
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        if (!this.cart) {
          await this.createCart();
        }
        for (const item of this.cartItems) {
          await api.addToCart(
            this.apiInstance,
            this.cart.id,
            item.product_id,
            item.attributes,
            item.quantity
          );
        }
        await this.fetchCart();
        localStorage.removeItem('cartItems');
        toast.success('Cart synced with backend!', { autoClose: 2000 });
      } catch (error) {
        console.error('Failed to sync cart with backend:', error.response?.data || error.message);
        toast.error('Failed to sync cart with backend', { autoClose: 3000 });
      }
    },

    async createOrderFromCart() {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        if (!this.cart || !this.cart.id) {
          throw new Error('No active cart found');
        }
        console.log('Creating order for cart:', this.cart.id);
        const response = await this.apiInstance.post(`/carts/${this.cart.id}/create-order/`);
        const order = response.data;
        console.log('Order created:', order.order_number);
        this.cart = null;
        this.cartItems = [];
        localStorage.removeItem('cartItems');
        await this.fetchOrdersData();
        return order;
      } catch (error) {
        console.error('Create order error:', error.response?.data || error.message);
        throw error;
      }
    },

    async fetchOrder(orderId) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const cleanOrderId = orderId.replace(/^MI/, '');
        const response = await this.apiInstance.get(`/orders/${cleanOrderId}/`);
        return response.data;
      } catch (error) {
        console.error('Fetch order error:', error.response?.data || error.message);
        throw error;
      }
    },

    async updateOrderShipping(orderId, shippingMethodId, deliveryLocationId) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const response = await this.apiInstance.put(`/orders/${orderId}/update-shipping/`, {
          shipping_method_id: shippingMethodId,
          delivery_location_id: deliveryLocationId,
        });
        return response.data;
      } catch (error) {
        console.error('Update order shipping error:', error.response?.data || error.message);
        throw error;
      }
    },

    async initiatePayment(orderId, phoneNumber) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const response = await this.apiInstance.post(`/process-payment/`, {
          order_id: orderId,
          phone_number: phoneNumber,
        });
        toast.success('Payment initiated successfully!', { autoClose: 2000 });
        return response.data;
      } catch (error) {
        console.error('Initiate payment error:', error.response?.data || error.message);
        const errorMessage = error.response?.data?.error || 'Failed to initiate payment. Please try again.';
        toast.error(errorMessage, { autoClose: 3000 });
        throw new Error(errorMessage);
      }
    },

    async verifyPayment(orderId) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const response = await this.apiInstance.get(`/payment-details/${orderId}/`);
        return response.data;
      } catch (error) {
        console.error('Verify payment error:', error.response?.data || error.message);
        throw error;
      }
    },

    async checkoutCart(checkoutData) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
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
      } catch (error) {
        console.error('Checkout error:', error.response?.data || error.message);
        throw error;
      }
    },

    async fetchOrdersData() {
      if (!this.isAuthenticated || !this.userId) {
        console.warn('Skipping fetchOrdersData: User is not authenticated or userId is missing');
        this.orders = [];
        this.completedOrders = [];
        return;
      }
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.orders = true;
      this.error.orders = null;
      try {
        const response = await api.fetchOrders(this.apiInstance, this.userId);
        console.log('Fetch orders response:', response);
        this.orders = response || [];
        this.completedOrders = this.orders.filter(order => order.status === 'Completed') || [];
      } catch (error) {
        console.error('Error loading orders:', error.response?.data || error.message);
        this.error.orders = error.response?.data?.error || 'Could not load orders. Please try again.';
        this.orders = [];
        this.completedOrders = [];
        toast.error(this.error.orders, { autoClose: 3000 });
      } finally {
        this.loading.orders = false;
      }
    },

    async fetchCompletedOrdersData() {
      if (!this.userId) {
        this.error.completedOrders = 'User ID not set';
        this.completedOrders = [];
        return;
      }
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.completedOrders = true;
      this.error.completedOrders = null;
      try {
        const data = await api.fetchCompletedOrders(this.apiInstance, this.userId);
        console.log('Fetch completed orders response:', data);
        this.completedOrders = data || [];
      } catch (error) {
        console.error('Error loading completed orders:', error.response?.data || error.message);
        this.error.completedOrders = error.response?.data?.error || 'Failed to load completed orders';
        this.completedOrders = [];
        toast.error(this.error.completedOrders, { autoClose: 3000 });
      } finally {
        this.loading.completedOrders = false;
      }
    },

    async fetchHomeCategories(page = 1, retryCount = 0) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.allhomeCategoriesWithProducts = true;
      this.error.allhomeCategoriesWithProducts = null;
      try {
        const data = await api.fetchHomeCategories(this.apiInstance, page);
       
        if (!data.results || !Array.isArray(data.results)) {
          throw new Error('Expected data.results to be an array');
        }

        this.allhomeCategoriesWithProducts = [
          ...this.allhomeCategoriesWithProducts,
          ...data.results,
        ];
        this.homeCategoriesPagination = {
          nextPage: data.next ? page + 1 : null,
          hasMore: !!data.next,
          totalCount: data.count || 0,
        };

        if (page === 1 && !this.homeCategoriesPagination.hasMore && this.allhomeCategoriesWithProducts.length === 0) {
          throw new Error('No categories found on page 1');
        }

        
      } catch (error) {
        if (retryCount < 3) {
          console.warn(`Page ${page} - Retrying fetch, attempt ${retryCount + 1}`);
          await new Promise(resolve => setTimeout(resolve, 1000));
          return this.fetchHomeCategories(page, retryCount + 1);
        }
        this.error.allhomeCategoriesWithProducts = error.message || 'Failed to load home categories';
        console.error(`Page ${page} - Fetch Home Categories Error:`, error);
        toast.error(this.error.allhomeCategoriesWithProducts);
      } finally {
        this.loading.allhomeCategoriesWithProducts = false;
      }
    },
    async fetchAllCategoriesWithProducts() {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.allCategoriesWithProducts = true;
      this.error.allCategoriesWithProducts = null;
      try {
        const data = await api.fetchAllCategoriesWithProducts(this.apiInstance);
        this.allCategoriesWithProducts = data;
      } catch (error) {
        console.error('Fetch Categories Error:', error);
        this.error.allCategoriesWithProducts = error.message || 'Failed to load categories with products';
      } finally {
        this.loading.allCategoriesWithProducts = false;
      }
    },
    // Existing actions
    async fetchPickupCategories(page = 1) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.pickupCategories = true;
      this.error.pickupCategories = null;
      try {
        const data = await api.fetchPickupCategories(this.apiInstance, page);
        if (!data.results || !Array.isArray(data.results)) {
          throw new Error('Expected data.results to be an array');
        }
        this.pickupCategories = [...this.pickupCategories, ...data.results];
        this.pickupCategoriesPagination = {
          nextPage: data.next ? page + 1 : null,
          hasMore: !!data.next,
          totalCount: data.count || 0,
        };
        localStorage.setItem('pickupCategories', JSON.stringify(this.pickupCategories));
      } catch (error) {
        this.error.pickupCategories = error.response?.data?.error || 'Failed to load pickup categories';
        toast.error(this.error.pickupCategories, { autoClose: 3000 });
      } finally {
        this.loading.pickupCategories = false;
      }
    },

    async fetchCategories() {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      this.loading.categories = true;
      this.error.categories = null;
      try {
        const data = await api.fetchCategories(this.apiInstance);
        this.categories = data;
      } catch (error) {
        this.error.categories = error.message || 'Failed to load categories';
      } finally {
        this.loading.categories = false;
      }
    },

    async fetchCategoryProducts(categorySlug) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
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

    async fetchRelatedProducts(categorySlug, productId) {
      const key = `${categorySlug}:${productId}`;
      this.loading.relatedProducts = true;
      this.error.relatedProducts[key] = null;
      try {
        const response = await api.fetchRelatedProducts(this.apiInstance, categorySlug, productId);
        this.relatedProducts[key] = Array.isArray(response) ? response : [];
        this.fetchedRelatedProducts[key] = true;
      } catch (error) {
        this.error.relatedProducts[key] = error.response?.data?.error || error.message || 'Failed to fetch related products';
        this.relatedProducts[key] = [];
        this.fetchedRelatedProducts[key] = false;
        console.error(`Error fetching related products for ${key}:`, error);
      } finally {
        this.loading.relatedProducts = false;
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
          `http://127.0.0.1:8000//api/products/search/?search=${encodeURIComponent(query)}&page=1&per_page=5&ordering=-created_at`
        );
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        this.searchSuggestions = data.results || [];
        console.log('Suggestions fetched:', this.searchSuggestions);
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
        this.userId = userData.id;
        this.currentUser = {
          id: userData.id,
          username: userData.username,
          email: userData.email,
          first_name: userData.first_name,
          last_name: userData.last_name,
          phone_number: userData.phone_number || '',
          profile_photo: userData.profile_photo || '',
          points: userData.points || 0,
          affiliate_code: userData.affiliate_code || '',
          date_joined: userData.date_joined,
        };
        localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
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
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
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
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        const response = await api.addDeliveryLocation(this.apiInstance, location);
        this.deliveryLocations.push(response);
        return response;
      } catch (error) {
        throw new Error(error.message || 'Failed to add delivery location');
      }
    },

    async setDefaultDeliveryLocation(locationId) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        await api.setDefaultDeliveryLocation(this.apiInstance, locationId);
        await this.fetchDeliveryLocations();
      } catch (error) {
        throw new Error(error.message || 'Failed to set default delivery location');
      }
    },

    async deleteDeliveryLocation(locationId) {
      if (!this.apiInstance) {
        this.initializeApiInstance();
      }
      try {
        await api.deleteDeliveryLocation(this.apiInstance, locationId);
        this.deliveryLocations = this.deliveryLocations.filter(loc => loc.id !== locationId);
      } catch (error) {
        throw new Error(error.message || 'Failed to delete delivery location');
      }
    },
      
    async searchAdminOrders(query, status, page = 1, perPage = 10) {
    if (!this.apiInstance) {
      this.initializeApiInstance();
    }
    this.orderSearchLoading = true;
    try {
      const response = await api.searchOrders(this.apiInstance, query, status, page, perPage);
      this.orderSearchResults = response.results || [];
      return response;
    } catch (error) {
      console.error('Error searching admin orders:', error);
      throw error;
    } finally {
      this.orderSearchLoading = false;
    }
    },

    async fetchOrderSearchSuggestions(query) {
    if (!this.apiInstance) {
      this.initializeApiInstance();
    }
    try {
      const suggestions = await api.searchSuggestions(this.apiInstance, query);
      this.orderSearchSuggestions = suggestions;
    } catch (error) {
      console.error('Error fetching order search suggestions:', error);
      this.orderSearchSuggestions = [];
    }
    },
  },
  persist: {
    key: 'ecommerce-search-history',
    paths: ['recentSearches', 'dashboardData','payAndPickCart', 'pickupCategories', 'pickupCategoriesPagination', 'searchResults', 'totalSearchResults', 'searchSuggestions', 'categories', 'relatedProducts', 'categoryProducts', 'allCategoriesWithProducts', 'allhomeCategoriesWithProducts', 'homeCategoriesPagination', 'deliveryLocations', 'productDetails', 'orders', 'completedOrders'],
    storage: localStorage,
  },
});