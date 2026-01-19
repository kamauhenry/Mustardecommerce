import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApiCall } from '../composables/useApiCall';
import { useApiInstance } from '../composables/useApiInstance';
import { LocalStorageManager, STORAGE_KEYS } from '../composables/useLocalStorage';
import { toast } from '../composables/useToast';

/**
 * Authentication Store Module
 * Handles user authentication, login, logout, and token management
 */
export const useAuthStore = defineStore('auth', () => {
  // State
  const currentUser = ref(LocalStorageManager.get(STORAGE_KEYS.CURRENT_USER, null));
  const userId = ref(LocalStorageManager.get(STORAGE_KEYS.USER_ID, null));
  const authToken = ref(LocalStorageManager.get(STORAGE_KEYS.AUTH_TOKEN, null));
  const loginMessage = ref(null);
  const isLoggingIn = ref(false);

  // Computed
  const isAuthenticated = computed(() => !!authToken.value);
  const isAdmin = computed(() => currentUser.value?.is_staff === true);
  const userEmail = computed(() => currentUser.value?.email || '');
  const userName = computed(() => {
    if (!currentUser.value) return '';
    return currentUser.value.username || currentUser.value.email || '';
  });

  // API instance
  const { api, updateToken, clearToken } = useApiInstance();

  /**
   * Login user with email and password
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<boolean>} - Success status
   */
  const login = async (email, password) => {
    const { execute, loading } = useApiCall();
    isLoggingIn.value = true;
    loginMessage.value = null;

    try {
      const response = await execute(
        async () => api.post('/users/login/', { email, password }),
        {
          showToast: false, // We'll handle toast manually
        }
      );

      if (response.token) {
        // Save auth data
        authToken.value = response.token;
        currentUser.value = response.user;
        userId.value = response.user?.id;

        // Update localStorage
        LocalStorageManager.set(STORAGE_KEYS.AUTH_TOKEN, response.token);
        LocalStorageManager.set(STORAGE_KEYS.CURRENT_USER, response.user);
        LocalStorageManager.set(STORAGE_KEYS.USER_ID, response.user?.id);

        // Update API instance token
        updateToken(response.token);

        loginMessage.value = 'Login successful';
        toast.success('Welcome back!');

        return true;
      } else {
        loginMessage.value = 'Invalid login response';
        toast.error('Login failed');
        return false;
      }
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Login failed';
      loginMessage.value = message;
      toast.error(message);
      return false;
    } finally {
      isLoggingIn.value = false;
    }
  };

  /**
   * Logout user and clear auth data
   */
  const logout = async () => {
    try {
      // Optionally call logout endpoint
      if (authToken.value) {
        await api.post('/users/logout/').catch(() => {
          // Ignore logout endpoint errors
        });
      }
    } finally {
      // Clear all auth data
      authToken.value = null;
      currentUser.value = null;
      userId.value = null;
      loginMessage.value = null;

      // Clear localStorage
      LocalStorageManager.remove(STORAGE_KEYS.AUTH_TOKEN);
      LocalStorageManager.remove(STORAGE_KEYS.CURRENT_USER);
      LocalStorageManager.remove(STORAGE_KEYS.USER_ID);

      // Clear API token
      clearToken();

      toast.info('Logged out successfully');
    }
  };

  /**
   * Register new user
   * @param {Object} userData - User registration data
   * @returns {Promise<boolean>} - Success status
   */
  const register = async (userData) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.post('/users/register/', userData),
        {
          successMessage: 'Registration successful! Please login.',
        }
      );

      return true;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Registration failed';
      toast.error(message);
      return false;
    }
  };

  /**
   * Verify authentication token
   * @returns {Promise<boolean>} - Token validity
   */
  const verifyToken = async () => {
    if (!authToken.value) {
      return false;
    }

    try {
      const response = await api.post('/users/verify-token/', {
        token: authToken.value,
      });

      if (response.data?.valid) {
        return true;
      } else {
        // Token invalid, logout
        await logout();
        return false;
      }
    } catch (error) {
      // Token verification failed, logout
      await logout();
      return false;
    }
  };

  /**
   * Refresh user data from server
   * @returns {Promise<boolean>} - Success status
   */
  const refreshUser = async () => {
    if (!isAuthenticated.value) {
      return false;
    }

    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get('/users/profile/'),
        { showToast: false }
      );

      currentUser.value = response;
      LocalStorageManager.set(STORAGE_KEYS.CURRENT_USER, response);

      return true;
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      return false;
    }
  };

  /**
   * Initialize auth state from localStorage
   */
  const initAuth = () => {
    const token = LocalStorageManager.get(STORAGE_KEYS.AUTH_TOKEN);
    const user = LocalStorageManager.get(STORAGE_KEYS.CURRENT_USER);
    const uid = LocalStorageManager.get(STORAGE_KEYS.USER_ID);

    if (token && user) {
      authToken.value = token;
      currentUser.value = user;
      userId.value = uid;
      updateToken(token);
    }
  };

  // Initialize on store creation
  initAuth();

  return {
    // State
    currentUser,
    userId,
    authToken,
    loginMessage,
    isLoggingIn,

    // Computed
    isAuthenticated,
    isAdmin,
    userEmail,
    userName,

    // Actions
    login,
    logout,
    register,
    verifyToken,
    refreshUser,
    initAuth,
  };
});
