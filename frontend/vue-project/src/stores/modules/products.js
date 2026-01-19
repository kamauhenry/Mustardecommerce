import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApiCall } from '../composables/useApiCall';
import { useApiInstance } from '../composables/useApiInstance';
import { toast } from '../composables/useToast';

/**
 * Products Store Module
 * Handles product catalog, categories, filtering, and product details
 */
export const useProductsStore = defineStore('products', () => {
  // State
  const products = ref([]);
  const categories = ref([]);
  const currentProduct = ref(null);
  const latestProducts = ref([]);
  const featuredProducts = ref([]);
  const productsByCategory = ref({});
  const isLoadingProducts = ref(false);
  const isLoadingCategories = ref(false);
  const isLoadingProduct = ref(false);

  // Home categories state (for HomePage)
  const allhomeCategoriesWithProducts = ref([]);
  const homeCategoriesPagination = ref({ nextPage: 1, hasMore: true, totalCount: 0 });
  const isLoadingHomeCategories = ref(false);
  const homeCategoriesError = ref(null);

  // Category products state (for CategoryProducts page)
  const categoryProducts = ref({});
  const categoryProductsErrors = ref({});
  const isLoadingCategoryProducts = ref(false);

  // Product details state (for ProductDetails page)
  const productDetails = ref({});

  // All categories with products state (for MOQCampaigns)
  const allCategoriesWithProducts = ref([]);
  const isLoadingAllCategories = ref(false);
  const allCategoriesError = ref(null);

  // Pickup categories state (for Pay & Pick page)
  const pickupCategories = ref([]);
  const pickupCategoriesPagination = ref({ nextPage: 1, hasMorePages: true, totalCount: 0 });
  const isLoadingPickupCategories = ref(false);
  const pickupCategoriesError = ref(null);

  // Pagination
  const currentPage = ref(1);
  const totalPages = ref(1);
  const pageSize = ref(12);
  const totalProducts = ref(0);

  // Filters
  const filters = ref({
    category: null,
    minPrice: null,
    maxPrice: null,
    inStock: false,
    sortBy: 'created_at',
    sortOrder: 'desc',
  });

  // API instance
  const { api } = useApiInstance();

  // Computed
  const hasProducts = computed(() => products.value.length > 0);
  const hasCategories = computed(() => categories.value.length > 0);

  /**
   * Fetch all products with pagination and filters
   * @param {number} page - Page number
   * @param {Object} filterOptions - Filter options
   */
  const fetchProducts = async (page = 1, filterOptions = {}) => {
    const { execute } = useApiCall();
    isLoadingProducts.value = true;

    try {
      const params = {
        page,
        page_size: pageSize.value,
        ...filters.value,
        ...filterOptions,
      };

      const response = await execute(
        async () => api.get('/products/', { params }),
        { showToast: false }
      );

      products.value = response.results || response;
      currentPage.value = page;
      totalPages.value = response.total_pages || 1;
      totalProducts.value = response.count || products.value.length;
    } catch (error) {
      toast.error('Failed to load products');
      console.error('Fetch products error:', error);
    } finally {
      isLoadingProducts.value = false;
    }
  };

  /**
   * Fetch product by ID
   * @param {number} productId - Product ID
   */
  const fetchProduct = async (productId) => {
    const { execute } = useApiCall();
    isLoadingProduct.value = true;

    try {
      const response = await execute(
        async () => api.get(`/products/${productId}/`),
        { showToast: false }
      );

      currentProduct.value = response;
      return response;
    } catch (error) {
      toast.error('Failed to load product details');
      console.error('Fetch product error:', error);
      return null;
    } finally {
      isLoadingProduct.value = false;
    }
  };

  /**
   * Fetch all categories
   */
  const fetchCategories = async () => {
    const { execute } = useApiCall();
    isLoadingCategories.value = true;

    try {
      const response = await execute(
        async () => api.get('/categories/'),
        { showToast: false }
      );

      categories.value = response;
    } catch (error) {
      toast.error('Failed to load categories');
      console.error('Fetch categories error:', error);
    } finally {
      isLoadingCategories.value = false;
    }
  };

  /**
   * Fetch products by category
   * @param {number} categoryId - Category ID
   * @param {number} page - Page number
   */
  const fetchProductsByCategory = async (categoryId, page = 1) => {
    const { execute } = useApiCall();

    try {
      const params = {
        category: categoryId,
        page,
        page_size: pageSize.value,
      };

      const response = await execute(
        async () => api.get('/products/', { params }),
        { showToast: false }
      );

      productsByCategory.value[categoryId] = response.results || response;
      return response.results || response;
    } catch (error) {
      toast.error('Failed to load category products');
      console.error('Fetch category products error:', error);
      return [];
    }
  };

  /**
   * Fetch latest products
   * @param {number} limit - Number of products to fetch
   */
  const fetchLatestProducts = async (limit = 12) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get(`/products/latest/?limit=${limit}`),
        { showToast: false }
      );

      latestProducts.value = response;
      return response;
    } catch (error) {
      console.error('Fetch latest products error:', error);
      return [];
    }
  };

  /**
   * Fetch featured products
   * @param {number} limit - Number of products to fetch
   */
  const fetchFeaturedProducts = async (limit = 12) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get(`/products/featured/?limit=${limit}`),
        { showToast: false }
      );

      featuredProducts.value = response;
      return response;
    } catch (error) {
      console.error('Fetch featured products error:', error);
      return [];
    }
  };

  /**
   * Apply filters to products
   * @param {Object} newFilters - New filter values
   */
  const applyFilters = async (newFilters) => {
    filters.value = { ...filters.value, ...newFilters };
    await fetchProducts(1, filters.value);
  };

  /**
   * Clear all filters
   */
  const clearFilters = async () => {
    filters.value = {
      category: null,
      minPrice: null,
      maxPrice: null,
      inStock: false,
      sortBy: 'created_at',
      sortOrder: 'desc',
    };
    await fetchProducts(1);
  };

  /**
   * Update sort order
   * @param {string} sortBy - Sort field
   * @param {string} sortOrder - Sort order (asc/desc)
   */
  const updateSort = async (sortBy, sortOrder = 'desc') => {
    filters.value.sortBy = sortBy;
    filters.value.sortOrder = sortOrder;
    await fetchProducts(1, filters.value);
  };

  /**
   * Go to next page
   */
  const nextPage = async () => {
    if (currentPage.value < totalPages.value) {
      await fetchProducts(currentPage.value + 1, filters.value);
    }
  };

  /**
   * Go to previous page
   */
  const previousPage = async () => {
    if (currentPage.value > 1) {
      await fetchProducts(currentPage.value - 1, filters.value);
    }
  };

  /**
   * Go to specific page
   * @param {number} page - Page number
   */
  const goToPage = async (page) => {
    if (page >= 1 && page <= totalPages.value) {
      await fetchProducts(page, filters.value);
    }
  };

  /**
   * Get related products
   * @param {number} productId - Product ID
   * @param {number} limit - Number of related products
   */
  const getRelatedProducts = async (productId, limit = 4) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get(`/products/${productId}/related/?limit=${limit}`),
        { showToast: false }
      );

      return response;
    } catch (error) {
      console.error('Fetch related products error:', error);
      return [];
    }
  };

  /**
   * Clear current product
   */
  const clearCurrentProduct = () => {
    currentProduct.value = null;
  };

  /**
   * Fetch home categories with products (paginated)
   * @param {number} page - Page number
   */
  const fetchHomeCategories = async (page = 1) => {
    const { execute } = useApiCall();
    isLoadingHomeCategories.value = true;
    homeCategoriesError.value = null;

    try {
      const response = await execute(
        async () => api.get(`home-categories/?page=${page}`),
        { showToast: false }
      );

      const results = response.results || response;

      if (page === 1) {
        allhomeCategoriesWithProducts.value = results;
      } else {
        allhomeCategoriesWithProducts.value = [
          ...allhomeCategoriesWithProducts.value,
          ...results,
        ];
      }

      homeCategoriesPagination.value = {
        nextPage: response.next ? page + 1 : page,
        hasMore: !!response.next,
        totalCount: response.count || allhomeCategoriesWithProducts.value.length,
      };

      return response;
    } catch (error) {
      homeCategoriesError.value = error.message || 'Failed to load categories';
      console.error('Fetch home categories error:', error);
      throw error;
    } finally {
      isLoadingHomeCategories.value = false;
    }
  };

  /**
   * Fetch category products by slug (for CategoryProducts page)
   * @param {string} categorySlug - Category slug
   */
  const fetchCategoryProducts = async (categorySlug) => {
    const { execute } = useApiCall();
    isLoadingCategoryProducts.value = true;
    categoryProductsErrors.value[categorySlug] = null;

    try {
      const response = await execute(
        async () => api.get(`category/${categorySlug}/products/`),
        { showToast: false }
      );

      categoryProducts.value[categorySlug] = response;
      return response;
    } catch (error) {
      categoryProductsErrors.value[categorySlug] = error.message || 'Failed to load category products';
      console.error('Fetch category products error:', error);
      throw error;
    } finally {
      isLoadingCategoryProducts.value = false;
    }
  };

  /**
   * Fetch category products by slug (alias)
   * @param {string} categorySlug - Category slug
   */
  const fetchCategoryProductsBySlug = async (categorySlug) => {
    return fetchCategoryProducts(categorySlug);
  };

  /**
   * Fetch product details by category and product slug
   * @param {string} categorySlug - Category slug
   * @param {string} productSlug - Product slug
   */
  const fetchProductBySlug = async (categorySlug, productSlug) => {
    const { execute } = useApiCall();
    isLoadingProduct.value = true;

    try {
      const response = await execute(
        async () => api.get(`products/${categorySlug}/${productSlug}/`),
        { showToast: false }
      );

      currentProduct.value = response;
      // Also store in productDetails for backward compatibility
      const key = `${categorySlug}:${productSlug}`;
      productDetails.value[key] = response;
      return response;
    } catch (error) {
      toast.error('Failed to load product details');
      console.error('Fetch product error:', error);
      throw error;
    } finally {
      isLoadingProduct.value = false;
    }
  };

  /**
   * Fetch product details (alias for backward compatibility)
   * @param {string} categorySlug - Category slug
   * @param {string} productSlug - Product slug
   */
  const fetchProductDetails = async (categorySlug, productSlug) => {
    return fetchProductBySlug(categorySlug, productSlug);
  };

  /**
   * Fetch related products
   * @param {string} categorySlug - Category slug
   * @param {number} productId - Product ID
   */
  const fetchRelatedProducts = async (categorySlug, productId) => {
    const { execute } = useApiCall();

    try {
      const response = await execute(
        async () => api.get(`category/${categorySlug}/products/${productId}/related/`),
        { showToast: false }
      );

      return response;
    } catch (error) {
      console.error('Fetch related products error:', error);
      return [];
    }
  };

  /**
   * Fetch all categories with products (for MOQ Campaigns)
   */
  const fetchAllCategoriesWithProducts = async () => {
    const { execute } = useApiCall();
    isLoadingAllCategories.value = true;
    allCategoriesError.value = null;

    try {
      const response = await execute(
        async () => api.get('moq-categories/'),
        { showToast: false }
      );

      allCategoriesWithProducts.value = response.results || response;
      return response;
    } catch (error) {
      allCategoriesError.value = error.message || 'Failed to load MOQ categories';
      console.error('Fetch MOQ categories error:', error);
      throw error;
    } finally {
      isLoadingAllCategories.value = false;
    }
  };

  /**
   * Fetch pickup categories with products (paginated)
   * @param {number} page - Page number
   */
  const fetchPickupCategories = async (page = 1) => {
    const { execute } = useApiCall();
    isLoadingPickupCategories.value = true;
    pickupCategoriesError.value = null;

    try {
      const response = await execute(
        async () => api.get(`pickup-categories/?page=${page}`),
        { showToast: false }
      );

      const results = response.results || response;

      if (page === 1) {
        pickupCategories.value = results;
      } else {
        pickupCategories.value = [
          ...pickupCategories.value,
          ...results,
        ];
      }

      pickupCategoriesPagination.value = {
        nextPage: response.next ? page + 1 : page,
        hasMorePages: !!response.next,
        totalCount: response.count || pickupCategories.value.length,
      };

      return response;
    } catch (error) {
      pickupCategoriesError.value = error.message || 'Failed to load pickup categories';
      console.error('Fetch pickup categories error:', error);
      throw error;
    } finally {
      isLoadingPickupCategories.value = false;
    }
  };

  // Loading/error state object for backward compatibility
  const loading = {
    get allhomeCategoriesWithProducts() { return isLoadingHomeCategories.value; },
    get allCategoriesWithProducts() { return isLoadingAllCategories.value; },
    get pickupCategories() { return isLoadingPickupCategories.value; },
    get products() { return isLoadingProducts.value; },
    get categories() { return isLoadingCategories.value; },
    get categoryProducts() { return isLoadingCategoryProducts.value; },
  };

  const error = {
    get allhomeCategoriesWithProducts() { return homeCategoriesError.value; },
    set allhomeCategoriesWithProducts(val) { homeCategoriesError.value = val; },
    get allCategoriesWithProducts() { return allCategoriesError.value; },
    set allCategoriesWithProducts(val) { allCategoriesError.value = val; },
    get pickupCategories() { return pickupCategoriesError.value; },
    set pickupCategories(val) { pickupCategoriesError.value = val; },
    get categoryProducts() { return categoryProductsErrors.value; },
  };

  return {
    // State
    products,
    categories,
    currentProduct,
    latestProducts,
    featuredProducts,
    productsByCategory,
    isLoadingProducts,
    isLoadingCategories,
    isLoadingProduct,
    currentPage,
    totalPages,
    pageSize,
    totalProducts,
    filters,

    // Home categories state
    allhomeCategoriesWithProducts,
    homeCategoriesPagination,
    isLoadingHomeCategories,
    homeCategoriesError,

    // Category products state
    categoryProducts,
    categoryProductsErrors,
    isLoadingCategoryProducts,

    // Product details state
    productDetails,

    // MOQ categories state
    allCategoriesWithProducts,
    isLoadingAllCategories,
    allCategoriesError,

    // Pickup categories state
    pickupCategories,
    pickupCategoriesPagination,
    isLoadingPickupCategories,
    pickupCategoriesError,

    // Backward compatibility objects
    loading,
    error,

    // Computed
    hasProducts,
    hasCategories,

    // Actions
    fetchProducts,
    fetchProduct,
    fetchCategories,
    fetchProductsByCategory,
    fetchLatestProducts,
    fetchFeaturedProducts,
    applyFilters,
    clearFilters,
    updateSort,
    nextPage,
    previousPage,
    goToPage,
    getRelatedProducts,
    clearCurrentProduct,
    fetchHomeCategories,
    fetchCategoryProducts,
    fetchCategoryProductsBySlug,
    fetchProductBySlug,
    fetchProductDetails,
    fetchRelatedProducts,
    fetchAllCategoriesWithProducts,
    fetchPickupCategories,
  };
});
