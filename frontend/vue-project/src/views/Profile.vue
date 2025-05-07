<template>
  <MainLayout>
    <div class="profile-page">
      <h1 class="profile-title">Profile</h1>
      <div v-if="isLoading" class="skeleton-container">
        <div class="skeleton-sidebar">
          <div v-for="n in 4" :key="n" class="skeleton-sidebar-item"></div>
        </div>
        <div class="skeleton-content">
          <div class="skeleton-section">
            <div class="skeleton-section-top">
              <div class="skeleton-title"></div>
              <div class="skeleton-button"></div>
            </div>
            <div class="skeleton-details">
              <div class="skeleton-photo"></div>
              <div class="skeleton-info">
                <div v-for="n in 5" :key="n" class="skeleton-text"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="profile-container">
        <!-- Sidebar -->
        <aside class="sidebar">
          <nav class="sidebar-nav">
            <ul>
              <li
                v-for="tab in tabs"
                :key="tab.id"
                :class="{ active: activeTab === tab.id }"
                @click="setActiveTab(tab.id)"
              >
                {{ tab.label }}
              </li>
            </ul>
            <span class="tab-indicator" :style="activeTabStyle"></span>
          </nav>
        </aside>

        <!-- Content Area -->
        <div class="content-area">
          <!-- User Information -->
          <div v-if="activeTab === 'user-info'" class="tab-content">
            <div class="profile-section">
              <div class="profile-section-top">
                <h2 class="profile-tabs-title">User Information</h2>
                <button @click="showEditProfileForm" class="edit-btn">Edit Profile</button>
              </div>
              <div class="profile-section-next">
                <div class="profile-photo">
                  <img
                    v-if="user.profile_photo"
                    :src="user.profile_photo"
                    alt="Profile Photo"
                    class="photo"
                  />
                  <img
                    v-else
                    src="@/assets/default_avatar.jpg"
                    alt="Default Avatar"
                    class="photo"
                  />
                </div>
                <div class="profile-info">
                  <p><span>Username:</span> {{ user.username || 'N/A' }}</p>
                  <p><span>Email:</span> {{ user.email || 'N/A' }}</p>
                  <p><span>First Name:</span> {{ user.first_name || 'N/A' }}</p>
                  <p><span>Last Name:</span> {{ user.last_name || 'N/A' }}</p>
                  <p><span>Phone Number:</span> {{ user.phone_number || 'N/A' }}</p>
                  <p><span>Points:</span> {{ user.points || 0 }}</p>
                  <p><span>Affiliate Code:</span> {{ user.affiliate_code || 'N/A' }}</p>
                  <p><span>Join Date:</span> {{ formatDate(user.date_joined) }}</p>
                </div>
              </div>
            </div>
            <!-- Edit Profile Form -->
            <div v-if="showEditProfile" class="edit-profile-form">
              <h3>Edit Profile</h3>
              <form @submit.prevent="updateProfile">
                <div class="form-group">
                  <label for="username">Username</label>
                  <input
                    type="text"
                    id="username"
                    v-model="editProfileForm.username"
                    required
                    :disabled="isSubmittingProfile"
                  />
                </div>
                <div class="form-group">
                  <label for="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    v-model="editProfileForm.email"
                    required
                    :disabled="isSubmittingProfile"
                  />
                </div>
                <div class="form-group">
                  <label for="first_name">First Name</label>
                  <input
                    type="text"
                    id="first_name"
                    v-model="editProfileForm.first_name"
                    required
                    :disabled="isSubmittingProfile"
                  />
                </div>
                <div class="form-group">
                  <label for="last_name">Last Name</label>
                  <input
                    type="text"
                    id="last_name"
                    v-model="editProfileForm.last_name"
                    required
                    :disabled="isSubmittingProfile"
                  />
                </div>
                <div class="form-group">
                  <label for="phone_number">Phone Number</label>
                  <input
                    type="tel"
                    id="phone_number"
                    v-model="editProfileForm.phone_number"
                    required
                    :disabled="isSubmittingProfile"
                  />
                </div>
                <div class="form-actions">
                  <button
                    type="submit"
                    class="save-btn"
                    :disabled="isSubmittingProfile"
                  >
                    {{ isSubmittingProfile ? 'Saving...' : 'Save' }}
                  </button>
                  <button
                    type="button"
                    @click="cancelEditProfile"
                    class="cancel-btn"
                    :disabled="isSubmittingProfile"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- Order History -->
          <div v-if="activeTab === 'orders'" class="tab-content">
            <div class="orders-section">
              <h2 class="profile-tabs-title">Order History</h2>
              <div v-if="ordersLoading" class="loading">Loading order history...</div>
              <div v-else-if="ordersError" class="error">{{ ordersError }}</div>
              <div v-else-if="!completedOrders.length">No completed orders yet.</div>
              <div v-else>
                <ul class="orders-list">
                  <li v-for="order in completedOrders" :key="order.id">
                    <div class="order-details">
                      <span class="order-number">Order {{ order.order_number }}</span>
                      <span class="order-date">{{ formatDate(order.created_at) }}</span>
                      <span class="order-status">{{ order.delivery_status }}</span>
                      <span class="order-total">KES {{ formatPrice(order.total_price) }}</span>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Security -->
          <div v-if="activeTab === 'security'" class="tab-content">
            <div class="security-section">
              <h2 class="profile-tabs-title">Security</h2>
              <button
                @click="showChangePasswordForm"
                class="change-password-btn"
                :disabled="isSubmittingPassword"
              >
                Change Password
              </button>
              <div v-if="showChangePassword" class="change-password-form">
                <h3>Change Password</h3>
                <form @submit.prevent="updatePassword">
                  <div class="form-group">
                    <label for="current-password">Current Password</label>
                    <input
                      type="password"
                      id="current-password"
                      v-model="changePasswordForm.currentPassword"
                      required
                      :disabled="isSubmittingPassword"
                    />
                  </div>
                  <div class="form-group">
                    <label for="new-password">New Password</label>
                    <input
                      type="password"
                      id="new-password"
                      v-model="changePasswordForm.newPassword"
                      required
                      :disabled="isSubmittingPassword"
                    />
                  </div>
                  <div class="form-group">
                    <label for="confirm-password">Confirm New Password</label>
                    <input
                      type="password"
                      id="confirm-password"
                      v-model="changePasswordForm.confirmPassword"
                      required
                      :disabled="isSubmittingPassword"
                    />
                  </div>
                  <div class="form-actions">
                    <button
                      type="submit"
                      class="save-btn"
                      :disabled="isSubmittingPassword"
                    >
                      {{ isSubmittingPassword ? 'Saving...' : 'Save' }}
                    </button>
                    <button
                      type="button"
                      @click="cancelChangePassword"
                      class="cancel-btn"
                      :disabled="isSubmittingPassword"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- Locations -->
          <div v-if="activeTab === 'locations'" class="tab-content">
            <div class="locations-section">
              <div class="locations-section-top">
                <h2 class="profile-tabs-title">Delivery Locations</h2>
                <button
                  @click="showAddLocationPopup"
                  class="add-location-btn"
                  :disabled="isSubmittingLocation"
                >
                  Add New Location
                </button>
              </div>
              <div v-if="locationsLoading" class="loading">Loading locations...</div>
              <div v-else-if="locationsError" class="error">{{ locationsError }}</div>
              <ul v-else class="locations-list">
                <li v-for="location in deliveryLocations" :key="location.id">
                  <div class="location-details">
                    <span class="location-name">{{ location.name }}</span>
                    <span class="location-address">{{ location.address }}</span>
                    <span v-if="location.is_default" class="default-tag">[Default]</span>
                  </div>
                  <div class="location-actions">
                    <button
                      @click="setAsDefault(location.id)"
                      :disabled="location.is_default || isSubmittingLocation"
                      class="set-default-btn"
                    >
                      Set as Default
                    </button>
                    <button
                      @click="confirmDeleteLocation(location.id)"
                      class="delete-btn"
                      :disabled="isSubmittingLocation"
                    >
                      Delete
                    </button>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Add Location Popup -->
      <AddDeliveryLocationPopup
        v-if="showPopup"
        @add-location="addLocation"
        @close="closePopup"
      />

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="modal-overlay">
        <div class="modal-content">
          <h3 class="profile-tabs-title">Confirm Deletion</h3>
          <p>Are you sure you want to delete this location?</p>
          <div class="modal-actions">
            <button
              @click="cancelDeleteLocation"
              class="cancel-btn"
              :disabled="isSubmittingLocation"
            >
              Cancel
            </button>
            <button
              @click="deleteLocation"
              class="confirm-btn"
              :disabled="isSubmittingLocation"
            >
              {{ isSubmittingLocation ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import { toast } from 'vue3-toastify';
import MainLayout from '@/components/navigation/MainLayout.vue';
import AddDeliveryLocationPopup from '@/views/AddDeliveryLocationPopup.vue';

// Store
const store = useEcommerceStore();

// Tabs
const tabs = [
  { id: 'user-info', label: 'User Information' },
  { id: 'orders', label: 'Order History' },
  { id: 'security', label: 'Security' },
  { id: 'locations', label: 'Location Information' },
];
const activeTab = ref('user-info');

// State
const isLoading = ref(true);
const showPopup = ref(false);
const showDeleteModal = ref(false);
const locationToDeleteId = ref(null);
const showEditProfile = ref(false);
const showChangePassword = ref(false);
const isSubmittingProfile = ref(false);
const isSubmittingPassword = ref(false);
const isSubmittingLocation = ref(false);

// Forms
const editProfileForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone_number: '',
});
const changePasswordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

