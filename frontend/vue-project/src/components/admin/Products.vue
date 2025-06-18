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
        <!-- Sub-Tabs -->
        <div class="sub-tabs">
          <button
            v-for="subTab in productSubTabs"
            :key="subTab"
            :class="{ active: productSubTab === subTab }"
            @click="productSubTab = subTab"
          >
            {{ subTab }}
          </button>
        </div>

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
          <p class="help-text">Note: For attributes, use a column 'attributes' with format "Color:Red,Blue;Size:Large"</p>
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
          <button class="refresh-button" @click="fetchData" :disabled="loading">
            {{ loading ? 'Refreshing...' : 'Refresh Inventory' }}
          </button>

          <div class="products-list">
            <table v-if="currentProducts.length">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Price (KES)</th>
                  <th>Below MOQ Price</th>
                  <th>MOQ</th>
                  <th>MOQ Progress</th>
                  <th v-if="productSubTab === 'Pick and Pay Products'">Inventory Quantity</th>
                  <th>Supplier</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="product in currentProducts"
                  :key="product.id"
                  class="product-row"
                  :class="{ 'recently-changed': productSubTab === 'Pick and Pay Products' && product.id === mostRecentPickAndPayProductId }"
                >
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
                  <td v-if="productSubTab === 'Pick and Pay Products'" class="inventory-quantity">
                    {{ product.inventory?.quantity || 0 }} units
                    <span v-if="product.id === mostRecentPickAndPayProductId" class="recently-updated">Recently Updated</span>
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

      <!-- Import from E-commerce Tab -->
      <div v-if="activeTab === 'Import from E-commerce'" class="import-ecommerce">
        <h3>Import Products from E-commerce</h3>
        <div class="form-group">
          <label>Platform</label>
          <select v-model="importPlatform">
            <option value="">Select Platform</option>
            <option value="alibaba">Alibaba</option>
            <option value="shein">Shein</option>
          </select>
        </div>
        <div class="form-group">
          <label>Import Type</label>
          <div>
            <input type="radio" id="single" value="single" v-model="importType" />
            <label for="single">Single Product</label>
          </div>
          <div>
            <input type="radio" id="category" value="category" v-model="importType" />
            <label for="category">Category</label>
          </div>
        </div>
        <div class="form-group">
          <label>URL</label>
          <input v-model="importUrl" placeholder="Enter product or category URL" />
        </div>
        <div class="form-group" v-if="importType === 'category'">
          <label>Number of Products to Import</label>
          <input v-model="importCount" type="number" min="1" placeholder="Enter number of products" />
        </div>
        <button @click="importProducts" :disabled="importLoading || !importPlatform || !importUrl">
          {{ importLoading ? 'Importing...' : 'Import' }}
        </button>
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
                @input="generateMetaData"
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
              <textarea
                v-model="form.description"
                placeholder="Enter product description"
                @input="generateMetaData"
              ></textarea>
            </div>
            <div class="form-group">
              <label>Price</label>
              <input v-model="form.price" type="number" step="0.01" required placeholder="Enter price" />
            </div>
            <div class="form-group">
              <label>
                <input type="checkbox" v-model="form.is_pick_and_pay" @change="generateMetaData" />
                Pay & Pick Product
              </label>
            </div>
            <div v-if="form.is_pick_and_pay" class="form-group">
              <label>Inventory Quantity</label>
              <input
                v-model="form.inventory_quantity"
                type="number"
                min="0"
                required
                placeholder="Enter available quantity"
                @input="generateMetaData"
              />
            </div>

            <!-- MOQ Fields: Hidden when Pay & Pick is selected -->
            <div v-if="!form.is_pick_and_pay">
              <div class="form-group">
                <label>Below MOQ Price</label>
                <input
                  v-model="form.below_moq_price"
                  type="number"
                  step="0.01"
                  placeholder="Enter below MOQ price (optional)"
                />
              </div>
              <div class="form-group">
                <label>MOQ (Minimum Order Quantity)</label>
                <input
                  v-model="form.moq"
                  type="number"
                  placeholder="Enter MOQ (optional)"
                />
              </div>
              <div class="form-group">
                <label>MOQ Per Person</label>
                <input
                  v-model="form.moq_per_person"
                  type="number"
                  placeholder="Enter MOQ per person (optional)"
                />
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
            </div>
            <div class="form-group">
              <label>Category</label>
              <select v-model="form.category_id" required @change="generateMetaData">
                <option value="">Select Category</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Supplier</label>
              <select v-model="form.supplier_id" @change="generateMetaData">
                <option value="">Select Supplier (optional)</option>
                <option v-for="supplier in suppliers" :key="supplier.id" :value="supplier.id">
                  {{ supplier.name }}
                </option>
              </select>
            </div>
            <div v-for="(attr, index) in form.attributes" :key="index" class="attribute-group">
              <div class="form-group">
                <label>Attribute Type</label>
                <select v-model="attr.attribute_id" @change="fetchValuesForAttr(index); generateMetaData()">
                  <option value="">Select Attribute Type</option>
                  <option
                    v-for="attrType in availableAttributeTypes(index)"
                    :key="attrType.id"
                    :value="attrType.id"
                  >
                    {{ attrType.name }}
                  </option>
                </select>
                <button type="button" @click="removeAttribute(index)" v-if="form.attributes.length > 1">Remove</button>
              </div>
              <div class="form-group" v-if="attr.attribute_id">
                <label>Attribute Values</label>
                <select v-model="attr.value_ids" multiple size="5" @change="generateMetaData">
                  <option v-for="value in attr.values" :key="value.id" :value="value.id">
                    {{ value.value }}
                  </option>
                </select>
                <div class="new-values">
                  <label>Add New Values (comma-separated)</label>
                  <input v-model="attr.newValues" type="text" placeholder="e.g., Blue, Red, Green" />
                  <button type="button" @click="addNewValuesForAttr(index)" :disabled="formLoading">Add Values</button>
                </div>
              </div>
            </div>
            <button type="button" @click="addAttribute">Add Attribute</button>
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
    const tabs = ['Products', 'Attributes', 'Suppliers', 'Import from E-commerce'];
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
    const importPlatform = ref('');
    const importUrl = ref('');
    const importType = ref('single');
    const importCount = ref(1);

    const filteredProducts = computed(() => {
      if (!searchQuery.value) return products.value;
      return products.value.filter(product =>
        product.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });
    const productSubTab = ref('All Products');
    const productSubTabs = ['All Products', 'Formow Products', 'Pick and Pay Products'];

    const allProducts = computed(() => filteredProducts.value);
    const formowProducts = computed(() => filteredProducts.value.filter(product => !product.is_pick_and_pay));
    const pickAndPayProducts = computed(() => {
      return filteredProducts.value
        .filter(product => product.is_pick_and_pay)
        .sort((a, b) => {
          const aTime = a.inventory?.last_updated ? new Date(a.inventory.last_updated).getTime() : 0;
          const bTime = b.inventory?.last_updated ? new Date(b.inventory.last_updated).getTime() : 0;
          return bTime - aTime;
        });
    });
    const currentProducts = computed(() => {
      if (productSubTab.value === 'Formow Products') return formowProducts.value;
      if (productSubTab.value === 'Pick and Pay Products') return pickAndPayProducts.value;
      return allProducts.value;
    });
    const mostRecentPickAndPayProductId = computed(() => pickAndPayProducts.value[0]?.id || null);
    const fetchData = async () => {
      try {
        loading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        const [productsResponse, categoriesResponse, suppliersResponse, attributeTypesResponse] = await Promise.all([
          api.fetchAllCategoriesWithProducts(apiInstance),
          api.fetchCategories(apiInstance),
          apiInstance.get('/admin/suppliers/').then(res => res.data),
          apiInstance.get('/admin/attributes/').then(res => res.data),
        ]);
        products.value = productsResponse.flatMap(category => category.products || []) || [];
        // Log Pick and Pay products' inventory
        products.value.forEach(product => {
          if (product.is_pick_and_pay) {
            console.log(`Product ${product.name} (ID: ${product.id}): Inventory Quantity = ${product.inventory?.quantity || 'None'}`);
          }
        });
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

    const fetchValuesForAttr = async (index) => {
      const attr = form.value.attributes[index];
      if (!attr.attribute_id) {
        attr.values = [];
        attr.value_ids = [];
        return;
      }
      try {
        const apiInstance = api.createApiInstance(store);
        const response = await apiInstance.get(`/admin/attribute-values/by-attribute/${attr.attribute_id}/`);
        attr.values = response.data;
      } catch (error) {
        toast.error('Failed to load attribute values.');
        attr.values = [];
      }
    };

    const addAttribute = () => {
      form.value.attributes.push({
        attribute_id: '',
        value_ids: [],
        values: [],
        newValues: '',
      });
    };

    const removeAttribute = (index) => {
      form.value.attributes.splice(index, 1);
    };

    const addNewValuesForAttr = async (index) => {
      const attr = form.value.attributes[index];
      if (!attr.newValues.trim() || !attr.attribute_id || formLoading.value) return;
      try {
        formLoading.value = true;
        const values = attr.newValues.split(',').map(v => v.trim()).filter(v => v);
        const apiInstance = api.createApiInstance(store);
        const response = await apiInstance.post('/admin/attribute-values/', {
          attribute_id: attr.attribute_id,
          values,
        });
        attr.values.push(...response.data);
        attr.value_ids.push(...response.data.map(v => v.id));
        attr.newValues = '';
        toast.success('Attribute values added successfully!');
      } catch (error) {
        toast.error('Failed to add attribute values.');
      } finally {
        formLoading.value = false;
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
          is_pick_and_pay: false,
          inventory_quantity: '',
          store_location: 'Reli-Coop house 1st floor F71',
          category_id: '',
          supplier_id: '',
          attributes: [{ attribute_id: '', value_ids: [], values: [], newValues: '' }],
          images: [],
          meta_title: '',
          meta_description: '',
          seo_keywords: '',
          og_title: '',
          og_description: '',
          structured_data: ''
        };
        generateMetaData();
      } else if (type === 'supplier') {
        form.value = { id: null, name: '', contact_email: '', phone: '', address: '' };
      }
      showModal.value = true;
    };

    const openEditModal = (type, item) => {
      editMode.value = true;
      modalType.value = type;
      if (type === 'product') {
        const attributesMap = {};
        item.attributes.forEach(attr => {
          attributesMap[attr.id] = {
            attribute_id: attr.id,
            value_ids: attr.values.map(v => v.id),
            values: attr.values,
            newValues: '',
          };
        });
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
          is_pick_and_pay: item.is_pick_and_pay || false,
          inventory_quantity: item.inventory?.quantity || '',
          store_location: item.is_pick_and_pay ? 'Reli-Coop house 1st floor F71' : item.inventory?.store_location || '',
          category_id: item.category?.id || '',
          supplier_id: item.supplier?.id || '',
          attributes: Object.values(attributesMap).length
            ? Object.values(attributesMap)
            : [{ attribute_id: '', value_ids: [], values: [], newValues: '' }],
          images: item.images || [],
          meta_title: '',
          meta_description: '',
          seo_keywords: '',
          og_title: '',
          og_description: '',
          structured_data: ''
        };
        generateMetaData();
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

    const saveItem = async (type) => {
      try {
        formLoading.value = true;
        error.value = null;
        const apiInstance = api.createApiInstance(store);
        let response;

        if (type === 'product') {
          // Set default MOQ values for Pay & Pick products
          if (form.value.is_pick_and_pay) {
            form.value.below_moq_price = null;
            form.value.moq = 1;
            form.value.moq_per_person = 1;
            form.value.moq_status = 'not_applicable';
            form.value.store_location = 'Reli-Coop house 1st floor F71';
          }
          generateMetaData(); // Ensure latest metadata
          const formData = new FormData();
          const fields = [
            'name', 'slug', 'description', 'price', 'below_moq_price', 'moq',
            'moq_per_person', 'moq_status', 'is_pick_and_pay', 'inventory_quantity',
            'store_location', 'category_id', 'supplier_id', 'meta_title', 'meta_description',
            'seo_keywords', 'og_title', 'og_description', 'structured_data'
          ];
          fields.forEach(key => {
            if (form.value[key] != null && key !== 'attributes' && key !== 'images') {
              formData.append(key, form.value[key]);
            }
          });
          const allValueIds = form.value.attributes.flatMap(attr => attr.value_ids || []);
          allValueIds.forEach(id => formData.append('attribute_value_ids', id));
          form.value.images.forEach(image => {
            if (image.file) {
              formData.append('images', image.file);
            }
          });

          if (editMode.value) {
            console.log('Updating product:', form.value.id);
            response = await api.updateProduct(apiInstance, form.value.id, formData);
            console.log('Product updated:', response);
            toast.success('Product updated successfully');
          } else {
            console.log('Creating product');
            response = await api.createProduct(apiInstance, formData);
            console.log('Product created:', response);
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
        console.error('Error in saveItem:', err);
        error.value = err.response?.data || err.message || `Failed to save ${type}. Please try again.`;
        toast.error(error.value.toString());
      } finally {
        formLoading.value = false;
      }
    };  
    const generateMetaData = () => {
      if (modalType.value === 'product') {
        // Generate slug
        if (form.value.name) {
          form.value.slug = form.value.name
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/(^-|-$)/g, '');
        }

        // Generate meta_title
        if (form.value.name) {
          const categoryName = categories.value.find(c => c.id === form.value.category_id)?.name || '';
          const title = `Buy ${form.value.name} in Nairobi${categoryName ? ' - ' + categoryName : ''}`;
          form.value.meta_title = title.length > 60 ? title.substring(0, 57) + '...' : title;
        } else {
          form.value.meta_title = '';
        }

        // Generate meta_description
        if (form.value.description) {
          let desc = form.value.description;
          if (desc.length > 160) {
            desc = desc.substring(0, 160);
            const lastSpace = desc.lastIndexOf(' ');
            desc = lastSpace > 0 ? desc.substring(0, lastSpace) + '...' : desc;
          }
          form.value.meta_description = desc;
        } else if (form.value.name) {
          const categoryName = categories.value.find(c => c.id === form.value.category_id)?.name || 'Product';
          const supplierName = suppliers.value.find(s => s.id === form.value.supplier_id)?.name || 'Quality Supplier';
          form.value.meta_description = `Shop ${form.value.name} online in Nairobi. Premium ${categoryName} from ${supplierName}. Buy now!`;
        } else {
          form.value.meta_description = '';
        }

        // Generate seo_keywords
        const keywords = ['buy', 'online', 'Nairobi'];
        if (form.value.name) keywords.push(form.value.name.toLowerCase());
        if (form.value.category_id) {
          const categoryName = categories.value.find(c => c.id === form.value.category_id)?.name;
          if (categoryName) keywords.push(categoryName.toLowerCase());
        }
        if (form.value.attributes) {
          form.value.attributes.forEach(attr => {
            attr.values?.forEach(val => {
              if (val.value) keywords.push(val.value.toLowerCase());
            });
          });
        }
        if (form.value.is_pick_and_pay) keywords.push('pay and pick', 'store pickup');
        form.value.seo_keywords = [...new Set(keywords)].join(', ');

        // Generate og_title
        form.value.og_title = form.value.meta_title || `Buy ${form.value.name || 'Product'} in Nairobi`;

        // Generate og_description
        form.value.og_description = form.value.meta_description || `Discover ${form.value.name || 'Product'} - Premium quality at great prices. Shop now in Nairobi!`;

        // Generate structured data
        if (form.value.name && form.value.price) {
          const schema = {
            '@context': 'https://schema.org',
            '@type': 'Product',
            name: form.value.name,
            description: form.value.meta_description || `Buy ${form.value.name} in Nairobi`,
            image: form.value.images?.[0]?.image || form.value.images?.[0]?.preview || '',
            offers: {
              '@type': 'Offer',
              price: parseFloat(form.value.price || 0).toFixed(2),
              priceCurrency: 'KES',
              availability: form.value.is_pick_and_pay && form.value.inventory_quantity > 0
                ? 'https://schema.org/InStock'
                : 'https://schema.org/PreOrder',
              url: `https://yourdomain.com/products/${form.value.slug || form.value.id || 'product'}`
            },
            brand: {
              '@type': 'Brand',
              name: suppliers.value.find(s => s.id === form.value.supplier_id)?.name || 'Unknown'
            },
            keywords: form.value.seo_keywords || 'buy, online, Nairobi'
          };
          form.value.structured_data = JSON.stringify(schema, null, 2);
        } else {
          form.value.structured_data = '';
        }
      }
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

    const availableAttributeTypes = (currentIndex) => {
      if (!form.value.attributes) return attributeTypes.value;
      const selectedIds = form.value.attributes
        .filter((_, index) => index !== currentIndex)
        .map(attr => attr.attribute_id)
        .filter(id => id);
      return attributeTypes.value.filter(attrType => !selectedIds.includes(attrType.id));
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

    const importProducts = async () => {
      if (!importPlatform.value || !importUrl.value) return;
      try {
        importLoading.value = true;
        const apiInstance = api.createApiInstance(store);
        const data = {
          platform: importPlatform.value,
          url: importUrl.value,
          import_type: importType.value,
        };
        if (importType.value === 'category') {
          data.import_count = importCount.value;
        }
        const response = await apiInstance.post('/admin/scrape-products/', data);
        toast.success(`Imported ${response.data.products.length} products successfully!`);
        await fetchData();
      } catch (err) {
        toast.error(err.response?.data?.error || 'Failed to import products.');
      } finally {
        importLoading.value = false;
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
      const pollingInterval = setInterval(() => {
        if (productSubTab.value === 'Pick and Pay Products') {
          fetchData();
        }
      }, 30000); // Refresh every 30 seconds
      return () => clearInterval(pollingInterval); 
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
      importPlatform,
      importUrl,
      importType,
      importCount,
      fetchData,
      fetchAttributeValues,
      createAttributeType,
      deleteAttributeType,
      selectAttributeType,
      createAttributeValues,
      openEditAttributeValueModal,
      deleteAttributeValue,
      fetchValuesForAttr,
      addAttribute,
      removeAttribute,
      addNewValuesForAttr,
      availableAttributeTypes,
      generateMetaData,
      openAddModal,
      openEditModal,
      closeModal,
      handleFileUpload,
      removeImage,
      handleFileImport,
      uploadProducts,
      importProducts,
      saveItem,
      productSubTab,
      productSubTabs,
      currentProducts,
      mostRecentPickAndPayProductId,
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
.attribute-group {
  border: 1px solid #ccc;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 5px;
}

.attribute-group button {
  margin-left: 10px;
}

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

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e9ecef;
}
.sub-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #e9ecef;
}
.sub-tabs button {
  padding: 8px 16px;
  background: none;
  border: none;
  font-size: 0.95rem;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: color 0.2s ease;
}
.sub-tabs button.active {
  color: #6f42c1;
  border-bottom: 2px solid #6f42c1;
}
.sub-tabs button:hover {
  color: #5a32a3;
}
.inventory-quantity {
  position: relative;
}
.recently-updated {
  color: #28a745;
  font-size: 0.8rem;
  margin-left: 10px;
  font-weight: bold;
}
.recently-changed {
  background-color: #e6f4ea !important;
}
.refresh-button {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
  margin-left: 10px;
  font-weight: 500;
}
.refresh-button:hover:not(:disabled) {
  background-color: #218838;
}
.refresh-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.import-section, .import-ecommerce {
  margin-bottom: 20px;
}

.import-section label, .import-ecommerce label {
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 5px;
}

.import-section input, .import-ecommerce input, .import-ecommerce select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 100%;
  margin-bottom: 10px;
}

.import-section button, .import-ecommerce button {
  padding: 8px 16px;
  background-color: #6f42c1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.import-section button:hover:not(:disabled), .import-ecommerce button:hover:not(:disabled) {
  background-color: #5a32a3;
}

.import-section button:disabled, .import-ecommerce button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.help-text {
  font-size: 0.9rem;
  color: #666;
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