<template>
  <AdminLayout>
    <div class="products">
      <h2>Products</h2>
      <button class="add-button" @click="openAddModal">Add Product</button>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Category</th>
            <th>MOQ</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>{{ product.name }}</td>
            <td>KES {{ product.price }}</td>
            <td>{{ product.category.name }}</td>
            <td>{{ product.moq || 'N/A' }}</td>
            <td>
              <button @click="openEditModal(product)">Edit</button>
              <button @click="deleteProduct(product.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Add/Edit Modal -->
      <div v-if="showModal" class="modal" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h3>{{ editMode ? 'Edit Product' : 'Add Product' }}</h3>
          <form @submit.prevent="saveProduct">
            <div class="form-group">
              <label>Name</label>
              <input v-model="form.name" required />
            </div>
            <div class="form-group">
              <label>Slug</label>
              <input v-model="form.slug" required />
            </div>
            <div class="form-group">
              <label>Price</label>
              <input v-model="form.price" type="number" step="0.01" required />
            </div>
            <div class="form-group">
              <label>MOQ</label>
              <input v-model="form.moq" type="number" />
            </div>
            <div class="form-group">
              <label>MOQ Status</label>
              <input v-model="form.moq_status" />
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
              <label>Thumbnail</label>
              <input type="file" @change="handleFileUpload" />
            </div>
            <button type="submit">{{ editMode ? 'Update' : 'Add' }}</button>
          </form>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import AdminLayout from '@/components/admin/AdminLayout.vue';

export default {
  components: { AdminLayout },
  setup() {
    const products = ref([]);
    const categories = ref([]);
    const showModal = ref(false);
    const editMode = ref(false);
    const form = ref({
      id: null,
      name: '',
      slug: '',
      price: '',
      moq: '',
      moq_status: '',
      category_id: '',
      thumbnail: null,
    });

    const fetchProducts = async () => {
      const response = await axios.get('products/');
      products.value = response.data;
    };

    const fetchCategories = async () => {
      const response = await axios.get('categories/');
      categories.value = response.data;
    };

    const openAddModal = () => {
      editMode.value = false;
      form.value = { id: null, name: '', slug: '', price: '', moq: '', moq_status: '', category_id: '', thumbnail: null };
      showModal.value = true;
    };

    const openEditModal = (product) => {
      editMode.value = true;
      form.value = { ...product, category_id: product.category.id };
      showModal.value = true;
    };

    const closeModal = () => {
      showModal.value = false;
    };

    const handleFileUpload = (event) => {
      form.value.thumbnail = event.target.files[0];
    };

    const saveProduct = async () => {
      const formData = new FormData();
      for (const key in form.value) {
        if (form.value[key] !== null) {
          formData.append(key, form.value[key]);
        }
      }

      if (editMode.value) {
        await axios.put(`products/${form.value.id}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        await axios.post('products/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }
      fetchProducts();
      closeModal();
    };

    const deleteProduct = async (id) => {
      if (confirm('Are you sure you want to delete this product?')) {
        await axios.delete(`products/${id}/`);
        fetchProducts();
      }
    };

    onMounted(() => {
      fetchProducts();
      fetchCategories();
    });

    return {
      products,
      categories,
      showModal,
      editMode,
      form,
      openAddModal,
      openEditModal,
      closeModal,
      handleFileUpload,
      saveProduct,
      deleteProduct,
    };
  },
};
</script>

<style scoped>
.products {
  padding: 1rem;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.add-button {
  background-color: #6f42c1;
  color: #fff;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 1rem;
}

.add-button:hover {
  opacity: 0.9;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
}

td button {
  padding: 0.25rem 0.5rem;
  margin-right: 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

td button:first-child {
  background-color: #6f42c1;
  color: #fff;
}

td button:last-child {
  background-color: #dc3545;
  color: #fff;
}

td button:hover {
  opacity: 0.9;
}

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
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.modal-content button {
  width: 100%;
  padding: 0.75rem;
  background-color: #6f42c1;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.modal-content button:hover {
  opacity: 0.9;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  th, td {
    padding: 0.5rem;
    font-size: 0.9rem;
  }

  .modal-content {
    max-width: 400px;
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  th, td {
    font-size: 0.8rem;
  }

  .modal-content {
    max-width: 300px;
    padding: 1rem;
  }

  .form-group input,
  .form-group select {
    font-size: 0.9rem;
  }
}
</style>
