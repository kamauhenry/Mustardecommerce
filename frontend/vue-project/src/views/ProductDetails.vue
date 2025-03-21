<template>
  <MainLayout>
    <div class="product-details-page">
      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> >
        <router-link :to="`/category/${categorySlug}/products`">{{ category?.name || 'Category' }}</router-link> >
        <span>{{ product?.name || 'Product' }}</span>
      </div>

      <!-- Main Product Section -->
      <div class="product-main">
        <!-- Product Images -->
        <div class="product-images">
          <h2 class="about-h2 product-h2">{{ product?.name || 'Product' }}</h2>
          <div class="share-section">
            <p class="share-product-p">Share to:</p>
            <div class="share-icons">
              <a href="#" class="share-icon"><i class="fab fa-facebook-f"></i></a>
              <a href="#" class="share-icon"><i class="fab fa-twitter"></i></a>
              <a href="#" class="share-icon"><i class="fab fa-whatsapp"></i></a>
              <a href="#" class="share-icon"><i class="fas fa-envelope"></i></a>
              <a href="#" class="share-icon"><i class="fas fa-link"></i></a>
            </div>
          </div>

          <div class="thumbnail-gallery">
            <img
              v-for="(image, index) in productImages"
              :key="index"
              :src="image || placeholder"
              :alt="`Thumbnail ${index + 1}`"
              @click="selectedImage = image"
              :class="{ active: selectedImage === image }"
            />
          </div>
        </div>

        <!-- Product Details -->
        <div class="product-info">
          <!-- Price, MOQ Info, and Rating -->
          <div class="price-section">
            <div class="price-moq">
              <span class="price">KES {{ product?.price || '0' }}</span>
              <div class="moq-info">
                <p>Below MOQ price: KES {{ product?.price || '0' }}</p>
                <p>Supplier MOQ: {{ product?.moq || '0' }} items</p>
                <p>Group buy order so far: 34</p>
                <p>MOQ Per Person: 1 items / bundle</p>
                <p>MOQ Number: 2R1Y1</p>
                <p>MOQ Status: <span class="status-active">{{ product?.moq_status || 'N/A' }}</span></p>
              </div>
            </div>
            <div class="rating">
              <p class="rating-p">Rating</p>
              <div class="stars">
                <i v-for="n in 5" :key="n" :class="n <= 2 ? 'fas fa-star' : 'far fa-star'"></i>
              </div>
              <p class="rating-p">Pending by Supplier MOQ</p>
              <p class="rating-p">113 Sold</p>
            </div>
          </div>

          <!-- Tabs for Order, Description, and Reviews -->
          <div class="tabs">
            <button :class="{ active: activeTab === 'order' }" @click="activeTab = 'order'">
              Order
            </button>
            <button :class="{ active: activeTab === 'description' }" @click="activeTab = 'description'">
              Description
            </button>
            <button :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">
              Customer Reviews
            </button>
          </div>
          <div class="tab-content">
            <!-- Order Tab -->
            <div v-if="activeTab === 'order'" class="order-form">
              <div class="form-group">
                <label>Total Quantity</label>
                <input type="number" v-model="totalQuantity" min="1" />
              </div>
              <div class="form-group">
                <label>Order Attributes</label>
                <div class="attributes">
                  <div class="attribute">
                    <label>Color</label>
                    <select v-model="selectedColor">
                      <option value="">Select Color</option>
                      <option v-for="color in product?.colors || []" :key="color" :value="color">
                        {{ color }}
                      </option>
                    </select>
                    <input type="number" v-model="colorQuantity" placeholder="0" min="0" />
                    <button @click="addAttribute">+</button>
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label>Shipping Method</label>
                <div class="shipping-options">
                  <label>
                    <input type="radio" v-model="shippingMethod" value="sea" />
                    <span>Sea approximate cost KES 199</span>
                  </label>
                  <label>
                    <input type="radio" v-model="shippingMethod" value="air" />
                    <span>Air approximate cost KES 600</span>
                  </label>
                </div>
              </div>
              <div class="form-group">
                <label>Promo Code</label>
                <input type="text" v-model="promoCode" placeholder="e.g 1CGTPB38" />
              </div>
              <div class="action-buttons">
                <button class="view-summary" @click="showSummary = true">View Summary</button>
                <button class="add-to-cart">Add to Cart</button>
              </div>
            </div>

            <!-- Description Tab -->
            <div v-if="activeTab === 'description'">
              <p class="product-description-p">{{ product?.description || 'No description available.' }}</p>
            </div>

            <!-- Reviews Tab -->
            <div v-if="activeTab === 'reviews'">
              <p class="reviews-p">No customer reviews yet.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- View Summary Popup -->
      <div v-if="showSummary" class="summary-popup" @click="showSummary = false">
        <div class="summary-content" @click.stop>
          <h3>Order Summary</h3>
          <div class="summary-details">
            <p><strong>Product:</strong> {{ product?.name || 'N/A' }}</p>
            <p><strong>Total Quantity:</strong> {{ totalQuantity }}</p>
            <p v-if="selectedColor"><strong>Color:</strong> {{ selectedColor }} ({{ colorQuantity }} items)</p>
            <p><strong>Shipping Method:</strong> {{ shippingMethod === 'sea' ? 'Sea (KES 199)' : 'Air (KES 600)' }}</p>
            <p v-if="promoCode"><strong>Promo Code:</strong> {{ promoCode }}</p>
            <p v-else>No promo code applied.</p>
            <p><strong>Total Price:</strong> KES {{ totalQuantity * (product?.price || 0) + (shippingMethod === 'sea' ? 199 : 600) }}</p>
          </div>
        </div>
      </div>

      <!-- Recommended Products -->
      <div class="recommended-products">
        <h2>Recommended Products</h2>
        <div v-if="recommendedProducts.length > 0" class="products-grid">
          <router-link
            v-for="recProduct in recommendedProducts"
            :key="recProduct.id"
            :to="`/products/${categorySlug}/${recProduct.slug}`"
            class="product-card"
            @click="trackProductClick(recProduct)"
          >
            <img :src="recProduct.thumbnail || placeholder" :alt="recProduct.name" class="product-image" />
            <h3 class="product-name">{{ recProduct.name }}</h3>
            <p class="product-price">KES {{ recProduct.price }}</p>
            <p class="moq-info">Below MOQ Price: KES {{ recProduct.price }}</p>
            <p class="moq-info">MOQ: {{ recProduct.moq }} items</p>
            <p class="moq-status">{{ recProduct.moq_status }}</p>
            <div class="progress-bar">
              <div class="progress" :style="{ width: recProduct.progress || '0%' }"></div>
            </div>
            <p class="progress-text">{{ recProduct.progress || '0%' }} Orders</p>
          </router-link>
        </div>
        <div v-else class="no-products">
          No recommended products available.
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted, ref, computed } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';
import { trackProduct } from '@/utils/tracking';
import placeholder from '@/assets/images/grey.jpg';

