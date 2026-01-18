import { ref } from 'vue';

/**
 * Composable for standardized API calls with loading, error handling, and success tracking
 * Eliminates 40+ duplicate try/catch blocks across the codebase
 *
 * @example
 * const { execute, loading, error, data } = useApiCall();
 * await execute(async () => {
 *   return await apiInstance.get('/products');
 * });
 */
export function useApiCall() {
  const loading = ref(false);
  const error = ref(null);
  const data = ref(null);
  const success = ref(false);

  /**
   * Execute an API call with standardized error handling
   * @param {Function} apiFunction - Async function that makes the API call
   * @param {Object} options - Configuration options
   * @param {Function} options.onSuccess - Callback on success
   * @param {Function} options.onError - Callback on error
   * @param {boolean} options.showToast - Whether to show toast notifications (default: true)
   * @param {string} options.successMessage - Custom success message
   * @param {string} options.errorMessage - Custom error message
   * @returns {Promise<any>} - Returns the API response data
   */
  const execute = async (apiFunction, options = {}) => {
    const {
      onSuccess = null,
      onError = null,
      showToast = true,
      successMessage = null,
      errorMessage = null,
    } = options;

    loading.value = true;
    error.value = null;
    success.value = false;

    try {
      const response = await apiFunction();
      data.value = response.data || response;
      success.value = true;

      if (onSuccess) {
        onSuccess(data.value);
      }

      if (showToast && successMessage) {
        // Toast notification will be handled by useToast composable
        console.log('[API Success]:', successMessage);
      }

      return data.value;
    } catch (err) {
      error.value = err;
      success.value = false;

      // Extract error message
      const message = errorMessage ||
        err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        'An unexpected error occurred';

      if (onError) {
        onError(message, err);
      }

      if (showToast) {
        console.error('[API Error]:', message);
      }

      // Log detailed error in development
      if (import.meta.env.DEV) {
        console.error('[API Error Details]:', {
          status: err.response?.status,
          data: err.response?.data,
          error: err,
        });
      }

      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Reset the composable state
   */
  const reset = () => {
    loading.value = false;
    error.value = null;
    data.value = null;
    success.value = false;
  };

  return {
    execute,
    reset,
    loading,
    error,
    data,
    success,
  };
}

/**
 * Simplified version for fire-and-forget API calls
 * @param {Function} apiFunction - Async function that makes the API call
 * @param {Object} options - Configuration options
 * @returns {Promise<any>}
 */
export async function apiCall(apiFunction, options = {}) {
  const { execute } = useApiCall();
  return await execute(apiFunction, options);
}
