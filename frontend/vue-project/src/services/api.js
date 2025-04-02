import axios from 'axios';

const createApiInstance = (store) => {
  const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
    timeout: 150000,
    withCredentials: true,
  });

  api.interceptors.request.use(
    (config) => {
      if (store.token) {
        config.headers['Authorization'] = `Token ${store.token}`;
      }
      if (store.userId) {
        config.headers['X-User-Id'] = store.userId;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  return api;
};

// Existing API Methods
const fetchCategories = async (api) => {
  try {
    const response = await api.get('categories/', { timeout: 60000 });
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

const fetchCategoryProducts = async (api, categorySlug, page = 1, perPage = 5) => {
  try {
    const response = await api.get(`category/${categorySlug}/products/`, { params: { page, per_page: perPage } }, { timeout: 60000 });
    return response.data;
  } catch (error) {
    console.error('Error fetching category products:', error.response?.data || error.message);
    throw error;
  }
};

const fetchProductDetails = async (api, categorySlug, productSlug) => {
  try {
    const response = await api.get(`products/${categorySlug}/${productSlug}/`, { timeout: 60000 });
    return response.data;
  } catch (error) {
    console.error('Error fetching product details:', error.response?.data || error.message);
    throw error;
  }
};

const fetchAllCategoriesWithProducts = async (api) => {
  try {
    const response = await api.get('all-categories-with-products/', { timeout: 60000 });
    return response.data;
  } catch (error) {
    console.error('Error fetching all categories with products:', error.response?.data || error.message);
    throw error;
  }
};

const fetchCart = async (api, cartId) => {
  if (!cartId) throw new Error('Cart ID not set');
  try {
    const response = await api.get(`carts/${cartId}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching cart:', error.response?.data || error.message);
    throw error;
  }
};

const fetchOrders = async (api, userId) => {
  if (!userId) throw new Error('User ID not set');
  try {
    const response = await api.get(`orders/?user=${userId}`);
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

const addToCart = async (api, cartId, productId, variantId, quantity = 1) => {
  try {
    const response = await api.post(`carts/${cartId}/add_item/`, {
      product: productId,
      variant: variantId,
      quantity,
    });
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
      payment_method: paymentMethod,
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

const login = async (api, credentials) => {
  try {
    const response = await api.post('login/', credentials); // Removed /auth
    return response.data;
  } catch (error) {
    console.error('Error logging in:', error.response?.data || error.message);
    throw error;
  }
};

const register = async (api, userData) => {
  try {
    const response = await api.post('register/', userData); // Removed /auth
    return response.data;
  } catch (error) {
    console.error('Error registering:', error.response?.data || error.message);
    throw error;
  }
};

const adminRegister = async (api, userData) => {
  try {
    const response = await api.post('admin-page/register/', userData);
    return response.data;
  } catch (error) {
    console.error('Error registering as admin:', error.response?.data || error.message);
    throw error;
  }
};

const adminLogin = async (api, credentials) => {
  try {
    const response = await api.post('admin-page/login/', credentials);
    return { user: response.data.user, token: response.data.token };
  } catch (error) {
    console.error('Error logging in as admin:', error.response?.data || error.message);
    throw error;
  }
};

const logout = async (api) => {
  try {
    const response = await api.post('logout/'); // Removed /auth
    return response.data;
  } catch (error) {
    console.error('Error logging out:', error.response?.data || error.message);
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

const updateProfile = async (api, userData) => {
  try {
    const response = await api.put('admin-page/profile/', userData);
    return response.data;
  } catch (error) {
    console.error('Error updating profile:', error.response?.data || error.message);
    throw error;
  }
};

const fetchDashboardData = async (api) => {
  try {
    const response = await api.get('admin-page/dashboard/');
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error.response?.data || error.message);
    throw error;
  }
};

const api = {
  createApiInstance,
  fetchCategories,
  createCategory,
  updateCategory,
  deleteCategory,
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
  login,
  register,
  adminLogin,
  adminRegister,
  logout,
  fetchProfile,
  updateProfile,
  fetchDashboardData,
};

export default api;
