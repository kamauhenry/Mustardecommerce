<template>
  <div class="popup-overlay">
    <div class="popup-content">
      <h2 class="popup-title">Please provide a delivery location</h2>

      <!-- Search Bar -->
      <div class="search-container">
        <input
          type="text"
          v-model="searchQuery"
          @input="debouncedFetchSuggestions"
          @keydown="handleKeydown"
          placeholder="Search for a location..."
          class="search-input"
        />
        <ul v-if="suggestions.length > 0" class="suggestions-dropdown">
          <li
            v-for="(suggestion, index) in suggestions"
            :key="suggestion.place_id"
            @click="selectSuggestion(suggestion)"
            :class="{ 'highlighted': index === highlightedIndex }"
            class="suggestion-item"
          >
            {{ suggestion.description }}
          </li>
        </ul>
      </div>

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
import { ref, getCurrentInstance } from 'vue';
import { GoogleMap, Marker } from 'vue3-google-map';
import axios from 'axios';
import { toast } from 'vue3-toastify';

const googleMapsApiKey = 'AIzaSyAmhYzyxBYyvs0sFbVVbXCnEdTbEgO1Tz8';
const emit = defineEmits(['add-location', 'close']);
const selectedLocation = ref(null);
const setAsDefault = ref(false);
const mapType = ref('roadmap');
const mapCenter = ref({ lat: -1.286389, lng: 36.817223 });
const searchQuery = ref('');
const suggestions = ref([]);
const highlightedIndex = ref(-1);
const isLoading = ref(false);

// Get toast instance
const instance = getCurrentInstance();
Properties.$toast;

// Debounce function
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

async function fetchPlaceName(lat, lng) {
  try {
    const response = await axios.get(
      `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${googleMapsApiKey}`
    );
    const results = response.data.results;
    return results.length > 0 ? results[0].formatted_address : 'Unknown Location';
  } catch (error) {
    console.error('Error fetching place name:', error);
    toast.error(`Error fetching place name: ${error.message || 'Unknown error'}`);
    return 'Unknown Location';
  }
}

const fetchSuggestions = async () => {
  if (!searchQuery.value) {
    suggestions.value = [];
    return;
  }

  try {
    const response = await axios.get(
      `http://localhost:8000/api/autocomplete/?input=${encodeURIComponent(searchQuery.value)}`
    );
    if (response.data.status !== 'OK') {
      throw new Error(response.data.error_message || 'API request failed');
    }
    suggestions.value = response.data.predictions;
    highlightedIndex.value = -1;
  } catch (error) {
    console.error('Error fetching suggestions:', error);
    toast.error(`Error fetching suggestions: ${error.message}`);
    suggestions.value = [];
  }
};

const debouncedFetchSuggestions = debounce(fetchSuggestions, 300);

const selectSuggestion = async (suggestion) => {
  try {
    const response = await axios.get(
      `http://localhost:8000/api/place-details/?place_id=${suggestion.place_id}`
    );
    if (response.data.status !== 'OK') {
      throw new Error(response.data.error_message || 'Place details request failed');
    }
    const result = response.data.result;
    const { lat, lng } = result.geometry.location;

    mapCenter.value = { lat, lng };
    const address = await fetchPlaceName(lat, lng);
    selectedLocation.value = {
      id: suggestion.place_id,
      name: suggestion.structured_formatting.main_text || result.name,
      address,
      latitude: lat,  // Changed from lat to latitude to match backend
      longitude: lng,  // Changed from lng to longitude to match backend
    };
    suggestions.value = [];
    searchQuery.value = '';
  } catch (error) {
    console.error('Error fetching place details:', error);
    toast.error(`Error selecting location: ${error.message}`);
  }
};

const handleKeydown = (event) => {
  if (!suggestions.value.length) return;

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault();
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, suggestions.value.length - 1);
      break;
    case 'ArrowUp':
      event.preventDefault();
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1);
      break;
    case 'Enter':
      event.preventDefault();
      if (highlightedIndex.value >= 0) {
        selectSuggestion(suggestions.value[highlightedIndex.value]);
      }
      break;
  }
};

const handleMapClick = async (event) => {
  const newCenter = {
    lat: event.latLng.lat(),
    lng: event.latLng.lng(),
  };
  mapCenter.value = newCenter;

  try {
    const address = await fetchPlaceName(newCenter.lat, newCenter.lng);
    selectedLocation.value = {
      id: `${newCenter.lat}-${newCenter.lng}`,
      name: address.split(',')[0],
      address,
      latitude: newCenter.lat,
      longitude: newCenter.lng,
    };
  } catch (error) {
    console.error('Error geocoding:', error);
    selectedLocation.value = {
      id: `${newCenter.lat}-${newCenter.lng}`,
      name: 'Unknown Location',
      address: 'Unknown Address',
      latitude: newCenter.lat,
      longitude: newCenter.lng,
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
    const address = await fetchPlaceName(newCenter.lat, newCenter.lng);
    selectedLocation.value = {
      ...selectedLocation.value,
      name: address.split(',')[0],
      address,
      latitude: newCenter.lat,
      longitude: newCenter.lng,
    };
  } catch (error) {
    console.error('Error geocoding:', error);
    selectedLocation.value = {
      ...selectedLocation.value,
      name: 'Unknown Location',
      address: 'Unknown Address',
      latitude: newCenter.lat,
      longitude: newCenter.lng,
    };
  }
};

const addLocation = () => {
  emit('add-location', {
    name: selectedLocation.value.name,
    address: selectedLocation.value.address,
    latitude: selectedLocation.value.latitude,
    longitude: selectedLocation.value.longitude,
    isDefault: setAsDefault.value,
  });
};
</script>

<style scoped>
/* Same styles as before */
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

.search-container {
  position: relative;
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1001;
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  padding: 0.5rem;
  cursor: pointer;
}

.suggestion-item:hover,
.suggestion-item.highlighted {
  background: #f5f5f5;
}

.location-name,
.location-address {
  display: block;
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
