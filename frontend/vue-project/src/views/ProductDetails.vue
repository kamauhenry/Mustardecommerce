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
            <font-awesome-icon icon="share" />
          </a>
          <a :href="instagramShareUrl" target="_blank" class="social-icon instagram" title="Share on Instagram">
            <font-awesome-icon :icon="['fab', 'instagram']" />
          </a>
          <a :href="whatsappShareUrl"   
          target="_blank" class="social-icon whatsapp" title="Share on WhatsApp">
            <font-awesome-icon :icon="['fab', 'whatsapp']" />
          </a>
          <button @click="copyToClipboard" class="social-icon clipboard" title="Copy to Clipboard">
            <font-awesome-icon icon="copy" />
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
                    <span>{{ attr.values.map(v => v.value).join(', ') }}</span>
                  </li>
                </ul>
                <p v-else>No attributes available.</p>
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
                      <font-awesome-icon icon="chevron-left" />
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
                      <font-awesome-icon icon="chevron-right" />
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
                        <font-awesome-icon
                          v-for="star in 5"
                          :key="star"
                          :icon="star <= review.rating ? 'star' : ['far', 'star']"
                          :style="{ color: star <= review.rating ? '#f5c518' : '#ccc' }"
                        />
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
                        <font-awesome-icon
                          v-for="star in 5"
                          :key="star"
                          :icon="star <= (hoveredRating || reviewRating) ? 'star' : ['far', 'star']"
                          @click="reviewRating = star"
                          @mouseover="hoveredRating = star"
                          @mouseleave="hoveredRating = null"
                          :style="{ color: star <= (hoveredRating || reviewRating) ? '#f5c518' : '#ccc' }"
                        />
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
                      <!-- In ProductDetails.vue template -->
                      <div v-if="product.attributes?.length" v-for="attr in product.attributes" :key="attr.id" class="attribute">
                        <label>{{ attr.name }}</label>
                        <select v-model="selectedAttributes[attr.name]" required>
                          <option disabled value="">Select {{ attr.name }}</option>
                          <option v-for="value in attr.values" :key="value.id" :value="value.value">
                            {{ value.value }}
                          </option>
                        </select>
                      </div>
                      <div class="attribute">
                        <label>Quantity</label>
                        <input
                          type="number"
                          v-model.number="quantity"
                          :min="product.moq_per_person || 1"
                          required
                        />
                      </div>
                    </div>
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
                    <div v-if="isLoadingShippingMethods" class="skeleton-shipping">
                      <div v-for="n in 2" :key="n" class="skeleton-shipping-option"></div>
                    </div>
                    <div v-else-if="shippingMethods.length" class="shipping-options">
                      <div
                        v-for="method in shippingMethods"
                        :key="method.id"
                        class="shipping-option"
                      >
                        <input
                          type="radio"
                          :id="`shipping-${method.id}`"
                          name="shipping"
                          :value="method.id"
                          v-model="selectedShippingMethodId"
                        />
                        <label :for="`shipping-${method.id}`">
                          {{ method.name }} (KES {{ method.price }})
                        </label>
                      </div>
                    </div>
                    <div v-else class="no-shipping">
                      No shipping methods available.
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
                <p v-if="selectedShippingMethod" class="shipping-cost">
                  Shipping Cost: KES {{ selectedShippingMethod.price }}
                </p>
                <p class="total-price">
                  Total: KES {{ totalPrice }}
                </p>
              </div>

              <!-- Add to Cart Button -->
              <div class="control">
                <button
                  class="add-to-cart"
                  @click="handleAddToCart"
                  :disabled="isAddingToCart || !allAttributesSelected || !selectedShippingMethodId"
                  :aria-label="isAddingToCart ? 'Adding to cart' : 'Add to cart'"
                >
                  <span v-if="isAddingToCart">
                    <font-awesome-icon icon="spinner" spin /> Adding to Cart...
                  </span>
                  <span v-else>Add to Cart</span>
                </button>
              </div>

              <!-- Rating -->
              <div class="rating">
                <font-awesome-icon
                  v-for="star in 5"
                  :key="star"
                  :icon="star <= Math.round(product.rating || 0) ? 'star' : ['far', 'star']"
                  style="color: #f5c518;"
                />
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
            <div class="related-products-grid" ref="relatedContainer">
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
              <font-awesome-icon icon="chevron-left" />
            </button>
            <button
              class="scroll-btn next"
              @click="scrollRelatedProducts('right')"
              :disabled="relatedScrollOffset >= maxRelatedScrollOffset"
              aria-label="Scroll right"
            >
              <font-awesome-icon icon="chevron-right" />
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
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
    const relatedCardWidth = ref(220);
    const relatedContainer = ref(null);
    const maxRelatedScrollOffset = computed(() =>
      Math.max(0, ((relatedProducts.value.length || 0) - 3) * relatedCardWidth.value)
    );

    // Form state
    const quantity = ref(1);
    const selectedAttributes = ref({});
    const shippingMethod = ref('ship');
    const promoCode = ref('');
    const placeholderImage = '/path/to/placeholder.jpg'; // Replace with actual image path

    // Tab state
    const activeTab = ref('Description');
    const tabs = ['Description', 'Gallery', 'Review', 'Order'];

    // Gallery state
    const currentImage = ref(null);
    const thumbnailOffset = ref(0);
    const thumbnailsPerPage = 4;
    const thumbnailWidth = ref(70);
    const thumbnailContainer = ref(null);
    const maxThumbnailOffset = computed(() =>
      Math.max(0, ((product.value?.images?.length || 0) - thumbnailsPerPage) * thumbnailWidth.value)
    );

    // Review state
    const reviews = ref([]);
    const showReviewForm = ref(false);
    const reviewContent = ref('');
    const reviewRating = ref(1);
    const hoveredRating = ref(null);
    const isSubmittingReview = ref(false);

    // Shipping Methods
    const shippingMethods = ref([]);
    const isLoadingShippingMethods = ref(false);
    const selectedShippingMethodId = ref(null);
    const selectedShippingMethod = computed(() =>
      shippingMethods.value.find(method => method.id === selectedShippingMethodId.value) || null
    );

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

    const xShareUrl = computed(() =>
      `https://x.com/intent/tweet?text=${encodeURIComponent(shareText.value)}`
    );
    const instagramShareUrl = computed(() =>
      `https://www.instagram.com/?url=${encodeURIComponent(productUrl.value)}`
    );
    const whatsappShareUrl = computed(() =>
      `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText.value)}`
    );

    const copyToClipboard = async () => {
      try {
        await navigator.clipboard.writeText(productUrl.value);
        toast.success('Link copied to clipboard!', { autoClose: 3000 });
      } catch (err) {
        toast.error('Failed to copy link.', { autoClose: 3000 });
      }
    };

    const attributeOptions = computed(() => {
      const options = {};
      if (product.value?.attributes) {
        product.value.attributes.forEach(attr => {
          options[attr.name] = attr.values.map(val => val.value);
          if (options[attr.name].length && !selectedAttributes.value[attr.name]) {
            selectedAttributes.value[attr.name] = options[attr.name][0];
          }
        });
      }
      return options;
    });

    const totalPrice = computed(() => {
      const productPrice = Number(effectivePrice.value) || 0;
      const shippingCost = selectedShippingMethod.value ? Number(selectedShippingMethod.value.price) : 0;
      return (productPrice + shippingCost).toFixed(2);
    });

    const effectivePrice = computed(() => {
      if (!product.value) return '0';
      const qty = Number(quantity.value) || 1;
      const moqPerPerson = Number(product.value.moq_per_person) || 2;
      const belowMoqPrice =
        Number(product.value.below_moq_price) || Number(product.value.price) || 0;
      const price = Number(product.value.price) || 0;
      if (product.value.moq_status === 'active' && qty < moqPerPerson) {
        return (belowMoqPrice * qty).toFixed(2);
      }
      return (price * qty).toFixed(2);
    });

    const allAttributesSelected = computed(() => {
      if (!product.value?.attributes || !product.value.attributes.length) {
        return true; // No attributes required
      }
      return product.value.attributes.every(attr => selectedAttributes.value[attr.name]);
    });

    const scrollThumbnails = async (direction) => {
      if (direction === 'left' && thumbnailOffset.value > 0) {
        thumbnailOffset.value -= thumbnailWidth.value;
      } else if (
        direction === 'right' &&
        thumbnailOffset.value < maxThumbnailOffset.value
      ) {
        thumbnailOffset.value += thumbnailWidth.value;
      }
      await nextTick();
      if (thumbnailContainer.value) {
        thumbnailContainer.value.style.transform = `translateX(-${thumbnailOffset.value}px)`;
      }
    };

    const scrollRelatedProducts = async (direction) => {
      if (direction === 'left' && relatedScrollOffset.value > 0) {
        relatedScrollOffset.value -= relatedCardWidth.value;
      } else if (
        direction === 'right' &&
        relatedScrollOffset.value < maxRelatedScrollOffset.value
      ) {
        relatedScrollOffset.value += relatedCardWidth.value;
      }
      await nextTick();
      if (relatedContainer.value) {
        relatedContainer.value.style.transform = `translateX(-${relatedScrollOffset.value}px)`;
      }
    };





    const fetchShippingMethods = async () => {
      isLoadingShippingMethods.value = true;
      try {
        const response = await api.get('/shipping-methods/');
        shippingMethods.value = response.data;
        if (shippingMethods.value.length && !selectedShippingMethodId.value) {
          selectedShippingMethodId.value = shippingMethods.value[0].id;
        }
      } catch (error) {
        shippingMethods.value = [];
        toast.error('Failed to load shipping methods.', { autoClose: 3000 });
      } finally {
        isLoadingShippingMethods.value = false;
      }
    };

    const handleAddToCart = async () => {
      if (!allAttributesSelected.value) {
        toast.warning('Please select all attributes', { autoClose: 3000 });
        return;
      }
      if (!selectedShippingMethodId.value) {
        toast.warning('Please select a shipping method', { autoClose: 3000 });
        return;
      }
      if (isAddingToCart.value) return;
      isAddingToCart.value = true;
      try {
        const affiliateCodeFromUrl = new URLSearchParams(window.location.search).get('aff');
        await store.addToCart(
          product.value.id,
          selectedAttributes.value,
          quantity.value,
          affiliateCodeFromUrl,
          selectedShippingMethodId.value
        );
        toast.success('Product added to cart successfully!', { autoClose: 3000 });
      } catch (error) {
        console.error('Add to cart error:', error);
        let errorMessage = 'Failed to add to cart.';
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response?.data?.error) {
          errorMessage = error.response.data.error;
        }
        toast.error(errorMessage, { autoClose: 3000 });
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
        toast.error(errorMessage, { autoClose: 3000 });
      } finally {
        isSubmittingReview.value = false;
      }
    };

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
        toast.error('Failed to load product details.', { autoClose: 3000 });
      } finally {
        isLoadingProduct.value = false;
      }
    };

    onMounted(() => {
      fetchShippingMethods();
      nextTick(() => {
        if (thumbnailContainer.value) {
          const firstThumbnail = thumbnailContainer.value.querySelector('.thumbnail');
          if (firstThumbnail) {
            thumbnailWidth.value = firstThumbnail.offsetWidth + 10;
          }
        }
        if (relatedContainer.value) {
          const firstCard = relatedContainer.value.querySelector('.related-product');
          if (firstCard) {
            relatedCardWidth.value = firstCard.offsetWidth + 24;
          }
        }
      });
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
        selectedAttributes.value = {};
        if (newProduct?.attributes) {
          newProduct.attributes.forEach(attr => {
            if (attr.values.length > 0) {
              selectedAttributes.value[attr.name] = attr.values[0].value; // Preselect first value
            }
          });
        }
      },
      { immediate: true }
    );

    watch(
      () => product.value?.images?.length,
      () => {
        thumbnailOffset.value = 0;
        nextTick(() => {
          if (thumbnailContainer.value) {
            thumbnailContainer.value.style.transform = `translateX(0px)`;
          }
        });
      }
    );

    watch(
      () => relatedProducts.value.length,
      () => {
        relatedScrollOffset.value = 0;
        nextTick(() => {
          if (relatedContainer.value) {
            relatedContainer.value.style.transform = `translateX(0px)`;
          }
        });
      }
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
      allAttributesSelected,
      handleAddToCart,
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
      thumbnailContainer,
      relatedContainer,

      shippingMethods,
      totalPrice,
      isLoadingShippingMethods,
      selectedShippingMethodId,
      selectedShippingMethod,
      fetchShippingMethods,
    };
  },
};
</script>

