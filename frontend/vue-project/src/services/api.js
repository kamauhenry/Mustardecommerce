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



const login = async (apiInstance, username, password) => {
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

export const fetchCurrentUserInfo = async (apiInstance) => {
  try {
    const response = await apiInstance.get('auth/user/');
    return response.data;
  } catch (error) {
    console.error('Error fetching current user info:', error.response?.data || error.message);
    throw error;
  }
};

const logout = async (api) => {
  try {
    // Optional: implement server-side logout if needed
    await api.post('auth/logout/');
  } catch (error) {
    console.error('Logout error:', error.response?.data || error.message);
  } finally {
    // Always remove the token from local storage
    localStorage.removeItem('authToken');
  }
};
// Named exports for specific API calls using the dynamic api instance
const fetchCategories = async (api) => {
  try {
    const response = await api.get('categories/', {
      timeout: 60000,  // Increased timeout to 60 seconds
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching categories:', error.response?.data || error.message);
    throw error;
  }
};


const fetchCategoryProducts = async (api, categorySlug, page = 1, perPage = 5) => {
  try {
    const response = await api.get(`category/${categorySlug}/products/`, { params: { page, per_page: perPage } }, {
      timeout: 60000,  // Increased timeout to 60 seconds
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching category products:', error.response?.data || error.message);
    throw error;
  }
}; //works

const fetchProductDetails = async (apiInstance, categorySlug, productSlug) => {
  const response = await apiInstance.get(`products/${categorySlug}/${productSlug}/`);
  return response.data;
};

const fetchAllCategoriesWithProducts = async (api) => {
  try {
    const response = await api.get('all-categories-with-products/', {
      timeout: 120000,  // Increased timeout to 60 seconds
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching all categories with products:', error.response?.data || error.message);
    throw error;
  }
}; //works

const fetchCart = async (api, userId) => {
  try {
    const response = await api.get(`users/${userId}/cart/`, {
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching cart:', error.response?.data || error.message);
    throw error;
  }
};




const fetchOrders = async (api, userId) => {
  if (!userId) throw new Error('User ID not set');
  try {
    const response = await api.get(`orders/user-orders/?user=${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error.response?.data || error.message);
    throw error;
  }
};

const fetchCompletedOrders = async (api, userId) => {
  if (!userId) throw new Error('User ID not set');
  try {
    const response = await api.get(`completed-orders/?user=${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching completed orders:', error.response?.data || error.message);
    throw error;
  }
};

const createCart = async (api, userId) => {
  try {
    const response = await api.post(`carts/`, {userId: userId});
    return response.data;
  } catch (error) {
    console.error('Error creating cart:', error.response?.data || error.message);
    throw error;
  }
};

const addToCart = async (api, cartId, productId, variantId, quantity = 1) => {
  try {
    console.log('Adding to cart:', { cartId, productId, variantId, quantity });
    const response = await api.post(`carts/${cartId}/add_item/`, {
      product: productId,
      variant: variantId,
      quantity,
    });
    console.log('Add to cart response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error adding to cart:', error.response?.data || error.message);
    throw error;
  }
};

const removeFromCart = async (api, cartId, itemId) => {
  try {
    const response = await api.post(`carts/${cartId}/remove_item/`, { item_id: itemId });
    return response.data;
  } catch (error) {
    console.error('Error removing from cart:', error.response?.data || error.message);
    throw error;
  }
};

const checkoutCart = async (api, cartId, shippingMethod, shippingAddress, paymentMethod) => {
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

const cancelOrder = async (api, orderId) => {
  try {
    const response = await api.post(`orders/${orderId}/cancel/`);
    return response.data;
  } catch (error) {
    console.error('Error canceling order:', error.response?.data || error.message);
    throw error;
  }
};
// Fixed version
// Utility function to search products
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

const api = {
  createApiInstance,
  fetchCategories,
  fetchCurrentUserInfo,
  fetchCategoryProducts,
  fetchProductDetails,
  fetchAllCategoriesWithProducts,
  fetchCart,
  fetchOrders,
  fetchCompletedOrders,
  addToCart,
  removeFromCart,
  checkoutCart,
  cancelOrder,
  searchProducts,
  createCart,
  login,
  logout
};

// Export the api object as the default export
export default api;