export default {
  props: {
    categorySlug: String,
    productSlug: String,
  },
  components: {
    MainLayout,
  },
  setup(props) {
    const store = useEcommerceStore();
    const selectedImage = ref(null);
    const totalQuantity = ref(1);
    const selectedColor = ref('');
    const colorQuantity = ref(0);
    const shippingMethod = ref('sea');
    const promoCode = ref('');
    const activeTab = ref('order'); // Default to 'order' tab
    const showSummary = ref(false); // Control the visibility of the summary popup

    // Fetch product data on mount
    onMounted(() => {
      store.fetchCategoryProducts(props.categorySlug);
    });

    // Get the category and product
    const category = computed(() => {
      return store.categoryProducts[props.categorySlug]?.category;
    });

    const product = computed(() => {
      const products = store.categoryProducts[props.categorySlug]?.products || [];
      return products.find(p => p.slug === props.productSlug);
    });

    // Product images (mocked for now, replace with actual data)
    const productImages = computed(() => {
      return product.value?.images || [product.value?.thumbnail];
    });

    // Set the initial selected image
    selectedImage.value = productImages.value?.[0] || placeholder;

    // Recommended products (other products in the same category)
    const recommendedProducts = computed(() => {
      const products = store.categoryProducts[props.categorySlug]?.products || [];
      return products
        .filter(p => p.slug !== props.productSlug) // Exclude the current product
        .map(p => ({
          ...p,
          progress: '50%', // Mocked progress, replace with actual data if available
        }));
    });

    // Track product click for recommended products
    const trackProductClick = (product) => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
      trackProduct(product, props.categorySlug);
    };

    return {
      store,
      category,
      product,
      productImages,
      selectedImage,
      totalQuantity,
      selectedColor,
      colorQuantity,
      shippingMethod,
      promoCode,
      activeTab,
      showSummary,
      recommendedProducts,
      trackProductClick,
      placeholder,
      addAttribute() {
        // Add logic to handle multiple attributes if needed
      },
    };
  },
};
</script>

