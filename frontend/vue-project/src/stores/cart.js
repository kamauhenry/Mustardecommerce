// stores/cart.js
import { defineStore } from 'pinia';
import axios from 'axios';

export const useCartStore = defineStore('cart', {
  state: () => ({
    cart: null, // Store the entire cart object (including items, total_items, subtotal)
  }),
  actions: {
    async fetchCart() {
      try {
        const response = await axios.get('/api/cart/');
        this.cart = response.data.length > 0 ? response.data[0] : null; // Take the first cart (user-specific)
      } catch (error) {
        console.error('Error fetching cart:', error);
        this.cart = null;
      }
    },
    async addToCart({ productId, variantId, quantity }) {
      try {
        if (!this.cart) {
          // Create a cart if it doesn't exist
          await axios.post('/api/cart/');
          await this.fetchCart(); // Refresh cart after creation
        }

        const response = await axios.post(`/api/cart/${this.cart.id}/add_item/`, {
          product: productId,
          variant: variantId,
          quantity: quantity,
        });

        this.cart = response.data; // Update the cart with the new data
      } catch (error) {
        console.error('Error adding to cart:', error);
        throw error; // Let the component handle the error
      }
    },
    async removeItem(itemId) {
      try {
        if (!this.cart) return;

        await axios.post(`/api/cart/${this.cart.id}/remove_item/`, {
          item_id: itemId,
        });

        await this.fetchCart(); // Refresh the cart after removal
      } catch (error) {
        console.error('Error removing item from cart:', error);
        throw error;
      }
    },
    async checkout({ shippingMethod, shippingAddress, paymentMethod }) {
      try {
        if (!this.cart) throw new Error('Cart is empty or not found');

        const response = await axios.post(`/api/cart/${this.cart.id}/checkout/`, {
          shipping_method: shippingMethod,
          shipping_address: shippingAddress,
          payment_method: paymentMethod,
        });

        this.cart = null; // Clear the cart after checkout
        return response.data; // Return the created orders
      } catch (error) {
        console.error('Error during checkout:', error);
        throw error;
      }
    },
  },
  getters: {
    cartItems: (state) => (state.cart ? state.cart.items : []),
    totalItems: (state) => (state.cart ? state.cart.total_items : 0),
    subtotal: (state) => (state.cart ? parseFloat(state.cart.subtotal) : 0),
  },
});
