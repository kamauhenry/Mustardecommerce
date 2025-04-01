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
                    :src="product?.thumbnail || placeholderImage"
                    class="main-image"
                    alt="Main Product Image"
                  />
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
                  <input type="number" v-model="quantity" min="1" />
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
                      <input type="number" v-model="quantity" min="1" />
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
                  <input type="text" v-model="promoCode" placeholder="Enter promo code" />
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

            <!-- Add to Cart Button -->
            <div class="control">
              <button class="add-to-cart" @click="handleAddToCart">Add to Cart</button>
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
import { ref, computed, onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '../components/navigation/MainLayout.vue';

export default {
  name: 'ProductDetails',
  components: { MainLayout },
  props: {
    categorySlug: { type: String, required: true },
    productSlug: { type: String, required: true },
  },
  setup(props) {
    const store = useEcommerceStore();

    // Product data
    const productKey = computed(() => `${props.categorySlug}:${props.productSlug}`);
    const product = computed(() => store.productDetails[productKey.value]);

    // Form state
    const quantity = ref(1);
    const selectedSize = ref('');
    const selectedColor = ref('');
    const shippingMethod = ref('ship');
    const promoCode = ref('');

    // Tab state
    const activeTab = ref('Description');
    const tabs = ['Description', 'Gallery', 'Review', 'Order'];

    // Placeholder image
    const placeholderImage = 'data:image/jpeg;base64,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';

    // Computed properties for sizes and colors
    const availableSizes = computed(() => {
      return [...new Set(product.value?.variants?.map(variant => variant.size) || [])];
    });

    const availableColors = computed(() => {
      return [...new Set(product.value?.variants?.map(variant => variant.color) || [])];
    });

    // Compute selected variant ID
    const selectedVariantId = computed(() => {
      if (!product.value?.variants) return null;
      const variant = product.value.variants.find(
        v => v.size === selectedSize.value && v.color === selectedColor.value
      );
      return variant ? variant.id : null;
    });

    // Fetch product details and cart on mount
    onMounted(async () => {
      // Fetch product details if not already loaded
      if (!store.productDetails[productKey.value]) {
        await store.fetchProductDetails(props.categorySlug, props.productSlug);
      }
      // Fetch cart to initialize cartItemCount
      await store.fetchCurrentUserInfo();
      await store.fetchCart();
    });

    // Add to cart handler
    const handleAddToCart = async () => {
      try {
        if (!selectedSize.value || !selectedColor.value) {
          alert('Please select both size and color');
          return;
        }

        await store.addToCart(
          product.value.id,
          selectedVariantId.value,
          quantity.value
        );

        alert('Product added to cart successfully!');
      } catch (error) {
        console.error('Add to cart error:', error);
        if (error.message === 'Please log in to add items to cart') {
          // The store will handle showing the auth modal
        }
      }
    };

    return {
      product,
      quantity,
      selectedSize,
      selectedColor,
      shippingMethod,
      promoCode,
      availableSizes,
      availableColors,
      activeTab,
      tabs,
      placeholderImage,
      handleAddToCart,
      showAuthModal: computed(() => store.isAuthModalVisible),
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
  font-weight: 700;
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
  background-color: #f0f0f0;
}

.main-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
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
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.add-review:hover {
  box-shadow: 0 5px 5px rgba(46, 46, 46, 0.1);
  transform: translateY(1px);
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

.control {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.add-to-cart {
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
  box-shadow: 0 5px 5px rgba(46, 46, 46, 0.1);
  transform: translateY(1px);
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
