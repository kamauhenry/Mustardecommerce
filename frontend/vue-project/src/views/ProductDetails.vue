<template>
  <MainLayout>
    <div class="product-details-page">
      <!-- Breadcrumb -->
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> &gt;
        <router-link :to="`/category/${categorySlug}/products`">{{ category?.name || 'Category' }}</router-link> &gt;
        <span>{{ product?.name || 'Product' }}</span>
      </div>

      <!-- Main Product Section -->
      <div class="product-main">
        <!-- Product Images -->
        <div class="product-images">
          <div class="main-image">
            <img :src="selectedImage || placeholder" :alt="product?.name" />
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
          <div class="share-section">
            <p>Share to:</p>
            <div class="share-icons">
              <a href="#" class="share-icon"><i class="fab fa-facebook-f"></i></a>
              <a href="#" class="share-icon"><i class="fab fa-twitter"></i></a>
              <a href="#" class="share-icon"><i class="fab fa-whatsapp"></i></a>
              <a href="#" class="share-icon"><i class="fas fa-envelope"></i></a>
              <a href="#" class="share-icon"><i class="fas fa-link"></i></a>
            </div>
          </div>
        </div>

        <!-- Product Details -->
        <div class="product-info">
          <h1 class="product-title">{{ product?.name || 'Product Name' }}</h1>
          <div class="price-section">
            <span class="price">KES {{ product?.price || '0' }}</span>
            <div class="moq-info">
              <p>Below MOQ price: KES {{ product?.price || '0' }}</p>
              <p>Supplier MOQ: {{ product?.moq || '0' }} items</p>
              <p>Group buy order so far: 34</p>
              <p>MOQ Per Person: 1 items / bundle</p>
              <p>MOQ Number: 2R1Y1</p>
              <p>MOQ Status: <span class="status-active">{{ product?.moq_status || 'N/A' }}</span></p>
            </div>
            <div class="rating">
              <p>Rating</p>
              <div class="stars">
                <i v-for="n in 5" :key="n" :class="n <= 2 ? 'fas fa-star' : 'far fa-star'"></i>
              </div>
              <p>Pending by Supplier MOQ</p>
              <p>113 Sold</p>
            </div>
          </div>

          <!-- Order Form -->
          <div class="order-form">
            <h3>Order</h3>
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
              <button class="view-summary">View Summary</button>
              <button class="add-to-cart">Add to Cart</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs for Description and Reviews -->
      <div class="tabs">
        <button :class="{ active: activeTab === 'description' }" @click="activeTab = 'description'">
          Description
        </button>
        <button :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">
          Customer Reviews
        </button>
      </div>
      <div class="tab-content">
        <div v-if="activeTab === 'description'">
          <p>{{ product?.description || 'No description available.' }}</p>
        </div>
        <div v-if="activeTab === 'reviews'">
          <p>No customer reviews yet.</p>
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
    const activeTab = ref('description');

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

.product-images {
  flex: 1;
}

.main-image img {
  width: 100%;
  height: 400px;
  object-fit: cover;
  border-radius: 8px;
}

.thumbnail-gallery {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  overflow-x: auto;
}

.thumbnail-gallery img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
}

.thumbnail-gallery img.active {
  border-color: #f28c38;
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
}

.product-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f28c38;
  margin-bottom: 1rem;
}

.price-section {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1rem;
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
  margin-left: auto;
  text-align: right;
}

.rating p {
  font-size: 0.9rem;
  margin: 0.2rem 0;
}

.stars i {
  color: #f28c38;
}

/* Order Form */
.order-form {
  border: 1px solid #ddd;
  padding: 1rem;
  border-radius: 8px;
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

/* Tabs */
.tabs {
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid #ddd;
  margin-bottom: 1rem;
}

.tabs button {
  background: none;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  color: #666;
}

.tabs button.active {
  color: #f28c38;
  border-bottom: 2px solid #f28c38;
}

.tab-content {
  margin-bottom: 2rem;
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
  grid-template-columns: repeat(5, 1fr);
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
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .product-main {
    flex-direction: column;
  }

  .main-image img {
    height: 300px;
  }

  .products-grid {
    grid-template-columns: repeat(2, 1fr);
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
}

@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: repeat(1, 1fr);
  }

  .main-image img {
    height: 200px;
  }

  .product-image {
    height: 80px;
  }
}
</style>
