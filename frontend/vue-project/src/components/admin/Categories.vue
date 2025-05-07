<template>
  <AdminLayout>
    <div class="categories">
      <h2>Manage Categories</h2>

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
  </AdminLayout>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import api from '@/services/api';

export default {
  components: { AdminLayout },
  setup() {
    const store = useEcommerceStore();
    const categories = ref([]);
    const form = ref({ name: '', description: '', slug: '', image: null });
    const editingCategory = ref(null);
    const loading = ref(false);
    const formLoading = ref(false);
    const error = ref(null);
    const imagePreview = ref(null);
    const imageInput = ref(null);

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
      form.value = { name: category.name, description: category.description || '', slug: category.slug, image: null };
      imagePreview.value = category.image || null;
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

    onMounted(() => {
      fetchAllCategoriesWithProducts();
    });

    watch(() => form.value.name, (newName) => {
      if (!editingCategory.value) {
        generateSlug();
      }
    });

    return {
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
    };
  },
};
</script>

<style scoped>
.categories {
  padding: 20px;
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

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .categories {
    padding: 10px;
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
}

@media (max-width: 480px) {
  .categories {
    padding: 8px;
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
}
</style>