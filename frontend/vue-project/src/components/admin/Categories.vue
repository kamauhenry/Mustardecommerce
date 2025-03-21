<template>
  <AdminLayout>
    <div class="categories">
      <h2>Manage Categories</h2>

      <!-- Form to Add/Edit Category -->
      <div class="category-form">
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
          <button type="submit">{{ editingCategory ? 'Update' : 'Add' }} Category</button>
          <button v-if="editingCategory" type="button" @click="cancelEdit">Cancel</button>
        </form>
      </div>

      <!-- Categories List -->
      <div class="categories-list">
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
              <td>{{ category.slug }}</td>
              <td>
                <button @click="editCategory(category)">Edit</button>
                <button @click="deleteCategory(category.id)">Delete</button>
              </td>
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

    const fetchCategories = async () => {
      try {
        const response = await api.fetchCategories(api.createApiInstance(store));
        categories.value = response;
      } catch (error) {
        console.error('Failed to fetch categories:', error);
        alert('Failed to load categories');
      }
    };

    const saveCategory = async () => {
      try {
        if (editingCategory.value) {
          // Update existing category
          await api.updateCategory(api.createApiInstance(store), editingCategory.value.id, form.value);
          alert('Category updated successfully');
        } else {
          // Create new category
          await api.createCategory(api.createApiInstance(store), form.value);
          alert('Category added successfully');
        }
        form.value = { name: '', slug: '' };
        editingCategory.value = null;
        await fetchCategories();
      } catch (error) {
        console.error('Failed to save category:', error);
        alert('Failed to save category: ' + (error.response?.data?.error || 'Unknown error'));
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
          await api.deleteCategory(api.createApiInstance(store), categoryId);
          alert('Category deleted successfully');
          await fetchCategories();
        } catch (error) {
          console.error('Failed to delete category:', error);
          alert('Failed to delete category: ' + (error.response?.data?.error || 'Unknown error'));
        }
      }
    };

    onMounted(() => {
      fetchCategories();
    });

    return { categories, form, editingCategory, saveCategory, editCategory, cancelEdit, deleteCategory };
  },
};
</script>

<style scoped>
.categories {
  padding: 20px;
}

.category-form {
  margin-bottom: 40px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

button[type="button"] {
  background: #dc3545;
}

.categories-list table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.categories-list th,
.categories-list td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.categories-list th {
  background: #6f42c1;
  color: white;
}

.categories-list td button {
  padding: 5px 10px;
  font-size: 14px;
}

.categories-list td button:first-child {
  background: #28a745;
}

.categories-list td button:last-child {
  background: #dc3545;
}
</style>
