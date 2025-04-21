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
        <button @click="ffetchAllCategoriesWithProducts" class="retry-button">Retry</button>
      </div>

      <!-- Form to Add/Edit Category -->
      <div v-else class="category-form">
        <h3>{{ editingCategory ? 'Edit Category' : 'Add New Category' }}</h3>
        <form @submit.prevent="saveCategory">
          <div class="form-group">
            <label>Name</label>
            <input v-model="form.name" required placeholder="Enter category name" />
          </div>
          <div class="form-group">
            <label>Slug (optional)</label>
            <input v-model="form.slug" placeholder="Enter category slug (optional)" />
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
              <th>Name</th>
              <th>Slug</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id">
              <td>{{ category.id }}</td>
              <td>{{ category.name }}</td>
              <td>{{ category.slug || 'N/A' }}</td>
              <td>
                <button @click="editCategory(category)" :disabled="formLoading">Edit</button>
                <button @click="deleteCategory(category.id)" :disabled="formLoading">Delete</button>
              </td>
            </tr>
            <tr v-if="!categories.length">
              <td colspan="4" class="no-data">No categories available.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import AdminLayout from '@/components/admin/AdminLayout.vue';
import api from '@/services/api';

export default {
  components: { AdminLayout },
  setup() {
    const store = useEcommerceStore();
    const categories = ref([]);
    const form = ref({ name: '', slug: '' });
    const editingCategory = ref(null);
    const loading = ref(false);
    const formLoading = ref(false);
    const error = ref(null);

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

    const saveCategory = async () => {
      try {
        formLoading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        if (editingCategory.value) {
          // Update existing category
          await api.updateCategory(apiInstance, editingCategory.value.id, form.value);
          alert('Category updated successfully');
        } else {
          // Create new category
          await api.createCategory(apiInstance, form.value);
          alert('Category added successfully');
        }
        form.value = { name: '', slug: '' };
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
      form.value = { name: category.name, slug: category.slug };
    };

    const cancelEdit = () => {
      editingCategory.value = null;
      form.value = { name: '', slug: '' };
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

    return {
      categories,
      form,
      editingCategory,
      loading,
      formLoading,
      error,
      fetchAllCategoriesWithProducts,
      saveCategory,
      editCategory,
      cancelEdit,
      deleteCategory,
    };
  },
};
</script>

<style scoped>
.categories {
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

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #6f42c1;
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
</style>
