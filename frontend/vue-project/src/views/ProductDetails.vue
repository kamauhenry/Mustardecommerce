<template>
  <MainLayout>
    <div class="product-details-container">
      <!-- Breadcrumb Navigation -->
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> &gt;
        <router-link :to="`/category/${categorySlug}`">{{ categorySlug|| 'Category' }}</router-link> &gt;
        <span>{{ product?.name || 'Product' }}</span>
      </div>

      <!-- Product Title -->
      <h1 class="product-title">{{ product?.name || 'Loading...' }}</h1>

      <!-- Social Sharing Icons -->
      <div class="social-share">
        <span>Share to:</span>
        <a href="#"><img src="" alt="Camera" /></a>
        <a href="#"><img src="" alt="Facebook" /></a>
        <a href="#"><img src="" alt="Twitter" /></a>
        <a href="#"><img src="" alt="Share" /></a>
      </div>

      <div class="product-content">
        <!-- Product Images -->
        <div class="product-images">
          <img
            v-if="product?.thumbnail"
            :src="product.thumbnail"
            :alt="product.name"
            class="main-image"
          />
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

        <!-- Product Details -->
        <div class="product-info">
          <!-- Pricing -->
          <div class="pricing">
            <h2 class="price">KES {{ product?.price || '0' }}</h2>
            <p class="moq-info">Below MOQ price: KES {{ product?.price || '0' }}</p>
        
            <p class="moq-info">Below MOQ price: KES {{ product?.price || '0' }}</p>
            <p class="moq-info">MOQ Per Person: {{ product?.moq || 'N/A' }} items/bundle</p>
          </div>

          <!-- Order Details -->
          <div class="order-details">
            <div class="quantity">
              <label>Total Quantity</label>
              <input type="number" id="quatity" v-model="quantity" min="1" />
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
                  <input type="number"id="qantity"  v-model="quantity" min="1" />
                </div>
              </div>
            </div>

            <!-- Shipping Method -->
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

            <!-- Promo Code -->
            <div class="promo-code">
              <label>Promo Code</label>
              <input type="text" id="promCode" v-model="promoCode" placeholder="Enter promo code" />
            </div>

            <!-- Add to Cart Button -->
            <div class="control">
              <button class="add-to-cart" @click="handleAddToCart">Add to cart</button>
            </div>
          </div>

          <!-- Rating -->
          <div class="rating">
            <span>Rating</span>
            <span class="stars">★★★★★</span>
            <span>({{ product?.rating || 0 }})</span>
          </div>
        </div>
      </div>

      <!-- Customer Reviews -->
      <div class="reviews">
        <h3>Customer Reviews</h3>
        <button class="add-review">Add Review</button>
      </div>
    </div>
    
    <!-- Auth Modals Component -->
    <AuthModals :autoShowLogin="showAuthModal" />
  </MainLayout>
</template>


<script>
import { onMounted, computed, ref } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '../components/navigation/MainLayout.vue';
import AuthModals from '@/components/auth/AuthModals.vue';

export default {
  name: "productDetails",
  props: { categorySlug: String, productSlug: String },
  components: {
    MainLayout,
    AuthModals
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
      showAuthModal: computed(() => store.isAuthModalVisible)
    };
  },
};
</script>

<style scoped>
/* Styles remain the same as in your original code */
.product-details-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Breadcrumb styling */
.breadcrumb {
  font-size: 14px;
  margin-bottom: 10px;
}

.breadcrumb a {
  color: #5E5500;
  text-decoration: none;
}

.breadcrumb a:hover {
  color: #5E5500;
  text-decoration: none;
}

.breadcrumb a:visited {
  color: #5E5500;
  text-decoration: none;
}

.breadcrumb a:active,
.breadcrumb a:focus {
  color: #5E5500;
  text-decoration: none;
}

.breadcrumb span {
  color: #5E5500;
}

.product-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.social-share {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.social-share img {
  width: 20px;
  height: 20px;
}

.product-content {
  display: flex;
  gap: 30px;
}

.product-images {
  flex: 1;
}

.main-image {
  width: 100%;
  max-width: 400px;
  height: auto;
  margin-bottom: 10px;
}

.thumbnails {
  display: flex;
  gap: 10px;
}

.thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
}

.product-info {
  flex: 1;
}

.pricing {
  margin-bottom: 20px;
}

.price {
  font-size: 24px;
  font-weight: bold;
  color: #000;
}

.moq-info {
  font-size: 14px;
  color: #666;
}

.order-details {
  margin-bottom: 20px;
}

.quantity {
  margin-bottom: 10px;
}

.quantity input {
  width: 60px;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.attributes {
  margin-bottom: 10px;
}

.attribute-row {
  display: flex;
  gap: 10px;
}

.attribute {
  flex: 1;
}

.attribute label {
  display: block;
  font-size: 14px;
  margin-bottom: 5px;
}

.attribute select,
.attribute input {
  width: 100%;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.shipping {
  margin-bottom: 10px;
}

.shipping-option {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.promo-code {
  margin-bottom: 20px;
}

.promo-code input {
  width: 100%;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.add-to-cart {
  background-color: #d4a017;
  color: #fff;
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 16px;
}

.add-to-cart:hover {
  background-color: #b88c14;
}

.rating {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.stars {
  color: #ccc;
}

.reviews {
  margin-top: 30px;
}

.add-review {
  background-color: #d4a017;
  color: #fff;
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.add-review:hover {
  background-color: #b88c14;
}
</style>