<style scoped>
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

.social-icon svg {
  font-size: 1.2rem;
}

.social-icon.x {
  background-color: #000000;
}

.social-icon.instagram {
  background: radial-gradient(
    circle at 30% 107%,
    #fdf497 0%,
    #fdf497 5%,
    #fd5949 45%,
    #d6249f 60%,
    #285aeb 90%
  );
}

.social-icon.whatsapp {
  background-color: #25d366;
}

.social-icon.clipboard {
  background-color: #ff7b00;
  border: none;
  cursor: pointer;
}

.social-icon:hover {
  opacity: 0.9;
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
  display: flex;
  gap: 10px;
  align-items: baseline;
}

.description ul li strong {
  font-weight: 700;
}

/* Gallery */
.product-images {
  position: relative;
}

.main-image-container {
  width: 100%;
  padding-top: 75%;
  position: relative;
  background-color: #f0f0f0;
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
  width: 100%;
  overflow: hidden;
}

.thumbnail-container {
  display: flex;
  gap: 10px;
  transition: transform 0.3s ease;
  overflow: hidden;
  flex: 1;
  justify-content: center;
  width: calc(70px * 4 + 10px * 3);
  max-width: 100%;
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
  border-color: #ff7b00;
}

.thumbnail-nav {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  border: none;
  padding: 8px;
  cursor: pointer;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
}