// Computed
const user = computed(() => store.currentUser || {});
const deliveryLocations = computed(() => store.deliveryLocations || []);
const completedOrders = computed(() =>
  store.orders.filter(order => order.delivery_status === 'delivered')
);
const ordersLoading = computed(() => store.loading.orders);
const ordersError = computed(() => store.error.orders);
const locationsLoading = computed(() => store.loading.deliveryLocations);
const locationsError = computed(() => store.error.deliveryLocations);

// Utility Functions
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

const formatPrice = (price) => {
  if (price == null) return 'N/A';
  return (Math.round(price * 100) / 100).toFixed(2);
};

// Profile Methods
const showEditProfileForm = () => {
  editProfileForm.value = { ...user.value };
  showEditProfile.value = true;
};

const cancelEditProfile = () => {
  showEditProfile.value = false;
};

const updateProfile = async () => {
  isSubmittingProfile.value = true;
  try {
    await store.updateUserProfile(editProfileForm.value);
    showEditProfile.value = false;
    toast.success('Profile updated successfully!');
  } catch (error) {
    console.error('Update profile error:', error);
    toast.error(error.message || 'Failed to update profile');
  } finally {
    isSubmittingProfile.value = false;
  }
};

// Password Methods
const showChangePasswordForm = () => {
  showChangePassword.value = true;
};

