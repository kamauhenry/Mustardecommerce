<!-- AddDeliveryLocationPopup.vue -->
<template>
  <div class="popup-overlay">
    <div class="popup-content">
      <h2 class="popup-title">Please provide a delivery location</h2>

      <!-- Display Selected Location -->
      <div v-if="selectedLocation" class="location-details">
        <span class="location-name">{{ selectedLocation.name }}</span>
        <span class="location-address">{{ selectedLocation.address }}</span>
      </div>

      <!-- Google Map -->
      <div class="map-container">
        <div v-if="isLoading" class="map-loading">Loading map...</div>
        <GoogleMap
          v-else
          :api-key="googleMapsApiKey"
          style="width: 100%; height: 300px"
          :center="mapCenter"
          :zoom="15"
          :map-type-id="mapType"
          @click="handleMapClick"
        >
          <Marker :options="{ position: mapCenter, draggable: true }" @dragend="handleMarkerDrag" />
        </GoogleMap>
      </div>

      <!-- Set as Default Checkbox -->
      <div class="default-checkbox">
        <input type="checkbox" id="set-default" v-model="setAsDefault" />
        <label for="set-default" class="set-default-label">Set as default delivery location</label>
      </div>

      <!-- Actions -->
      <div class="popup-actions">
        <button class="cancel-button" @click="$emit('close')">Cancel</button>
        <button class="add-button" @click="addLocation" :disabled="!selectedLocation">
          Add Location
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { GoogleMap, Marker } from 'vue3-google-map';
import axios from 'axios';
import Toast from 'vue-toast-notification';

const googleMapsApiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const emit = defineEmits(['add-location', 'close']);
const selectedLocation = ref('');
const setAsDefault = ref(false);
const mapType = ref('roadmap');
const mapCenter = ref({ lat: -1.286389, lng: 36.817223 });

async function fetchPlaceName(lat, lng) {
  try {
    const response = await axios.get(
      `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${googleMapsApiKey}`
    );
    const results = response.data.results;
    return results.length > 0 ? results[0].formatted_address : 'Unknown Location';
  } catch (error) {
    Toast.open({
      message: `Error fetching place name: ${error.message || 'Unknown error'}`,
      type: 'error',
    });
    return 'Unknown Location';
  }
}

const handleMapClick = async (event) => {
  const newCenter = {
    lat: event.latLng.lat(),
    lng: event.latLng.lng(),
  };
  mapCenter.value = newCenter;

  try {
    const response = await axios.get(
      `https://maps.googleapis.com/maps/api/geocode/json?latlng=${newCenter.lat},${newCenter.lng}&key=${googleMapsApiKey}`
    );
    const results = response.data.results;
    let addressName = 'Unknown Location';

    if (results && results.length > 0) {
      const addressComponents = results[0].address_components;
      // Attempt to find a suitable name (e.g., neighborhood, route, locality)
      const neighborhood = addressComponents.find(component => component.types.includes('neighborhood'));
      const route = addressComponents.find(component => component.types.includes('route'));
      const locality = addressComponents.find(component => component.types.includes('locality'));

      if (neighborhood) {
        addressName = neighborhood.long_name;
      } else if (route) {
        addressName = route.long_name;
      } else if (locality) {
        addressName = locality.long_name;
      } else {
        addressName = results[0].formatted_address; // Fallback to formatted address
      }
    }

    const address = await fetchPlaceName(newCenter.lat, newCenter.lng);
    selectedLocation.value = {
      id: `${newCenter.lat}-${newCenter.lng}`,
      name: addressName,
      address,
      lat: newCenter.lat,
      lng: newCenter.lng,
    };
  } catch (error) {
    console.error('Error geocoding:', error);
    
    // Handle error appropriately, perhaps show a default name
    selectedLocation.value = {
      id: `${newCenter.lat}-${newCenter.lng}`,
      name: 'Unknown Location',
      address: 'Unknown Address',
      lat: newCenter.lat,
      lng: newCenter.lng,
    };
  }
};

const handleMarkerDrag = async (event) => {
  const newCenter = {
    lat: event.latLng.lat(),
    lng: event.latLng.lng(),
  };
  mapCenter.value = newCenter;

  try {
    const response = await axios.get(
      `https://maps.googleapis.com/maps/api/geocode/json?latlng=${newCenter.lat},${newCenter.lng}&key=${googleMapsApiKey}`
    );
    const results = response.data.results;
    let addressName = 'Unknown Location';

    if (results && results.length > 0) {
      const addressComponents = results[0].address_components;
      // Attempt to find a suitable name (e.g., neighborhood, route, locality)
      const neighborhood = addressComponents.find(component => component.types.includes('neighborhood'));
      const route = addressComponents.find(component => component.types.includes('route'));
      const locality = addressComponents.find(component => component.types.includes('locality'));

      if (neighborhood) {
        addressName = neighborhood.long_name;
      } else if (route) {
        addressName = route.long_name;
      } else if (locality) {
        addressName = locality.long_name;
      } else {
        addressName = results[0].formatted_address; // Fallback to formatted address
      }
    }
    selectedLocation.value = {
      ...selectedLocation.value,
      name: addressName,
      lat: newCenter.lat,
      lng: newCenter.lng,
    };
    const address = await fetchPlaceName(newCenter.lat, newCenter.lng);
    selectedLocation.value.address = address;
  } catch (error) {
    console.error('Error geocoding:', error);
    // Handle error appropriately, perhaps show a default name
    selectedLocation.value = {
      ...selectedLocation.value,
      name: 'Unknown Location',
      address: 'Unknown Address',
      lat: newCenter.lat,
      lng: newCenter.lng,
    };
  }
};

const addLocation = () => {
  emit('add-location', {
    id: selectedLocation.value.id,
    name: selectedLocation.value.name,
    address: selectedLocation.value.address,
    isDefault: setAsDefault.value,
  });
};
</script>


<style scoped>
.popup-overlay {
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

.popup-content {
  padding: 1.5rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.popup-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.location-name, .location-address {
  display: block;
}

.location-select {
  margin-bottom: 1rem;
}

.label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: #666;
  margin-bottom: 0.25rem;
}

.select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.map-container {
  position: relative;
  margin-bottom: 1rem;
}

.default-checkbox {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-start;
  align-items: baseline;
  gap: 0.5rem;
}

.default-checkbox input {
  cursor: pointer;
  display: inline;
  width: fit-content;
}

.default-checkbox label {
  font-size: 0.9rem;
  display: inline;
}

.popup-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.cancel-button,
.add-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.cancel-button {
  background: #f5f5f5;
  color: #333;
}

.add-button {
  background: #f28c38;
  color: white;
}

.add-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.add-button:hover:not(:disabled) {
  background: #e07b30;
}
</style>
