<template>
  <MainLayout>
    <div class="product-details-container">
      <!-- Skeleton for Main Product Content -->
      <div v-if="isLoadingProduct" class="skeleton-product-details">
        <div class="skeleton-breadcrumb"></div>
        <div class="skeleton-product-title"></div>
        <div class="skeleton-product-content">
          <div class="skeleton-product-left">
            <div class="skeleton-tabs">
              <div v-for="n in 4" :key="n" class="skeleton-tab"></div>
            </div>
            <div class="skeleton-main-image"></div>
            <div class="skeleton-thumbnails">
              <div v-for="n in 3" :key="n" class="skeleton-thumbnail"></div>
            </div>
          </div>
          <div class="skeleton-product-right">
            <div class="skeleton-price"></div>
            <div class="skeleton-moq-info"></div>
            <div class="skeleton-moq-info"></div>
            <div class="skeleton-button"></div>
            <div class="skeleton-rating"></div>
          </div>
        </div>
      </div>
      <!-- Error State -->
      <div v-else-if="!product" class="error">Failed to load product.</div>
      <!-- Main Product Content -->
      <div v-else>
        <!-- Breadcrumb Navigation -->
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <router-link to="/">Home</router-link> /
          <router-link :to="`/category/${categorySlug}/products`">{{ categorySlug || 'Category' }}</router-link> /
          <span>{{ product.name || 'Product' }}</span>
        </nav>

        <!-- Product Title -->
        <h1 class="product-title">{{ product.name || 'Loading...' }}</h1>

        <!-- Social Sharing Links -->
        <div class="social-sharing">
          <span>Share:</span>
          <a :href="xShareUrl" target="_blank" class="social-icon x" title="Share on X">
            <i class="fab fa-x"></i>
          </a>
          <a :href="instagramShareUrl" target="_blank" class="social-icon instagram" title="Share on Instagram">
            <i class="fab fa-instagram"></i>
          </a>
          <a :href="whatsappShareUrl" target="_blank" class="social-icon whatsapp" title="Share on WhatsApp">
            <i class="fab fa-whatsapp"></i>
          </a>
          <button @click="copyToClipboard" class="social-icon clipboard" title="Copy to Clipboard">
            <i class="fas fa-copy"></i>
          </button>
        </div>

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
                <h3>Product Description</h3>
                <p>{{ product.description || 'No description available.' }}</p>
                <h3>Attributes</h3>
                <ul v-if="product.attributes?.length">
                  <li v-for="attr in product.attributes" :key="attr.id">
                    <strong>{{ attr.name }}:</strong>
                    <span>{{ attributeOptions[attr.name]?.join(', ') || 'N/A' }}</span>
                  </li>
                </ul>
                <p v-else>No attributes available.</p>
                <h3>Details</h3>
                <ul>
                  <li><strong>Material:</strong> {{ product.material || 'N/A' }}</li>
                  <li><strong>Fit:</strong> {{ product.fit || 'N/A' }}</li>
                  <li><strong>Product Code:</strong> {{ product.code || 'N/A' }}</li>
                </ul>
              </div>

              <!-- Gallery Tab -->
              <div v-if="activeTab === 'Gallery'" class="gallery">
                <div class="product-images">
                  <div class="main-image-container">
                    <img
                      :src="currentImage || placeholderImage"
                      class="main-image"
                      :alt="`Main image of ${product.name}`"
                    />
                  </div>
                  <div class="thumbnails" v-if="product.images?.length > 1">
                    <button
                      class="thumbnail-nav prev"
                      @click="scrollThumbnails('left')"
                      :disabled="thumbnailOffset === 0"
                    >
                      <span class="fas fa-chevron-left"></span>
                    </button>
                    <div class="thumbnail-container" ref="thumbnailContainer">
                      <img
                        v-for="(image, index) in product.images"
                        :key="index"
                        :src="image.thumbnail || image.image || placeholderImage"
                        :alt="`Thumbnail ${index + 1} of ${product.name}`"
                        class="thumbnail"
                        :class="{ active: currentImage === (image.image || placeholderImage) }"
                        @click="currentImage = image.image || placeholderImage"
                      />
                    </div>
                    <button
                      class="thumbnail-nav next"
                      @click="scrollThumbnails('right')"
                      :disabled="thumbnailOffset >= maxThumbnailOffset"
                    >
                      <span class="fas fa-chevron-right"></span>
                    </button>
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
                        <span
                          v-for="star in 5"
                          :key="star"
                          :class="star <= review.rating ? 'fas fa-star' : 'far fa-star'"
                        ></span>
                      </div>
                      <p class="review-meta">
                        By {{ review.username }} on
                        {{ new Date(review.created_at).toLocaleDateString() }}
                      </p>
                    </div>
                  </div>
                </div>
                <p v-else class="no-reviews">
                  No reviews yet. Be the first to share your thoughts!
                </p>
                <div v-if="isAuthenticated" class="review-actions">
                  <button
                    v-if="!showReviewForm"
                    class="button button-primary"
                    @click="showReviewForm = true"
                    :disabled="isSubmittingReview"
                  >
                    Add a Review
                  </button>
                  <form v-else @submit.prevent="submitReview" class="review-form">
                    <textarea
                      v-model="reviewContent"
                      placeholder="Write your review here..."
                      required
                      rows="5"
                      id="review"
                      :disabled="isSubmittingReview"
                    ></textarea>
                    <div class="rating-input">
                      <label for="reviewRating">Your Rating:</label>
                      <div class="star-rating">
                        <span
                          v-for="star in 5"
                          :key="star"
                          :class="star <= (hoveredRating || reviewRating) ? 'fas fa-star' : 'far fa-star'"
                          @click="reviewRating = star"
                          @mouseover="hoveredRating = star"
                          @mouseleave="hoveredRating = null"
                          :style="{ color: star <= (hoveredRating || reviewRating) ? '#f5c518' : '#ccc' }"
                        ></span>
                      </div>
                    </div>
                    <div class="form-actions">
                      <button
                        type="submit"
                        class="button button-primary"
                        :disabled="isSubmittingReview"
                      >
                        {{ isSubmittingReview ? 'Submitting...' : 'Submit Review' }}
                      </button>
                      <button
                        type="button"
                        class="button button-secondary"
                        @click="showReviewForm = false"
                        :disabled="isSubmittingReview"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
                <p v-else class="login-prompt">
                  Please <router-link to="/login">log in</router-link> to add a review.
                </p>
              </div>

              <!-- Order Tab -->
              <div v-if="activeTab === 'Order'" class="order-tab">
                <div class="order-details">
                  <div class="attributes">
                    <label>Order Attributes</label>
                    <div class="attribute-row">
                      <div
                        v-if="product.attributes?.length"
                        v-for="attr in product.attributes"
                        :key="attr.id"
                        class="attribute"
                      >
                        <label>{{ attr.name }}</label>
                        <select
                          v-model="selectedAttributes[attr.name]"
                          required
                          @change="updateVariant"
                        >
                          <option disabled value="">Select {{ attr.name }}</option>
                          <option
                            v-for="value in attributeOptions[attr.name] || []"
                            :key="value"
                            :value="value"
                          >
                            {{ value }}
                          </option>
                        </select>
                      </div>
                      <div class="attribute">
                        <label>Quantity</label>
                        <input
                          type="number"
                          v-model.number="quantity"
                          min="1"
                          required
                        />
                      </div>
                    </div>
                    <!-- Display Selected Attributes -->
                    <div v-if="Object.keys(selectedAttributes).length" class="selected-attributes">
                      <h4>Selected Attributes:</h4>
                      <ul>
                        <li v-for="(value, name) in selectedAttributes" :key="name">
                          <strong>{{ name }}:</strong> {{ value || 'Not selected' }}
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div class="shipping">
                    <label>Shipping Method</label>
                    <div class="shipping-option">
                      <input
                        type="radio"
                        id="ship"
                        name="shipping"
                        value="ship"
                        v-model="shippingMethod"
                      />
                      <label for="ship">Ship (Approx. KES 310 each)</label>
                    </div>
                    <div class="shipping-option">
                      <input
                        type="radio"
                        id="air"
                        name="shipping"
                        value="air"
                        v-model="shippingMethod"
                      />
                      <label for="air">Air (Approx. cost TBD)</label>
                    </div>
                  </div>

                  <div class="promo-code">
                    <label>Promo Code</label>
                    <input
                      type="text"
                      v-model="promoCode"
                      placeholder="Enter promo code"
                    />
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
                <h2 class="price">KES {{ effectivePrice }}</h2>
                <p class="moq-info">
                  Below MOQ price: KES
                  {{ product.below_moq_price || product.price || '0' }}
                </p>
                <p class="moq-info">Price: {{ product.price }}</p>
                <p class="moq-info">
                  MOQ Per Person: {{ product.moq_per_person || 'N/A' }} items/bundle
                </p>
                <p class="moq-info">Quantity: {{ quantity }}</p>
                <p class="moq-info">MOQ Status: {{ product.moq_status }}</p>
              </div>

              <!-- Add to Cart Button -->
              <div class="control">
                <button
                  class="add-to-cart"
                  @click="handleAddToCart"
                  :disabled="isAddingToCart || !selectedVariant"
                  :aria-label="isAddingToCart ? 'Adding to cart' : 'Add to cart'"
                >
                  {{ isAddingToCart ? 'Adding to Cart...' : 'Add to Cart' }}
                </button>
              </div>

              <!-- Rating -->
              <div class="rating">
                <span
                  v-for="star in 5"
                  :key="star"
                  :class="star <= Math.round(product.rating || 0) ? 'fas fa-star' : 'far fa-star'"
                  style="color: #f5c518;"
                ></span>
                <span>({{ product.rating || 0 }})</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Related Products Section -->
        <div class="related-products">
          <h3>You May Also Like</h3>
          <!-- Skeleton for Related Products -->
          <div v-if="isLoadingRelated" class="skeleton-related-products">
            <div v-for="n in 3" :key="n" class="skeleton-related-product">
              <div class="skeleton-related-image"></div>
              <div class="skeleton-related-name"></div>
              <div class="skeleton-related-price"></div>
            </div>
          </div>
          <!-- Related Products Content -->
          <div
            v-else-if="Array.isArray(relatedProducts) && relatedProducts.length"
            class="related-products-container"
          >
            <div class="related-products-grid">
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
                <div class="related-product-card">
                  <img
                    :src="relatedProduct.thumbnail || placeholderImage"
                    :alt="relatedProduct.name"
                    class="related-product-image"
                  />
                  <div class="related-product-info">
                    <h4 class="related-product-name">{{ relatedProduct.name }}</h4>
                    <p class="related-product-price">KES {{ relatedProduct.price }}</p>
                  </div>
                </div>
              </router-link>
            </div>
            <!-- Scroll Indicators -->
            <button
              class="scroll-btn prev"
              @click="scrollRelatedProducts('left')"
              :disabled="relatedScrollOffset <= 0"
              aria-label="Scroll left"
            >
              <i class="fas fa-chevron-left"></i>
            </button>
            <button
              class="scroll-btn next"
              @click="scrollRelatedProducts('right')"
              :disabled="relatedScrollOffset >= maxRelatedScrollOffset"
              aria-label="Scroll right"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
          <div v-else class="no-related">No related products available.</div>
          <router-link :to="`/category/${categorySlug}/products`" class="show-more">
            Show More
          </router-link>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useHead } from '@vueuse/head';
