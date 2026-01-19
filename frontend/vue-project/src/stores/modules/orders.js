import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApiCall } from '../composables/useApiCall';
import { useApiInstance } from '../composables/useApiInstance';
import { toast } from '../composables/useToast';

/**
 * Orders Store Module
 * Handles order management, order history, and order tracking
 */
export const useOrdersStore = defineStore('orders', () => {
  // State
  const orders = ref([]);
  const currentOrder = ref(null);
  const isLoadingOrders = ref(false);
  const isLoadingOrder = ref(false);
  const isCreatingOrder = ref(false);

  // Pagination
  const currentPage = ref(1);
  const totalPages = ref(1);
  const totalOrders = ref(0);

  // API instance
  const { api } = useApiInstance();

  // Computed
  const hasOrders = computed(() => orders.value.length > 0);
  const pendingOrders = computed(() =>
    orders.value.filter(order => order.status === 'pending')
  );
  const completedOrders = computed(() =>
    orders.value.filter(order => order.status === 'completed' || order.status === 'delivered')
  );

  /**
   * Fetch user's orders
   * @param {number} page - Page number
   */
  const fetchOrders = async (page = 1) => {
    const { execute } = useApiCall();
    isLoadingOrders.value = true;

    try {
      const params = {
        page,
        page_size: 10,
      };

      const response = await execute(
        async () => api.get('/orders/', { params }),
        { showToast: false }
      );

      orders.value = response.results || response;
      currentPage.value = page;
      totalPages.value = response.total_pages || 1;
      totalOrders.value = response.count || orders.value.length;
    } catch (error) {
      toast.error('Failed to load orders');
      console.error('Fetch orders error:', error);
    } finally {
      isLoadingOrders.value = false;
    }
  };

  /**
   * Fetch order by ID
   * @param {number} orderId - Order ID
   */
  const fetchOrder = async (orderId) => {
    const { execute } = useApiCall();
    isLoadingOrder.value = true;

    try {
      const response = await execute(
        async () => api.get(`/orders/${orderId}/`),
        { showToast: false }
      );

      currentOrder.value = response;
      return response;
    } catch (error) {
      toast.error('Failed to load order details');
      console.error('Fetch order error:', error);
      return null;
    } finally {
      isLoadingOrder.value = false;
    }
  };

  /**
   * Create new order
   * @param {Object} orderData - Order data
   */
  const createOrder = async (orderData) => {
    const { execute } = useApiCall();
    isCreatingOrder.value = true;

    try {
      const response = await execute(
        async () => api.post('/orders/', orderData),
        {
          successMessage: 'Order created successfully',
        }
      );

      // Add to orders list
      orders.value.unshift(response);
      currentOrder.value = response;

      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to create order';
      toast.error(message);
      return null;
    } finally {
      isCreatingOrder.value = false;
    }
  };

  /**
   * Cancel order
   * @param {number} orderId - Order ID
   */
  const cancelOrder = async (orderId) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.post(`/orders/${orderId}/cancel/`),
        {
          successMessage: 'Order cancelled successfully',
        }
      );

      // Update order in list
      const index = orders.value.findIndex(o => o.id === orderId);
      if (index !== -1) {
        orders.value[index] = response;
      }

      // Update current order if it's the same
      if (currentOrder.value?.id === orderId) {
        currentOrder.value = response;
      }

      return true;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to cancel order';
      toast.error(message);
      return false;
    }
  };

  /**
   * Track order status
   * @param {string} trackingNumber - Tracking number
   */
  const trackOrder = async (trackingNumber) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get(`/orders/track/${trackingNumber}/`),
        { showToast: false }
      );

      return response;
    } catch (error) {
      toast.error('Failed to track order');
      console.error('Track order error:', error);
      return null;
    }
  };

  /**
   * Get order invoice
   * @param {number} orderId - Order ID
   */
  const getOrderInvoice = async (orderId) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get(`/orders/${orderId}/invoice/`, {
          responseType: 'blob',
        }),
        { showToast: false }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice-${orderId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Invoice downloaded');
      return true;
    } catch (error) {
      toast.error('Failed to download invoice');
      console.error('Get invoice error:', error);
      return false;
    }
  };

  /**
   * Reorder - create new order from existing order
   * @param {number} orderId - Order ID to reorder
   */
  const reorder = async (orderId) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.post(`/orders/${orderId}/reorder/`),
        {
          successMessage: 'Items added to cart',
        }
      );

      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to reorder';
      toast.error(message);
      return null;
    }
  };

  /**
   * Go to next page
   */
  const nextPage = async () => {
    if (currentPage.value < totalPages.value) {
      await fetchOrders(currentPage.value + 1);
    }
  };

  /**
   * Go to previous page
   */
  const previousPage = async () => {
    if (currentPage.value > 1) {
      await fetchOrders(currentPage.value - 1);
    }
  };

  /**
   * Go to specific page
   * @param {number} page - Page number
   */
  const goToPage = async (page) => {
    if (page >= 1 && page <= totalPages.value) {
      await fetchOrders(page);
    }
  };

  /**
   * Clear current order
   */
  const clearCurrentOrder = () => {
    currentOrder.value = null;
  };

  /**
   * Update order shipping method and delivery location
   * @param {number} orderId - Order ID
   * @param {number|null} shippingMethodId - Shipping method ID
   * @param {number} deliveryLocationId - Delivery location ID
   */
  const updateOrderShipping = async (orderId, shippingMethodId, deliveryLocationId) => {
    const { execute } = useApiCall();

    try {
      const payload = {
        delivery_location_id: deliveryLocationId,
      };
      if (shippingMethodId) {
        payload.shipping_method_id = shippingMethodId;
      }

      const response = await execute(
        async () => api.patch(`/orders/${orderId}/update_shipping/`, payload),
        { showToast: false }
      );

      // Update current order if it's the same
      if (currentOrder.value?.id === orderId) {
        currentOrder.value = response;
      }

      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to update shipping';
      toast.error(message);
      throw error;
    }
  };

  /**
   * Initiate M-Pesa payment for order
   * @param {number} orderId - Order ID
   * @param {string} phoneNumber - Phone number for M-Pesa
   */
  const initiatePayment = async (orderId, phoneNumber) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.post(`/orders/${orderId}/initiate_payment/`, {
          phone_number: phoneNumber,
        }),
        { showToast: false }
      );

      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to initiate payment';
      toast.error(message);
      throw error;
    }
  };

  /**
   * Get order status color for UI
   * @param {string} status - Order status
   * @returns {string} - Color class
   */
  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      processing: 'info',
      shipped: 'primary',
      delivered: 'success',
      cancelled: 'danger',
      refunded: 'secondary',
    };
    return colors[status] || 'secondary';
  };

  return {
    // State
    orders,
    currentOrder,
    isLoadingOrders,
    isLoadingOrder,
    isCreatingOrder,
    currentPage,
    totalPages,
    totalOrders,

    // Computed
    hasOrders,
    pendingOrders,
    completedOrders,

    // Actions
    fetchOrders,
    fetchOrder,
    createOrder,
    cancelOrder,
    trackOrder,
    getOrderInvoice,
    reorder,
    nextPage,
    previousPage,
    goToPage,
    clearCurrentOrder,
    getStatusColor,
    updateOrderShipping,
    initiatePayment,
  };
});
