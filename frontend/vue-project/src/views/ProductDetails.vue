<template>
  <MainLayout>
    <div class="product-details-container">
      <!-- Breadcrumb Navigation -->
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> /
        <router-link :to="`/category/${categorySlug}/products`">{{ categorySlug || 'Category' }}</router-link> /
        <span>{{ product?.name || 'Product' }}</span>
      </div>

      <!-- Product Title -->
      <h1 class="product-title">{{ product?.name || 'Loading...' }}</h1>

      <!-- Product Content -->
      <div class="product-content">
        <!-- Left Section: Tabs and Images -->
        <div class="product-left">
          <!-- Tabs -->
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

          <!-- Tab Content -->
          <div class="tab-content">
            <!-- Description Tab -->
            <div v-if="activeTab === 'Description'" class="description">
              <h3>Design and Materials</h3>
              <p>{{ product?.description || 'No description available.' }}</p>
              <ul>
                <li><strong>Material:</strong> {{ product?.material || 'N/A' }}</li>
                <li><strong>Fit:</strong> {{ product?.fit || 'N/A' }}</li>
                <li><strong>Product Code:</strong> {{ product?.code || 'N/A' }}</li>
              </ul>
            </div>

            <!-- Gallery Tab -->
            <div v-if="activeTab === 'Gallery'" class="gallery">
              <div class="product-images">
                <div class="main-image-container">
                  <img
                    v-if="product?.thumbnail"
                    :src="product.thumbnail"
                    class="main-image"
                    alt="Main Product Image"
                  />
                  <div v-else class="no-image"></div>
                </div>
                <div class="thumbnails">
                  <img
                    v-for="(image, index) in product?.images || []"
                    :key="index"
                    :src="image"
                    :alt="`Thumbnail ${index + 1}`"
                    class="thumbnail"
                  />
                </div>
              </div>
            </div>

            <!-- Review Tab -->
            <div v-if="activeTab === 'Review'" class="reviews">
              <h3>Customer Reviews</h3>
              <button class="add-review">Add Review</button>
              <p>No reviews yet. Be the first to review this product!</p>
            </div>

            <!-- Order Tab -->
            <div v-if="activeTab === 'Order'" class="order-tab">
              <div class="order-details">
                <div class="quantity">
                  <label>Total Quantity</label>
                  <input type="number" id="quantity" v-model="quantity" min="1" />
                </div>

                <div class="attributes">
                  <label>Order Attributes</label>
                  <div class="attribute-row">
                    <div class="attribute">
                      <label>Size/Patterns</label>
                      <select v-model="selectedSize">
                        <option disabled value="">Select Size</option>
                        <option v-for="size in availableSizes" :key="size" :value="size">
                          {{ size }}
                        </option>
                      </select>
                    </div>
                    <div class="attribute">
                      <label>Color</label>
                      <select v-model="selectedColor">
                        <option disabled value="">Select Color</option>
                        <option v-for="color in availableColors" :key="color" :value="color">
                          {{ color }}
                        </option>
                      </select>
                    </div>
                    <div class="attribute">
                      <label>Quantity</label>
                      <input type="number" id="attribute-quantity" v-model="quantity" min="1" />
                    </div>
                  </div>
                </div>

                <div class="shipping">
                  <label>Shipping Method</label>
                  <div class="shipping-option">
                    <input type="radio" id="ship" name="shipping" value="ship" v-model="shippingMethod" />
                    <label for="ship">Ship Approximation cost KES 310 each</label>
                  </div>
                  <div class="shipping-option">
                    <input type="radio" id="air" name="shipping" value="air" v-model="shippingMethod" />
                    <label for="air">Air Approximation cost</label>
                  </div>
                </div>

                <div class="promo-code">
                  <label>Promo Code</label>
                  <input type="text" id="promoCode" v-model="promoCode" placeholder="Enter promo code" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Section: Product Info -->
        <div class="product-right">
          <div class="product-info">
            <!-- Pricing -->
            <div class="pricing">
              <h2 class="price">KES {{ product?.price || '0' }}</h2>
              <p class="moq-info">Below MOQ price: KES {{ product?.below_moq_price || product?.price || '0' }}</p>
              <p class="moq-info">MOQ Per Person: {{ product?.moq || 'N/A' }} items/bundle</p>
            </div>

            <!-- Size and Color Selection -->
            <!-- <div class="attributes">
              <div class="attribute">
                <label>Size</label>
                <select v-model="selectedSize">
                  <option disabled value="">Select Size</option>
                  <option v-for="size in availableSizes" :key="size" :value="size">
                    {{ size }}
                  </option>
                </select>
              </div>
              <div class="attribute">
                <label>Color</label>
                <div class="color-options">
                  <span
                    v-for="color in availableColors"
                    :key="color"
                    :style="{ backgroundColor: color.toLowerCase() }"
                    :class="{ selected: selectedColor === color }"
                    @click="selectedColor = color"
                  ></span>
                </div>
              </div>
            </div> -->

            <!-- Add to Cart Button -->
            <div class="control">
              <button class="add-to-cart" @click="handleAddToCart">Add to Cart</button>
              <!-- <button class="guaranteed">100% Guaranteed Original</button> -->
            </div>

            <!-- Rating -->
            <div class="rating">
              <span class="stars">★★★★★</span>
              <span>({{ product?.rating || 0 }})</span>
            </div>
          </div>
        </div>
      </div>

      <!-- You May Also Like -->
      <div class="related-products">
        <h3>You May Also Like</h3>
        <p>Explore similar products...</p>
        <router-link :to="`/category/${categorySlug}/products`" class="show-more">Show More</router-link>
      </div>
    </div>
  </MainLayout>
