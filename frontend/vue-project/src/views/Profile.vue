<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <MainLayout>
    <div class="profile-container">
      <!-- Header -->
      <h2 class="account-header">MY ACCOUNT</h2>
      
      <!-- Profile Section -->
      <div class="profile-section">
        <div class="photo-container">
          <div class="profile-photo">
            <span>Change photo</span>
          </div>
          <div class="edit-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2">
              <path d="M20 6L9 17l-5-5" />
            </svg>
          </div>
        </div>
        
        <div class="profile-details">
          <h2 class="profile-name">John Doe</h2>
          
          <div class="details-grid">
            <div class="detail-item">
              <span class="detail-label">Username:</span>
              <span class="detail-value">Do1</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Affiliate code:</span>
              <span class="detail-value">Do1sd33</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">MustPoints:</span>
              <span class="detail-value">0</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Phone:</span>
              <span class="detail-value">254712345678</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Member since:</span>
              <span class="detail-value">1/1/25</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Email:</span>
              <span class="detail-value">john.doe@ex.com</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Items Ordered:</span>
              <span class="detail-value">2</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="action-buttons">
        <button class="edit-button">Edit User</button>
        <button class="password-button">Change Password</button>
      </div>
      
      <!-- Delivery Locations -->
      <h2 class="locations-header">DELIVERY LOCATIONS</h2>
      
      <div class="location-section">
        <div class="map-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="80" height="80" fill="none" stroke="#333" stroke-width="1">
            <path d="M3 6v15h18V6M3 6a3 3 0 013-3h12a3 3 0 013 3M3 6l9 6 9-6" />
            <circle cx="12" cy="10" r="2" />
          </svg>
        </div>
        
        <div class="location-details">
          <div class="location-name">
            Kenya
            <div class="location-edit-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2">
                <path d="M20 6L9 17l-5-5" />
              </svg>
            </div>
            <div class="location-delete-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#000" stroke-width="2">
                <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14" />
              </svg>
            </div>
            <div class="location-add-button">
              ADD+
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import MainLayout from "@/components/navigation/MainLayout.vue";

export default {
  name: 'Profile',
  components: {
    MainLayout,
  },
  data() {
    return {
      user: {
        name: 'John Doe',
        username: 'Do1',
        affiliateCode: 'Do1sd33',
        mustPoints: 0,
        phone: '254712345678',
        memberSince: '1/1/25',
        email: 'john.doe@ex.com',
        itemsOrdered: 2
      },
      locations: [
        {
          name: 'Kenya'
        }
      ]
    }
  }
}
</script>

<style scoped>
.profile-container {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.account-header,
.locations-header {
  color: #7b7921;
  font-weight: bold;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.profile-section {
  display: flex;
  margin-bottom: 30px;
}

.photo-container {
  position: relative;
  margin-right: 30px;
}

.profile-photo {
  width: 180px;
  height: 180px;
  background-color: #aaa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border-radius: 4px;
}

.edit-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #f28c00;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.profile-details {
  flex: 1;
}

.profile-name {
  font-weight: bold;
  margin-bottom: 20px;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.detail-item {
  display: flex;
  margin-bottom: 10px;
}

.detail-label {
  font-weight: bold;
  margin-right: 8px;
  width: 120px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.edit-button {
  background-color: #ce720f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.password-button {
  background-color: #ce720f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.location-section {
  display: flex;
  align-items: center;
}

.map-icon {
  width: 120px;
  height: 120px;
  margin-right: 30px;
}

.location-details {
  flex: 1;
}

.location-name {
  font-weight: bold;
  display: flex;
  align-items: center;
}

.location-edit-icon {
  margin-left: 15px;
  background-color: #f28c00;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.location-delete-icon {
  margin-left: 10px;
  background-color: #fff;
  border: 1px solid #ccc;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.location-add-button {
  background-color: #f28c00;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 15px;
  font-size: 12px;
  cursor: pointer;
}
</style>