const cancelChangePassword = () => {
  changePasswordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  };
  showChangePassword.value = false;
};

const updatePassword = async () => {
  if (changePasswordForm.value.newPassword !== changePasswordForm.value.confirmPassword) {
    toast.error('New passwords do not match');
    return;
  }
  isSubmittingPassword.value = true;
  try {
    await store.changePassword(
      changePasswordForm.value.currentPassword,
      changePasswordForm.value.newPassword,
      changePasswordForm.value.confirmPassword
    );
    showChangePassword.value = false;
    toast.success('Password changed successfully!');
    cancelChangePassword();
  } catch (error) {
    console.error('Change password error:', error);
    toast.error(error.message || 'Failed to change password');
  } finally {
    isSubmittingPassword.value = false;
  }
};

// Location Methods
const showAddLocationPopup = () => {
  console.log('showAddLocationPopup: Setting showPopup to true');
  showPopup.value = true;
};

const closePopup = () => {
  showPopup.value = false;
  console.log('closePopup: Popup closed');
};

const addLocation = async (newLocation) => {
  isSubmittingLocation.value = true;
  try {
    await store.addDeliveryLocation(newLocation);
    toast.success('Location added successfully!');
    closePopup();
  } catch (error) {
    console.error('Failed to add location:', error);
    toast.error(error.message || 'Failed to add location');
  } finally {
    isSubmittingLocation.value = false;
  }
};

