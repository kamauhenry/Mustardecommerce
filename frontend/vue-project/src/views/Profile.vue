<template>
  <MainLayout>
    <div class="profile-page">
      <h1 class="page-title">Profile</h1>
      <div v-if="isLoading" class="loading">Loading...</div>
      <div v-else class="profile-container">
        <!-- Left Sidebar -->
        <aside class="sidebar">
          <nav class="sidebar-nav">
            <ul>
              <li
                :class="{ active: activeTab === 'user-info' }"
                @click="setActiveTab('user-info')"
              >
                User Information
              </li>
              <li
                :class="{ active: activeTab === 'orders' }"
                @click="setActiveTab('orders')"
              >
                Orders
              </li>
              <li
                :class="{ active: activeTab === 'security' }"
                @click="setActiveTab('security')"
              >
                Security
              </li>
              <li
                :class="{ active: activeTab === 'locations' }"
                @click="setActiveTab('locations')"
              >
                Location Information
              </li>
            </ul>
            <!-- Single Tab Indicator -->
            <span class="tab-indicator" :style="activeTabStyle"></span>
          </nav>
        </aside>

        <!-- Right Content Area -->
        <div class="content-area">
          <!-- User Information Tab -->
          <div v-if="activeTab === 'user-info'" class="tab-content">
            <div class="profile-section">
              <div class="profile-section-top">
                <h2 class="profile-tabs-title">User Information</h2>
                <button @click="showEditProfileForm" class="edit-btn">Edit Profile</button>
              </div>
              <div class="profile-section-next">
                <div class="profile-photo">
                  <div class="profile-photo-img">
                    <img
                      v-if="user.profile_photo"
                      :src="user.profile_photo"
                      alt="Profile Photo"
                      class="photo"
                    />
                    <div v-else class="photo-placeholder">No Photo</div>
                  </div>
                  <div class="change-photo">
                    <button @click="triggerFileInput" class="change-photo-btn">
                      Change Photo
                    </button>
                    <input
                      type="file"
                      ref="fileInput"
                      @change="handleProfilePhotoChange"
                      style="display: none"
                      accept="image/*"
                    />
                  </div>
                </div>
                <div class="profile-info">
                  <p><span>Username:</span> {{ user.username || 'N/A' }}</p>
                  <p><span>Email:</span> {{ user.email || 'N/A' }}</p>
                  <p><span>User Type:</span> {{ user.user_type || 'N/A' }}</p>
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
                  />
                </div>
                <div class="form-group">
                  <label for="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    v-model="editProfileForm.email"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="email">First Name</label>
                  <input
                    type="text"
                    id="first_name"
                    v-model="editProfileForm.first_name"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="email">Last Name</label>
                  <input
                    type="text"
                    id="last_name"
                    v-model="editProfileForm.last_name"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="email">Last Name</label>
                  <input
                    type="tel"
                    id="phone_number"
                    v-model="editProfileForm.phone_number"
                    required
                  />
                </div>
                <div class="form-actions">
                  <button type="submit" class="save-btn">Save</button>
                  <button type="button" @click="cancelEditProfile" class="cancel-btn">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- Orders Tab -->
          <div v-if="activeTab === 'orders'" class="tab-content">
            <div class="orders-section">
              <h2 class="profile-tabs-title">Orders</h2>
              <div v-if="ordersLoading" class="loading">Loading orders...</div>
              <div v-else-if="ordersError" class="error">{{ ordersError }}</div>
              <div v-else>
                <ul class="orders-list">
                  <li v-for="order in orders" :key="order.id">
                    <div class="order-details">
                      <span class="order-number">Order #{{ order.id }}</span>
                      <span class="order-date">{{ formatDate(order.created_at) }}</span>
                      <span class="order-status">{{ order.delivery_status }}</span>
                      <span class="order-total">${{ order.total_price }}</span>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Security Tab -->
          <div v-if="activeTab === 'security'" class="tab-content">
            <div class="security-section">
              <h2 class="profile-tabs-title">Security</h2>
              <button @click="showChangePasswordForm" class="change-password-btn">
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
                    />
                  </div>
                  <div class="form-group">
                    <label for="new-password">New Password</label>
                    <input
                      type="password"
                      id="new-password"
                      v-model="changePasswordForm.newPassword"
                      required
                    />
                  </div>
                  <div class="form-group">
                    <label for="confirm-password">Confirm New Password</label>
                    <input
                      type="password"
                      id="confirm-password"
                      v-model="changePasswordForm.confirmPassword"
                      required
                    />
                  </div>
                  <div class="form-actions">
                    <button type="submit" class="save-btn">Save</button>
                    <button type="button" @click="cancelChangePassword" class="cancel-btn">
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- Location Information Tab -->
          <div v-if="activeTab === 'locations'" class="tab-content">
            <div class="locations-section">
              <div class="locations-section-top">
                <h2 class="profile-tabs-title">Delivery Locations</h2>
                <button @click="showAddLocationPopup" class="add-location-btn">
                Add New Location
              </button>
              </div>
              <ul class="locations-list">
                <li v-for="location in deliveryLocations" :key="location.id">
                  <div class="location-details">
                    <span class="location-name">{{ location.name }}</span>
                    <span class="location-address">{{ location.address }}</span>
                    <span v-if="location.is_default" class="default-tag">[Default]</span>
                  </div>
                  <div class="location-actions">
                    <button
                      @click="setAsDefault(location.id)"
                      :disabled="location.is_default"
                      class="set-default-btn"
                    >
                      Set as Default
                    </button>
                    <button @click="confirmDeleteLocation(location.id)" class="delete-btn">
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
            <button @click="cancelDeleteLocation" class="cancel-btn">Cancel</button>
            <button @click="deleteLocation" class="confirm-btn">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';
