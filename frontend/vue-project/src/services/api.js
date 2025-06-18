import axios from 'axios';

function getAuthToken() {
  return localStorage.getItem('authToken');
}

// Function to get CSRF token from cookies
const getCsrfTokenFromCookies = () => {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [key, value] = cookie.trim().split('=');
    if (key === name) {
      return value;
    }
  }
  return null;
};

export const createApiInstance = (store) => {

  const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
    timeout: 150000,
    withCredentials: true, // Ensure cookies are sent with requests
  });

  // Request interceptor for auth token and CSRF token
  api.interceptors.request.use(
    (config) => {
      const token = getAuthToken();
      const publicEndpoints = [
        'auth/forgot-password/',
        'auth/send-otp/',
        'auth/register/',
        'auth/reset-password/', // Matches /auth/reset-password/{token}/
        'auth/verify-otp/',
        'auth/login/'
      ];
      if (token && !publicEndpoints.some(path => config.url.includes(path))) {
        config.headers['Authorization'] = `Token ${token}`;
      }
      if (['post', 'put', 'delete'].includes(config.method.toLowerCase())) {
        const csrfToken = getCsrfTokenFromCookies();
        if (csrfToken) {
          config.headers['X-CSRFToken'] = csrfToken;
        }
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for handling 401/403
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      const isLoginRequest = error.config?.url.includes('auth/login/') || error.config?.url.includes('admin-page/login/');
      if (
        error.response &&
        (error.response.status === 401 || error.response.status === 403) &&
        error.config?.url !== 'auth/logout/' &&
        !isLoginRequest
      ) {
        console.log('Response interceptor - unauthorized, logging out');
        localStorage.removeItem('authToken');
        if (store && typeof store.logout === 'function') {
          store.logout();
        }
        if (error.config?.url.includes('admin-page/dashboard/') && error.response.status === 403) {
          window.location.href = '/admin-page/login';
        }
      }
      return Promise.reject(error);
    }
  );


  return api;
};


// Authentication APIs
export const register = async (apiInstance, userData) => {
  try {
    const response = await apiInstance.post('auth/register/', userData);
    const token = response.data.token;
    localStorage.setItem('authToken', token);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error.response?.data || error.message);
    throw error;
  }
};

export const login = async (apiInstance, username, password) => {
  if (!username || !password) {
    throw new Error('Username and password are required');
    
  }
  
  try {
    const response = await apiInstance.post('auth/login/', { username, password });
    const token = response.data.token;
    localStorage.setItem('authToken', token);
    console.log('Login response:', response.data);
    
    return response.data;
  } catch (error) {
    console.error('Login error details:', error.response?.data || error.message);
    
    throw error;
  }
};

// Google Authentication APIs
export const googleAuth = async (apiInstance, googleToken) => {
  try {
    const response = await apiInstance.post('auth/google/', {
      access_token: googleToken,
    });
    const token = response.data.token;
    localStorage.setItem('authToken', token);
    return response.data;
  } catch (error) {
    console.error('Google auth error:', error.response?.data || error.message);
    throw error;
  }
};

export const logout = async (api) => {
  try {
    await api.post('auth/logout/');
    console.log('Logout successful');
  } catch (error) {

  } finally {
    localStorage.removeItem('authToken');
  }
};

export const fetchCurrentUserInfo = async (apiInstance) => {
  try {
    const response = await apiInstance.get('auth/user/me');
    return response.data;
  } catch (error) {
    console.error('Error fetching current user info:', error.response?.data || error.message);
    throw error;
  }
};

// User Profile APIs
export const getUserProfile = async (api) => {
  try {
    const response = await api.get('user/profile/me');
    return response.data;
  } catch (error) {
    console.error('Error fetching user profile:', error.response?.data || error.message);
    throw error;
  }
};

