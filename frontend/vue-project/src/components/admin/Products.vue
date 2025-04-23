<template>
  <AdminLayout>
    <div class="admin-panel">
      <h2>Admin Dashboard</h2>

      <!-- Navigation Tabs -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab"
        >
          {{ tab }}
        </button>
      </div>

      <!-- Products Tab -->
      <div v-if="activeTab === 'Products'" class="products">
        <!-- Search Bar -->
        <div class="search-bar">
          <input
            v-model="searchQuery"
            placeholder="Search products by name..."
            @input="handleSearch"
          />
        </div>

        <!-- CSV Import -->
        <div class="import-section">
          <label>Import Products (CSV/Excel)</label>
          <input type="file" accept=".csv,.xlsx,.xls" @change="handleFileImport" />
          <button @click="uploadProducts" :disabled="importLoading || !importFile">
            {{ importLoading ? 'Importing...' : 'Upload' }}
          </button>
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
          <button class="add-button" @click="openAddModal('product')" :disabled="formLoading">
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
                    <button @click="openEditModal('product', product)" :disabled="formLoading" class="edit-button">Edit</button>
                    <button @click="deleteItem('product', product.id)" :disabled="formLoading" class="delete-button">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-else>No products found.</p>
          </div>
        </div>
      </div>

      <!-- Attributes Tab -->
      <div v-if="activeTab === 'Attributes'" class="attributes">
        <h3>Manage Attributes</h3>

        <!-- Manage Attribute Types -->
        <div class="attribute-types">
          <h4>Attribute Types</h4>
          <div class="form-group">
            <label for="new_attribute_name">New Attribute Type</label>
            <input
              v-model="newAttributeName"
              type="text"
              id="new_attribute_name"
              placeholder="e.g., Color, Size"
            />
            <button @click="createAttributeType" :disabled="formLoading || !newAttributeName.trim()">
              Add Attribute Type
            </button>
          </div>
          <div v-if="attributeTypes.length" class="attribute-types-list">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="attr in attributeTypes" :key="attr.id">
                  <td>{{ attr.name }}</td>
                  <td>
                    <button @click="selectAttributeType(attr)" :disabled="formLoading" class="edit-button">
                      Manage Values
                    </button>
                    <button @click="deleteAttributeType(attr.id)" :disabled="formLoading" class="delete-button">
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else>No attribute types found.</p>
        </div>

        <!-- Manage Attribute Values -->
        <div v-if="selectedAttributeType" class="attribute-values">
          <h4>Values for {{ selectedAttributeType.name }}</h4>
          <div class="form-group">
            <label for="new_attribute_values">New Values (comma-separated)</label>
            <input
              v-model="newAttributeValues"
              type="text"
              id="new_attribute_values"
              placeholder="e.g., Blue, Red, Green"
            />
            <button @click="createAttributeValues" :disabled="formLoading || !newAttributeValues.trim()">
              Add Values
            </button>
          </div>
          <div v-if="attributeValues.length" class="attribute-values-list">
            <table>
              <thead>
                <tr>
                  <th>Value</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="value in attributeValues" :key="value.id">
                  <td>{{ value.value }}</td>
                  <td>
                    <button @click="openEditAttributeValueModal(value)" :disabled="formLoading" class="edit-button">
                      Edit
                    </button>
                    <button @click="deleteAttributeValue(value.id)" :disabled="formLoading" class="delete-button">
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else>No values found for this attribute.</p>
        </div>
      </div>

      <!-- Suppliers Tab -->
      <div v-if="activeTab === 'Suppliers'" class="suppliers">
        <h3>Manage Suppliers</h3>
        <button class="add-button" @click="openAddModal('supplier')" :disabled="formLoading">
          Add Supplier
        </button>

        <!-- Loading State -->
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          Loading suppliers...
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-message">
          {{ error }}
          <button @click="fetchData" class="retry-button">Retry</button>
        </div>

        <!-- Suppliers List -->
        <div v-else class="suppliers-content">
          <table v-if="suppliers.length">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Address</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="supplier in suppliers" :key="supplier.id" class="supplier-row">
                <td>{{ supplier.name }}</td>
                <td>{{ supplier.contact_email || 'N/A' }}</td>
                <td>{{ supplier.phone || 'N/A' }}</td>
                <td>{{ supplier.address || 'N/A' }}</td>
                <td class="supplier-actions">
                  <button @click="openEditModal('supplier', supplier)" :disabled="formLoading" class="edit-button">Edit</button>
                  <button @click="deleteItem('supplier', supplier.id)" :disabled="formLoading" class="delete-button">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-else>No suppliers found.</p>
        </div>
      </div>

      <!-- Product Modal -->
      <div v-if="showModal && modalType === 'product'" class="modal" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h3>{{ editMode ? 'Edit Product' : 'Add Product' }}</h3>
          <form @submit.prevent="saveItem('product')">
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
            </div>
            <div class="form-group">
              <label for="attribute_id">Attribute Type</label>
              <select
                v-model="form.selectedAttributeId"
                id="attribute_id"
                @change="fetchAttributeValuesForProduct"
              >
                <option value="">Select Attribute Type</option>
                <option v-for="attr in attributeTypes" :key="attr.id" :value="attr.id">
                  {{ attr.name }}
                </option>
              </select>
            </div>
            <div class="form-group" v-if="form.selectedAttributeId">
              <label>Attribute Values</label>
              <select
                v-model="form.attribute_value_ids"
                multiple
                size="5"
              >
                <option
                  v-for="value in attributeValues"
                  :key="value.id"
                  :value="value.id"
                >
                  {{ value.value }}
                </option>
              </select>
              <div class="new-values">
                <label for="new_attribute_values">Add New Values (comma-separated)</label>
                <input
                  v-model="form.newAttributeValues"
                  type="text"
                  id="new_attribute_values"
                  placeholder="e.g., Blue, Red, Green"
                />
                <button type="button" @click="addNewAttributeValues" :disabled="formLoading">
                  Add Values
                </button>
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

      <!-- Supplier Modal -->
      <div v-if="showModal && modalType === 'supplier'" class="modal" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h3>{{ editMode ? 'Edit Supplier' : 'Add Supplier' }}</h3>
          <form @submit.prevent="saveItem('supplier')">
            <div class="form-group">
              <label>Name</label>
              <input v-model="form.name" required placeholder="Enter supplier name" />
            </div>
            <div class="form-group">
              <label>Contact Email</label>
              <input v-model="form.contact_email" type="email" placeholder="Enter contact email (optional)" />
            </div>
            <div class="form-group">
              <label>Phone</label>
              <input v-model="form.phone" placeholder="Enter phone number (optional)" />
            </div>
            <div class="form-group">
              <label>Address</label>
              <textarea v-model="form.address" placeholder="Enter address (optional)"></textarea>
            </div>
            <button type="submit" :disabled="formLoading">
              {{ formLoading ? 'Saving...' : (editMode ? 'Update' : 'Add') }}
            </button>
          </form>
        </div>
      </div>

      <!-- Attribute Value Modal -->
      <div v-if="showModal && modalType === 'attribute_value'" class="modal" @click="closeModal">
        <div class="modal-content" @click.stop>
          <h3>{{ editMode ? 'Edit Attribute Value' : 'Add Attribute Value' }}</h3>
          <form @submit.prevent="saveItem('attribute_value')">
            <div class="form-group">
              <label>Attribute Type</label>
              <input :value="selectedAttributeType?.name" disabled />
            </div>
            <div class="form-group">
              <label>Value</label>
              <input v-model="form.value" required placeholder="e.g., Blue" />
            </div>
            <button type="submit" :disabled="formLoading">
              {{ formLoading ? 'Saving...' : (editMode ? 'Update' : 'Add') }}
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
import { toast } from 'vue3-toastify';
import api from '@/services/api';

