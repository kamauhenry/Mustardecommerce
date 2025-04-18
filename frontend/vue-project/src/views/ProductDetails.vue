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
            <div v-if="activeTab === 'Review'" class="reviews-tab">
              <div v-if="reviews.length" class="reviews-list">
                <div v-for="review in reviews" :key="review.id" class="review-item">
                  <div class="review-content">
                    <p>{{ review.content }}</p>
                    <div class="review-rating">
                      <span v-for="star in 5" :key="star" :class="star <= review.rating ? 'fas fa-star' : 'far fa-star'"></span>
                    </div>
                    <p class="review-meta">By {{ review.username }} on {{ new Date(review.created_at).toLocaleDateString() }}</p>
                  </div>
                </div>
              </div>
              <p v-else class="no-reviews">No reviews yet. Be the first to share your thoughts!</p>
              <div v-if="isAuthenticated" class="review-actions">
                <button v-if="!showReviewForm" class="button button-primary" @click="showReviewForm = true">Add a Review</button>
                <form v-else @submit.prevent="submitReview" class="review-form">
                  <textarea
                    v-model="reviewContent"
                    placeholder="Write your review here..."
                    required
                    rows="5" 
                    id='review'
                  ></textarea>
                  <div class="rating-input">
                    <label for="reviewRating">Your Rating:</label>
                    <div class="star-rating">
                      <span
                        v-for="star in 5"
                        :key="star"
                        :class="star <= reviewRating ? 'fas fa-star' : 'far fa-star'"
                        @click="reviewRating = star"
                        @mouseover="hoveredRating = star"
                        @mouseleave="hoveredRating = null"
                        :style="{ color: star <= (hoveredRating || reviewRating) ? '#f5c518' : '#ccc' }"
                      ></span>
                    </div>
                  </div>
                  <div class="form-actions">
                    <button type="submit" class="button button-primary">Submit Review</button>
                    <button type="button" class="button button-secondary" @click="showReviewForm = false">Cancel</button>
                  </div>
                </form>
              </div>
              <p v-else class="login-prompt">Please <router-link to="/login">log in</router-link> to add a review.</p>
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
              <span
                v-for="star in 5"
                :key="star"
                :class="star <= Math.round(product?.rating || 0) ? 'fas fa-star' : 'far fa-star'"
                style="color: #f5c518;"
              ></span>
              <span>({{ product?.rating || 0 }})</span>
            </div>
          </div>
        </div>
      </div>

      <div class="related-products">
        <h3>You May Also Like</h3>
        <div v-if="isLoadingRelated" class="loading">Loading related products...</div>
        <div v-else-if="relatedProducts.length" class="related-products-grid">
          <router-link
              v-for="relatedProduct in relatedProducts"
              :key="relatedProduct.id"
              :to="{
                name: 'product-detail',
                params: { categorySlug: categorySlug, productSlug: relatedProduct.slug }
              }"
              class="related-product"
              :aria-label="`View ${relatedProduct.name}`"
            >
            <img
              :src="relatedProduct.thumbnail || placeholderImage"
              :alt="relatedProduct.name"
              class="related-product-image"
            />
            <h4 class="related-product-name">{{ relatedProduct.name }}</h4>
            <p class="related-product-price">KES {{ relatedProduct.price }}</p>
          </router-link>
        </div>
        <div v-else class="no-related">No related products available.</div>
        <router-link :to="`/category/${categorySlug}/products`" class="show-more">Show More</router-link>
      </div>
    </div>
  </MainLayout>
</template>