import AddDeliveryLocationPopup from '@/components/auth/AddDeliveryLocationPopup.vue';
import { getCurrentInstance } from 'vue';

export default {
  name: 'ProfilePage',
  components: {
    MainLayout,
    AddDeliveryLocationPopup,
  },
  setup() {
    const store = useEcommerceStore();
    const showPopup = ref(false);
    const isLoading = ref(true);
    const fileInput = ref(null);
    const showDeleteModal = ref(false);
    const locationToDeleteId = ref(null);
    const activeTab = ref('user-info'); // Default tab
    const { proxy } = getCurrentInstance();

    // Fetch user profile and delivery locations on mount
    onMounted(async () => {
      try {
        isLoading.value = true;
        await store.fetchUserProfile();
        await store.fetchDeliveryLocations();
      } catch (error) {
        console.error('Error loading profile data:', error);
      } finally {
        isLoading.value = false;
      }
    });

    // Get user data from store
    const user = computed(() => store.currentUser || {});

    // Get delivery locations from store
    const deliveryLocations = computed(() => store.deliveryLocations || []);

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getFullYear()}`;
    };

    const triggerFileInput = () => {
      fileInput.value.click();
    };

    const handleProfilePhotoChange = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      try {
        const formData = new FormData();
        formData.append('profile_photo', file);
        await store.updateProfilePhoto(formData);
        proxy.$toast.success('Profile photo updated successfully!');
      } catch (error) {
        console.error('Failed to update profile photo:', error);
        proxy.$toast.error('Failed to update profile photo');
      }
    };

    const showAddLocationPopup = () => {
      showPopup.value = true;
    };

    const closePopup = () => {
      showPopup.value = false;
    };

    const addLocation = async (newLocation) => {
      try {
        await store.addDeliveryLocation(newLocation);
        proxy.$toast.success('Location added successfully!');
        closePopup();
      } catch (error) {
        proxy.$toast.error('Failed to add location');
        console.error('Failed to add location:', error);
      }
    };

    const setAsDefault = async (locationId) => {
      try {
        await store.setDefaultDeliveryLocation(locationId);
        proxy.$toast.success('Default delivery location changed successfully!');
      } catch (error) {
        proxy.$toast.error('Failed to set default location');
        console.error('Failed to set default location:', error);
      }
    };

    const confirmDeleteLocation = (locationId) => {
      locationToDeleteId.value = locationId;
      showDeleteModal.value = true;
    };

    const deleteLocation = async () => {
      try {
        await store.deleteDeliveryLocation(locationToDeleteId.value);
        proxy.$toast.success('Location deleted successfully!');
      } catch (error) {
        console.error('Failed to delete location:', error);
        proxy.$toast.error(`Failed to delete location: ${error.message || 'Unknown error'}`);
      } finally {
        closeDeleteModal();
      }
    };

    const cancelDeleteLocation = () => {
      closeDeleteModal();
    };

    const closeDeleteModal = () => {
      showDeleteModal.value = false;
      locationToDeleteId.value = null;
    };

    const editUser = () => {
      proxy.$toast.error('Edit profile functionality to be implemented.');
    };

    const changePassword = () => {
      proxy.$toast.error('Edit profile functionality to be implemented.');
    };

    // Tab navigation
    const setActiveTab = (tab) => {
      activeTab.value = tab;
    };

    // Calculate the position of the tab indicator
    const activeTabStyle = computed(() => {
      const tabHeight = 50; // Height of each tab (adjust based on your design)
      const tabIndex = {
        'user-info': 0,
        'orders': 1,
        'security': 2,
        'locations': 3,
      }[activeTab.value];
      const topPosition = tabIndex * tabHeight;
      return {
        top: `${topPosition}px`,
        transition: 'top 0.3s ease', // Smooth transition
      };
    });

    return {
      user,
      deliveryLocations,
      showPopup,
      isLoading,
      fileInput,
      showDeleteModal,
      activeTab,
      activeTabStyle,
      formatDate,
      triggerFileInput,
      handleProfilePhotoChange,
      showAddLocationPopup,
      closePopup,
      addLocation,
      setAsDefault,
      confirmDeleteLocation,
      deleteLocation,
      cancelDeleteLocation,
      editUser,
      changePassword,
      setActiveTab,
    };
  },
};
</script>

<style scoped>

.page-title {
  margin-bottom: 1.5rem;
}

.loading {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
}

.profile-container {
  display: flex;
  gap: 2rem;
}

/* Sidebar */
.sidebar {
  width: 20vw;
  height: 50vh;
  position: relative;
  padding-top: 1rem;
  border-radius: 10px;
}

.sidebar-nav {
  position: relative;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li {
  padding: 1rem 1.5rem;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s ease;
  height: 50px; /* Fixed height for consistent indicator positioning */
  display: flex;
  align-items: center;
}

.sidebar-nav li.active {
  font-weight: 600;
  color: #f28c38;
}

/* Tab Indicator */
.tab-indicator {
  position: absolute;
  right: -2px; /* Align with the border-right of the sidebar */
  width: 4px;
  height: 50px; /* Match the height of each tab */
  background: #f28c38;
  display: block;
}

/* Content Area */
.content-area {
  flex: 1;
  padding: 1rem;
}

.tab-content {
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.about-h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

/* Profile Section */
.profile-section {
  margin-bottom: 2rem;
}

.profile-section-top, .locations-section-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.profile-section-next {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 2rem;
}

.profile-tabs-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f28c38;
  text-transform: uppercase;
  margin: 0.5rem 0;
}

.profile-photo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin: 0 1rem 1rem;
}

.profile-info p {
  margin: 1rem 0;
}

.profile-info p span {
  font-weight: 700;
  color: #666;
}

.photo,
.photo-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}

.photo-placeholder {
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 0.9rem;
}

.change-photo-btn,
.change-password-btn,
.set-default-btn,
.delete-btn,
.save-btn
{
  padding: 0.5rem .7rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 700;
}

.change-photo-btn:hover,
.change-password-btn:hover,
.set-default-btn:hover:not(:disabled),
.delete-btn:hover,
.save-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.change-photo-btn {
  background: #f28c38;
  color: white;
}
.edit-btn, .add-location-btn {
  color: rgb(206, 102, 61);
  font-size: 1rem;
  font-weight: 700;
  background-color: inherit;
  padding: 0 .7rem;
  border: none;
  cursor: pointer;
}

.edit-btn:hover, .add-location-btn:hover {
  box-shadow: 0 1px rgba(242, 140, 56, 0.4);
}

.change-password-btn {
  background: #f28c38dc;
  color: white;
}

.change-password-btn:hover {
  background: #f28c38;
}

/* Edit Profile Form */
.edit-profile-form,
.change-password-form {
  margin-top: 2rem;
  padding: 1rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.save-btn {
  background: #4CAF50;
  color: white;
}

.save-btn:hover {
  background: #45a049;
}

/* Orders Section */
.orders-section {
  margin-bottom: 2rem;
}

.orders-list {
  list-style: none;
  padding: 0;
}

.orders-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #ddd;
}

.order-details {
  display: flex;
  gap: 1rem;
  align-items: center;
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

/* Security Section */
.security-section {
  margin-bottom: 2rem;
}

/* Locations Section */
.locations-list {
  list-style: none;
  padding: 0;
}

.locations-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.location-details {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.location-name {
  font-weight: 600;
}

.location-address {
  color: #666;
}

.default-tag {
  color: #4CAF50;
  font-size: 0.85rem;
}

.location-actions {
  display: flex;
  gap: 0.5rem;
}

.set-default-btn {
  background: #f28c38dc;
  color: white;
}

.set-default-btn:hover:not(:disabled) {
  background: #f28c38;
}

.set-default-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.delete-btn {
  background: #f44336;
  color: white;
}

.delete-btn:hover {
  background: #da190b;
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
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.cancel-btn,
.confirm-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 700;
}

.cancel-btn {
  background: #3f3f3f;
  color: #d3d3d3;
}

.cancel-btn:hover, .confirm-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.confirm-btn {
  background: #f44336;
  color: white;
}

/* Responsive Design */
@media (max-width: 768px) {
  .profile-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 2px solid #ddd;
  }

  .sidebar-nav li {
    padding: 1rem;
    height: auto;
  }

  .tab-indicator {
    display: none; /* Hide indicator on mobile for simplicity */
  }

  .content-area {
    padding: 1rem 0;
  }
}
</style>
