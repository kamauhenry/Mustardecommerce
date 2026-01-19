import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApiCall } from '../composables/useApiCall';
import { useApiInstance } from '../composables/useApiInstance';
import { LocalStorageManager, STORAGE_KEYS } from '../composables/useLocalStorage';
import { toast } from '../composables/useToast';

/**
 * User Store Module
 * Handles user profile, addresses, wishlist, and preferences
 */
export const useUserStore = defineStore('user', () => {
  // State
  const profile = ref(LocalStorageManager.get(STORAGE_KEYS.CURRENT_USER, null));
  const addresses = ref([]);
  const wishlist = ref(LocalStorageManager.get(STORAGE_KEYS.WISHLIST, []));
  const isLoadingProfile = ref(false);
  const isLoadingAddresses = ref(false);
  const isUpdatingProfile = ref(false);

  // API instance
  const { api } = useApiInstance();

  // Computed
  const hasProfile = computed(() => profile.value !== null);
  const hasAddresses = computed(() => addresses.value.length > 0);
  const hasWishlist = computed(() => wishlist.value.length > 0);
  const defaultAddress = computed(() =>
    addresses.value.find(addr => addr.is_default) || addresses.value[0] || null
  );

  /**
   * Fetch user profile
   */
  const fetchProfile = async () => {
    const { execute } = useApiCall();
    isLoadingProfile.value = true;

    try {
      const response = await execute(
        async () => api.get('user/profile/me'),
        { showToast: false }
      );

      profile.value = response;
      LocalStorageManager.set(STORAGE_KEYS.CURRENT_USER, response);
      return response;
    } catch (error) {
      toast.error('Failed to load profile');
      console.error('Fetch profile error:', error);
      throw error;
    } finally {
      isLoadingProfile.value = false;
    }
  };

  /**
   * Update user profile
   * @param {Object} profileData - Updated profile data
   */
  const updateProfile = async (profileData) => {
    const { execute } = useApiCall();
    isUpdatingProfile.value = true;

    try {
      const response = await execute(
        async () => api.put('user/update-user/', profileData),
        {
          successMessage: 'Profile updated successfully',
        }
      );

      profile.value = response;
      LocalStorageManager.set(STORAGE_KEYS.CURRENT_USER, response);

      return true;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to update profile';
      toast.error(message);
      return false;
    } finally {
      isUpdatingProfile.value = false;
    }
  };

  /**
   * Change user password
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   */
  const changePassword = async (currentPassword, newPassword) => {
    const { execute } = useApiCall();

    try {
      await execute(
        async () => api.post('/users/change-password/', {
          current_password: currentPassword,
          new_password: newPassword,
        }),
        {
          successMessage: 'Password changed successfully',
        }
      );

      return true;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to change password';
      toast.error(message);
      return false;
    }
  };

  /**
   * Fetch delivery locations (addresses)
   */
  const fetchAddresses = async () => {
    const { execute } = useApiCall();
    isLoadingAddresses.value = true;

    try {
      const response = await execute(
        async () => api.get('user/delivery-locations/'),
        { showToast: false }
      );

      addresses.value = response;
      return response;
    } catch (error) {
      toast.error('Failed to load delivery locations');
      console.error('Fetch addresses error:', error);
      throw error;
    } finally {
      isLoadingAddresses.value = false;
    }
  };

  /**
   * Add new delivery location
   * @param {Object} locationData - Location data
   */
  const addAddress = async (locationData) => {
    const { execute } = useApiCall();

    try {
      const payload = {
        name: locationData.name,
        address: locationData.address,
        latitude: locationData.latitude,
        longitude: locationData.longitude,
        is_default: locationData.isDefault || locationData.is_default || false,
      };

      const response = await execute(
        async () => api.post('user/delivery-locations/', payload),
        {
          successMessage: 'Location added successfully',
        }
      );

      addresses.value.push(response);
      return response;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to add location';
      toast.error(message);
      throw error;
    }
  };

  /**
   * Update delivery location
   * @param {number} locationId - Location ID
   * @param {Object} locationData - Updated location data
   */
  const updateAddress = async (locationId, locationData) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.put(`user/delivery-locations/${locationId}/`, locationData),
        {
          successMessage: 'Location updated successfully',
        }
      );

      const index = addresses.value.findIndex(addr => addr.id === locationId);
      if (index !== -1) {
        addresses.value[index] = response;
      }

      return true;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to update location';
      toast.error(message);
      return false;
    }
  };

  /**
   * Delete delivery location
   * @param {number} locationId - Location ID
   */
  const deleteAddress = async (locationId) => {
    const { execute } = useApiCall();

    try {
      await execute(
        async () => api.delete(`user/delivery-locations/${locationId}/`),
        {
          successMessage: 'Location deleted successfully',
        }
      );

      const index = addresses.value.findIndex(addr => addr.id === locationId);
      if (index !== -1) {
        addresses.value.splice(index, 1);
      }

      return true;
    } catch (error) {
      const message = error.response?.data?.message ||
                     error.response?.data?.error ||
                     'Failed to delete location';
      toast.error(message);
      throw error;
    }
  };

  /**
   * Set default delivery location
   * @param {number} locationId - Location ID
   */
  const setDefaultAddress = async (locationId) => {
    const { execute } = useApiCall();

    try {
      await execute(
        async () => api.put(`user/delivery-locations/${locationId}/set-default/`),
        {
          successMessage: 'Default location updated',
        }
      );

      // Update all addresses
      addresses.value = addresses.value.map(addr => ({
        ...addr,
        is_default: addr.id === locationId,
      }));

      return true;
    } catch (error) {
      toast.error('Failed to set default location');
      throw error;
    }
  };

  /**
   * Add product to wishlist
   * @param {Object} product - Product to add
   */
  const addToWishlist = (product) => {
    const exists = wishlist.value.find(item => item.id === product.id);
    if (exists) {
      toast.info('Product already in wishlist');
      return;
    }

    wishlist.value.push({
      id: product.id,
      name: product.name,
      price: product.price,
      image: product.image || product.images?.[0]?.image,
      addedAt: Date.now(),
    });

    LocalStorageManager.set(STORAGE_KEYS.WISHLIST, wishlist.value);
    toast.success('Added to wishlist');
  };

  /**
   * Remove product from wishlist
   * @param {number} productId - Product ID
   */
  const removeFromWishlist = (productId) => {
    const index = wishlist.value.findIndex(item => item.id === productId);
    if (index !== -1) {
      wishlist.value.splice(index, 1);
      LocalStorageManager.set(STORAGE_KEYS.WISHLIST, wishlist.value);
      toast.info('Removed from wishlist');
    }
  };

  /**
   * Clear wishlist
   */
  const clearWishlist = () => {
    wishlist.value = [];
    LocalStorageManager.remove(STORAGE_KEYS.WISHLIST);
    toast.info('Wishlist cleared');
  };

  /**
   * Check if product is in wishlist
   * @param {number} productId - Product ID
   * @returns {boolean}
   */
  const isInWishlist = (productId) => {
    return wishlist.value.some(item => item.id === productId);
  };

  /**
   * Sync wishlist to server
   */
  const syncWishlistToServer = async () => {
    if (!hasWishlist.value) return;

    const { execute } = useApiCall();

    try {
      await execute(
        async () => api.post('/users/wishlist/sync/', {
          items: wishlist.value,
        }),
        { showToast: false }
      );
    } catch (error) {
      console.error('Failed to sync wishlist to server:', error);
    }
  };

  /**
   * Initialize user state from localStorage
   */
  const initUser = () => {
    const savedProfile = LocalStorageManager.get(STORAGE_KEYS.CURRENT_USER);
    const savedWishlist = LocalStorageManager.get(STORAGE_KEYS.WISHLIST, []);

    if (savedProfile) {
      profile.value = savedProfile;
    }

    wishlist.value = savedWishlist;
  };

  // Initialize on store creation
  initUser();

  return {
    // State
    profile,
    addresses,
    wishlist,
    isLoadingProfile,
    isLoadingAddresses,
    isUpdatingProfile,

    // Computed
    hasProfile,
    hasAddresses,
    hasWishlist,
    defaultAddress,

    // Actions
    fetchProfile,
    updateProfile,
    changePassword,
    fetchAddresses,
    addAddress,
    updateAddress,
    deleteAddress,
    setDefaultAddress,
    addToWishlist,
    removeFromWishlist,
    clearWishlist,
    isInWishlist,
    syncWishlistToServer,
    initUser,

    // Aliases for backward compatibility with components
    currentUser: profile,
    deliveryLocations: addresses,
    fetchUserProfile: fetchProfile,
    updateUserProfile: updateProfile,
    fetchDeliveryLocations: fetchAddresses,
    addDeliveryLocation: addAddress,
    setDefaultDeliveryLocation: setDefaultAddress,
    deleteDeliveryLocation: deleteAddress,
  };
});
