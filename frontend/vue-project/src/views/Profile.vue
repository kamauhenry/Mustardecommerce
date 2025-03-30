<template>
  <MainLayout>
    <div class="profile-page">
      <h1>Profile</h1>
      <div v-if="isLoading" class="loading">Loading...</div>
      <div v-else>
        <!-- User Profile Section -->
        <div class="profile-section">
          <h2>User Information</h2>
          <div class="profile-photo">
            <img
              v-if="user.profile_photo"
              :src="user.profile_photo"
              alt="Profile Photo"
              class="photo"
            />
            <div v-else class="photo-placeholder">No Photo</div>
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
          <p><strong>Username:</strong> {{ user.username || 'N/A' }}</p>
          <p><strong>Email:</strong> {{ user.email || 'N/A' }}</p>
          <p><strong>User Type:</strong> {{ user.user_type || 'N/A' }}</p>
          <p><strong>Points:</strong> {{ user.points || 0 }}</p>
          <p><strong>Affiliate Code:</strong> {{ user.affiliate_code || 'N/A' }}</p>
          <p><strong>Join Date:</strong> {{ formatDate(user.date_joined) }}</p>
          <button @click="editUser" class="edit-btn">Edit Profile</button>
          <button @click="changePassword" class="change-password-btn">
            Change Password
          </button>
        </div>

        <!-- Delivery Locations Section -->
        <div class="locations-section">
          <h2>Delivery Locations</h2>
          <button @click="showAddLocationPopup" class="add-location-btn">
            Add New Location
          </button>
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

      <!-- Add Location Popup -->
      <AddDeliveryLocationPopup
        v-if="showPopup"
        @add-location="addLocation"
        @close="closePopup"
      />

      <!-- Delete Confirmation Modal -->
      <div v-if="showDeleteModal" class="modal-overlay">
        <div class="modal-content">
          <h3>Confirm Deletion</h3>
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
import axios from 'axios';
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

    return {
      user,
      deliveryLocations,
      showPopup,
      isLoading,
      fileInput,
      showDeleteModal,
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
    };
  },
};
</script>

<style scoped>
.profile-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
}

.profile-section,
.locations-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border-radius: 8px;
  background: #f9f9f9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.profile-section h2,
.locations-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.profile-photo {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
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
.edit-btn,
.change-password-btn,
.add-location-btn,
.set-default-btn,
.delete-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.change-photo-btn {
  background: #f28c38;
  color: white;
}

.change-photo-btn:hover {
  background: #e07b30;
}

.edit-btn {
  background: #4CAF50;
  color: white;
}

.edit-btn:hover {
  background: #45a049;
}

.change-password-btn {
  background: #2196F3;
  color: white;
}

.change-password-btn:hover {
  background: #1e87db;
}

.add-location-btn {
  background: #f28c38;
  color: white;
  margin-bottom: 1rem;
}

.add-location-btn:hover {
  background: #e07b30;
}

.locations-list {
  list-style: none;
  padding: 0;
}

.locations-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #ddd;
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
  background: #2196F3;
  color: white;
}

.set-default-btn:hover:not(:disabled) {
  background: #1e87db;
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
}

.cancel-btn {
  background: #f5f5f5;
  color: #333;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.confirm-btn {
  background: #f44336;
  color: white;
}

.confirm-btn:hover {
  background: #da190b;
}
</style>
