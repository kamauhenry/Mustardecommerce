<template>
  <AdminLayout>
    <div class="admin-container">
      <h2>Admin Dashboard</h2>

      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <button 
          @click="activeTab = 'categories'" 
          :class="{ active: activeTab === 'categories' }"
          class="tab-button"
        >
          Manage Categories
        </button>
        <button 
          @click="activeTab = 'moq-requests'" 
          :class="{ active: activeTab === 'moq-requests' }"
          class="tab-button"
        >
          MOQ Requests
          <span v-if="moqRequestsCount > 0" class="badge">{{ moqRequestsCount }}</span>
        </button>
      </div>

      <!-- Categories Tab -->
      <div v-if="activeTab === 'categories'" class="categories">
        <!-- Loading State -->
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          Loading categories...
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-message">
          {{ error }}
          <button @click="fetchAllCategoriesWithProducts" class="retry-button">Retry</button>
        </div>

        <!-- Form to Add/Edit Category -->
        <div v-else class="category-form">
          <h3>{{ editingCategory ? 'Edit Category' : 'Add New Category' }}</h3>
          <form @submit.prevent="saveCategory">
            <div class="form-group">
              <label>Name</label>
              <input v-model="form.name" required placeholder="Enter category name" @input="generateSlug" />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="form.description" placeholder="Enter category description"></textarea>
            </div>
            <div class="form-group">
              <label>Category Image</label>
              <input type="file" accept="image/*" @change="handleImageUpload" ref="imageInput" />
              <div v-if="imagePreview" class="image-preview">
                <img :src="imagePreview" alt="Image Preview" />
                <button type="button" @click="clearImage" class="clear-image-btn">Remove Image</button>
              </div>
            </div>
            <button type="submit" :disabled="formLoading">
              {{ formLoading ? 'Saving...' : (editingCategory ? 'Update' : 'Add') }} Category
            </button>
            <button v-if="editingCategory" type="button" @click="cancelEdit" :disabled="formLoading">
              Cancel
            </button>
          </form>
        </div>

        <!-- Categories List -->
        <div v-if="!loading && !error" class="categories-list">
          <h3>Categories</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Image</th>
                <th>Name</th>
                <th>Slug</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="category in categories" :key="category.id">
                <td>{{ category.id }}</td>
                <td>
                  <img v-if="category.image" :src="category.image" alt="Category Image" class="category-image" />
                  <span v-else>N/A</span>
                </td>
                <td>{{ category.name }}</td>
                <td>{{ category.slug || 'N/A' }}</td>
                <td>
                  <button @click="editCategory(category)" :disabled="formLoading">Edit</button>
                  <button @click="deleteCategory(category.id)" :disabled="formLoading">Delete</button>
                </td>
              </tr>
              <tr v-if="!categories.length">
                <td colspan="5" class="no-data">No categories available.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- MOQ Requests Tab -->
      <div v-if="activeTab === 'moq-requests'" class="moq-requests">
        <!-- Loading State -->
        <div v-if="moqLoading" class="loading">
          <div class="spinner"></div>
          Loading MOQ requests...
        </div>

        <!-- Error Message -->
        <div v-if="moqError" class="error-message">
          {{ moqError }}
          <button @click="fetchMOQRequests" class="retry-button">Retry</button>
        </div>

        <!-- MOQ Requests Content -->
        <div v-else class="moq-content">
          <!-- Status Filter -->
          <div class="filter-section">
            <h3>MOQ Requests</h3>
            <div class="filter-controls">
              <label>Filter by Status:</label>
              <select v-model="statusFilter" @change="fetchMOQRequests">
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>

          <!-- MOQ Requests Table -->
          <div class="requests-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Product Name</th>
                  <th>Quantity</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="request in moqRequests" :key="request.id">
                  <td>{{ request.id }}</td>
                  <td>{{ request.user_email }}</td>
                  <td>
                    <div class="product-info">
                      <span class="product-name">{{ request.product_name }}</span>
                      <a v-if="request.product_link" :href="request.product_link" target="_blank" class="product-link">
                        View Product
                      </a>
                    </div>
                  </td>
                  <td>{{ request.quantity }}</td>
                  <td>
                    <span :class="['status-badge', `status-${request.status}`]">
                      {{ request.status.charAt(0).toUpperCase() + request.status.slice(1) }}
                    </span>
                  </td>
                  <td>{{ formatDate(request.created_at) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button @click="viewRequestDetails(request)" class="view-btn">
                        View
                      </button>
                      <button 
                        v-if="request.status === 'pending'"
                        @click="updateRequestStatus(request.id, 'approved')" 
                        class="approve-btn"
                        :disabled="updatingStatus"
                      >
                        Approve
                      </button>
                      <button 
                        v-if="request.status === 'pending'"
                        @click="updateRequestStatus(request.id, 'rejected')" 
                        class="reject-btn"
                        :disabled="updatingStatus"
                      >
                        Reject
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!moqRequests.length">
                  <td colspan="7" class="no-data">No MOQ requests found.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Request Details Modal -->
      <div v-if="selectedRequest" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>MOQ Request Details</h3>
            <button @click="closeModal" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="detail-row">
              <strong>Request ID:</strong> {{ selectedRequest.id }}
            </div>
            <div class="detail-row">
              <strong>User:</strong> {{ selectedRequest.user_email }}
            </div>
            <div class="detail-row">
              <strong>Product Name:</strong> {{ selectedRequest.product_name }}
            </div>
            <div class="detail-row">
              <strong>Product Link:</strong> 
              <a v-if="selectedRequest.product_link" :href="selectedRequest.product_link" target="_blank">
                {{ selectedRequest.product_link }}
              </a>
              <span v-else>N/A</span>
            </div>
            <div class="detail-row">
              <strong>Quantity:</strong> {{ selectedRequest.quantity }}
            </div>
            <div class="detail-row">
              <strong>Status:</strong> 
              <span :class="['status-badge', `status-${selectedRequest.status}`]">
                {{ selectedRequest.status.charAt(0).toUpperCase() + selectedRequest.status.slice(1) }}
              </span>
            </div>
            <div class="detail-row">
              <strong>Description:</strong> 
              <p>{{ selectedRequest.description || 'No description provided' }}</p>
            </div>
            <div class="detail-row">
              <strong>Created:</strong> {{ formatDate(selectedRequest.created_at) }}
            </div>
          </div>
          <div class="modal-footer">
            <button v-if="selectedRequest.status === 'pending'" @click="updateRequestStatus(selectedRequest.id, 'approved')" class="approve-btn">
              Approve
            </button>
            <button v-if="selectedRequest.status === 'pending'" @click="updateRequestStatus(selectedRequest.id, 'rejected')" class="reject-btn">
              Reject
            </button>
            <button @click="closeModal" class="cancel-btn">Close</button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import { useAuthStore } from '@/stores/modules/auth';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import api from '@/services/api';

export default {
  components: { AdminLayout },
  setup() {
    const authStore = useAuthStore();
    // Create minimal store object for api.js compatibility
    const store = { isAuthenticated: computed(() => authStore.isAuthenticated) };
    
    // Tab management
    const activeTab = ref('categories');
    
    // Categories data
    const categories = ref([]);
    const form = ref({ name: '', description: '', slug: '', image: null });
    const editingCategory = ref(null);
    const loading = ref(false);
    const formLoading = ref(false);
    const error = ref(null);
    const imagePreview = ref(null);
    const imageInput = ref(null);

    // MOQ Requests data
    const moqRequests = ref([]);
    const moqLoading = ref(false);
    const moqError = ref(null);
    const statusFilter = ref('');
    const selectedRequest = ref(null);
    const updatingStatus = ref(false);

    // Computed properties
    const moqRequestsCount = computed(() => {
      return moqRequests.value.filter(req => req.status === 'pending').length;
    });

    // Categories methods
    const fetchAllCategoriesWithProducts = async () => {
      try {
        loading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const response = await api.fetchCategories(apiInstance);
        categories.value = response || [];
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to load categories. Please try again.';
        console.error('Failed to fetch categories:', err);
      } finally {
        loading.value = false;
      }
    };

    const handleImageUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        form.value.image = file;
        const reader = new FileReader();
        reader.onload = (e) => {
          imagePreview.value = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    };

    const clearImage = () => {
      form.value.image = null;
      imagePreview.value = null;
      imageInput.value.value = '';
    };

    const generateSlug = () => {
      form.value.slug = form.value.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
    };

    const saveCategory = async () => {
      try {
        formLoading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const formData = new FormData();
        formData.append('name', form.value.name);
        formData.append('description', form.value.description);
        formData.append('slug', form.value.slug);
        if (form.value.image) formData.append('image', form.value.image);

        if (editingCategory.value) {
          await api.updateCategory(apiInstance, editingCategory.value.id, formData);
          alert('Category updated successfully');
        } else {
          await api.createCategory(apiInstance, formData);
          alert('Category added successfully');
        }
        form.value = { name: '', description: '', slug: '', image: null };
        imagePreview.value = null;
        editingCategory.value = null;
        await fetchAllCategoriesWithProducts();
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to save category. Please try again.';
        console.error('Failed to save category:', err);
      } finally {
        formLoading.value = false;
      }
    };

    const editCategory = (category) => {
      editingCategory.value = category;
      form.value = { 
        name: category.name, 
        description: category.description || '', 
        slug: category.slug, 
        image: null 
      };
      imagePreview.value = category.primary_image || null;
    };

    const cancelEdit = () => {
      editingCategory.value = null;
      form.value = { name: '', description: '', slug: '', image: null };
      imagePreview.value = null;
    };

    const deleteCategory = async (categoryId) => {
      if (confirm('Are you sure you want to delete this category?')) {
        try {
          formLoading.value = true;
          error.value = null;
          const apiInstance = api.createApiInstance(store);
          await api.deleteCategory(apiInstance, categoryId);
          alert('Category deleted successfully');
          await fetchAllCategoriesWithProducts();
        } catch (err) {
          error.value = err.response?.data?.error || 'Failed to delete category. Please try again.';
          console.error('Failed to delete category:', err);
        } finally {
          formLoading.value = false;
        }
      }
    };

    // MOQ Requests methods
    const fetchMOQRequests = async () => {
      try {
        moqLoading.value = true;
        moqError.value = null;
        const apiInstance = api.createApiInstance(store);
        
        // Build query parameters
        const params = {};
        if (statusFilter.value) {
          params.status = statusFilter.value;
        }
        
        const response = await apiInstance.get('/moqrequest/', { params });
        moqRequests.value = response.data.results || response.data || [];
      } catch (err) {
        moqError.value = err.response?.data?.error || 'Failed to load MOQ requests. Please try again.';
        console.error('Failed to fetch MOQ requests:', err);
      } finally {
        moqLoading.value = false;
      }
    };

    const updateRequestStatus = async (requestId, newStatus) => {
      try {
        updatingStatus.value = true;
        const apiInstance = api.createApiInstance(store);
        
        await apiInstance.post(`/moqrequest/${requestId}/update_status/`, {
          status: newStatus
        });
        
        // Update the local data
        const requestIndex = moqRequests.value.findIndex(req => req.id === requestId);
        if (requestIndex !== -1) {
          moqRequests.value[requestIndex].status = newStatus;
        }
        
        // Update selected request if it's the same
        if (selectedRequest.value && selectedRequest.value.id === requestId) {
          selectedRequest.value.status = newStatus;
        }
        
        alert(`Request ${newStatus} successfully`);
        
      } catch (err) {
        moqError.value = err.response?.data?.error || 'Failed to update request status. Please try again.';
        console.error('Failed to update request status:', err);
      } finally {
        updatingStatus.value = false;
      }
    };

    const viewRequestDetails = (request) => {
      selectedRequest.value = request;
    };

    const closeModal = () => {
      selectedRequest.value = null;
    };

    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    // Watch for tab changes
    watch(activeTab, (newTab) => {
      if (newTab === 'moq-requests' && moqRequests.value.length === 0) {
        fetchMOQRequests();
      }
    });

    // Watch for form name changes
    watch(() => form.value.name, (newName) => {
      if (!editingCategory.value) {
        generateSlug();
      }
    });

    onMounted(() => {
      fetchAllCategoriesWithProducts();
    });

    return {
      // Tab management
      activeTab,
      
      // Categories
      categories,
      form,
      editingCategory,
      loading,
      formLoading,
      error,
      imagePreview,
      imageInput,
      fetchAllCategoriesWithProducts,
      saveCategory,
      editCategory,
      cancelEdit,
      deleteCategory,
      handleImageUpload,
      clearImage,
      
      // MOQ Requests
      moqRequests,
      moqLoading,
      moqError,
      statusFilter,
      selectedRequest,
      updatingStatus,
      moqRequestsCount,
      fetchMOQRequests,
      updateRequestStatus,
      viewRequestDetails,
      closeModal,
      formatDate,
    };
  },
};
</script>

<style scoped>
.admin-container {
  padding: 20px;
  background-color: transparent;
  border-radius: 0;
  box-shadow: none;
}

/* Tab Navigation */
.tab-navigation {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 20px;
}

.tab-button {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  position: relative;
}

.tab-button:hover {
  color: #4f46e5;
  background-color: #f8f9fa;
}

.tab-button.active {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
}

.badge {
  background-color: #e74c3c;
  color: white;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

/* Existing category styles */
.categories {
  padding: 0;
}

h2 {
  font-size: 1.75rem;
  color: #4f46e5;
  margin-bottom: 24px;
  border-bottom: none;
  padding-bottom: 0;
  font-weight: 700;
}

h3 {
  font-size: 1.1rem;
  color: #4f46e5;
  margin-bottom: 12px;
  border-bottom: none;
  padding-bottom: 0;
  font-weight: 700;
}

.category-form {
  margin-bottom: 30px;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input[type="text"],
.form-group input[type="file"],
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-group textarea {
  height: 100px;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6f42c1;
}

.image-preview {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.image-preview img {
  max-width: 100px;
  max-height: 100px;
  object-fit: cover;
  border-radius: 4px;
}

.clear-image-btn {
  background-color: #e74c3c;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
}

.clear-image-btn:hover:not(:disabled) {
  background-color: #c0392b;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  margin-right: 10px;
}

button[type="submit"] {
  background-color: #6f42c1;
  color: white;
}

button[type="submit"]:hover:not(:disabled) {
  background-color: #5a32a3;
}

button[type="button"] {
  background-color: #f1f1f1;
  color: #333;
}

button[type="button"]:hover:not(:disabled) {
  background-color: #e0e0e0;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.categories-list {
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.categories-list table {
  width: 100%;
  border-collapse: collapse;
}

.categories-list th,
.categories-list td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.categories-list th {
  background-color: #6f42c1;
  color: white;
  font-weight: 600;
}

.categories-list tr:hover {
  background-color: #f9f9f9;
}

.categories-list td button {
  padding: 6px 12px;
  border-radius: 4px;
}

.categories-list td button:first-child {
  background-color: #6f42c1;
  color: white;
  margin-right: 5px;
}

.categories-list td button:first-child:hover:not(:disabled) {
  background-color: #5a32a3;
}

.categories-list td button:last-child {
  background-color: #e74c3c;
  color: white;
}

.categories-list td button:last-child:hover:not(:disabled) {
  background-color: #c0392b;
}

.category-image {
  max-width: 50px;
  max-height: 50px;
  object-fit: cover;
  border-radius: 4px;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 20px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #666;
  margin: 20px 0;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #6f42c1;
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-message {
  color: #e74c3c;
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.2rem;
  font-weight: 500;
  padding: 15px;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  background-color: #ffe6e6;
}

.retry-button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.retry-button:hover {
  background-color: #5a32a3;
}

/* MOQ Requests Styles */
.moq-requests {
  padding: 0;
}

.moq-content {
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-controls label {
  font-weight: 500;
  color: #333;
}

.filter-controls select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background-color: white;
}

.requests-table table {
  width: 100%;
  border-collapse: collapse;
}

.requests-table th,
.requests-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.requests-table th {
  background-color: #6f42c1;
  color: white;
  font-weight: 600;
}

.requests-table tr:hover {
  background-color: #f9f9f9;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-name {
  font-weight: 500;
}

.product-link {
  color: #6f42c1;
  text-decoration: none;
  font-size: 0.9rem;
}

.product-link:hover {
  text-decoration: underline;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-approved {
  background-color: #d4edda;
  color: #155724;
}

.status-rejected {
  background-color: #f8d7da;
  color: #721c24;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.action-buttons button {
  padding: 4px 8px;
  font-size: 0.85rem;
  border-radius: 4px;
  margin-right: 0;
}

.view-btn {
  background-color: #6f42c1;
  color: white;
}

.view-btn:hover:not(:disabled) {
  background-color: #5a32a3;
}

.approve-btn {
  background-color: #28a745;
  color: white;
}

.approve-btn:hover:not(:disabled) {
  background-color: #218838;
}

.reject-btn {
  background-color: #dc3545;
  color: white;
}

.reject-btn:hover:not(:disabled) {
  background-color: #c82333;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #4f46e5;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  margin: 0;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.detail-row {
  margin-bottom: 15px;
}

.detail-row strong {
  display: inline-block;
  min-width: 120px;
  color: #333;
}

.detail-row p {
  margin: 5px 0 0 0;
  color: #666;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover:not(:disabled) {
  background-color: #5a6268;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .admin-container {
    padding: 10px;
  }

  .tab-navigation {
    margin-bottom: 15px;
  }

  .tab-button {
    padding: 10px 16px;
    font-size: 0.9rem;
  }

  h2 {
    font-size: 1.5rem;
    margin-bottom: 20px;
  }

  h3 {
    font-size: 1rem;
    margin-bottom: 10px;
  }

  .category-form {
    padding: 15px;
    margin-bottom: 20px;
  }

  .form-group {
    margin-bottom: 12px;
  }

  .form-group label {
    font-size: 0.9rem;
  }

  .form-group input[type="text"],
  .form-group input[type="file"],
  .form-group textarea {
    font-size: 0.9rem;
    padding: 6px 10px;
  }

  .image-preview img {
    max-width: 80px;
    max-height: 80px;
  }

  button {
    padding: 6px 12px;
    font-size: 0.9rem;
    margin-right: 8px;
  }

  .categories-list {
    padding: 15px;
  }

  .categories-list table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }

  .categories-list th,
  .categories-list td {
    padding: 10px 12px;
    font-size: 0.9rem;
  }

  .category-image {
    max-width: 40px;
    max-height: 40px;
  }

  .categories-list td button {
    padding: 5px 10px;
    font-size: 0.85rem;
  }

  .loading {
    font-size: 1rem;
  }

  .spinner {
    width: 20px;
    height: 20px;
  }

  .error-message {
    font-size: 1rem;
    padding: 12px;
  }

  .retry-button {
    padding: 6px 12px;
    font-size: 0.9rem;
  }

  /* MOQ Requests Mobile */
  .moq-content {
    padding: 15px;
  }

  .filter-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .filter-controls {
    width: 100%;
    justify-content: flex-start;
  }

  .filter-controls select {
    flex: 1;
    max-width: 200px;
  }

  .requests-table table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }

  .requests-table th,
  .requests-table td {
    padding: 8px 10px;
    font-size: 0.85rem;
  }

  .product-info {
    min-width: 150px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 3px;
  }

  .action-buttons button {
    font-size: 0.8rem;
    padding: 3px 6px;
  }

  .status-badge {
    font-size: 0.8rem;
    padding: 2px 6px;
  }

  .modal-content {
    width: 95%;
    margin: 10px;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 15px;
  }

  .modal-header h3 {
    font-size: 1.1rem;
  }

  .detail-row strong {
    min-width: 100px;
    font-size: 0.9rem;
  }

  .modal-footer {
    flex-direction: column;
    gap: 8px;
  }

  .modal-footer button {
    width: 100%;
    margin-right: 0;
  }
}

@media (max-width: 480px) {
  .admin-container {
    padding: 8px;
  }

  .tab-button {
    padding: 8px 12px;
    font-size: 0.85rem;
  }

  .badge {
    font-size: 0.7rem;
    padding: 1px 4px;
  }

  h2 {
    font-size: 1.25rem;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 0.9rem;
    margin-bottom: 8px;
  }

  .category-form {
    padding: 10px;
    margin-bottom: 16px;
  }

  .form-group {
    margin-bottom: 10px;
  }

  .form-group label {
    font-size: 0.85rem;
  }

  .form-group input[type="text"],
  .form-group input[type="file"],
  .form-group textarea {
    font-size: 0.85rem;
    padding: 5px 8px;
  }

  .image-preview img {
    max-width: 60px;
    max-height: 60px;
  }

  button {
    padding: 5px 10px;
    font-size: 0.85rem;
    margin-right: 6px;
  }

  .categories-list {
    padding: 10px;
  }

  .categories-list th,
  .categories-list td {
    padding: 8px 10px;
    font-size: 0.85rem;
  }

  .category-image {
    max-width: 30px;
    max-height: 30px;
  }

  .categories-list td button {
    padding: 4px 8px;
    font-size: 0.8rem;
  }

  .no-data {
    padding: 15px;
    font-size: 0.9rem;
  }

  .loading {
    font-size: 0.9rem;
  }

  .spinner {
    width: 18px;
    height: 18px;
  }

  .error-message {
    font-size: 0.9rem;
    padding: 10px;
  }

  .retry-button {
    padding: 5px 10px;
    font-size: 0.85rem;
  }

  /* MOQ Requests Mobile Small */
  .moq-content {
    padding: 10px;
  }

  .filter-controls label {
    font-size: 0.85rem;
  }

  .filter-controls select {
    font-size: 0.85rem;
    padding: 6px 10px;
  }

  .requests-table th,
  .requests-table td {
    padding: 6px 8px;
    font-size: 0.8rem;
  }

  .product-info {
    min-width: 120px;
  }

  .product-name {
    font-size: 0.8rem;
  }

  .product-link {
    font-size: 0.75rem;
  }

  .action-buttons button {
    font-size: 0.75rem;
    padding: 2px 4px;
  }

  .status-badge {
    font-size: 0.7rem;
    padding: 1px 4px;
  }

  .modal-content {
    width: 98%;
    margin: 5px;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 10px;
  }

  .modal-header h3 {
    font-size: 1rem;
  }

  .detail-row {
    margin-bottom: 10px;
  }

  .detail-row strong {
    min-width: 80px;
    font-size: 0.85rem;
  }

  .detail-row p {
    font-size: 0.85rem;
  }
}
</style>