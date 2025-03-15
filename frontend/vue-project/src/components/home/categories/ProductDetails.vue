<!-- views/ProductDetails.vue -->
<template>
  <MainLayout>
    <div class="product-details-page">
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> >
        <router-link :to="`/category/${product?.category?.id}`">
          {{ product?.category?.name }}
        </router-link> >
        <span>{{ product?.name }}</span>
      </div>

      <div class="product-details">
        <div class="product-images">
          <img :src="mainImage" :alt="product?.name" class="main-image" />
          <div class="thumbnails">
            <img
              v-for="(thumb, index) in thumbnails"
              :key="index"
              :src="thumb"
              :alt="'Thumbnail ' + index"
              @click="mainImage = thumb"
              class="thumbnail"
            />
          </div>
        </div>

        <div class="product-info">
          <h1>{{ product?.name }}</h1>
          <p class="price">KES {{ product?.price }}</p>
          <p v-if="product?.below_moq_price" class="moq">Below MOQ Price: KES {{ product.below_moq_price }}</p>
          <p v-if="product?.moq_status === 'active'" class="moq-details">MOQ: {{ product.moq }} items</p>
          <p v-if="product?.moq_status === 'active'" class="moq-details">MOQ Progress: {{ product.moq_progress_percentage }}%</p>
          <p v-if="product?.moq_status === 'active'" class="moq-details">Max Per Person: {{ product.moq_per_person }}</p>
          <div class="rating">Rating: {{ product?.rating || 'No rating' }}</div>

          <div class="order-options">
            <h3>Total Quantity</h3>
            <input type="number" v-model.number="quantity" :max="product?.moq_per_person" min="1" class="quantity-input" />

            <h3>Order Attributes</h3>
            <div class="attributes">
              <div class="attribute-field">
                <label>Size</label>
                <select v-model="selectedSize" class="select-field">
                  <option disabled value="">Select Size</option>
                  <option v-for="size in uniqueSizes" :key="size" :value="size">{{ size }}</option>
                </select>
              </div>
              <div class="attribute-field">
                <label>Color</label>
                <select v-model="selectedColor" class="select-field">
                  <option disabled value="">Select Color</option>
                  <option v-for="color in uniqueColors" :key="color" :value="color">{{ color }}</option>
                </select>
              </div>
            </div>

            <h3>Shipping Method</h3>
            <div class="shipping-methods">
              <label class="shipping-option">
                <input type="radio" v-model="shippingMethod" value="standard" />
                Standard (KES 150 each)
              </label>
              <label class="shipping-option">
                <input type="radio" v-model="shippingMethod" value="express" />
                Express (KES 600 each)
              </label>
            </div>

            <h3>Promo Code</h3>
            <input type="text" v-model="promoCode" placeholder="e.g. 1C6TPB38" class="promo-input" />
          </div>

          <div class="action-buttons">
            <button @click="viewSummary" class="summary-btn">View Summary</button>
            <button @click="addToCart" class="cart-btn">Add to Cart</button>
          </div>
        </div>
      </div>

      <div v-if="showSummary" class="modal">
        <div class="modal-content">
          <h2>Order Summary</h2>
          <p><strong>Product:</strong> {{ product?.name }}</p>
          <p><strong>Price:</strong> KES {{ product?.price }}</p>
          <p><strong>Quantity:</strong> {{ quantity }}</p>
          <p><strong>Size:</strong> {{ selectedSize || 'Not selected' }}</p>
          <p><strong>Color:</strong> {{ selectedColor || 'Not selected' }}</p>
          <p><strong>Shipping Method:</strong> {{ shippingMethod === 'standard' ? 'Standard (KES 150 each)' : 'Express (KES 600 each)' }}</p>
          <p><strong>Promo Code:</strong> {{ promoCode || 'None' }}</p>
          <p><strong>Total:</strong> KES {{ calculateTotal() }}</p>
          <button @click="showSummary = false" class="close-btn">Close</button>
        </div>
      </div>

      <div class="tabs">
        <button :class="{ active: activeTab === 'description' }" @click="activeTab = 'description'">Description</button>
        <button :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">Customer Reviews</button>
      </div>
      <div class="tab-content">
        <div v-if="activeTab === 'description'">
          <p>{{ product?.description }}</p>
        </div>
        <div v-if="activeTab === 'reviews'">
          <div v-if="reviews.length">
            <div v-for="review in reviews" :key="review.id" class="review">
              <p><strong>{{ review.user.username }}</strong> (Rating: {{ review.rating }}/5)</p>
              <p>{{ review.content }}</p>
              <p class="review-date">{{ new Date(review.created_at).toLocaleDateString() }}</p>
            </div>
          </div>
          <p v-else>No reviews yet. Be the first to review this product!</p>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { useProductStore } from '@/stores/products';
import { useCartStore } from '@/stores/cart';
import MainLayout from "@/components/navigation/MainLayout.vue";