<script>
import { ref, computed, onMounted, watch } from 'vue';
import { createApiInstance, fetchRelatedProducts , fetchProductReviews, submitProductReview} from '@/services/api';
import { useEcommerceStore } from '@/stores/ecommerce';
import { toast } from 'vue3-toastify';
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
    const api = createApiInstance(store);
    const isAuthenticated = computed(() => store.isAuthenticated);
    
    // Product data
    const productKey = computed(() => `${props.categorySlug}:${props.productSlug}`);
    const product = computed(() => store.productDetails[productKey.value]);

    const relatedProducts = ref([]);
    const relatedProductsError = ref(null);
    const isLoadingRelated = ref(false);

    // Form state
    const quantity = ref(1);
    const selectedSize = ref('');
    const selectedColor = ref('');
    const shippingMethod = ref('ship');
    const promoCode = ref('');

    // Tab state
    const activeTab = ref('Description');
    const tabs = ['Description', 'Gallery', 'Review', 'Order'];

    // Review state
    const reviews = ref([]); // Initialize as empty array
    const showReviewForm = ref(false);
    const reviewContent = ref('');
    const reviewRating = ref(1);
    const hoveredRating = ref(null);
 
    const fetchReviews = async () => {
      if (!product.value?.id) return;
      try {
        const response = await fetchProductReviews(api, product.value.id);
        reviews.value = response.reviews || [];
      } catch (error) {
        console.error('Error fetching reviews:', error);
        reviews.value = [];
        toast.error('Failed to load reviews.', { autoClose: 3000 });
      }
    };

    const submitReview = async () => {
      if (!product.value?.id) return;
      if (!reviewContent.value.trim()) {
        toast.error('Review content cannot be empty.', { autoClose: 3000 });
        return;
      }
      if (!Number.isInteger(reviewRating.value) || reviewRating.value < 1 || reviewRating.value > 5) {
        toast.error('Please select a rating between 1 and 5.', { autoClose: 3000 });
        return;
      }
      const reviewData = {
        content: reviewContent.value.trim(),
        rating: reviewRating.value,
      };
      console.log('Submitting review with data:', reviewData);
      try {
        const response = await submitProductReview(api, product.value.id, reviewData);
        reviews.value.push(response);
        reviewContent.value = '';
        reviewRating.value = 1;
        showReviewForm.value = false;
        toast.success('Review submitted successfully!', { autoClose: 3000 });
        // Refresh product details to update rating
        await store.fetchProductDetails(props.categorySlug, props.productSlug);
      } catch (error) {
        const errorMessage = error.response?.data?.content?.[0] ||
                            error.response?.data?.rating?.[0] ||
                            error.response?.data?.non_field_errors?.[0] ||
                            'Failed to submit review.';
        console.error('Error submitting review:', error.response?.data || error.message);
        toast.error(errorMessage, { autoClose: 3000 });
      }
    };
    // Placeholder image
    const placeholderImage = 'data:image/jpeg;base64,...'; // Your placeholder image

    // Computed properties for sizes and colors
    const availableSizes = computed(() => {
      return [...new Set(product.value?.variants?.map(variant => variant.size) || [])];
    });

    const availableColors = computed(() => {
      return [...new Set(product.value?.variants?.map(variant => variant.color) || [])];
    });

    const selectedVariantId = computed(() => {
      if (!product.value?.variants) return null;
      const variant = product.value.variants.find(
        v => v.size === selectedSize.value && v.color === selectedColor.value
      );
      return variant ? variant.id : null;
    });

    const fetchProductAndRelated = async () => {
      const key = productKey.value;
      if (!store.productDetails[key]) {
        console.log('Fetching product details for:', key);
        await store.fetchProductDetails(props.categorySlug, props.productSlug);
      }
      const currentProduct = store.productDetails[key];
      if (currentProduct && currentProduct.id) {
        console.log('Fetching related products for:', `${props.categorySlug}:${currentProduct.id}`);
        isLoadingRelated.value = true;
        try {
          const response = await fetchRelatedProducts(api, props.categorySlug, currentProduct.id);
          relatedProducts.value = Array.isArray(response) ? response : [];
          relatedProductsError.value = null;
        } catch (error) {
          relatedProductsError.value = error.response?.data?.error || error.message || 'Failed to fetch related products';
          relatedProducts.value = [];
          console.error('Failed to fetch related products:', error);
        } finally {
          isLoadingRelated.value = false;
        }
      }
    };

    onMounted(fetchProductAndRelated);

    watch([productKey, activeTab], ([newKey, newTabValue], [oldKey]) => {
      if (newKey !== oldKey) {
        fetchProductAndRelated();
      }
      if (newTabValue === 'Review') {
        fetchReviews();
      }
    });
    watch(reviewRating, (newRating) => {
      console.log('reviewRating updated:', newRating);
    });
    // Add to cart handler
    const handleAddToCart = async () => {
      try {
        if (!selectedSize.value || !selectedColor.value) {
          toast.warning('Please select both size and color', { autoClose: 3000 });
          return;
        }
        await store.addToCart(
          product.value.id,
          selectedVariantId.value,
          quantity.value
        );
        toast.success('Product added to cart successfully!', { autoClose: 3000 });
      } catch (error) {
        console.error('Add to cart error:', error);
        toast.error('Failed to add to cart.', { autoClose: 3000 });
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
      relatedProducts,
      isLoadingRelated,
      relatedProductsError,
      showAuthModal: computed(() => store.isAuthModalVisible),
      reviews,
      showReviewForm,
      reviewContent,
      reviewRating,
      isAuthenticated,
      submitReview,
      hoveredRating, 
    };
  },
};
</script>

