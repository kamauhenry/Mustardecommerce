<template>
  <MainLayout>
    <div class="profile-container">
      <div class="profile-header">
        <h1>Profile</h1>
      </div>

      <!-- User Info Section -->
      <div class="user-info-section">
        <div class="profile-photo-container">
          <div class="profile-photo" @click="triggerFileInput">
            <span v-if="!user.profilePhoto">CLICK TO CHANGE PHOTO</span>
            <img v-else :src="user.profilePhoto" alt="Profile Photo" />
          </div>
          <input type="file" ref="fileInput" style="display: none" @change="handleProfilePhotoChange" accept="image/*" />

          <div class="profile-actions">
            <button class="action-button primary-button" @click="editUser">Edit User</button>
            <button class="action-button secondary-button" @click="changePassword">Change Password</button>
          </div>
        </div>

        <div class="user-details">
          <h2 class="user-name">User Information</h2>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Username</span>
              <span class="info-value">{{ user.username }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">Affiliate Code</span>
              <span class="info-value">{{ user.affiliate_code || 'Not available' }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">{{ user.points ? 'Points' : 'Affiliate Points' }}</span>
              <span class="info-value">{{ user.points || 0 }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">Phone</span>
              <span class="info-value">{{ user.phone || 'Not set' }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">Member Since</span>
              <span class="info-value">{{ formatDate(user.date_joined) }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">Email</span>
              <span class="info-value">{{ user.email || 'Not set' }}</span>
            </div>

            <div class="info-item">
              <span class="info-label">Items Ordered</span>
              <span class="info-value">{{ user.orders_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Delivery Locations Section -->
      <div class="locations-section">
        <div class="section-header">
          <h2>DELIVERY LOCATIONS</h2>
          <button class="add-button" @click="showAddLocationPopup">ADD +</button>
        </div>

        <div class="locations-container">
          <div v-if="deliveryLocations.length === 0" class="no-locations">
            No delivery locations added yet.
          </div>

          <div v-else class="location-map-grid">
            <div v-for="location in deliveryLocations" :key="location.id" class="location-map-item">
              <div class="map-container">
                <!-- Map display would go here - using a placeholder for now -->
                <div class="map-placeholder">
                  <!-- You would integrate an actual map component here -->
                  <iframe
                    width="100%"
                    height="100%"
                    frameborder="0"
                    scrolling="no"
                    marginheight="0"
                    marginwidth="0"
                    :src="`https://maps.google.com/maps?q=${encodeURIComponent(location.address)}&t=&z=15&ie=UTF8&iwloc=&output=embed`">
                  </iframe>
                </div>

                <div class="location-actions">
                  <button class="location-edit-btn" @click="editLocation(location.id)">
                    <span class="icon-edit">✏️</span>
                  </button>
                  <button class="location-delete-btn" @click="deleteLocation(location.id)">
                    <span class="icon-delete">🗑️</span>
                  </button>
                </div>
              </div>

              <div class="location-details">
                <h3>{{ location.name }}</h3>
                <p>{{ location.address }}</p>
                <span v-if="location.isDefault" class="default-badge">Default</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Add Location Popup -->
      <AddDeliveryLocationPopup
        v-if="showPopup"
        @close="closePopup"
        @add-location="addLocation"
      />

      <div v-if="showDeleteModal" class="modal-overlay">
        <div class="modal">
          <h2>Confirm Delete</h2>
          <p>Are you sure you want to delete this location?</p>
          <div class="modal-actions">
            <button class="cancel-button" @click="cancelDeleteLocation">Cancel</button>
            <button class="delete-button" @click="deleteLocation">Delete</button>
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
    const showDeleteModal = ref(false); // Add this line
    const locationToDeleteId = ref(null); // Add this line
    const { proxy } = getCurrentInstance()

    // Use the store to fetch user profile and delivery locations
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
        proxy.$toast.error(`Failed to update profile photo`);
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
        proxy.$toast.error(`Failed to add location`);
        console.error('Failed to add location:', error);
      }
    };

    const editLocation = (locationId) => {
      // Would need to implement a location editing component
      proxy.$toast.error('Edit location functionality to be implemented.');
    };

    const setAsDefault = async (locationId) => {
      try {
        await store.setDefaultDeliveryLocation(locationId);
        proxy.$toast.success('Default delivery location changed successfully!');
      } catch (error) {
        proxy.$toast.error(`Failed to set default location`);
        console.error('Failed to set default location:', error);
      }
    };

    const deleteLocation = async (locationId) => {
      locationToDeleteId.value = locationId;
      showDeleteModal.value = true;
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
      // Would need to implement a profile editing component
      proxy.$toast.error(`Edit profile functionality to be implemented.`);
    };

    const changePassword = () => {
      // Would need to implement a profile editing component
      proxy.$toast.error(`Edit profile functionality to be implemented.`);
    };

    return {
      user,
      deliveryLocations,
      showPopup,
      isLoading,
      fileInput,
      formatDate,
      triggerFileInput,
      handleProfilePhotoChange,
      showAddLocationPopup,
      closePopup,
      addLocation,
      editLocation,
      setAsDefault,
      deleteLocation,
      editUser,
      changePassword,
    };
  },
};
</script>

<style scoped>
/* Main Container */
.profile-container {
  font-family: 'Roboto', sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header h1 {
  color: #ff5722;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

/* User Info Section */
.user-info-section {
  display: flex;
  gap: 2rem;
  margin-bottom: 3rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

.profile-photo-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 250px;
}

.profile-photo {
  width: 250px;
  height: 250px;
  background-color: #b0bec5;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 0.875rem;
  text-align: center;
  border-radius: 4px;
}

.profile-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.action-button {
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.primary-button {
  background-color: #ff5722;
  color: white;
}

.primary-button:hover {
  background-color: #e64a19;
}

.secondary-button {
  background-color: #f5f5f5;
  color: #333;
}

.secondary-button:hover {
  background-color: #e0e0e0;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 700;
}

.info-value {
  font-size: 1rem;
  font-weight: 500;
}

/* Delivery Locations Section */
.locations-section {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  color: #ff5722;
  font-size: 1.25rem;
  font-weight: 600;
}

.add-button {
  background-color: #ff5722;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.add-button:hover {
  background-color: #e64a19;
}

.no-locations {
  text-align: center;
  padding: 2rem;
  font-style: italic;
}

.location-map-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.location-map-item {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.location-map-item:hover {
  transform: translateY(-4px);
}

.map-container {
  position: relative;
  height: 200px;
  width: 100%;
}

.map-placeholder {
  height: 100%;
  width: 100%;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.location-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 0.5rem;
}

.location-edit-btn, .location-delete-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.location-edit-btn {
  background-color: #ff5722;
  color: white;
}

.location-delete-btn {
  background-color: #f44336;
  color: white;
}

.location-details {
  padding: 1rem;
}

.location-details h3 {
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.location-details p {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
}

.default-badge {
  display: inline-block;
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.modal h2 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #333;
}

.modal p {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 20px;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.cancel-button,
.delete-button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}

.cancel-button {
  background-color: #ddd;
  color: #333;
}

.delete-button {
  background-color: #f44336;
  color: white;
}

/* Responsive Design */
@media (max-width: 768px) {
  .user-info-section {
    flex-direction: column;
  }

  .profile-photo-container {
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