<style scoped>
.product-details-page {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* Breadcrumb */
.breadcrumb {
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.breadcrumb a,
.breadcrumb span {
  color: #f28c38;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

/* Main Product Section */
.product-main {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.product-h2 {
  font-size: 1.5rem;
}

.product-images {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.thumbnail-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
  width: 100%;
  min-width: 200px;
  height: 400px;
}

.thumbnail-gallery img {
  flex: 1 1 calc(25% - 0.5rem);
  width: inherit;
  height: auto;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: transform 0.2s ease;
}

.thumbnail-gallery img.active,
.thumbnail-gallery img:hover {
  border-color: #f28c38;
  transform: scale(1.05);
}

.share-section {
  margin-top: 1rem;
}

.share-section p {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.share-icons {
  display: flex;
  gap: 0.5rem;
}

.share-icon {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #f0f0f0;
  color: #333;
  text-decoration: none;
}

.share-icon:hover {
  background-color: #f28c38;
  color: #fff;
}

/* Product Info */
.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.price-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.price-moq {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.price {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f28c38;
}

.moq-info p {
  font-size: 0.9rem;
  margin: 0.2rem 0;
}

.status-active {
  color: #28a745;
  font-weight: 600;
}

.rating {
  text-align: right;
}

.rating p {
  font-size: 0.9rem;
  margin: 0.2rem 0;
}

.stars i {
  color: #f28c38;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid #ddd;
  margin-bottom: 1rem;
  overflow-x: auto;
}

.tabs button {
  background: none;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  color: #666;
  white-space: nowrap;
}

.tabs button.active {
  color: #f28c38;
  border-bottom: 2px solid #f28c38;
}

.tab-content {
  margin-bottom: 2rem;
}

/* Order Form */
.order-form {
  padding: 1rem;
}

.order-form h3 {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.attributes {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.attribute {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.attribute label {
  font-size: 0.9rem;
  font-weight: 600;
}

.attribute select,
.attribute input {
  flex: 1;
}

.attribute button {
  background-color: #f28c38;
  color: #fff;
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.shipping-options {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.shipping-options label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.shipping-options input {
  width: auto;
}

.shipping-options span {
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.view-summary,
.add-to-cart {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.view-summary {
  background-color: #fff;
  color: #f28c38;
  border: 1px solid #f28c38;
}

.add-to-cart {
  background-color: #f28c38;
  color: #fff;
}

.view-summary:hover,
.add-to-cart:hover {
  opacity: 0.9;
}

/* Summary Popup */
.summary-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.summary-content {
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.summary-content h3 {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #f28c38;
}

.summary-details p {
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

.summary-details strong {
  font-weight: 600;
}

/* Recommended Products */
.recommended-products {
  margin-top: 2rem;
}

.recommended-products h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f28c38;
  margin-bottom: 1rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.product-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  border-radius: 6px;
  padding: 0.5rem;
  transition: transform 0.2s ease;
  text-decoration: none;
  color: inherit;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-image {
  width: 100%;
  height: 120px;
  background-color: #e0e0e0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  object-fit: cover;
}

.product-name {
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0.25rem 0;
  text-align: left;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-price {
  font-size: 0.8rem;
  font-weight: 700;
  margin: 0.25rem 0;
}

.moq-info {
  font-size: 0.7rem;
  margin: 0.25rem 0;
}

.moq-status {
  font-size: 0.7rem;
  color: #28a745;
  background-color: #e6f4ea;
  padding: 0.2rem 0.4rem;
  border-radius: 12px;
  margin: 0.25rem 0;
}

.progress-bar {
  width: 100%;
  height: 5px;
  background-color: #e0e0e0;
  border-radius: 3px;
  margin: 0.25rem 0;
}

.progress {
  height: 100%;
  background-color: #f28c38;
  border-radius: 3px;
}

.progress-text {
  font-size: 0.7rem;
  color: #666;
}

.no-products {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #666;
}

/* Responsive Adjustments */
@media (max-width: 1200px) {
  .product-main {
    gap: 1.5rem;
  }

  .thumbnail-gallery img {
    flex: 1 1 calc(33.33% - 0.5rem);
    width: auto;
    height: auto;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .product-main {
    flex-direction: column;
    gap: 1rem;
  }

  .product-h2 {
    font-size: 1.3rem;
  }

  .price-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .rating {
    text-align: left;
    margin-top: 1rem;
  }

  .thumbnail-gallery {
    justify-content: center;
  }

  .thumbnail-gallery img {
    flex: 1 1 calc(50% - 0.5rem);
    width: auto;
    height: auto;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .product-image {
    height: 100px;
  }

  .product-name {
    font-size: 0.8rem;
  }

  .product-price {
    font-size: 0.75rem;
  }

  .moq-info,
  .moq-status,
  .progress-text {
    font-size: 0.65rem;
  }

  .summary-content {
    max-width: 350px;
  }
}

@media (max-width: 480px) {
  .product-details-page {
    padding: 0.5rem;
  }

  .product-h2 {
    font-size: 1.1rem;
  }

  .price {
    font-size: 1.3rem;
  }

  .moq-info p {
    font-size: 0.8rem;
  }

  .rating p {
    font-size: 0.8rem;
  }

  .thumbnail-gallery img {
    flex: 1 1 calc(50% - 0.5rem);
    width: .5rem;
    height: auto;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }

  .product-image {
    height: 80px;
  }

  .product-name {
    font-size: 0.75rem;
  }

  .product-price {
    font-size: 0.7rem;
  }

  .moq-info,
  .moq-status,
  .progress-text {
    font-size: 0.6rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .view-summary,
  .add-to-cart {
    width: 100%;
  }

  .summary-content {
    max-width: 300px;
    padding: 1.5rem;
  }

  .summary-details p {
    font-size: 0.8rem;
  }
}
</style>