const setAsDefault = async (locationId) => {
  isSubmittingLocation.value = true;
  try {
    await store.setDefaultDeliveryLocation(locationId);
    toast.success('Default delivery location set!');
  } catch (error) {
    console.error('Failed to set default location:', error);
    toast.error(error.message || 'Failed to set default location');
  } finally {
    isSubmittingLocation.value = false;
  }
};

const confirmDeleteLocation = (locationId) => {
  locationToDeleteId.value = locationId;
  showDeleteModal.value = true;
};

const deleteLocation = async () => {
  isSubmittingLocation.value = true;
  try {
    await store.deleteDeliveryLocation(locationToDeleteId.value);
    toast.success('Location deleted successfully!');
  } catch (error) {
    console.error('Failed to delete location:', error);
    toast.error(error.message || 'Failed to delete location');
  } finally {
    showDeleteModal.value = false;
    locationToDeleteId.value = null;
    isSubmittingLocation.value = false;
  }
};

const cancelDeleteLocation = () => {
  showDeleteModal.value = false;
  locationToDeleteId.value = null;
};

// Tab Navigation
const setActiveTab = (tab) => {
  activeTab.value = tab;
  if (tab === 'orders' && !store.orders.length) {
    store.fetchOrdersData();
  }
};

const activeTabStyle = computed(() => {
  const tabHeight = 50;
  const tabIndex = tabs.findIndex(tab => tab.id === activeTab.value);
  return {
    top: `${tabIndex * tabHeight}px`,
    transition: 'top 0.3s ease',
  };
});