import {
  createApiInstance,
  fetchRelatedProducts,
  fetchProductReviews,
  submitProductReview,
} from '@/services/api';
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
    const isLoadingProduct = ref(true);
    const relatedProducts = ref([]);
    const relatedProductsError = ref(null);
    const isLoadingRelated = ref(false);

    // Related Products Scroll
    const relatedScrollOffset = ref(0);
    const relatedCardWidth = 220; // Width of each card + margin
    const maxRelatedScrollOffset = computed(() =>
      Math.max(0, ((relatedProducts.value.length || 0) - 3) * relatedCardWidth)
    );

    // Form state
    const quantity = ref(1);
    const selectedAttributes = ref({});
    const shippingMethod = ref('ship');
    const promoCode = ref('');

    // Tab state
    const activeTab = ref('Description');
    const tabs = ['Description', 'Gallery', 'Review', 'Order'];

    // Gallery state
    const currentImage = ref(null);
    const thumbnailOffset = ref(0);
    const thumbnailsPerPage = 4;
    const thumbnailWidth = 70;
    const maxThumbnailOffset = computed(() =>
      Math.max(0, ((product.value?.images?.length || 0) - thumbnailsPerPage) * thumbnailWidth)
    );

    // Review state
    const reviews = ref([]);
    const showReviewForm = ref(false);
    const reviewContent = ref('');
    const reviewRating = ref(1);
    const hoveredRating = ref(null);
    const isSubmittingReview = ref(false);

    // Cart state
    const isAddingToCart = ref(false);

    // Affiliate and Sharing state
    const affiliateCode = computed(() => store.user?.affiliate_code || '');
    const productUrl = computed(() =>
      `${window.location.origin}/products/${props.categorySlug}/${props.productSlug}/?aff=${affiliateCode.value}`
    );
    const shareText = computed(() =>
      `Check out this amazing product: ${product.value?.name || ''} at ${productUrl.value}`
    );

    // SEO state
    const metaTitle = computed(() =>
      product.value?.meta_title || product.value?.name || 'Product Details'
    );
    const metaDescription = computed(() =>
      product.value?.meta_description ||
      product.value?.description?.slice(0, 160) ||
      'Discover this amazing product at our store.'
    );
    const metaKeywords = computed(() =>
      [
        product.value?.name,
        product.value?.category?.name,
        ...(product.value?.attributes?.map(attr => attr.name) || []),
        'ecommerce',
        'buy online',
      ]
        .filter(Boolean)
        .join(', ')
    );
    const currentUrl = computed(() =>
      window.location.origin + `/products/${props.categorySlug}/${props.productSlug}/`
    );
    const schemaMarkup = computed(() => ({
      '@context': 'https://schema.org',
      '@type': 'Product',
      name: product.value?.name || '',
      image: product.value?.images?.map(img => img.image) || [placeholderImage],
      description: product.value?.description || 'No description available.',
      sku: product.value?.code || 'N/A',
      brand: {
        '@type': 'Brand',
        name: product.value?.supplier?.name || 'Unknown',
      },
      offers: {
        '@type': 'Offer',
        priceCurrency: 'KES',
        price: product.value?.price || 0,
        availability:
          product.value?.moq_status === 'active'
            ? 'https://schema.org/InStock'
            : 'https://schema.org/OutOfStock',
        url: currentUrl.value,
      },
      aggregateRating: product.value?.rating
        ? {
            '@type': 'AggregateRating',
            ratingValue: product.value.rating,
            reviewCount: reviews.value.length || 1,
          }
        : undefined,
    }));

    // Use @vueuse/head to manage meta tags and JSON-LD
    useHead({
      title: metaTitle,
      meta: [
        { name: 'description', content: metaDescription },
        { name: 'keywords', content: metaKeywords },
        { name: 'robots', content: 'index, follow' },
        { property: 'og:title', content: metaTitle },
        { property: 'og:description', content: metaDescription },
        { property: 'og:image', content: () => product.value?.thumbnail || placeholderImage },
        { property: 'og:url', content: currentUrl },
        { property: 'og:type', content: 'product' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: metaTitle },
        { name: 'twitter:description', content: metaDescription },
        { name: 'twitter:image', content: () => product.value?.thumbnail || placeholderImage },
      ],
      script: [
        {
          type: 'application/ld+json',
          innerHTML: schemaMarkup,
        },
      ],
    });

    // Social sharing URLs
    const xShareUrl = computed(() =>
      `https://x.com/intent/tweet?text=${encodeURIComponent(shareText.value)}`
    );
    const instagramShareUrl = computed(() =>
      `https://www.instagram.com/?url=${encodeURIComponent(productUrl.value)}`
    );
    const whatsappShareUrl = computed(() =>
      `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText.value)}`
    );

    // Copy to clipboard
    const copyToClipboard = async () => {
      try {
        await navigator.clipboard.writeText(productUrl.value);
        toast.success('Link copied to clipboard!', { autoClose: 3000 });
      } catch (err) {
        toast.error('Failed to copy link.', { autoClose: 3000 });
      }
    };

    // Attribute options
    const attributeOptions = computed(() => {
      if (!product.value?.attributes || !Array.isArray(product.value.attributes)) {
        console.warn('No attributes available for product:', product.value);
        return {};
      }
      const options = {};
      product.value.attributes.forEach(attr => {
        const values = new Set();
        if (product.value.variants && Array.isArray(product.value.variants)) {
          product.value.variants.forEach(variant => {
            const attrValue = variant.attribute_values?.find(
              av => av.attribute_name === attr.name
            );
            if (attrValue) values.add(attrValue.value);
          });
        }
        options[attr.name] = Array.from(values);
        // Initialize selectedAttributes if not set
        if (options[attr.name].length && !selectedAttributes.value[attr.name]) {
          selectedAttributes.value[attr.name] = options[attr.name][0];
        }
      });
      console.log('Computed attributeOptions:', options);
      return options;
    });

    // Effective price
    const effectivePrice = computed(() => {
      if (!product.value) return '0';
      const qty = Number(quantity.value) || 1;
      const moqPerPerson = Number(product.value.moq_per_person) || 2;
      const belowMoqPrice =
        Number(product.value.below_moq_price) || Number(product.value.price) || 0;
      const price = Number(product.value.price) || 0;
      if (product.value.moq_status === 'active' && qty < moqPerPerson) {
        return belowMoqPrice.toFixed(2);
      }
      return price.toFixed(2);
    });

    // Selected variant
    const selectedVariant = computed(() => {
      if (!product.value?.variants || !Array.isArray(product.value.variants)) {
        console.warn('No variants available for product:', product.value);
        return null;
      }
      if (!product.value?.attributes || !Array.isArray(product.value.attributes)) {
        console.warn('No attributes available for variants:', product.value);
        return null;
      }
      const variant = product.value.variants.find(variant => {
        return product.value.attributes.every(attr => {
          const selectedValue = selectedAttributes.value[attr.name];
          const variantValue = variant.attribute_values?.find(
            av => av.attribute_name === attr.name
          )?.value;
          return selectedValue === variantValue;
        });
      });
      console.log('Selected variant:', variant);
      return variant;
    });

    // Methods
    const scrollThumbnails = direction => {
      if (direction === 'left' && thumbnailOffset.value > 0) {
        thumbnailOffset.value -= thumbnailWidth;
      } else if (
        direction === 'right' &&
        thumbnailOffset.value < maxThumbnailOffset.value
      ) {
        thumbnailOffset.value += thumbnailWidth;
      }
      const container = document.querySelector('.thumbnail-container');
      if (container) {
        container.style.transform = `translateX(-${thumbnailOffset.value}px)`;
      }
    };

    const scrollRelatedProducts = direction => {
      if (direction === 'left' && relatedScrollOffset.value > 0) {
        relatedScrollOffset.value -= relatedCardWidth;
      } else if (
        direction === 'right' &&
        relatedScrollOffset.value < maxRelatedScrollOffset.value
      ) {
        relatedScrollOffset.value += relatedCardWidth;
      }
      const container = document.querySelector('.related-products-grid');
      if (container) {
        container.style.transform = `translateX(-${relatedScrollOffset.value}px)`;
      }
    };

    const updateVariant = () => {
      if (selectedVariant.value && product.value?.images?.length) {
        currentImage.value = product.value.images[0].image || placeholderImage;
      }
      console.log('Updated selectedAttributes:', selectedAttributes.value);
    };

    const handleAddToCart = async () => {
      if (!selectedVariant.value) {
        toast.warning(
          'Please select all attributes or the selected combination is not available',
          { autoClose: 3000 }
        );
        return;
      }
      if (isAddingToCart.value) return;
      isAddingToCart.value = true;
      try {
        const affiliateCodeFromUrl = new URLSearchParams(window.location.search).get('aff');
        await store.addToCart(
          product.value.id,
          selectedVariant.value.id,
          quantity.value,
          affiliateCodeFromUrl
        );
        toast.success('Product added to cart successfully!', { autoClose: 3000 });
      } catch (error) {
        console.error('Add to cart error:', error);
        toast.error('Failed to add to cart.', { autoClose: 3000 });
      } finally {
        isAddingToCart.value = false;
      }
    };

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
      if (
        !Number.isInteger(reviewRating.value) ||
        reviewRating.value < 1 ||
        reviewRating.value > 5
      ) {
        toast.error('Please select a rating between 1 and 5.', { autoClose: 3000 });
        return;
      }
      if (isSubmittingReview.value) return;
      isSubmittingReview.value = true;
      const reviewData = {
        content: reviewContent.value.trim(),
        rating: reviewRating.value,
      };
      try {
        const response = await submitProductReview(api, product.value.id, reviewData);
        reviews.value.push(response);
        reviewContent.value = '';
        reviewRating.value = 1;
        showReviewForm.value = false;
        toast.success('Review submitted successfully!', { autoClose: 3000 });
        await store.fetchProductDetails(props.categorySlug, props.productSlug);
      } catch (error) {
        let errorMessage = 'Failed to submit review.';
        if (error.response?.data) {
          if (error.response.data.content?.[0]) {
            errorMessage = error.response.data.content[0];
          } else if (error.response.data.rating?.[0]) {
            errorMessage = error.response.data.rating[0];
          } else if (error.response.data.non_field_errors?.[0]) {
            errorMessage = error.response.data.non_field_errors[0];
          } else if (typeof error.response.data === 'string') {
            errorMessage = error.response.data;
          } else if (error.response.data.detail) {
            errorMessage =
              typeof error.response.data.detail === 'string'
                ? error.response.data.detail
                : 'An error occurred while submitting the review.';
          }
        }
        console.error('Error submitting review:', error.response?.data || error.message);
        toast.error(errorMessage, { autoClose: 3000 });
      } finally {
        isSubmittingReview.value = false;
      }
    };

    const placeholderImage = 'data:image/jpeg;base64,...'; // Your placeholder image

    const fetchProductAndRelated = async () => {
      isLoadingProduct.value = true;
      const key = productKey.value;
      try {
        await store.fetchProductDetails(props.categorySlug, props.productSlug);
        const currentProduct = store.productDetails[key];
        if (currentProduct && currentProduct.id) {
          currentImage.value = currentProduct.images?.[0]?.image || placeholderImage;
          isLoadingRelated.value = true;
          try {
            const response = await fetchRelatedProducts(
              api,
              props.categorySlug,
              currentProduct.id
            );
            relatedProducts.value = Array.isArray(response) ? response : [];
            relatedProductsError.value = null;
          } catch (error) {
            relatedProductsError.value =
              error.response?.data?.error ||
              error.message ||
              'Failed to fetch related products';
            relatedProducts.value = [];
            toast.error('Failed to load related products.', { autoClose: 3000 });
          } finally {
            isLoadingRelated.value = false;
          }
        } else {
          relatedProducts.value = [];
        }
      } catch (error) {
        console.error('Failed to fetch product details:', error);
        toast.error('Failed to load product details.', { autoClose: 3000 });
      } finally {
        isLoadingProduct.value = false;
      }
    };

    onMounted(() => {
      fetchProductAndRelated();
    });

    watch([productKey, activeTab], ([newKey, newTabValue], [oldKey]) => {
      if (newKey !== oldKey) {
        fetchProductAndRelated();
      }
      if (newTabValue === 'Review') {
        fetchReviews();
      }
    });

    watch(
      product,
      newProduct => {
        if (newProduct?.images?.length) {
          currentImage.value = newProduct.images[0].image || placeholderImage;
        }
        // Reset and initialize selectedAttributes
        selectedAttributes.value = {};
        if (newProduct?.attributes) {
          newProduct.attributes.forEach(attr => {
            if (attributeOptions.value[attr.name]?.length) {
              selectedAttributes.value[attr.name] = attributeOptions.value[attr.name][0];
            }
          });
        }
      },
      { immediate: true }
    );

    return {
      product,
      isLoadingProduct,
      quantity,
      selectedAttributes,
      attributeOptions,
      shippingMethod,
      promoCode,
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
      effectivePrice,
      hoveredRating,
      currentImage,
      thumbnailOffset,
      maxThumbnailOffset,
      scrollThumbnails,
      isAddingToCart,
      isSubmittingReview,
      selectedVariant,
      updateVariant,
      metaTitle,
      metaDescription,
      metaKeywords,
      currentUrl,
      schemaMarkup,
      xShareUrl,
      instagramShareUrl,
      whatsappShareUrl,
      copyToClipboard,
      relatedScrollOffset,
      maxRelatedScrollOffset,
      scrollRelatedProducts,
    };
  },
};
</script>