export default {
  components: { AdminLayout },
  setup() {
    const store = useEcommerceStore();
    const activeTab = ref('Products');
    const tabs = ['Products', 'Attributes', 'Suppliers'];
    const products = ref([]);
    const categories = ref([]);
    const suppliers = ref([]);
    const attributeTypes = ref([]);
    const selectedAttributeType = ref(null);
    const attributeValues = ref([]);
    const searchQuery = ref('');
    const showModal = ref(false);
    const modalType = ref('');
    const editMode = ref(false);
    const form = ref({});
    const importFile = ref(null);
    const importLoading = ref(false);
    const loading = ref(false);
    const formLoading = ref(false);
    const error = ref(null);
    const newAttributeName = ref('');
    const newAttributeValues = ref('');

    const filteredProducts = computed(() => {
      if (!searchQuery.value) return products.value;
      return products.value.filter(product =>
        product.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });

    const fetchData = async () => {
      try {
        loading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const [productsResponse, categoriesResponse, suppliersResponse, attributeTypesResponse] = await Promise.all([
          api.fetchProducts(apiInstance),
          api.fetchCategories(apiInstance),
          apiInstance.get('/admin/suppliers/').then(res => res.data),
          apiInstance.get('/admin/attributes/').then(res => res.data),
        ]);
        products.value = productsResponse.flatMap(category => category.products || []) || [];
        categories.value = categoriesResponse || [];
        suppliers.value = suppliersResponse || [];
        attributeTypes.value = attributeTypesResponse || [];
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to load data. Please try again.';
        console.error('Failed to fetch data:', err);
        toast.error(error.value);
      } finally {
        loading.value = false;
      }
    };

    const fetchAttributeValues = async (attributeId) => {
      try {
        const apiInstance = api.createApiInstance(store);
        const response = await apiInstance.get(`/admin/attribute-values/by-attribute/${attributeId}/`);
        attributeValues.value = response.data;
      } catch (error) {
        toast.error('Failed to load attribute values.');
      }
    };

    const fetchAttributeValuesForProduct = async () => {
      if (!form.value.selectedAttributeId) {
        attributeValues.value = [];
        form.value.attribute_value_ids = [];
        return;
      }
      try {
        const apiInstance = api.createApiInstance(store);
        const response = await apiInstance.get(`/admin/attribute-values/by-attribute/${form.value.selectedAttributeId}/`);
        attributeValues.value = response.data;
      } catch (error) {
        toast.error('Failed to load attribute values.');
        attributeValues.value = [];
      }
    };

    const createAttributeType = async () => {
      if (!newAttributeName.value.trim() || formLoading.value) return;
      try {
        formLoading.value = true;
        const apiInstance = api.createApiInstance(store);
        const response = await apiInstance.post('/admin/attributes/', {
          name: newAttributeName.value,
        });
        attributeTypes.value.push(response.data);
        newAttributeName.value = '';
        toast.success('Attribute type created successfully!');
      } catch (error) {
        toast.error('Failed to create attribute type.');
      } finally {
        formLoading.value = false;
      }
    };

    const deleteAttributeType = async (id) => {
      if (!confirm('Are you sure you want to delete this attribute type?')) return;
      try {
        formLoading.value = true;
        const apiInstance = api.createApiInstance(store);
        await apiInstance.delete(`/admin/attributes/${id}/`);
        attributeTypes.value = attributeTypes.value.filter(attr => attr.id !== id);
        if (selectedAttributeType.value?.id === id) {
          selectedAttributeType.value = null;
          attributeValues.value = [];
        }
        toast.success('Attribute type deleted successfully!');
      } catch (error) {
        toast.error(error.response?.data?.error || 'Failed to delete attribute type.');
      } finally {
        formLoading.value = false;
      }
    };

    const selectAttributeType = (attribute) => {
      selectedAttributeType.value = attribute;
      fetchAttributeValues(attribute.id);
    };

    const createAttributeValues = async () => {
      if (!newAttributeValues.value.trim() || !selectedAttributeType.value || formLoading.value) return;
      try {
        formLoading.value = true;
        const values = newAttributeValues.value.split(',').map(v => v.trim()).filter(v => v);
        const apiInstance = api.createApiInstance(store);
        const response = await apiInstance.post('/admin/attribute-values/', {
          attribute_id: selectedAttributeType.value.id,
          values,
        });
        attributeValues.value.push(...response.data);
        newAttributeValues.value = '';
        toast.success('Attribute values created successfully!');
      } catch (error) {
        toast.error('Failed to create attribute values.');
      } finally {
        formLoading.value = false;
      }
    };

    const openEditAttributeValueModal = (value) => {
      editMode.value = true;
      modalType.value = 'attribute_value';
      form.value = {
        id: value.id,
        attribute_id: selectedAttributeType.value.id,
        value: value.value,
      };
      showModal.value = true;
    };

    const deleteAttributeValue = async (id) => {
      if (!confirm('Are you sure you want to delete this attribute value?')) return;
      try {
        formLoading.value = true;
        const apiInstance = api.createApiInstance(store);
        await apiInstance.delete(`/admin/attribute-values/${id}/`);
        attributeValues.value = attributeValues.value.filter(val => val.id !== id);
        toast.success('Attribute value deleted successfully!');
      } catch (error) {
        toast.error('Failed to delete attribute value.');
      } finally {
        formLoading.value = false;
      }
    };

    const addNewAttributeValues = async () => {
      if (!form.value.newAttributeValues.trim() || !form.value.selectedAttributeId || formLoading.value) return;
      try {
        formLoading.value = true;
        const values = form.value.newAttributeValues.split(',').map(v => v.trim()).filter(v => v);
        const apiInstance = api.createApiInstance(store);
        const response = await apiInstance.post('/admin/attribute-values/', {
          attribute_id: form.value.selectedAttributeId,
          values,
        });
        attributeValues.value.push(...response.data);
        form.value.attribute_value_ids.push(...response.data.map(v => v.id));
        form.value.newAttributeValues = '';
        toast.success('Attribute values added successfully!');
      } catch (error) {
        toast.error('Failed to add attribute values.');
      } finally {
        formLoading.value = false;
      }
    };

    const handleSearch = () => {
      // Filtering handled by computed property
    };

    const generateSlug = () => {
      if (!editMode.value && form.value.name && modalType.value === 'product') {
        form.value.slug = form.value.name
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/(^-|-$)/g, '');
      }
    };

    const openAddModal = (type) => {
      editMode.value = false;
      modalType.value = type;
      if (type === 'product') {
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
          attribute_value_ids: [],
          selectedAttributeId: '',
          newAttributeValues: '',
          images: [],
          meta_title: '',
          meta_description: '',
        };
      } else if (type === 'supplier') {
        form.value = { id: null, name: '', contact_email: '', phone: '', address: '' };
      }
      showModal.value = true;
    };

    const openEditModal = (type, item) => {
      editMode.value = true;
      modalType.value = type;
      if (type === 'product') {
        form.value = {
          id: item.id,
          name: item.name,
          slug: item.slug,
          description: item.description || '',
          price: item.price,
          below_moq_price: item.below_moq_price || '',
          moq: item.moq || '',
          moq_per_person: item.moq_per_person || '',
          moq_status: item.moq_status || 'active',
          category_id: item.category?.id || '',
          supplier_id: item.supplier?.id || '',
          attribute_value_ids: item.attributes?.flatMap(attr => attr.values.map(val => val.id)) || [],
          selectedAttributeId: item.attributes?.length ? item.attributes[0]?.id : '',
          newAttributeValues: '',
          images: item.images || [],
          meta_title: item.meta_title || '',
          meta_description: item.meta_description || '',
        };
        if (form.value.selectedAttributeId) {
          fetchAttributeValuesForProduct();
        }
      } else if (type === 'supplier') {
        form.value = {
          id: item.id,
          name: item.name,
          contact_email: item.contact_email || '',
          phone: item.phone || '',
          address: item.address || '',
        };
      }
      showModal.value = true;
    };

    const closeModal = () => {
      showModal.value = false;
      if (modalType.value === 'product') {
        form.value.images.forEach(image => {
          if (image.preview) URL.revokeObjectURL(image.preview);
        });
      }
      form.value = {};
      modalType.value = '';
    };

    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        const preview = URL.createObjectURL(file);
        form.value.images.push({ file, preview });
      });
    };

    const removeImage = (index) => {
      const image = form.value.images[index];
      if (image.preview) URL.revokeObjectURL(image.preview);
      form.value.images.splice(index, 1);
    };

    const handleFileImport = (event) => {
      importFile.value = event.target.files[0];
    };

    const uploadProducts = async () => {
      if (!importFile.value) return;
      try {
        importLoading.value = true;
        const formData = new FormData();
        formData.append('file', importFile.value);
        const apiInstance = api.createApiInstance(store);
        const response = await apiInstance.post('/admin/bulk-import/', formData);
        toast.success(`Imported ${response.data.created} products successfully!`);
        if (response.data.errors.length) {
          toast.warning(`Some rows failed: ${JSON.stringify(response.data.errors)}`);
        }
        await fetchData();
        importFile.value = null;
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to import products.';
        toast.error(error.value);
      } finally {
        importLoading.value = false;
      }
    };

    const saveItem = async (type) => {
      try {
        formLoading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        let response;

        if (type === 'product') {
          const formData = new FormData();
          for (const key in form.value) {
            if (key !== 'images' && key !== 'attribute_value_ids' && key !== 'selectedAttributeId' && key !== 'newAttributeValues' && form.value[key] != null) {
              formData.append(key, form.value[key]);
            }
          }
          if (form.value.attribute_value_ids) {
            form.value.attribute_value_ids.forEach(id => {
              if (Number.isInteger(Number(id))) {
                formData.append('attribute_value_ids', id);
              }
            });
          }
          form.value.images.forEach(image => {
            if (image.file) {
              formData.append('images', image.file);
            }
          });
          if (editMode.value) {
            response = await api.updateProduct(apiInstance, form.value.id, formData);
            toast.success('Product updated successfully');
          } else {
            response = await api.createProduct(apiInstance, formData);
            toast.success('Product added successfully');
          }
        } else if (type === 'supplier') {
          if (editMode.value) {
            response = await apiInstance.put(`/admin/suppliers/${form.value.id}/`, form.value);
            toast.success('Supplier updated successfully');
          } else {
            response = await apiInstance.post('/admin/suppliers/', form.value);
            toast.success('Supplier added successfully');
          }
          suppliers.value = (await apiInstance.get('/admin/suppliers/')).data;
        } else if (type === 'attribute_value') {
          const payload = {
            attribute_id: selectedAttributeType.value.id,
            value: form.value.value,
          };
          if (editMode.value) {
            response = await apiInstance.put(`/admin/attribute-values/${form.value.id}/`, payload);
            toast.success('Attribute value updated successfully');
          } else {
            response = await apiInstance.post('/admin/attribute-values/', payload);
            toast.success('Attribute value added successfully');
          }
          await fetchAttributeValues(selectedAttributeType.value.id);
        }
        await fetchData();
        closeModal();
      } catch (err) {
        error.value = err.response?.data || `Failed to save ${type}. Please try again.`;
        console.error(`Failed to save ${type}:`, JSON.stringify(err.response?.data, null, 2));
        toast.error(JSON.stringify(error.value, null, 2));
      } finally {
        formLoading.value = false;
      }
    };

    const deleteItem = async (type, id) => {
      if (confirm(`Are you sure you want to delete this ${type}?`)) {
        try {
          formLoading.value = true;
          error.value = null;
          const apiInstance = api.createApiInstance(store);
          if (type === 'product') {
            await api.deleteProduct(apiInstance, id);
            toast.success('Product deleted successfully');
          } else if (type === 'supplier') {
            await apiInstance.delete(`/admin/suppliers/${id}/`);
            toast.success('Supplier deleted successfully');
          }
          await fetchData();
        } catch (err) {
          error.value = err.response?.data?.error || `Failed to delete ${type}. Please try again.`;
          console.error(`Failed to delete ${type}:`, err);
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
      activeTab,
      tabs,
      products,
      categories,
      suppliers,
      attributeTypes,
      selectedAttributeType,
      attributeValues,
      searchQuery,
      filteredProducts,
      showModal,
      modalType,
      editMode,
      form,
      importFile,
      importLoading,
      loading,
      formLoading,
      error,
      newAttributeName,
      newAttributeValues,
      fetchData,
      fetchAttributeValues,
      fetchAttributeValuesForProduct,
      createAttributeType,
      deleteAttributeType,
      selectAttributeType,
      createAttributeValues,
      openEditAttributeValueModal,
      deleteAttributeValue,
      addNewAttributeValues,
      handleSearch,
      generateSlug,
      openAddModal,
      openEditModal,
      closeModal,
      handleFileUpload,
      removeImage,
      handleFileImport,
      uploadProducts,
      saveItem,
      deleteItem,
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
.admin-panel {
  padding: 20px;
  background-color: #f4f6f9;
  min-height: 100vh;
}

h2 {
  font-size: 1.75rem;
  color: #4f46e5;
  margin-bottom: 24px;
  font-weight: 700;
}

h3 {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

h4 {
  font-size: 1.1rem;
  margin-bottom: 10px;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e9ecef;
}

.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: color 0.2s ease;
}

.tabs button.active {
  color: #6f42c1;
  border-bottom: 2px solid #6f42c1;
}

.tabs button:hover {
  color: #5a32a3;
}

/* Search Bar */
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

/* Import Section */
.import-section {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.import-section label {
  font-weight: 500;
  color: #333;
}

.import-section input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.import-section button {
  padding: 8px 16px;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.import-section button:hover:not(:disabled) {
  background-color: #5a32a3;
}

.import-section button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Add Button */
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

/* Tables */
.products-list, .attribute-types-list, .attribute-values-list, .suppliers-content {
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

.product-row:hover, .attribute-row:hover, .supplier-row:hover {
  background-color: #f8f9fa;
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
.product-actions, .attribute-actions, .supplier-actions {
  white-space: nowrap;
}

.product-actions button, .attribute-actions button, .supplier-actions button {
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

.product-actions button:disabled, .attribute-actions button:disabled, .supplier-actions button:disabled {
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

/* Attribute Types and Values */
.attribute-types, .attribute-values {
  margin-bottom: 20px;
}

.attribute-types-list table, .attribute-values-list table {
  width: 100%;
}

.attribute-types-list th, .attribute-values-list th {
  background-color: #f8f9fa;
  padding: 10px;
}

.attribute-types-list td, .attribute-values-list td {
  padding: 10px;
}

.new-values {
  margin-top: 10px;
}

.new-values input {
  width: calc(100% - 100px);
  display: inline-block;
  margin-right: 10px;
}

.new-values button {
  width: 90px;
  display: inline-block;
  vertical-align: top;
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
  .admin-panel {
    padding: 15px;
  }

  h2 {
    font-size: 1.5rem;
  }

  .tabs button {
    padding: 8px 12px;
    font-size: 0.9rem;
  }

  thead th {
    padding: 8px 10px;
    font-size: 0.85rem;
  }

  tbody td {
    padding: 8px 10px;
    font-size: 0.8rem;
  }

  .product-actions button, .attribute-actions button, .supplier-actions button {
    padding: 4px 8px;
    font-size: 0.75rem;
  }

  .moq-progress-container {
    height: 15px;
  }
}

@media (max-width: 480px) {
  .modal-content {
    max-width: 300px;
    padding: 10px;
  }

  .form-group input,
  .form-group select,
  .form-group textarea {
    font-size: 0.9rem;
  }

  .new-values input {
    width: 100%;
    margin-bottom: 10px;
  }

  .new-values button {
    width: 100%;
  }
}
</style>