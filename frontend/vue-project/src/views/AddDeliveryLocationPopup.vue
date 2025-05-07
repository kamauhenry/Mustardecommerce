<template>
  <div class="popup-overlay">
    <div class="popup-content">
      <h3>Add New Delivery Location</h3>
      <form @submit.prevent="submitLocation">
        <div class="form-group">
          <label for="name">Location Name</label>
          <input
            type="text"
            id="name"
            v-model="locationForm.name"
            required
            placeholder="e.g., Home, Office"
            :disabled="isSubmitting"
          />
        </div>
        <div class="form-group">
          <label for="address">Address</label>
          <div class="input-wrapper">
            <input
              type="text"
              id="address"
              v-model="locationForm.address"
              ref="addressInput"
              required
              placeholder="Start typing to search..."
              :disabled="isSubmitting || isLoadingSuggestions"
              @input="fetchSuggestions"
            />
            <span v-if="isLoadingSuggestions" class="loading-spinner"></span>
          </div>
          <ul v-if="suggestions && suggestions.length" class="suggestions-list">
            <li
              v-for="suggestion in suggestions"
              :key="suggestion.place_id"
              @click="selectSuggestion(suggestion)"
            >
              {{ suggestion.description }}
            </li>
          </ul>
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" v-model="locationForm.is_default" :disabled="isSubmitting" />
            Set as Default
          </label>
        </div>
        <div class="form-actions">
          <button type="submit" class="save-btn" :disabled="isSubmitting">
            {{ isSubmitting ? 'Saving...' : 'Save' }}
          </button>
          <button type="button" class="cancel-btn" @click="close" :disabled="isSubmitting">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { toast } from 'vue3-toastify';
import axios from 'axios';

const emit = defineEmits(['add-location', 'close']);

const locationForm = ref({
  name: '',
  address: '',
  latitude: null,
  longitude: null,
  is_default: false,
});
const suggestions = ref([]);
const isSubmitting = ref(false);
const isLoadingSuggestions = ref(false);
const addressInput = ref(null);

console.log('AddDeliveryLocationPopup mounted, suggestions:', suggestions.value);

const fetchSuggestions = async () => {
  const query = locationForm.value.address;
  if (!query) {
    suggestions.value = [];
    console.log('fetchSuggestions: Empty query, cleared suggestions');
    return;
  }
  isLoadingSuggestions.value = true;
  try {
    const response = await axios.get('/api/autocomplete/', { params: { input: query } });
    suggestions.value = response.data.predictions || [];
    console.log('fetchSuggestions: Suggestions updated', suggestions.value);
  } catch (error) {
    console.error('Error fetching suggestions:', error);
    const errorMessage = error.response?.data?.error || 'Failed to load address suggestions';
    toast.error(errorMessage);
    suggestions.value = [];
  } finally {
    isLoadingSuggestions.value = false;
  }
};

const selectSuggestion = async (suggestion) => {
  try {
    const response = await axios.get('/api/place_details/', {
      params: { place_id: suggestion.place_id },
    });
    const result = response.data.result;
    locationForm.value.address = result.formatted_address;
    locationForm.value.latitude = result.geometry.location.lat;
    locationForm.value.longitude = result.geometry.location.lng;
    suggestions.value = [];
    console.log('selectSuggestion: Address selected', locationForm.value);
  } catch (error) {
    console.error('Error fetching place details:', error);
    const errorMessage = error.response?.data?.error || 'Failed to load address details';
    toast.error(errorMessage);
  }
};

const submitLocation = async () => {
  if (!locationForm.value.latitude || !locationForm.value.longitude) {
    toast.error('Please select a valid address from suggestions');
    return;
  }
  isSubmitting.value = true;
  try {
    await emit('add-location', { ...locationForm.value });
    console.log('submitLocation: Location emitted', locationForm.value);
  } catch (error) {
    toast.error('Failed to add location');
    console.error('submitLocation error:', error);
  } finally {
    isSubmitting.value = false;
  }
};

const close = () => {
  emit('close');
  console.log('close: Popup closed');
};

onMounted(() => {
  console.log('AddDeliveryLocationPopup onMounted, suggestions:', suggestions.value);
});
</script>

<style scoped>
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  overflow: auto;
}

.popup-content {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  position: relative;
  margin: 1rem auto;
}

h3 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  color:#D4A017;
  text-align: center;
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

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.form-group input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.input-wrapper {
  position: relative;
}

.loading-spinner {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  border: 2px solid#D4A017;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: translateY(-50%) rotate(360deg); }
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  max-height: 150px;
  overflow-y: auto;
  background: white;
  position: absolute;
  width: 100%;
  z-index: 2100;
}

.suggestions-list li {
  padding: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.suggestions-list li:hover {
  background: #f9f9f9;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.save-btn,
.cancel-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  min-height: 2.75rem;
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

@media (max-width: 320px) {
  .popup-content {
    padding: 1rem;
    margin: 0.5rem;
  }

  h3 {
    font-size: 1.1rem;
  }

  .form-group label,
  .form-group input,
  .suggestions-list li {
    font-size: 0.85rem;
  }

  .save-btn,
  .cancel-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
    min-height: 2.5rem;
  }

  .loading-spinner {
    width: 14px;
    height: 14px;
  }
}
</style>