<style scoped>

@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
/* Skeleton for Product Details */
.skeleton-product-details {
  padding: 20px;
}

.skeleton-breadcrumb {
  width: 30%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 15px;
}

.skeleton-product-title {
  width: 50%;
  height: 30px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 20px;
}

.skeleton-product-content {
  display: flex;
  gap: 30px;
}

.skeleton-product-left {
  flex: 2;
}

.skeleton-tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.skeleton-tab {
  width: 80px;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-main-image {
  width: 100%;
  height: 300px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

.skeleton-thumbnails {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.skeleton-thumbnail {
  width: 60px;
  height: 60px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-product-right {
  flex: 1;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 5px 5px rgba(46, 46, 46, 0.1);
}

.skeleton-price {
  width: 50%;
  height: 30px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 10px;
}

.skeleton-moq-info {
  width: 70%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 10px;
}

.skeleton-button {
  width: 100%;
  height: 40px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 10px;
}

.skeleton-rating {
  width: 30%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
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



.description ul li strong {
  font-weight: 700;
}

/* Gallery */
/* Gallery */
.product-images {
  position: relative;
}

.main-image-container {
  width: 100%;
  padding-top: 75%; /* 4:3 aspect ratio */
  position: relative;
  background-color: #f0f0f0;
}



/* Social Sharing */
.social-sharing {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.social-sharing span {
  font-weight: 500;
  color: #333;
}

.social-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: #fff;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.social-icon i {
  font-size: 1.2rem;
}

.social-icon.x {
  background-color: #000000; /* X brand color */
}

.social-icon.instagram {
  background: radial-gradient(
    circle at 30% 107%,
    #fdf497 0%,
    #fdf497 5%,
    #fd5949 45%,
    #d6249f 60%,
    #285aeb 90%
  ); /* Instagram gradient */
}

.social-icon.whatsapp {
  background-color: #25d366; /* WhatsApp green */
}

.social-icon.clipboard {
  background-color: #007bff; /* Blue for copy button */
  border: none;
  cursor: pointer;
}

.social-icon:hover {
  opacity: 0.9;
}


.main-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.thumbnails {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
  position: relative;
}

.thumbnail-container {
  display: flex;
  gap: 10px;
  transition: transform 0.3s ease;
  overflow: hidden;
  flex: 1;
  justify-content: center;
}

.thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.thumbnail.active,
.thumbnail:hover {
  border-color: #007bff;
}

.thumbnail-nav {
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border: none;
  padding: 10px;
  cursor: pointer;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
}

.thumbnail-nav.prev {
  left: 0;
}

.thumbnail-nav.next {
  right: 0;
}

.thumbnail-nav:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Description */
.description ul li {
  display: flex;
  gap: 10px;
  align-items: baseline;
}

/* Button States */
.button:disabled,
.add-to-cart:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #ccc;
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
  display: inline-bl#bd8741;
  background-color: #ffa200; 
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
  
/* Responsiveness */

  .thumbnails {
    max-width: 100%;
  }

  .thumbnail-container {
    justify-content: flex-start;
  }

  .thumbnail-nav {
    padding: 5px;
  }

  .product-title {
    font-size: 1.5rem;
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
  padding: 20px 0;
  background-color: #f8f9fa; /* Light gray background for distinction */
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.related-products h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  padding-left: 20px;
}

.related-products-container {
  position: relative;
  padding: 0 40px; /* Space for scroll buttons */
}

.related-products-grid {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: 20px;
  padding: 10px 0;
  scroll-behavior: smooth;
  transition: transform 0.3s ease;
  /* Hide scrollbar for cleaner look */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.related-products-grid::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.related-product {
  flex: 0 0 200px;
  text-decoration: none;
  color: inherit;
}

.related-product-card {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease, filter 0.3s ease;
}

.related-product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  filter: brightness(1.05);
}

.related-product-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-bottom: 1px solid #eee;
}

.related-product-info {
  padding: 10px;
  text-align: center;
}

.related-product-name {
  font-size: 1rem;
  font-weight: 500;
  color: #333;
  margin: 5px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-product-price {
  font-size: 0.9rem;
  font-weight: 600;
  color: #007bff;
}

.no-related {
  padding: 20px;
  text-align: center;
  color: #666;
  font-size: 1rem;
}

.show-more {
  display: inline-block;
  font-weight: 600;
  color: #fff;
  background-color: #007bff;
  padding: 10px 20px;
  margin-left: 40 px;
  border-radius: 8px;
  text-transform: uppercase;
  text-decoration: none;
  margin: 20px auto;
  text-align: center;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  
}

.show-more:hover {
  background-color: #0056b3;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);

}

/* Scroll Buttons for Related Products */
.scroll-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 123, 255, 0.8);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease, opacity 0.3s ease;
}

.scroll-btn:hover {
  background-color: #0056b3;
}

.scroll-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.scroll-btn.prev {
  left: 0;
}

.scroll-btn.next {
  right: 0;
}

.scroll-btn i {
  font-size: 1.2rem;
}

/* Attributes Section */
.attributes {
  margin-bottom: 20px;
}

.attributes label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.attribute-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.attribute {
  flex: 1;
  min-width: 150px;
}

.attribute select,
.attribute input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

.attribute select:focus,
.attribute input:focus {
  border-color: #007bff;
  outline: none;
}

.selected-attributes {
  margin-top: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.selected-attributes h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.selected-attributes ul {
  list-style: none;
  padding: 0;
}

.selected-attributes li {
  font-size: 0.9rem;
  color: #333;
  margin-bottom: 5px;
}

.selected-attributes li strong {
  font-weight: 500;
}

/* Skeleton for Related Products */
.skeleton-related-products {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: 20px;
  padding: 10px 40px;
}

.skeleton-related-product {
  flex: 0 0 200px;
  text-align: center;
}

.skeleton-related-image {
  width: 100%;
  height: 150px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 10px;
}

.skeleton-related-name {
  width: 80%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin: 0 auto 10px;
}

.skeleton-related-price {
  width: 50%;
  height: 18px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin: 0 auto;
}

/* Shimmer Animation */
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Responsiveness */
@media (max-width: 768px) {
  .related-products {
    padding: 15px 0;
  }

  .related-products-container {
    padding: 0 30px;
  }

  .related-product {
    flex: 0 0 180px;
  }

  .related-product-card {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .related-product-image {
    height: 120px;
  }

  .related-product-name {
    font-size: 0.9rem;
  }

  .related-product-price {
    font-size: 0.85rem;
  }

  .scroll-btn {
    width: 35px;
    height: 35px;
  }

  .scroll-btn i {
    font-size: 1rem;
  }

  .attribute-row {
    flex-direction: column;
    gap: 10px;
  }

  .attribute {
    min-width: 100%;
  }
}

@media (max-width: 480px) {
  .related-products h3 {
    font-size: 1.3rem;
    padding-left: 15px;
  }

  .related-products-container {
    padding: 0 20px;
  }

  .related-product {
    flex: 0 0 160px;
  }

  .related-product-image {
    height: 100px;
  }

  .related-product-name {
    font-size: 0.85rem;
  }

  .related-product-price {
    font-size: 0.8rem;
  }

  .show-more {
    padding: 8px 15px;
    font-size: 0.9rem;
  }
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
