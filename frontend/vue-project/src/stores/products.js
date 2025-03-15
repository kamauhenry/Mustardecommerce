// stores/products.js
import { defineStore } from 'pinia';
import axios from 'axios';

export const useProductStore = defineStore('products', {
  state: () => ({
    categories: [],
    products: [],
    currentProduct: null,
    variants: [],
    reviews: [],
  }),
  actions: {
    async fetchCategories() {
      try {
        const response = await axios.get('/api/categories-with-products/');
        this.categories = response.data;
      } catch (error) {
        console.error('Error fetching categories:', error);
        this.categories = [];
      }
    },
    async fetchProductsByCategory(categoryId) {
      try {
        const response = await axios.get(`/api/category-products/${categoryId}/`);
        this.products = response.data.products;
      } catch (error) {
        console.error('Error fetching products by category:', error);
        this.products = [];
      }
    },
    async fetchProduct(categorySlug, productSlug) {
      try {
        const response = await axios.get(`/api/product/${categorySlug}/${productSlug}/`);
        this.currentProduct = response.data;
      } catch (error) {
        console.error('Error fetching product:', error);
        this.currentProduct = null;
      }
    },
    async fetchVariants(productId) {
      try {
        const response = await axios.get(`/api/products/${productId}/variants/`);
        this.variants = response.data;
      } catch (error) {
        console.error('Error fetching variants:', error);
        this.variants = [];
      }
    },
    async fetchReviews(productId) {
      try {
        const response = await axios.get(`/api/products/${productId}/reviews/`);
        this.reviews = response.data;
      } catch (error) {
        console.error('Error fetching reviews:', error);
        this.reviews = [];
      }
    },
  },
});
