<template>
  <AdminLayout>
    <div class="products">
      <h2>Manage Products</h2>

      <!-- Search Bar -->
      <div class="search-bar">
        <input
          v-model="searchQuery"
          placeholder="Search products by name..."
          @input="handleSearch"
        />
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        Loading products...
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="fetchData" class="retry-button">Retry</button>
      </div>

      <!-- Products List -->
      <div v-else class="products-content">
        <button class="add-button" @click="openAddModal" :disabled="formLoading">
          Add Product
        </button>

        <div class="products-list">
          <table v-if="filteredProducts.length">
            <thead>
              <tr>
                <th>Name</th>
                <th>Price (KES)</th>
                <th>Below MOQ Price</th>
                <th>MOQ</th>
                <th>MOQ Progress</th>
                <th>Supplier</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProducts" :key="product.id" class="product-row">
                <td class="product-name">{{ product.name }}</td>
                <td class="product-price">{{ formatPrice(product.price) }}</td>
                <td class="below-moq-price">{{ product.below_moq_price ? formatPrice(product.below_moq_price) : 'N/A' }}</td>
                <td class="moq-info">{{ product.moq || 'N/A' }} items</td>
                <td class="moq-progress-cell">
                  <div class="moq-progress-container">
                    <div
                      class="moq-progress-bar"
                      :style="{ width: Math.min(100, product.moq_progress?.percentage || 0) + '%' }"
                    ></div>
                    <span class="moq-progress-text">
                      {{ product.moq_progress?.percentage || 0 }}%
                    </span>
                  </div>
                </td>
                <td>{{ product.supplier?.name || 'N/A' }}</td>
                <td class="product-actions">
                  <button @click="openEditModal(product)" :disabled="formLoading" class="edit-button">Edit</button>
                  <button @click="deleteProduct(product.id)" :disabled="formLoading" class="delete-button">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Add/Edit Product Modal -->
      <div v-if="showModal" class="modal" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h3>{{ editMode ? 'Edit Product' : 'Add Product' }}</h3>
          <form @submit.prevent="saveProduct">
            <div class="form-group">
              <label>Name</label>
              <input
                v-model="form.name"
                required
                placeholder="Enter product name"
                @input="generateSlug"
              />
            </div>
            <div class="form-group">
              <label>Slug</label>
              <input
                v-model="form.slug"
                required
                placeholder="Product slug (auto-generated)"
                readonly
              />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="form.description" placeholder="Enter product description"></textarea>
            </div>
            <div class="form-group">
              <label>Price</label>
              <input v-model="form.price" type="number" step="0.01" required placeholder="Enter price" />
            </div>
            <div class="form-group">
              <label>Below MOQ Price</label>
              <input v-model="form.below_moq_price" type="number" step="0.01" placeholder="Enter below MOQ price (optional)" />
            </div>
            <div class="form-group">
              <label>MOQ (Minimum Order Quantity)</label>
              <input v-model="form.moq" type="number" placeholder="Enter MOQ (optional)" />
            </div>
            <div class="form-group">
              <label>MOQ Per Person</label>
              <input v-model="form.moq_per_person" type="number" placeholder="Enter MOQ per person (optional)" />
            </div>
            <div class="form-group">
              <label>MOQ Status</label>
              <select v-model="form.moq_status">
                <option value="active">Active</option>
                <option value="closed">Closed</option>
                <option value="completed">Completed</option>
                <option value="not_applicable">Not Applicable</option>
              </select>
            </div>
            <div class="form-group">
              <label>Category</label>
              <select v-model="form.category_id" required>
                <option value="">Select Category</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Supplier</label>
              <select v-model="form.supplier_id">
                <option value="">Select Supplier (optional)</option>
                <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
                  {{ supplier.name }}
                </option>
              </select>
              <button type="button" @click="openAddSupplierModal">Add New Supplier</button>
            </div>
            <div class="form-group">
              <label>Variant Attributes</label>
              <div>
                <select multiple v-model="form.attribute_ids">
                  <option v-for="attribute in attributes" :key="attribute.id" :value="attribute.id">
                    {{ attribute.attribute_name }}: {{ attribute.value }}
                  </option>
                </select>
                <button type="button" @click="openAddAttributeModal">Add New Attribute</button>
              </div>
            </div>
            <div class="form-group">
              <label>Product Images</label>
              <input type="file" multiple @change="handleFileUpload" accept="image/*" />
              <div v-if="form.images?.length" class="image-preview">
                <div v-for="(image, index) in form.images" :key="index" class="image-item">
                  <img :src="image.preview || image.image" alt="Product image" />
                  <button type="button" @click="removeImage(index)">Remove</button>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>Meta Title (for SEO)</label>
              <input v-model="form.meta_title" placeholder="Enter meta title (optional)" />
            </div>
            <div class="form-group">
              <label>Meta Description (for SEO)</label>
              <textarea v-model="form.meta_description" placeholder="Enter meta description (optional)"></textarea>
            </div>
            <button type="submit" :disabled="formLoading">
              {{ formLoading ? 'Saving...' : (editMode ? 'Update' : 'Add') }}
            </button>
          </form>
        </div>
      </div>

      <!-- Add Supplier Modal -->
      <div v-if="showSupplierModal" class="modal" @click="closeSupplierModal">
        <div class="modal-content" @click.stop>
          <h3>Add Supplier</h3>
          <form @submit.prevent="saveSupplier">
            <div class="form-group">
              <label>Name</label>
              <input v-model="supplierForm.name" required placeholder="Enter supplier name" />
            </div>
            <div class="form-group">
              <label>Contact Email</label>
              <input v-model="supplierForm.contact_email" type="email" placeholder="Enter contact email (optional)" />
            </div>
            <div class="form-group">
              <label>Phone</label>
              <input v-model="supplierForm.phone" placeholder="Enter phone number (optional)" />
            </div>
            <div class="form-group">
              <label>Address</label>
              <textarea v-model="supplierForm.address" placeholder="Enter address (optional)"></textarea>
            </div>
            <button type="submit" :disabled="formLoading">
              {{ formLoading ? 'Saving...' : 'Add Supplier' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Add Attribute Modal -->
      <div v-if="showAttributeModal" class="modal" @click="closeAttributeModal">
        <div class="modal-content" @click.stop>
          <h3>Add Variant Attribute</h3>
          <form @submit.prevent="saveAttribute">
            <div class="form-group">
              <label>Attribute Name</label>
              <input v-model="attributeForm.attribute_name" required placeholder="e.g., Color, Size" />
            </div>
            <div class="form-group">
              <label>Value</label>
              <input v-model="attributeForm.value" required placeholder="e.g., Blue, Large" />
            </div>
            <button type="submit" :disabled="formLoading">
              {{ formLoading ? 'Saving...' : 'Add Attribute' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import api from '@/services/api';

import { toast } from 'vue3-toastify';

export default {
  components: { AdminLayout },
  setup() {
    const store = useEcommerceStore();
    
    const products = ref([]);
    const categories = ref([]);
    const suppliers = ref([]);
    const attributes = ref([]);
    const searchQuery = ref('');
    const showModal = ref(false);
    const showSupplierModal = ref(false);
    const showAttributeModal = ref(false);
    const editMode = ref(false);
    const form = ref({
      id: null,
      name: '',
      slug: '',
      description: '',
      price: '',
      below_moq_price: '',
      moq: '',
      moq_per_person: '',
      moq_status: 'active',
      category_id: '',
      supplier_id: '',
      attribute_ids: [],
      images: [],
      meta_title: '',
      meta_description: '',
    });
    const supplierForm = ref({
      name: '',
      contact_email: '',
      phone: '',
      address: '',
    });
    const attributeForm = ref({
      attribute_name: '',
      value: '',
    });
    const loading = ref(false);
    const formLoading = ref(false);
    const error = ref(null);

    const fetchData = async () => {
      try {
        loading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const productsResponse = await api.fetchProducts(apiInstance);
        products.value = productsResponse.flatMap(category => category.products || []) || [];
        const categoriesResponse = await api.fetchCategories(apiInstance);
        categories.value = categoriesResponse || [];
        const suppliersResponse = await api.fetchSuppliers(apiInstance);
        suppliers.value = suppliersResponse || [];
        const attributesResponse = await api.fetchAttributes(apiInstance);
        attributes.value = attributesResponse || [];
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to load data. Please try again.';
        console.error('Failed to fetch data:', err);
        toast.error(error.value);
      } finally {
        loading.value = false;
      }
    };

    const filteredProducts = computed(() => {
      if (!searchQuery.value) return products.value;
      return products.value.filter(product =>
        product.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });

    const handleSearch = () => {
      // Filtering handled by computed property
    };

    const generateSlug = () => {
      if (!editMode.value && form.value.name) {
        form.value.slug = form.value.name
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/(^-|-$)/g, '');
      }
    };

    const openAddModal = () => {
      editMode.value = false;
      form.value = {
        id: null,
        name: '',
        slug: '',
        description: '',
        price: '',
        below_moq_price: '',
        moq: '',
        moq_per_person: '',
        moq_status: 'active',
        category_id: '',
        supplier_id: '',
        attribute_ids: [],
        images: [],
        meta_title: '',
        meta_description: '',
      };
      showModal.value = true;
    };

    const openEditModal = (product) => {
      editMode.value = true;
      form.value = {
        id: product.id,
        name: product.name,
        slug: product.slug,
        description: product.description || '',
        price: product.price,
        below_moq_price: product.below_moq_price || '',
        moq: product.moq || '',
        moq_per_person: product.moq_per_person || '',
        moq_status: product.moq_status || 'active',
        category_id: product.category?.id || '',
        supplier_id: product.supplier?.id || '',
        attribute_ids: product.attributes?.map(attr => attr.id) || [],
        images: product.images || [],
        meta_title: product.meta_title || '',
        meta_description: product.meta_description || '',
      };
      showModal.value = true;
    };

    const closeModal = () => {
      showModal.value = false;
      form.value.images.forEach(image => {
        if (image.preview) URL.revokeObjectURL(image.preview);
      });
      form.value = {
        id: null,
        name: '',
        slug: '',
        description: '',
        price: '',
        below_moq_price: '',
        moq: '',
        moq_per_person: '',
        moq_status: 'active',
        category_id: '',
        supplier_id: '',
        attribute_ids: [],
        images: [],
        meta_title: '',
        meta_description: '',
      };
    };

    const openAddSupplierModal = () => {
      supplierForm.value = { name: '', contact_email: '', phone: '', address: '' };
      showSupplierModal.value = true;
    };

    const closeSupplierModal = () => {
      showSupplierModal.value = false;
      supplierForm.value = { name: '', contact_email: '', phone: '', address: '' };
    };

    const openAddAttributeModal = () => {
      attributeForm.value = { attribute_name: '', value: '' };
      showAttributeModal.value = true;
    };

    const closeAttributeModal = () => {
      showAttributeModal.value = false;
      attributeForm.value = { attribute_name: '', value: '' };
    };

    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        const preview = URL.createObjectURL(file);
        form.value.images.push({ file, preview });
      });
      console.log('Selected images:', form.value.images.map(img => img.file?.name || img.image));
    };

    const removeImage = (index) => {
      const image = form.value.images[index];
      if (image.preview) URL.revokeObjectURL(image.preview);
      form.value.images.splice(index, 1);
    };

    const saveProduct = async () => {
      try {
        formLoading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const formData = new FormData();
        
        // Append scalar fields
        for (const key in form.value) {
          if (key !== 'images' && key !== 'attribute_ids' && form.value[key] != null) {
            formData.append(key, form.value[key]);
          }
        }
        
        // Append attribute_ids
        form.value.attribute_ids.forEach((id, index) => {
          formData.append(`attribute_ids[${index}]`, id);
        });
        
        // Append images under 'images'
        form.value.images.forEach(image => {
          if (image.file) {
            formData.append('images', image.file);
          }
        });

        // Log FormData entries
        console.log('FormData entries:');
        for (let [key, value] of formData.entries()) {
          console.log(`${key}:`, value instanceof File ? value.name : value);
        }

        let response;
        if (editMode.value) {
          response = await api.updateProduct(apiInstance, form.value.id, formData);
          toast.success('Product updated successfully');
        } else {
          response = await api.createProduct(apiInstance, formData);
          toast.success('Product added successfully');
        }
        console.log('API response:', response);
        await fetchData();
        closeModal();
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to save product. Please try again.';
        console.error('Failed to save product:', err.response?.data || err.message);
        toast.error(error.value);
      } finally {
        formLoading.value = false;
      }
    };

    const saveSupplier = async () => {
      try {
        formLoading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const response = await api.createSupplier(apiInstance, supplierForm.value);
        suppliers.value.push(response);
        form.value.supplier_id = response.id;
        toast.success('Supplier added successfully');
        closeSupplierModal();
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to save supplier. Please try again.';
        console.error('Failed to save supplier:', err);
        toast.error(error.value);
      } finally {
        formLoading.value = false;
      }
    };

    const saveAttribute = async () => {
      try {
        formLoading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const response = await api.createAttribute(apiInstance, attributeForm.value);
        attributes.value.push(response);
        form.value.attribute_ids.push(response.id);
        toast.success('Attribute added successfully');
        closeAttributeModal();
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to save attribute. Please try again.';
        console.error('Failed to save attribute:', err);
        toast.error(error.value);
      } finally {
        formLoading.value = false;
      }
    };

    const deleteProduct = async (id) => {
      if (confirm('Are you sure you want to delete this product?')) {
        try {
          formLoading.value = true;
          error.value = null;
          const apiInstance = api.createApiInstance(store);
          await api.deleteProduct(apiInstance, id);
          toast.success('Product deleted successfully');
          await fetchData();
        } catch (err) {
          error.value = err.response?.data?.error || 'Failed to delete product. Please try again.';
          console.error('Failed to delete product:', err);
          toast.error(error.value);
        } finally {
          formLoading.value = false;
        }
      }
    };

    onMounted(() => {
      fetchData();
    });

    return {
      products,
      categories,
      suppliers,
      attributes,
      searchQuery,
      filteredProducts,
      showModal,
      showSupplierModal,
      showAttributeModal,
      editMode,
      form,
      supplierForm,
      attributeForm,
      loading,
      formLoading,
      error,
      fetchData,
      handleSearch,
      generateSlug,
      openAddModal,
      openEditModal,
      closeModal,
      openAddSupplierModal,
      closeSupplierModal,
      openAddAttributeModal,
      closeAttributeModal,
      handleFileUpload,
      removeImage,
      saveProduct,
      saveSupplier,
      saveAttribute,
      deleteProduct,
      formatPrice: (price) => {
        if (price == null) return 'N/A';
        const num = Number(price);
        return isNaN(num) ? 'N/A' : num.toFixed(2);
      },
    };
  },
};
</script>


<style scoped>
/* Existing styles */
.products {
  padding: 0;
  background-color: transparent;
  border-radius: 0;
  box-shadow: none;
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
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

/* Search Bar Styling */
.search-bar {
  margin-bottom: 20px;
}

.search-bar input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid transparent;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.search-bar input:focus {
  outline: none;
  border-color: #6f42c1;
  box-shadow: 0 0 5px rgba(111, 66, 193, 0.2);
}

.add-button {
  padding: 8px 16px;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
  font-weight: 500;
}

.add-button:hover:not(:disabled) {
  background-color: #5a32a3;
}

.add-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Products List Styling */
.products-list {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

thead th {
  background-color: #f8f9fa;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.95rem;
  border-bottom: 2px solid #e9ecef;
  color: #495057;
}

tbody td {
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.9rem;
  color: #495057;
}

.product-row:hover {
  background-color: #f8f9fa;
}

.product-name {
  font-weight: 500;
  color: #212529;
}

.product-price {
  font-weight: 600;
  color: #6f42c1;
}

.below-moq-price {
  color: #6c757d;
}

.moq-info {
  color: #6c757d;
}

/* MOQ Progress Bar */
.moq-progress-cell {
  width: 150px;
}

.moq-progress-container {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: #e6f4ea;
  border-radius: 20px;
  overflow: hidden;
}

.moq-progress-bar {
  height: 100%;
  padding: 2px;
  background: linear-gradient(45deg, #28a745, #5fd778);
  transition: width 0.5s ease;
}

.moq-progress-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 0.65rem;
  font-weight: bold;
  text-shadow: 0 0 2px #fff;
}

/* Action Buttons */
.product-actions {
  white-space: nowrap;
}

.product-actions button {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  margin-right: 5px;
}

.edit-button {
  background-color: #6f42c1;
  color: white;
}

.edit-button:hover:not(:disabled) {
  background-color: #5a32a3;
}

.delete-button {
  background-color: #e74c3c;
  color: white;
}

.delete-button:hover:not(:disabled) {
  background-color: #c0392b;
}

.product-actions button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Styling */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
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

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6f42c1;
}

.form-group select[multiple] {
  height: 100px;
}

.form-group textarea {
  min-height: 100px;
}

.form-group button {
  margin-top: 5px;
  padding: 6px 12px;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-group button:hover:not(:disabled) {
  background-color: #5a32a3;
}

.modal-content button[type="submit"] {
  width: 100%;
  padding: 10px;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.modal-content button[type="submit"]:hover:not(:disabled) {
  background-color: #5a32a3;
}

.modal-content button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Image Preview */
.image-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.image-item {
  position: relative;
  width: 100px;
  height: 100px;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.image-item button {
  position: absolute;
  top: 5px;
  right: 5px;
  background: red;
  color: white;
  border: none;
  padding: 2px 5px;
  border-radius: 2px;
  cursor: pointer;
}

/* Loading and Error States */
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

/* Responsive Adjustments */
@media (max-width: 768px) {
  h2 {
    font-size: 1.5rem;
  }

  .products {
    padding: 15px;
  }

  thead th {
    padding: 8px 10px;
    font-size: 0.85rem;
  }

  tbody td {
    padding: 8px 10px;
    font-size: 0.8rem;
  }

  .product-actions button {
    padding: 4px 8px;
    font-size: 0.75rem;
  }

  .moq-progress-container {
    height: 15px;
  }
}

@media (max-width: 480px) {
  .products-list {
    font-size: 0.8rem;
  }

  .modal-content {
    max-width: 300px;
    padding: 10px;
  }

  .form-group input,
  .form-group select,
  .form-group textarea {
    font-size: 0.9rem;
  }
}
</style>