// Lifecycle
onMounted(async () => {
  try {
    isLoading.value = true;
    await Promise.all([
      store.fetchUserProfile(),
      store.fetchDeliveryLocations(),
      store.fetchOrdersData(),
    ]);
  } catch (error) {
    console.error('Error loading profile data:', error);
    toast.error('Failed to load profile data');
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.profile-page {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-title {
  font-family: cursive;
  color:#D4A017;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 1rem 0 2rem;
  text-align: left;
}

.loading, .error {
  text-align: center;
  font-size: 1rem;
  color: #666;
  margin: 1rem 0;
}

/* Skeleton Loader */
.skeleton-container {
  display: flex;
  gap: 1.5rem;
  padding: 1rem;
}

.skeleton-sidebar {
  width: 200px;
}

.skeleton-sidebar-item {
  height: 50px;
  margin: 0.5rem 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-content {
  flex: 1;
}

.skeleton-section {
  padding: 1rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.skeleton-section-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.skeleton-title {
  width: 120px;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-button {
  width: 80px;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-details {
  display: flex;
  gap: 1.5rem;
}

.skeleton-photo {
  width: 80px;
  height: 80px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 50%;
}

.skeleton-info {
  flex: 1;
}

.skeleton-text {
  width: 70%;
  height: 16px;
  margin: 0.5rem 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Profile Container */
.profile-container {
  display: flex;
  gap: 1.5rem;
}

/* Sidebar */
.sidebar {
  width: 200px;
  position: relative;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li {
  padding: 0.75rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  height: 50px;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}

.sidebar-nav li.active {
  font-weight: 600;
  color:#D4A017;
  background: #f9f9f9;
}

.tab-indicator {
  position: absolute;
  right: 0;
  width: 4px;
  height: 50px;
  background:#D4A017;
}

/* Content Area */
.content-area {
  flex: 1;
  padding: 1rem;
}

.tab-content {
  background: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.profile-section-top, .locations-section-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.profile-section-next {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.profile-tabs-title {
  font-size: 1.25rem;
  font-weight: 700;
  color:#D4A017;
  margin: 0;
}

.profile-photo img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-info p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.profile-info p span {
  font-weight: 600;
  color: #666;
  display: inline-block;
  width: 120px;
}

/* Forms */
.edit-profile-form, .change-password-form {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  max-width: 300px;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

/* Orders */
.orders-list {
  list-style: none;
  padding: 0;
}

.orders-list li {
  padding: 0.75rem 0;
  border-bottom: 1px solid #eee;
}

.order-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.9rem;
}

.order-number {
  font-weight: 600;
}

.order-status {
  color: #4CAF50;
}

.order-total {
  font-weight: 600;
}

/* Locations */
.locations-list {
  list-style: none;
  padding: 0;
}

.locations-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #eee;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.location-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-width: 60%;
}

.location-name {
  font-weight: 600;
  font-size: 0.9rem;
}

.location-address {
  color: #666;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.default-tag {
  color: #4CAF50;
  font-size: 0.85rem;
}

.location-actions {
  display: flex;
  gap: 0.5rem;
}

/* Buttons */
.edit-btn, .add-location-btn {
  background:#D4A017;
  border: none;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  min-height: 2.75rem;
  transition: background 0.2s;
}

.edit-btn:hover, .add-location-btn:hover:not(:disabled) {
  background: #e07b30;
}

.change-password-btn, .set-default-btn, .delete-btn, .save-btn, .cancel-btn, .confirm-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  min-height: 2.75rem;
}

.change-password-btn {
  background:#D4A017;
  color: white;
}

.change-password-btn:hover:not(:disabled) {
  background: #e07b30;
}

.set-default-btn {
  background:#D4A017;
  color: white;
}

.set-default-btn:hover:not(:disabled) {
  background: #e07b30;
}

.set-default-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.delete-btn, .confirm-btn {
  background: #f44336;
  color: white;
}

.delete-btn:hover:not(:disabled), .confirm-btn:hover:not(:disabled) {
  background: #da190b;
}

.save-btn {
  background: #4CAF50;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #45a049;
}

.cancel-btn {
  background: #3f3f3f;
  color: #d3d3d3;
}

.cancel-btn:hover:not(:disabled) {
  background: #2f2f2f;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color:#D4A017;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .profile-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
  }

  .sidebar-nav ul {
    display: flex;
    overflow-x: auto;
    white-space: nowrap;
    padding-bottom: 0.5rem;
  }

  .sidebar-nav li {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    height: auto;
  }

  .tab-indicator {
    display: none;
  }

  .skeleton-container {
    flex-direction: column;
  }

  .skeleton-sidebar {
    width: 100%;
    display: flex;
    overflow-x: auto;
  }

  .skeleton-sidebar-item {
    width: 120px;
    flex-shrink: 0;
    margin: 0.5rem;
  }
}

@media (max-width: 320px) {
  .profile-page {
    padding: 0.5rem;
  }

  .profile-title {
    font-size: 1.25rem;
    margin: 0.5rem 0 1rem;
  }

  .profile-tabs-title {
    font-size: 1.1rem;
  }

  .profile-info p,
  .order-details,
  .location-details,
  .location-actions,
  .form-group label,
  .form-group input {
    font-size: 0.85rem;
  }

  .profile-photo img {
    width: 60px;
    height: 60px;
  }

  .profile-info p span {
    width: 100px;
  }

  .form-group input {
    max-width: 100%;
  }

  .edit-btn,
  .add-location-btn,
  .change-password-btn,
  .set-default-btn,
  .delete-btn,
  .save-btn,
  .cancel-btn,
  .confirm-btn {
    padding: 0.4rem 0.8rem;
    min-height: 2.5rem;
    font-size: 0.85rem;
  }

  .skeleton-photo {
    width: 60px;
    height: 60px;
  }

  .skeleton-text {
    height: 14px;
  }
}
</style>