.thumbnail-nav:hover {
  background: rgba(0, 0, 0, 0.9);
}

.thumbnail-nav:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.thumbnail-nav.prev {
  left: -16px;
}

.thumbnail-nav.next {
  right: -16px;
}

.thumbnail-nav svg {
  font-size: 1rem;
}

/* Reviews Tab */
.reviews-tab {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

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

.review-rating svg {
  font-size: 1rem;
}

.review-meta {
  font-size: 0.85rem;
  color: #666;
  font-style: italic;
}

.no-reviews {
  font-size: 1rem;
  color: #666;
  text-align: center;
  margin: 20px 0;
  font-weight: 500;
}

.login-prompt {
  font-size: 1rem;
  color: #666;
  text-align: center;
  margin: 20px 0;
}

.login-prompt a {
  color: #ff7b00;
  text-decoration: none;
}

.login-prompt a:hover {
  text-decoration: underline;
}

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
  background-color: #ffa200;
}

.button:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transform: translateY(-1px);
}

.button-primary {
  background-color: #ff7b00;
}

.button-secondary {
  background-color: #6c757d;
}

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

.review-form textarea:focus {
  border-color: #ff7b00;
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

.star-rating svg {
  font-size: 1.2rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 10px;
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

.skeleton-shipping {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-shipping-option {
  height: 20px;
  background: #e0e0e0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}

.shipping-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shipping-option {
  display: flex;
  align-items: center;
  gap: 10px;
}

.shipping-option input[type="radio"] {
  margin: 0;
}

.shipping-option label {
  flex: 1;
}

.no-shipping {
  color: #888;
  font-style: italic;
}

.pricing .shipping-cost,
.pricing .total-price {
  font-size: 1.1rem;
  margin: 10px 0;
}

.pricing .total-price {
  font-weight: bold;
  color: #2c3e50;
}

/* Animation for skeleton */
@keyframes pulse {
  0% {
    background-color: #e0e0e0;
  }
  50% {
    background-color: #f5f5f5;
  }
  100% {
    background-color: #e0e0e0;
  }
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

.add-to-cart:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.rating svg {
  font-size: 1rem;
}

.rating span {
  font-size: 0.9rem;
  color: #666;
}

/* Related Products */
.related-products {
  margin-top: 40px;
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

.related-products h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 1.5rem;
  padding-left: 1rem;
  letter-spacing: 0.5px;
}

.related-products-container {
  position: relative;
  padding: 0 3rem;
  overflow: hidden;
  width: 100%;
}

.related-products-grid {
  display: flex;
  flex-wrap: nowrap;
  gap: 1.5rem;
  padding: 0.5rem 0;
  transition: transform 0.4s ease-in-out;
  scrollbar-width: none;
  -ms-overflow-style: none;
  overflow: hidden;
  width: calc(220px * 3 + 1.5rem * 2);
}

.related-products-grid::-webkit-scrollbar {
  display: none;
}

.related-product {
  flex: 0 0 220px;
  text-decoration: none;
  color: inherit;
  transition: transform 0.3s ease;
}

.related-product-card {
  background-color: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease, filter 0.3s ease;
}

.related-product-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  filter: brightness(1.03);
}

.related-product-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-bottom: 1px solid #f1f1f1;
  transition: transform 0.3s ease;
}

.related-product-card:hover .related-product-image {
  transform: scale(1.05);
}

.related-product-info {
  padding: 1rem;
  text-align: center;
}

.related-product-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c2c2c;
  margin: 0.5rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.2s ease;
}

.related-product-card:hover .related-product-name {
  color: #ff7b00;
}

.related-product-price {
  font-size: 1rem;
  font-weight: 700;
  color: #ff7b00;
  letter-spacing: 0.5px;
}

.no-related {
  padding: 1.5rem;
  text-align: center;
  color: #666;
  font-size: 1.1rem;
  font-weight: 500;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.show-more {
  display: inline-block;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(90deg, #ff7b00, #d47304);
  padding: 0.75rem 1rem;
  border-radius: 10px;
  text-transform: uppercase;
  text-decoration: none;
  margin: 1.5rem auto;
  text-align: center;
  transition: background 0.3s ease, box-shadow 0.3s ease, transform 0.2s ease;
}

.show-more:hover {
  background: linear-gradient(90deg, #b8470a, #e05d0c);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

/* Scroll Buttons for Related Products */
.scroll-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: linear-gradient(45deg, #ff7b00, #00aaff);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: background 0.3s ease, transform 0.2s ease, opacity 0.3s ease;
}

.scroll-btn:hover {
  background: linear-gradient(45deg, #0056b3, #ff7b00);
  transform: translateY(-50%) scale(1.05);
}

.scroll-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #ccc;
}

.scroll-btn.prev {
  left: 0.5rem;
}

.scroll-btn.next {
  right: 0.5rem;
}

.scroll-btn svg {
  font-size: 1.4rem;
}

/* Skeleton for Related Products */
.skeleton-related-products {
  display: flex;
  flex-wrap: nowrap;
  gap: 1.5rem;
  padding: 0.5rem 3rem;
}

.skeleton-related-product {
  flex: 0 0 220px;
  text-align: center;
}

.skeleton-related-image {
  width: 100%;
  height: 160px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
  margin-bottom: 0.75rem;
}

.skeleton-related-name {
  width: 80%;
  height: 22px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
  margin: 0 auto 0.5rem;
}

.skeleton-related-price {
  width: 50%;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
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
  .product-content {
    flex-direction: column;
    gap: 20px;
  }

  .product-left,
  .product-right {
    width: 100%;
  }

  .product-right {
    padding: 15px;
  }

  .product-title {
    font-size: 1.5rem;
  }

  .tabs {
    gap: 10px;
  }

  .tabs button {
    font-size: 0.9rem;
  }

  .thumbnails {
    max-width: 100%;
  }

  .thumbnail {
    width: 50px;
    height: 50px;
  }

  .thumbnail-container {
    justify-content: flex-start;
  }

  .thumbnail-nav {
    padding: 5px;
  }

  .social-sharing {
    gap: 10px;
  }

  .social-icon {
    width: 28px;
    height: 28px;
  }

  .social-icon svg {
    font-size: 1rem;
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

  .star-rating svg {
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

  .attribute-row {
    flex-direction: column;
    gap: 10px;
  }

  .attribute {
    min-width: 100%;
  }

  .related-products {
    padding: 1.5rem;
    border-radius: 12px;
  }

  .related-products h3 {
    font-size: 1.5rem;
    padding-left: 0.75rem;
  }

  .related-products-container {
    padding: 0 2rem;
  }

  .related-product {
    flex: 0 0 200px;
  }

  .related-product-card {
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  }

  .related-product-image {
    height: 140px;
  }

  .related-product-name {
    font-size: 1rem;
  }

  .related-product-price {
    font-size: 0.9rem;
  }

  .scroll-btn {
    width: 40px;
    height: 40px;
  }

  .scroll-btn svg {
    font-size: 1.2rem;
  }

  .show-more {
    padding: 0.6rem 1.2rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .related-products {
    padding: 1rem;
  }

  .related-products h3 {
    font-size: 1.3rem;
  }

  .related-products-container {
    padding: 0 1.5rem;
  }

  .related-product {
    flex: 0 0 180px;
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
    width: 36px;
    height: 36px;
  }

  .scroll-btn svg {
    font-size: 1rem;
  }

  .show-more {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }
}
</style>