import { defineStore } from 'pinia';
import api from '@/services/api';

// Create an API instance to use throughout the store
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
      userId: localStorage.getItem('userId') || null, // Persist user ID
    };

    // Initialize API instance with the store
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

        // Check if the category exists in allCategoriesWithProducts
        const categoryData = this.allCategoriesWithProducts.find(cat => cat.slug === categorySlug);
        if (categoryData && categoryData.products?.length) {
          console.log(`Pre-fetched products for ${categorySlug} (allCategoriesWithProducts):`, categoryData.products);
          // Compare the data
          if (data.products.length === 0 && categoryData.products.length > 0) {
            console.warn(`Discrepancy detected: fetchCategoryProducts returned no products, but allCategoriesWithProducts has ${categoryData.products.length} products for ${categorySlug}`);
          }
        } else {
          console.warn(`Category ${categorySlug} not found in allCategoriesWithProducts`);
        }

        // Initialize categoryProducts with pre-fetched data if available
        if (!this.categoryProducts[categorySlug]) {
          this.categoryProducts[categorySlug] = {
            category: categoryData
              ? { slug: categoryData.slug, name: categoryData.name }
              : data.category || { slug: categorySlug, name: categorySlug },
            products: categoryData?.products || [], // Initialize with pre-fetched products
            total: categoryData?.products?.length || data.total || 0,
          };
        }

        // Deduplicate products based on their ID
        const existingProductIds = new Set(
          this.categoryProducts[categorySlug].products.map(p => p.id)
        );
        const uniqueNewProducts = data.products.filter(
          product => !existingProductIds.has(product.id)
        );

        // Append only unique products
        this.categoryProducts[categorySlug].products.push(...uniqueNewProducts);
        // Update total if the API provides a higher total
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
        // Notice we're passing the cartId (which is the userId in this case)
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
  getters: {
    cartTotal: (state) => {
      return state.cart?.items?.reduce((sum, item) => sum + item.line_total, 0) || 0;
    },
    cartItemCount: (state) => {
      return state.cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;
    },
    isAuthenticated: (state) => !!state.userId,
  },
});