</template>


<script>
import { onMounted, computed, ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '../components/navigation/MainLayout.vue';

export default {
  name: "productDetails",
  props: { categorySlug: String, productSlug: String },
  components: {
    MainLayout,
  },
  setup(props) {
    const store = useEcommerceStore();
    const productKey = computed(() => `${props.categorySlug}:${props.productSlug}`);
    const product = computed(() => store.productDetails[productKey.value]);

    // Reactive state for form inputs
    const quantity = ref(1);
    const selectedSize = ref('');
    const selectedColor = ref('');
    const shippingMethod = ref('ship');
    const promoCode = ref('');

    // Tab state
    const activeTab = ref('Description');
    const tabs = ['Description', 'Gallery', 'Review', 'Order'];

    // Computed properties for sizes and colors from variants
    const availableSizes = computed(() => {
      return [...new Set(product.value?.variants?.map(variant => variant.size) || [])];
    });

    const availableColors = computed(() => {
      return [...new Set(product.value?.variants?.map(variant => variant.color) || [])];
    });

    onMounted(() => {
      if (!store.productDetails[productKey.value]) {
        store.fetchProductDetails(props.categorySlug, props.productSlug);
      }
    });

    const selectedVariantId = computed(() => {
      if (!product.value?.variants) return null;
      const variant = product.value.variants.find(
        v => v.size === selectedSize.value && v.color === selectedColor.value
      );
      return variant ? variant.id : null;
    });

    const handleAddToCart = async () => {
      try {
        // Validate size and color selection
        if (!selectedSize.value || !selectedColor.value) {
          alert('Please select both size and color');
          return;
        }

        // Add to cart will handle authentication checks
        await store.addToCart(
          product.value.id,
          selectedVariantId.value,
          quantity.value
        );

        alert('Product added to cart successfully!');
      } catch (error) {
        console.error('Add to cart error:', error);

        // The store will handle showing the auth modal if needed
        if (error.message === 'Please log in to add items to cart') {
          // Optional: you can add additional user feedback here
        }
      }
    };

    return {
      store,
      product,
      quantity,
      selectedSize,
      selectedColor,
      availableSizes,
      availableColors,
      selectedVariantId,
      shippingMethod,
      promoCode,
      handleAddToCart,
      activeTab,
      tabs,
      showAuthModal: computed(() => store.isAuthModalVisible)
    };
  },
};
</script>

<style scoped>
.product-details-container {
  margin: 0 auto;
  padding: 20px;
  font-family: 'Roboto', sans-serif;
}

/* Breadcrumb */
.breadcrumb {
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.breadcrumb a {
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

/* Product Title */
.product-title {
  font-size: 1.5rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 20px;
}

/* Product Content */
.product-content {
  display: flex;
  gap: 30px;
}

/* Left Section */
.product-left {
  flex: 2;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.tabs button {
  background: none;
  border: none;
  padding: 10px 0;
  font-size: 1rem;
  font-weight: 500;
  text-transform: uppercase;
  cursor: pointer;
  position: relative;
}

.tabs button.active {
  font-weight: 700;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 2px;
}

/* Tab Content */
.tab-content {
  margin-bottom: 30px;
}

.description h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.description p {
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 15px;
}

.description ul {
  list-style: none;
  padding: 0;
}

.description ul li {
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.description ul li strong {
  font-weight: 700;;
}

/* Gallery */
.product-images {
  position: relative;
  padding-top: 75%; /* 4:3 aspect ratio */
}

.main-image-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0; /* Grey background if no image */
}

.main-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-image {
  width: 100%;
  height: 100%;
  background-color: #f0f0f0;
}

.thumbnails {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 10px;
}

.thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.thumbnail:hover {
  border-color: #333;
}

/* Reviews */
.reviews h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.add-review {
  background-color: #333;
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.add-review:hover {
  background-color: #555;
}

.reviews p {
  font-size: 0.9rem;
  color: #666;
}

/* Order Tab */
.order-details {
  margin-bottom: 20px;
}

.quantity {
  margin-bottom: 15px;
}

.quantity label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 5px;
}

.quantity input {
  width: 80px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.attributes {
  margin-bottom: 15px;
}

.attributes label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 5px;
}

.attribute-row {
  display: flex;
  gap: 15px;
}

.attribute {
  flex: 1;
}

.attribute label {
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.attribute select,
.attribute input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.shipping {
  margin-bottom: 15px;
}

.shipping label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 5px;
}

.shipping-option {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.shipping-option label {
  font-size: 0.9rem;
}

.promo-code {
  margin-bottom: 15px;
}

.promo-code label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 5px;
}

.promo-code input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* Right Section */
.product-right {
  display: flex;
  flex: 1;
  height: fit-content;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 5px 5px rgba(46, 46, 46, 0.1);
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pricing {
  margin-bottom: 20px;
}

.price {
  font-size: 1.8rem;
  font-weight: 700;
}

.moq-info {
  font-size: 0.9rem;
  margin-top: 5px;
}

.attributes .attribute {
  margin-bottom: 15px;
}

.attributes label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 5px;
}

.attributes select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.color-options {
  display: flex;
  gap: 10px;
}

.color-options span {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1px solid #ddd;
  cursor: pointer;
}

.color-options span.selected {
  border: 2px solid #333;
}

.control {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.add-to-cart {
  background-color: #333;
  color: #fff;
  padding: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  text-transform: uppercase;
  width: 100%;
}

.add-to-cart:hover {
  background-color: #555;
}

.guaranteed {
  /* background-color: #fff; */
  color: #333;
  padding: 12px;
  /* border: 1px solid #333; */
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  text-transform: uppercase;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.guaranteed::before {
  content: '✔';
  font-size: 1rem;
}

.rating {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stars {
  color: #f5c518;
  font-size: 1rem;
}

.rating span {
  font-size: 0.9rem;
  color: #666;
}

/* Related Products */
.related-products {
  margin-top: 40px;
  padding-top: 1rem;
}

.related-products h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.related-products p {
  font-size: 0.9rem;
  /* color: #666; */
  margin-bottom: 15px;
}

.show-more {
  font-weight: 600;
  color: #fff;
  padding: 10px;
  border-radius: 10px;
  text-transform: uppercase;
  text-decoration: none;
  margin-top: 0.5rem;
}

.show-more:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Responsiveness */
@media (max-width: 768px) {
  .product-content {
    flex-direction: column;
  }

  .product-left,
  .product-right {
    flex: none;
    width: 100%;
  }

  .product-right {
    padding: 15px;
  }

  .product-title {
    font-size: 2rem;
  }

  .tabs {
    gap: 10px;
  }

  .tabs button {
    font-size: 0.9rem;
  }

  .attribute-row {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