export const updateUserProfile = async (api, profileData) => {
  try {
    const response = await api.put(`user/update-user/`, profileData);
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
export const fetchProductReviews = async (apiInstance, productId) => {
  try {
    const response = await apiInstance.get(`products/${productId}/reviews/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching product reviews:', error.response?.data || error.message);
    throw error;
  }
};

export const submitProductReview = async (apiInstance, productId, reviewData) => {
  try {
    const response = await apiInstance.post(`products/${productId}/reviews/`, reviewData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error submitting product review:', error.response?.data || error.message);
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

// Category APIs
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

const createCategory = async (api, categoryData) => {
  try {
    const response = await api.post('categories/', categoryData);
    return response.data;
  } catch (error) {
    console.error('Error creating category:', error.response?.data || error.message);
    throw error;
  }
};

const updateCategory = async (api, categoryId, categoryData) => {
  try {
    const response = await api.put(`categories/${categoryId}/`, categoryData);
    return response.data;
  } catch (error) {
    console.error('Error updating category:', error.response?.data || error.message);
    throw error;
  }
};

const deleteCategory = async (api, categoryId) => {
  try {
    const response = await api.delete(`categories/${categoryId}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting category:', error.response?.data || error.message);
    throw error;
  }
};

// Product APIs
export const fetchProducts = async (api) => {
  try {
    const response = await api.get('all-categories-with-products/', {
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching products:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchSuppliers = async (api) => {
  try {
    const response = await api.get('admin/suppliers/');
    return response.data;
  } catch (error) {
    console.error('Error fetching suppliers:', error.response?.data || error.message);
    throw error;
  }
};

export const createSupplier = async (api, supplierData) => {
  try {
    const response = await api.post('admin/suppliers/', supplierData);
    return response.data;
  } catch (error) {
    console.error('Error creating supplier:', error.response?.data || error.message);
    throw error;
  }
};

// Attribute APIs
export const fetchAttributes = async (api) => {
  try {
    const response = await api.get('admin/attribute-values/');
    return response.data;
  } catch (error) {
    console.error('Error fetching attributes:', error.response?.data || error.message);
    throw error;
  }
};

export const createAttribute = async (api, attributeData) => {
  try {
    const response = await api.post('admin/attribute-values/', attributeData);
    return response.data;
  } catch (error) {
    console.error('Error creating attribute:', error.response?.data || error.message);
    throw error;
  }
};

// Modified Product APIs
export const createProduct = async (api, data) => {
  try {
    const response = await api.post('admin/products/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('Error creating product:', error.response?.data || error.message);
    throw error;
  }
};

export const updateProduct = async (api, id, data) => {
  try {
    const response = await api.put(`admin/products/${id}/`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    console.error('Error updating product:', error.response?.data || error.message);
    throw error;
  }
};

export const deleteProduct = async (api, id) => {
  try {
    const response = await api.delete(`admin/products/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting product:', error.response?.data || error.message);
    throw error;
  }
};

// Order APIs
export const fetchAllOrders = async (api) => {
  try {
    const response = await api.get('orders/');
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error.response?.data || error.message);
    throw error;
  }
};

export const deleteOrder = async (api, orderId) => {
  try {
    const response = await api.delete(`orders/${orderId}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting order:', error.response?.data || error.message);
    throw error;
  }
};

// Existing APIs
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

export const fetchAllCategoriesWithProducts = async (apiInstance) => {
  try {
    const response = await apiInstance.get('all-categories-with-products/', {
      timeout: 120000,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching all categories with products:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchPickupCategories = async (apiInstance, page = 1) => {
  try {
    const response = await apiInstance.get(`home-categories/pickup/?page=${page}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching pickup categories:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchHomeCategories = async (apiInstance, page = 1) => {
  try {

    const response = await apiInstance.get(`home-categories/?page=${page}`, {
      timeout: 60000,
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching home categories:', error.response?.data || error.message);
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
export const fetchOrder = async (apiInstance, orderId) => {
  try {
    const cleanOrderId = orderId
    const response = await apiInstance.get(`/orders/${cleanOrderId}/`);
    return response.data;
  } catch (error) {
    console.error('Fetch order error:', error.response?.data || error.message);
    throw error;
  }
};

export const fetchOrders = async (api, userId) => {
  if (!userId) throw new Error('User ID not set');
  try {
    const response = await api.get(`orders/?user=${userId}`);
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

export const addToCart = async (api, cartId, productId, attributes, quantity = 1, shippingMethodId = null) => {
  try {
    console.log('Adding to cart:', { cartId, productId, attributes, quantity, shippingMethodId });
    const payload = {
      productId: productId,
      attributes: attributes,
      quantity: quantity,
    };
    if (shippingMethodId) {
      payload.shippingMethodId = shippingMethodId;
    }
    const response = await api.post(`carts/${cartId}/add_item/`, payload);
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

export const checkoutCart = async (api, cartId, shippingMethod, ) => {
  try {
    const response = await api.post(`carts/${cartId}/checkout/`, {
      shipping_method: shippingMethod,

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

export const fetchRelatedProducts = async (apiInstance, categorySlug, productId) => {
  try {
    console.log(`Fetching related products for category: ${categorySlug}, product: ${productId}`);
    const response = await apiInstance.get(`category/${categorySlug}/products/${productId}/related/`, {
      timeout: 60000,
    });
    console.log('Related products response:', response.data);
    return response.data; // Should be an array
  } catch (error) {
    console.error('Error fetching related products:', error.response?.data || error.message);
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

export const adminRegister = async (apiInstance, userData) => {
  try {
    const response = await apiInstance.post('admin-page/register/', userData);
    const token = response.data.token;
    if (!token) {
      throw new Error('No token received from server');
    }
    localStorage.setItem('authToken', token);
    return response.data;
  } catch (error) {
    console.error('Admin registration error:', error.response?.data || error.message);
    throw error;
  }
};

export const adminLogin = async (apiInstance, credentials) => {
  try {
    const response = await apiInstance.post('admin-page/login/', credentials);
    const token = response.data.token;
    if (!token) {
      throw new Error('No token received from server');
    }
    localStorage.setItem('authToken', token);
    return response.data;
  } catch (error) {
    console.error('Admin login error:', error.response?.data || error.message);
    throw error;
  }
};

const fetchProfile = async (api) => {
  try {
    const response = await api.get('admin-page/profile/');
    return response.data;
  } catch (error) {
    console.error('Error fetching profile:', error.response?.data || error.message);
    throw error;
  }
};

const updateProfile = async (apiInstance, userData) => {
  try {
    const response = await apiInstance.put('admin-page/profile/', userData);
    return response.data;
  } catch (error) {
    console.error('Error updating profile:', error.response?.data || error.message);
    throw error;
  }
};

const fetchDashboardData = async (apiInstance) => {
  if (!apiInstance) {
    throw new Error('API instance is null');
  }
  try {
    console.log('Fetching dashboard data from /api/admin-page/dashboard/');
    const response = await apiInstance.get('admin-page/dashboard/');
    console.log('Dashboard data fetched successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard data:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });
    throw error;
  }
};

export const fetchAllOrdersAdmin = async (apiInstance, params = {}) => {
  try {
    const response = await apiInstance.get('admin/orders/', {
      params: { ...params, _t: Date.now() }, // Cache-busting timestamp
      timeout: 60000, // 10-second timeout
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching all orders:', error.response?.data || error.message);
    throw error;
  }
};

export const getMOQFulfilledProducts = async (apiInstance) => {
  try {
    const response = await apiInstance.get('admin/moq-fulfilled-products/', {
      params: {
        moq_status: 'active', // Explicitly filter for active MOQ status
        _t: Date.now() // Cache-busting
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching MOQ fulfilled products:', error.response?.data || error.message);
    throw error;
  }
};
export const searchOrders = async (apiInstance, query, status, page = 1, perPage = 10) => {
  try {
    const response = await apiInstance.get('admin/orders/', {
      params: {
        search: query,
        delivery_status: status,
        page,
        per_page: perPage,
        _t: Date.now()
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error searching orders:', error.response?.data || error.message);
    throw error;
  }
};

export const searchSuggestions = async (apiInstance, query) => {
  try {
    const response = await apiInstance.get('admin/orders/', {
      params: {
        search: query,
        per_page: 5,
        fields: 'order_number',
        _t: Date.now()
      }
    });
    return response.data.results.map(order => order.order_number) || [];
  } catch (error) {
    console.error('Error fetching search suggestions:', error.response?.data || error.message);
    return [];
  }
};

export const placeOrderForProduct = async (apiInstance, productId) => {
  try {
    const response = await apiInstance.post(`admin/products/${productId}/place-order/`);
    return response.data;
  } catch (error) {
    console.error('Error placing order for product:', error.response?.data || error.message);
    throw error;
  }
};

export const bulkUpdateOrderStatus = async (apiInstance, orderIds, deliveryStatus) => {
  try {
    const response = await apiInstance.post('admin/orders/bulk-update/', {
      order_ids: orderIds,
      delivery_status: deliveryStatus,
    });
    return response.data;
  } catch (error) {
    console.error('Error updating orders:', error.response?.data || error.message);
    throw error;
  }
};
export const updateSingleOrderStatus = async (apiInstance, orderId, deliveryStatus) => {
  try {
    console.log('Sending single order update payload:', { order_id: orderId, deliveryStatus });
    const response = await apiInstance.post(`admin/orders/${orderId}/update-status/`, {
      delivery_status: deliveryStatus,
    });
    console.log('Single order update response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error updating order status:', error.response?.data || error.message);
    throw error;
  }
};

export const createShippingMethod = async (apiInstance, shippingMethodData) => {
  try {
    console.log('Sending create shipping method payload:', shippingMethodData);
    const response = await apiInstance.post('shipping_methods1/', shippingMethodData);
    console.log('Create shipping method response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error creating shipping method:', error.response?.data || error.message);
    throw error;
  }
};

export const updateShippingMethod = async (apiInstance, shippingMethodId, shippingMethodData) => {
  try {
    console.log('Sending update shipping method payload:', { shippingMethodId, shippingMethodData });
    const response = await apiInstance.patch(`shipping_methods1/${shippingMethodId}/`, shippingMethodData);
    console.log('Update shipping method response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error updating shipping method:', error.response?.data || error.message);
    throw error;
  }
};

export const deleteShippingMethod = async (apiInstance, shippingMethodId) => {
  try {
    console.log('Sending delete shipping method request:', { shippingMethodId });
    const response = await apiInstance.delete(`shipping_methods1/${shippingMethodId}/`);
    console.log('Delete shipping method response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error deleting shipping method:', error.response?.data || error.message);
    throw error;
  }
};


export default {
  createApiInstance,
  register,
  login,
  googleAuth,
  logout,
  fetchCurrentUserInfo,
  getUserProfile,
  updateUserProfile,
  getDeliveryLocations,
  addDeliveryLocation,
  setDefaultDeliveryLocation,
  deleteDeliveryLocation,
  fetchCategories,
  fetchRelatedProducts,
  createCategory,
  updateCategory,
  deleteCategory,
  fetchProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  fetchAllOrders,
  deleteOrder,
  fetchCategoryProducts,
  fetchProductDetails,
  fetchAllCategoriesWithProducts,
  fetchCart,
  fetchOrders,
  fetchOrder,
  fetchCompletedOrders,
  createCart,
  addToCart,
  removeFromCart,
  checkoutCart,
  cancelOrder,
  searchProducts,
  adminLogin,
  adminRegister,
  fetchProfile,
  updateProfile,
  fetchDashboardData,
  fetchProductReviews, 
  submitProductReview,
  bulkUpdateOrderStatus,
  placeOrderForProduct,
  getMOQFulfilledProducts,
  fetchAllOrdersAdmin,
  updateSingleOrderStatus,
  fetchSuppliers,
  createSupplier,
  fetchAttributes,
  createAttribute,
  fetchHomeCategories,
  deleteShippingMethod,
  updateShippingMethod,
  createShippingMethod,
  fetchPickupCategories,
  searchOrders,
  searchSuggestions,

  fetchDeliveryLocations: getDeliveryLocations,

};