<style scoped>
.related-products-grid {
  display: flex;           /* Enables Flexbox to align items in a row */
  flex-wrap: nowrap;       /* Keeps all items in a single row */
  overflow-x: auto;        /* Adds horizontal scrolling if items overflow */
  gap: 20px;               /* Adds space between products */
  padding: 10px 0;         /* Optional: adds vertical padding */
}

.related-product {
  flex: 0 0 auto;          /* Prevents stretching or shrinking, uses defined width */
  width: 200px;            /* Fixed width for each product card */
  text-align: center;      /* Centers content inside each product */
  text-decoration: none;   /* Removes underline from router-link */
  color: inherit;          /* Inherits text color from parent */
}

.related-product-image {
  width: 100%;             /* Fills the product container */
  height: auto;            /* Maintains aspect ratio */
  max-height: 150px;       /* Limits height for consistency */
  object-fit: cover;       /* Ensures image fits nicely */
}

.related-product-name {
  font-size: 1rem;         /* Reasonable font size for product name */
  margin: 10px 0;          /* Adds spacing above and below */
}

.related-product-price {
  font-size: 0.9rem;       /* Slightly smaller font for price */
  color: #333;             /* Darker color for readability */
}
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
/* Reviews Tab */
.reviews-tab {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Reviews List */
.reviews-list {
  margin-bottom: 20px;
}

.review-item {
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.review-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.review-content p {
  font-size: 1rem;
  line-height: 1.6;
  color: #333;
  margin: 0;
}

.review-rating {
  display: flex;
  gap: 5px;
}

.review-rating .fas.fa-star {
  color: #f5c518; /* Gold for filled stars */
  font-size: 1rem;
}

.review-rating .far.fa-star {
  color: #ccc; /* Grey for empty stars */
  font-size: 1rem;
}

.review-meta {
  font-size: 0.85rem;
  color: #666;
  font-style: italic;
}

/* No Reviews Message */
.no-reviews {
  font-size: 1rem;
  color: #666;
  text-align: center;
  margin: 20px 0;
  font-weight: 500;
}

/* Login Prompt */
.login-prompt {
  font-size: 1rem;
  color: #666;
  text-align: center;
  margin: 20px 0;
}

.login-prompt a {
  color: #007bff;
  text-decoration: none;
}

.login-prompt a:hover {
  text-decoration: underline;
}

/* Button Base Style (Consistent with .show-more and .add-to-cart) */
.button {
  font-weight: 600;
  color: #fff;
  padding: 10px 20px;
  border-radius: 10px;
  text-transform: uppercase;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: box-shadow 0.3s ease, transform 0.2s ease;
  display: inline-block;
  background-color: #007bff; /* Default background */
}

.button:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transform: translateY(-1px);
}

.button-primary {
  background-color: #007bff; /* Blue for primary actions */
}

.button-secondary {
  background-color: #6c757d; /* Grey for secondary actions */
}

/* Review Form */
.review-form {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.review-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.3s ease;
}
.no-related{
  padding:10px;
  margin-bottom:20px;
}
.review-form textarea:focus {
  border-color: #007bff;
  outline: none;
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 15px;
}

.rating-input label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
}

.star-rating {
  display: flex;
  gap: 8px;
}

.star-rating span {
  font-size: 1.2rem;
  cursor: pointer;
  transition: color 0.2s ease;
}

.star-rating span:hover,
.star-rating span.active {
  color: #f5c518; /* Gold on hover or when selected */
}

.form-actions {
  display: flex;
  gap: 10px;
}

/* Responsiveness for Reviews */
@media (max-width: 768px) {
  .reviews-tab {
    padding: 15px;
  }

  .review-content p {
    font-size: 0.95rem;
  }

  .review-meta {
    font-size: 0.8rem;
  }

  .review-form textarea {
    min-height: 80px;
  }

  .star-rating span {
    font-size: 1rem;
  }

  .form-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .button {
    width: 100%;
    text-align: center;
  }
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
  padding-top: 10px;
  border-radius: 10px;
  text-transform: uppercase;
  text-decoration: none;
  margin-top: 0.6rem;
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
