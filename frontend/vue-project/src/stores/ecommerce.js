import { defineStore } from 'pinia';
import api from '@/services/api';

let apiInstance = null;

export const useEcommerceStore = defineStore('ecommerce', {
  state: () => {
    const state = {
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
        auth: false,
        profile: false,
        dashboard: false,
      },
      error: {
        categories: null,
        categoryProducts: null,
        productDetails: null,
        allCategoriesWithProducts: null,
        cart: null,
        orders: null,
        completedOrders: null,
        auth: null,
        profile: null,
        dashboard: null,
      },
      userId: localStorage.getItem('userId') || null,
      token: localStorage.getItem('token') || null,
      user: JSON.parse(localStorage.getItem('user')) || null,
      dashboardData: null,
    };

    apiInstance = api.createApiInstance(state);

    return state;
  },
  actions: {
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
        console.log(`Fetching products for category: ${categorySlug}, page: ${page}`);
        const data = await api.fetchCategoryProducts(apiInstance, categorySlug, page);
        console.log(`API response for ${categorySlug} (fetchCategoryProducts):`, data);

        const categoryData = this.allCategoriesWithProducts.find(cat => cat.slug === categorySlug);
        if (categoryData && categoryData.products?.length) {
          console.log(`Pre-fetched products for ${categorySlug} (allCategoriesWithProducts):`, categoryData.products);
          if (data.products.length === 0 && categoryData.products.length > 0) {
            console.warn(`Discrepancy detected: fetchCategoryProducts returned no products, but allCategoriesWithProducts has ${categoryData.products.length} products for ${categorySlug}`);
          }
        } else {
          console.warn(`Category ${categorySlug} not found in allCategoriesWithProducts`);
        }

        if (!this.categoryProducts[categorySlug]) {
          this.categoryProducts[categorySlug] = {
            category: categoryData
              ? { slug: categoryData.slug, name: categoryData.name }
              : data.category || { slug: categorySlug, name: categorySlug },
            products: categoryData?.products || [],
            total: categoryData?.products?.length || data.total || 0,
          };
        }

        const existingProductIds = new Set(
          this.categoryProducts[categorySlug].products.map(p => p.id)
        );
        const uniqueNewProducts = data.products.filter(
          product => !existingProductIds.has(product.id)
        );

        this.categoryProducts[categorySlug].products.push(...uniqueNewProducts);
        if (data.total > this.categoryProducts[categorySlug].total) {
          this.categoryProducts[categorySlug].total = data.total;
        }
        console.log(`Updated products for ${categorySlug}:`, this.categoryProducts[categorySlug].products);
      } catch (error) {
        this.error.categoryProducts = error.message || `Failed to load products for ${categorySlug}`;
        console.error(`Error fetching products for ${categorySlug}:`, error);
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

    async fetchCartData() {
      if (!this.userId) throw new Error('User ID not set');
      this.loading.cart = true;
      this.error.cart = null;
      try {
        const cart = await api.fetchCart(apiInstance, this.userId);
        this.cart = cart;
      } catch (error) {
        this.error.cart = error.message || 'Failed to load cart';
      } finally {
        this.loading.cart = false;
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

    async login(credentials) {
      this.loading.auth = true;
      this.error.auth = null;
      try {
        const response = await api.login(apiInstance, credentials);
        this.token = response.token;
        this.userId = response.user_id;
        this.user = { id: response.user_id, username: response.username, email: response.email, user_type: response.user_type };
        localStorage.setItem('token', response.token);
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('user', JSON.stringify(this.user));
        apiInstance = api.createApiInstance(this);
      } catch (error) {
        this.error.auth = error.message || 'Login failed';
        throw error;
      } finally {
        this.loading.auth = false;
      }
    },

    async register(userData) {
      this.loading.auth = true;
      this.error.auth = null;
      try {
        const response = await api.register(apiInstance, userData);
        this.token = response.token;
        this.userId = response.user_id;
        this.user = { id: response.user_id, username: response.username, email: response.email, user_type: response.user_type };
        localStorage.setItem('token', response.token);
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('user', JSON.stringify(this.user));
        apiInstance = api.createApiInstance(this);
      } catch (error) {
        this.error.auth = error.message || 'Registration failed';
        throw error;
      } finally {
        this.loading.auth = false;
      }
    },

    async adminLogin(credentials) {
      this.loading.auth = true;
      this.error.auth = null;
      try {
        const response = await api.adminLogin(apiInstance, credentials);
        this.token = response.token;
        this.userId = response.user_id;
        this.user = { id: response.user_id, username: response.username, email: response.email, user_type: response.user_type };
        localStorage.setItem('token', response.token);
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('user', JSON.stringify(this.user));
        apiInstance = api.createApiInstance(this);
      } catch (error) {
        this.error.auth = error.message || 'Admin login failed';
        throw error;
      } finally {
        this.loading.auth = false;
      }
    },

    async adminRegister(userData) {
      this.loading.auth = true;
      this.error.auth = null;
      try {
        const response = await api.adminRegister(apiInstance, userData);
        this.token = response.token;
        this.userId = response.user_id;
        this.user = { id: response.user_id, username: response.username, email: response.email, user_type: response.user_type };
        localStorage.setItem('token', response.token);
        localStorage.setItem('userId', response.user_id);
        localStorage.setItem('user', JSON.stringify(this.user));
        apiInstance = api.createApiInstance({ userId: this.userId, token: this.token });
      } catch (error) {
        error.value.auth = error.message || 'Admin registration failed';
        throw error;
      } finally {
        this.loading.auth = false;
      }
    },

    async logout() {
      this.loading.auth = true;
      try {
        await api.logout(apiInstance);
      } catch (error) {
        console.error('Logout failed:', error);
      } finally {
        this.token = null;
        this.userId = null;
        this.user = null;
        this.cart = null;
        this.orders = [];
        this.completedOrders = [];
        localStorage.removeItem('token');
        localStorage.removeItem('userId');
        localStorage.removeItem('user');
        apiInstance = api.createApiInstance(this);
        this.loading.auth = false;
      }
    },

    async fetchProfile() {
      this.loading.profile = true;
      this.error.profile = null;
      try {
        const response = await api.fetchProfile(apiInstance);
        this.user = response;
        localStorage.setItem('user', JSON.stringify(this.user));
      } catch (error) {
        this.error.profile = error.message || 'Failed to load profile';
      } finally {
        this.loading.profile = false;
      }
    },

    async updateProfile(userData) {
      this.loading.profile = true;
      this.error.profile = null;
      try {
        const response = await api.updateProfile(apiInstance, userData);
        this.user = response;
        localStorage.setItem('user', JSON.stringify(this.user));
      } catch (error) {
        this.error.profile = error.message || 'Failed to update profile';
        throw error;
      } finally {
        this.loading.profile = false;
      }
    },

    async fetchDashboardData() {
      this.loading.dashboard = true;
      this.error.dashboard = null;
      try {
        const data = await api.fetchDashboardData(apiInstance);
        this.dashboardData = data;
      } catch (error) {
        this.error.dashboard = error.message || 'Failed to load dashboard data';
      } finally {
        this.loading.dashboard = false;
      }
    },

    isAdmin() {
      // Check if the user is an admin
      return this.user && (this.user.user_type === 'admin' || !('user_type' in this.user));
    },

    setUserId(userId) {
      this.userId = userId;
      localStorage.setItem('userId', userId);
      apiInstance = api.createApiInstance(this);
    },
  },
  getters: {
    cartTotal: (state) => {
      return state.cart?.items?.reduce((sum, item) => sum + item.line_total, 0) || 0;
    },
    cartItemCount: (state) => {
      return state.cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;
    },
    isAuthenticated: (state) => !!state.token,
  },
});