export default {
  components: { MainLayout },
  setup() {
    const productStore = useProductStore();
    const cartStore = useCartStore();
    return { productStore, cartStore };
  },
  data() {
    return {
      quantity: 1,
      selectedSize: "",
      selectedColor: "",
      shippingMethod: "standard",
      promoCode: "",
      activeTab: "description",
      showSummary: false,
      mainImage: "",
    };
  },
  computed: {
    product() {
      return this.productStore.currentProduct;
    },
    variants() {
      return this.productStore.variants;
    },
    reviews() {
      return this.productStore.reviews;
    },
    uniqueSizes() {
      return [...new Set(this.variants.map(variant => variant.size))];
    },
    uniqueColors() {
      return [...new Set(this.variants.map(variant => variant.color))];
    },
    selectedVariant() {
      return this.variants.find(variant => variant.size === this.selectedSize && variant.color === this.selectedColor);
    },
    thumbnails() {
      if (!this.product) return [];
      return [
        this.product.thumbnail || 'https://picsum.photos/80/80',
        `https://picsum.photos/id/${this.product.id + 1}/80/80`,
        `https://picsum.photos/id/${this.product.id + 2}/80/80`,
      ];
    },
  },
  async created() {
    const { category_slug, product_slug } = this.$route.params;
    await this.productStore.fetchProduct(category_slug, product_slug);
    if (this.product) {
      this.mainImage = this.product.thumbnail || 'https://picsum.photos/200/300';
      await this.productStore.fetchVariants(this.product.id);
      await this.productStore.fetchReviews(this.product.id);
    }
  },
  methods: {
    calculateTotal() {
      const basePrice = (this.product?.price || 0) * this.quantity;
      const shippingCost = this.shippingMethod === 'standard' ? 150 * this.quantity : 600 * this.quantity;
      return basePrice + shippingCost;
    },
    viewSummary() {
      if (!this.selectedVariant) {
        alert('Please select a size and color.');
        return;
      }
      this.showSummary = true;
    },
    async addToCart() {
      if (!this.selectedVariant) {
        alert('Please select a size and color.');
        return;
      }
      try {
        await this.cartStore.addToCart({
          productId: this.product.id,
          variantId: this.selectedVariant.id,
          quantity: this.quantity,
        });
        alert(`Added ${this.product.name} to cart!`);
        this.$router.push("/cart");
      } catch (error) {
        alert(error.response?.data?.error || 'Failed to add to cart. Please try again.');
      }
    },
  },
};
</script>

<style scoped>
.product-details-page {
  padding: 20px;
  background: #1a1a1a;
  color: #fff;
  font-family: Arial, sans-serif;
}

.breadcrumb {
  margin-bottom: 20px;
  color: #ffcc00;
  font-size: 14px;
}

.breadcrumb a {
  color: #ffcc00;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb span {
  color: #fff;
}

.product-details {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
}

.product-images {
  flex: 1;
  max-width: 50%;
}

.main-image {
  width: 100%;
  height: 400px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #333;
}

.thumbnails {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid #444;
}

.thumbnail:hover {
  border-color: #ff6200;
  opacity: 0.8;
}

.product-info {
  flex: 1;
  padding: 20px;
  background: #333;
  border-radius: 8px;
}

.product-info h1 {
  font-size: 24px;
  margin-bottom: 10px;
  color: #fff;
}

.price {
  color: #ffcc00;
  font-size: 20px;
  font-weight: bold;
  margin: 10px 0;
}

.moq {
  color: #ccc;
  font-size: 14px;
  margin: 5px 0;
}

.moq-details {
  color: #999;
  font-size: 12px;
  margin: 2px 0;
}

.progress-text {
  color: #ffcc00;
  font-size: 14px;
  margin: 10px 0;
}

.rating {
  color: #ccc;
  margin: 10px 0;
}

.order-options {
  margin-top: 20px;
}

.order-options h3 {
  font-size: 16px;
  color: #ff6200;
  margin-bottom: 10px;
  border-bottom: 1px solid #444;
  padding-bottom: 5px;
}

.quantity-input,
.select-field,
.promo-input {
  width: 100%;
  padding: 8px;
  margin: 5px 0;
  border-radius: 4px;
  border: 1px solid #555;
  background: #222;
  color: #fff;
}

.attributes {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.attribute-field {
  flex: 1;
}

.shipping-methods {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shipping-option {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #ccc;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.summary-btn,
.cart-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.summary-btn {
  background: #444;
  color: #fff;
}

.summary-btn:hover {
  background: #555;
}

.cart-btn {
  background: #ff6200;
  color: #fff;
}

.cart-btn:hover {
  background: #e55b00;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: #333;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  color: #fff;
}

.modal-content h2 {
  color: #ff6200;
  margin-bottom: 15px;
}

.modal-content p {
  margin: 5px 0;
}

.close-btn {
  padding: 8px 15px;
  background: #ff6200;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 15px;
}

.close-btn:hover {
  background: #e55b00;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  background: none;
  color: #ccc;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tabs button.active {
  color: #fff;
  border-bottom: 2px solid #ffcc00;
}

.tab-content {
  padding: 20px;
  background: #333;
  border-radius: 8px;
}

.review {
  border-bottom: 1px solid #444;
  padding: 10px 0;
}

.review-date {
  color: #999;
  font-size: 12px;
}
</style>
