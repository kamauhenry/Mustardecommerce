// stores/orders.js
import { defineStore } from 'pinia';
import axios from 'axios';

export const useOrderStore = defineStore('orders', {
  state: () => ({
    orders: [],
    completedOrders: [],
  }),
  actions: {
    async fetchOrders() {
      try {
        const response = await axios.get('/api/orders/');
        this.orders = response.data;
      } catch (error) {
        console.error('Error fetching orders:', error);
        this.orders = [];
      }
    },
    async fetchCompletedOrders() {
      try {
        const response = await axios.get('/api/completed-orders/');
        this.completedOrders = response.data;
      } catch (error) {
        console.error('Error fetching completed orders:', error);
        this.completedOrders = [];
      }
    },
    async cancelOrder(orderId) {
      try {
        const response = await axios.post(`/api/orders/${orderId}/cancel/`);
        await this.fetchOrders(); // Refresh orders after cancellation
        return response.data;
      } catch (error) {
        console.error('Error cancelling order:', error);
        throw error;
      }
    },
  },
});
