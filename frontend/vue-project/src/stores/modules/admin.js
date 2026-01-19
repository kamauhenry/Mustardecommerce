import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApiCall } from '../composables/useApiCall';
import { useApiInstance } from '../composables/useApiInstance';
import { toast } from '../composables/useToast';

/**
 * Admin Store Module
 * Handles admin-specific operations like dashboard stats and management
 */
export const useAdminStore = defineStore('admin', () => {
  // State
  const dashboardStats = ref(null);
  const isLoadingStats = ref(false);

  // API instance
  const { api } = useApiInstance();

  // Computed
  const hasStats = computed(() => dashboardStats.value !== null);

  /**
   * Fetch dashboard data (stats, recent orders, charts)
   */
  const fetchDashboardData = async () => {
    const { execute } = useApiCall();
    isLoadingStats.value = true;

    try {
      const response = await execute(
        async () => api.get('admin-page/dashboard/'),
        { showToast: false }
      );

      dashboardStats.value = response;
      return response;
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error('Fetch dashboard data error:', error);
      throw error;
    } finally {
      isLoadingStats.value = false;
    }
  };

  /**
   * Manage product (create/update/delete)
   * @param {string} action - Action to perform (create/update/delete)
   * @param {Object} productData - Product data
   * @param {number} productId - Product ID (for update/delete)
   */
  const manageProduct = async (action, productData = null, productId = null) => {
    const { execute } = useApiCall();

    try {
      let response;
      let successMessage = '';

      switch (action) {
        case 'create':
          response = await execute(
            async () => api.post('/admin/products/', productData),
            { showToast: false }
          );
          successMessage = 'Product created successfully';
          break;

        case 'update':
          response = await execute(
            async () => api.put(`/admin/products/${productId}/`, productData),
            { showToast: false }
          );
          successMessage = 'Product updated successfully';
          break;

        case 'delete':
          response = await execute(
            async () => api.delete(`/admin/products/${productId}/`),
            { showToast: false }
          );
          successMessage = 'Product deleted successfully';
          break;

        default:
          toast.error('Invalid action');
          return null;
      }

      toast.success(successMessage);
      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     `Failed to ${action} product`;
      toast.error(message);
      return null;
    }
  };

  /**
   * Manage category (create/update/delete)
   * @param {string} action - Action to perform (create/update/delete)
   * @param {Object} categoryData - Category data
   * @param {number} categoryId - Category ID (for update/delete)
   */
  const manageCategory = async (action, categoryData = null, categoryId = null) => {
    const { execute } = useApiCall();

    try {
      let response;
      let successMessage = '';

      switch (action) {
        case 'create':
          response = await execute(
            async () => api.post('/admin/categories/', categoryData),
            { showToast: false }
          );
          successMessage = 'Category created successfully';
          break;

        case 'update':
          response = await execute(
            async () => api.put(`/admin/categories/${categoryId}/`, categoryData),
            { showToast: false }
          );
          successMessage = 'Category updated successfully';
          break;

        case 'delete':
          response = await execute(
            async () => api.delete(`/admin/categories/${categoryId}/`),
            { showToast: false }
          );
          successMessage = 'Category deleted successfully';
          break;

        default:
          toast.error('Invalid action');
          return null;
      }

      toast.success(successMessage);
      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     `Failed to ${action} category`;
      toast.error(message);
      return null;
    }
  };

  /**
   * Update order status
   * @param {number} orderId - Order ID
   * @param {string} status - New status
   */
  const updateOrderStatus = async (orderId, status) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.patch(`/admin/orders/${orderId}/`, { status }),
        {
          successMessage: 'Order status updated',
        }
      );

      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to update order status';
      toast.error(message);
      return null;
    }
  };

  /**
   * Get all users (admin only)
   * @param {number} page - Page number
   */
  const fetchUsers = async (page = 1) => {
    const { execute } = useApiCall();

    try {
      const params = { page, page_size: 20 };
      const response = await execute(
        async () => api.get('/admin/users/', { params }),
        { showToast: false }
      );

      return response;
    } catch (error) {
      toast.error('Failed to load users');
      console.error('Fetch users error:', error);
      return null;
    }
  };

  /**
   * Export data (orders, products, users)
   * @param {string} dataType - Type of data to export
   * @param {Object} filters - Export filters
   */
  const exportData = async (dataType, filters = {}) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get(`/admin/export/${dataType}/`, {
          params: filters,
          responseType: 'blob',
        }),
        { showToast: false }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${dataType}-export.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Export downloaded successfully');
      return true;
    } catch (error) {
      toast.error('Failed to export data');
      console.error('Export data error:', error);
      return false;
    }
  };

  return {
    // State
    dashboardStats,
    isLoadingStats,

    // Computed
    hasStats,

    // Actions
    fetchDashboardData,
    manageProduct,
    manageCategory,
    updateOrderStatus,
    fetchUsers,
    exportData,
  };
});
