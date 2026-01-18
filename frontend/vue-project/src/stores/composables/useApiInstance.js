import { createApiInstance } from '@/services/api';
import { LocalStorageManager, STORAGE_KEYS } from './useLocalStorage';

/**
 * Composable for accessing the API instance with automatic token management
 * Eliminates 15+ duplicate apiInstance initialization checks
 *
 * @returns {Object} - API instance with token management
 *
 * @example
 * const { api, updateToken, clearToken } = useApiInstance();
 * const response = await api.get('/products');
 */
export function useApiInstance() {
  /**
   * Get or create API instance
   * Automatically configures with current auth token
   */
  const getApi = () => {
    const token = LocalStorageManager.get(STORAGE_KEYS.AUTH_TOKEN);
    return createApiInstance(token);
  };

  /**
   * Update the auth token
   * @param {string} token - New authentication token
   */
  const updateToken = (token) => {
    if (token) {
      LocalStorageManager.set(STORAGE_KEYS.AUTH_TOKEN, token);
    } else {
      LocalStorageManager.remove(STORAGE_KEYS.AUTH_TOKEN);
    }
  };

  /**
   * Clear the auth token
   */
  const clearToken = () => {
    LocalStorageManager.remove(STORAGE_KEYS.AUTH_TOKEN);
  };

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  const isAuthenticated = () => {
    return LocalStorageManager.has(STORAGE_KEYS.AUTH_TOKEN);
  };

  /**
   * Get current auth token
   * @returns {string|null}
   */
  const getToken = () => {
    return LocalStorageManager.get(STORAGE_KEYS.AUTH_TOKEN);
  };

  return {
    api: getApi(),
    updateToken,
    clearToken,
    isAuthenticated,
    getToken,
  };
}

/**
 * Direct API instance getter without composable overhead
 * Use this for non-reactive contexts
 */
export function getApiInstance() {
  const token = LocalStorageManager.get(STORAGE_KEYS.AUTH_TOKEN);
  return createApiInstance(token);
}
