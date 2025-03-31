// services/api.js
import axios from 'axios';

function getAuthToken() {
  return localStorage.getItem('authToken');
}

export const createApiInstance = (store) => {
  console.log('Creating apiInstance with store:', store);
  const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
    timeout: 150000,
  });

  // Request interceptor to add auth token
  api.interceptors.request.use(
    (config) => {
      const token = getAuthToken();
      console.log('Request interceptor - token:', token);
      if (token) {
        config.headers['Authorization'] = `Token ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle unauthorized errors
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        console.log('Response interceptor - unauthorized, logging out');
        localStorage.removeItem('authToken');
        if (store && typeof store.logout === 'function') {
          store.logout();
        }
      }
      return Promise.reject(error);
    }
  );

  console.log('apiInstance created:', api);
  return api;
};

// Authentication APIs
export const login = async (apiInstance, username, password) => {
  try {
    const response = await apiInstance.post('auth/login/', { username, password });
    const token = response.data.token;
    localStorage.setItem('authToken', token);
    return response.data;
  } catch (error) {
    console.error('Login error:', error.response?.data || error.message);
    throw error;
  }
};

export const logout = async (api) => {
  try {
    await api.post('auth/logout/');
  } catch (error) {
    console.error('Logout error:', error.response?.data || error.message);
  } finally {
    localStorage.removeItem('authToken');
  }
};

export const fetchCurrentUserInfo = async (apiInstance) => {
  try {
    const response = await apiInstance.get('auth/user/');
    return response.data;
  } catch (error) {
    console.error('Error fetching current user info:', error.response?.data || error.message);
    throw error;
  }
};

// User Profile APIs
export const getUserProfile = async (api) => {
  try {
    const response = await api.get('user/profile/');
    return response.data;
  } catch (error) {
    console.error('Error fetching user profile:', error.response?.data || error.message);
    throw error;
  }
};

export const updateUserProfile = async (api, profileData) => {
  try {
    const response = await api.put('user/profile/', profileData);
    return response.data;
  } catch (error) {
    console.error('Error updating user profile:', error.response?.data || error.message);
    throw error;
  }
};

// Delivery Location APIs
export const getDeliveryLocations = async (api) => {
  try {
    const response = await api.get('user/delivery-locations/');
    return response.data;
  } catch (error) {
    console.error('Error fetching delivery locations:', error.response?.data || error.message);
    throw error;
  }
};

export const addDeliveryLocation = async (api, location) => {
  try {
    const locationData = {
      name: location.name,
      address: location.address,
      latitude: location.latitude,
      longitude: location.longitude,
      is_default: location.isDefault,
    };
    const response = await api.post('user/delivery-locations/', locationData);
    return response.data;
  } catch (error) {
    console.error('Error adding delivery location:', error.response?.data || error.message);
    throw error;
  }
};

export const setDefaultDeliveryLocation = async (api, locationId) => {
  try {
    const response = await api.put(`user/delivery-locations/${locationId}/set-default/`);
    return response.data;
  } catch (error) {
    console.error('Error setting default delivery location:', error.response?.data || error.message);
    throw error;
  }
};

export const deleteDeliveryLocation = async (api, locationId) => {
  try {
    const response = await api.delete(`user/delivery-locations/${locationId}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting delivery location:', error.response?.data || error.message);
    throw error;
  }
};

// Existing APIs
export const fetchCategories = async (api) => {
  try {
    const response = await api.get('categories/', {
      timeout: 60000,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching categories:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchCategoryProducts = async (api, categorySlug) => {
  try {
    console.log(`Fetching category products for slug: ${categorySlug}`);
    console.log(`Request URL: category/${categorySlug}/products/`);
    const response = await api.get(`category/${categorySlug}/products/`, {
      timeout: 60000,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching category products:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchProductDetails = async (apiInstance, categorySlug, productSlug) => {
  const response = await apiInstance.get(`products/${categorySlug}/${productSlug}/`);
  return response.data;
};

export const fetchAllCategoriesWithProducts = async (api) => {
  try {
    const response = await api.get('all-categories-with-products/', {
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching all categories with products:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchCart = async (api, userId) => {
  try {
    const response = await api.get(`users/${userId}/cart/`, {
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching cart:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchOrders = async (api, userId) => {
  if (!userId) throw new Error('User ID not set');
  try {
    const response = await api.get(`orders/user-orders/?user=${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchCompletedOrders = async (api, userId) => {
  if (!userId) throw new Error('User ID not set');
  try {
    const response = await api.get(`completed-orders/?user=${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching completed orders:', error.response?.data || error.message);
    throw error;
  }
};

export const createCart = async (api, userId) => {
  try {
    console.log(`Creating cart at: /api/users/${userId}/create_cart/`);
    const response = await api.post(`users/${userId}/create_cart/`, { userId: userId });
    return response.data;
  } catch (error) {
    console.error('Error creating cart:', error.response?.data || error.message);
    throw error;
  }
};

export const addToCart = async (api, cartId, productId, variantId, quantity = 1) => {
  try {
    console.log('Adding to cart:', { cartId, productId, variantId, quantity });
    const response = await api.post(`carts/${cartId}/add_item/`, {
      productId: productId,
      variantId: variantId,
      quantity: quantity,
    });
    console.log('Add to cart response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error adding to cart:', error.response?.data || error.message);
    throw error;
  }
};

export const removeFromCart = async (api, cartId, itemId) => {
  try {
    const response = await api.post(`carts/${cartId}/remove_item/`, { item_id: itemId });
    return response.data;
  } catch (error) {
    console.error('Error removing from cart:', error.response?.data || error.message);
    throw error;
  }
};

export const checkoutCart = async (api, cartId, shippingMethod, shippingAddress, paymentMethod) => {
  try {
    const response = await api.post(`carts/${cartId}/checkout/`, {
      shipping_method: shippingMethod,
      shipping_address: shippingAddress,
    });
    return response.data;
  } catch (error) {
    console.error('Error checking out cart:', error.response?.data || error.message);
    throw error;
  }
};

export const cancelOrder = async (api, orderId) => {
  try {
    const response = await api.post(`orders/${orderId}/cancel/`);
    return response.data;
  } catch (error) {
    console.error('Error canceling order:', error.response?.data || error.message);
    throw error;
  }
};

export const searchProducts = async (apiInstance, query, page = 1, perPage = 10) => {
  const response = await apiInstance.get('/products/search/', {
    params: {
      search: query,
      page,
      per_page: perPage,
      ordering: '-created_at',
    },
  });
  return response.data;
};

export default {
  createApiInstance,
  login,
  logout,
  fetchCurrentUserInfo,
  getUserProfile,
  updateUserProfile,
  getDeliveryLocations,
  addDeliveryLocation,
  setDefaultDeliveryLocation,
  deleteDeliveryLocation,
  fetchCategories,
  fetchCategoryProducts,
  fetchProductDetails,
  fetchAllCategoriesWithProducts,
  fetchCart,
  fetchOrders,
  fetchCompletedOrders,
  createCart,
  addToCart,
  removeFromCart,
  checkoutCart,
  cancelOrder,
  searchProducts,
};
