
<template>
  <MainLayout>
    <div class="product-detail-container" v-if="product">
      <div class="breadcrumb">
        <router-link to="/">Home</router-link> &gt;
        <router-link :to="`/category/${product.category_name}`">{{ product.category_name }}</router-link> &gt;
        <span>{{ product.name }}</span>
      </div>
  
      <div class="product-main">
        <div class="product-gallery">
          <div class="main-image">
            <img :src="product.picture || product.thumbnail" :alt="product.name" class="product-image">
          </div>
          <div class="thumbnail-gallery">
            <!-- Would show additional images if available -->
            <img :src="product.thumbnail" :alt="product.name" class="thumbnail-image">
          </div>
        </div>
  
        <div class="product-info">
          <h1 class="product-title">{{ product.name }}</h1>
          
          <div class="product-price-info">
            <div class="regular-price">
              <span class="price-label">KES {{ product.price }}</span>
              <div v-if="product.moq_status === 'active'" class="moq-info">
                <span class="below-moq-price">Below MOQ price: KES {{ product.below_moq_price || product.price }}</span>
                <div class="moq-progress">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="`width: ${product.moq_progress?.percentage || 0}%`"></div>
                  </div>
                  <span class="progress-text">
                    {{ product.moq_progress?.current || 0 }}/{{ product.moq }} 
                    ({{ product.moq_progress?.percentage || 0 }}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
  
          <div class="moq-per-person" v-if="product.moq_status === 'active'">
            MOQ Per Person: {{ product.moq_per_person }} items/bundle
          </div>
  
          <div class="order-section">
            <h3>Order</h3>
            
            <div class="quantity-selector">
              <label for="quantity">Total Quantity</label>
              <input 
                type="number" 
                id="quantity" 
                v-model.number="quantity" 
                :min="product.moq_per_person" 
                :step="product.moq_per_person"
                class="quantity-input"
              >
            </div>
  
            <div class="order-attributes">
              <div class="variant-selector">
                <div class="size-selector">
                  <label for="size">Size/Patterns</label>
                  <select id="size" v-model="selectedSize" class="variant-select">
                    <option value="" disabled>Select Size/Patterns</option>
                    <option 
                      v-for="size in availableSizes" 
                      :key="size" 
                      :value="size"
                    >
                      {{ size }}
                    </option>
                  </select>
                </div>
  
                <div class="color-selector">
                  <label for="color">Color</label>
                  <select id="color" v-model="selectedColor" class="variant-select">
                    <option value="" disabled>Select color</option>
                    <option 
                      v-for="color in availableColors" 
                      :key="color" 
                      :value="color"
                    >
                      {{ color }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
  
            <div class="shipping-method">
              <h4>Shipping Method</h4>
              <div class="shipping-options">
                <label class="shipping-option">
                  <input type="radio" v-model="shippingMethod" value="standard">
                  Ship Approximation cost KES 310 each
                </label>
                <label class="shipping-option">
                  <input type="radio" v-model="shippingMethod" value="air">
                  Air Approximate cost
                </label>
              </div>
            </div>
  
            <div class="promo-code">
              <label for="promo">Promo Code</label>
              <input type="text" id="promo" v-model="promoCode" class="promo-input">
            </div>
  
            <button 
              @click="addToCart" 
              class="add-to-cart-button"
              :disabled="!isValidSelection"
            >
              Add to Cart
            </button>
          </div>
        </div>
      </div>
  
      <div class="product-description">
        <h2>Description</h2>
        <div v-html="product.description"></div>
      </div>
  
      <div class="customer-reviews">
        <h2>Customer Review</h2>
        <div class="rating-display">
          <span class="stars">
            <span v-for="i in 5" :key="i" :class="['star', i <= product.rating ? 'filled' : '']">★</span>
          </span>
          <span class="rating-value">{{ product.rating }}</span>
        </div>
        <button class="add-review-button">Add Review</button>
      </div>
    </div>
    <div v-else class="loading">
      Loading product details...
    </div>
  </MainLayout>
  </template>
  
  <script>
  import MainLayout from "@/components/navigation/MainLayout.vue";
  import axios from 'axios';
  
  export default {
    components: {
      MainLayout,
    },
    name: 'ProductDetail',
    props: {
      categorySlug: {
        type: String,
        required: true
      },
      productSlug: {
        type: String,
        required: true
      }
    },
    data() {
      return {
        product: null,
        loading: true,
        quantity: 1,
        selectedSize: '',
        selectedColor: '',
        shippingMethod: 'standard',
        promoCode: '',
        selectedVariantId: null
      };
    },
    computed: {
      availableSizes() {
        if (!this.product || !this.product.variants) return [];
        return [...new Set(this.product.variants.map(v => v.size))];
      },
      availableColors() {
        if (!this.product || !this.product.variants) return [];
        if (this.selectedSize) {
          return [...new Set(this.product.variants
            .filter(v => v.size === this.selectedSize)
            .map(v => v.color))];
        }
        return [...new Set(this.product.variants.map(v => v.color))];
      },
      isValidSelection() {
        return this.quantity > 0 && this.selectedSize && this.selectedColor;
      },
      selectedVariant() {
        if (!this.product || !this.selectedVariantId) return null;
        return this.product.variants.find(v => v.id === this.selectedVariantId);
      }
    },
    watch: {
      selectedSize() {
        this.selectedColor = '';
        this.updateSelectedVariant();
      },
      selectedColor() {
        this.updateSelectedVariant();
      }
    },
    created() {
      this.fetchProductDetails();
    },
    methods: {
      fetchProductDetails() {
        this.loading = true;
        axios.get(`/api/products/${this.categorySlug}/${this.productSlug}/`)
          .then(response => {
            this.product = response.data;
            if (this.product.moq_status === 'active' && this.product.moq_per_person > 1) {
              this.quantity = this.product.moq_per_person;
            }
            this.loading = false;
          })
          .catch(error => {
            console.error('Error fetching product details:', error);
            this.loading = false;
          });
      },
      updateSelectedVariant() {
        if (!this.selectedSize || !this.selectedColor || !this.product) {
          this.selectedVariantId = null;
          return;
        }
        const variant = this.product.variants.find(
          v => v.size === this.selectedSize && v.color === this.selectedColor
        );
        this.selectedVariantId = variant ? variant.id : null;
      },
      addToCart() {
        if (!this.isValidSelection) return;
        if (this.product.moq_status === 'active' && 
            this.quantity < this.product.moq_per_person) {
          alert(`Minimum order quantity per person is ${this.product.moq_per_person}`);
          return;
        }
        const cartItem = {
          product: this.product.id,
          variant: this.selectedVariantId,
          quantity: this.quantity
        };
        axios.post('/api/cart/items/', cartItem)
          .then(response => {
            alert('Product added to cart!');
          })
          .catch(error => {
            console.error('Error adding to cart:', error);
            if (error.response && error.response.data) {
              alert(`Error: ${JSON.stringify(error.response.data)}`);
            } else {
              alert('Failed to add product to cart. Please try again.');
            }
          });
      }
    }
  }
  </script>
  
  <style scoped>
  .product-detail-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  .breadcrumb {
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }
  
  .breadcrumb a {
    color: #666;
    text-decoration: none;
  }
  
  .breadcrumb a:hover {
    text-decoration: underline;
  }
  
  .product-main {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
  }
  
  .product-gallery {
    flex: 1;
  }
  
  .main-image {
    width: 100%;
    border: 1px solid #eee;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1rem;
  }
  
  .product-image {
    width: 100%;
    height: auto;
    display: block;
  }
  
  .thumbnail-gallery {
    display: flex;
    gap: 0.5rem;
  }
  
  .thumbnail-image {
    width: 80px;
    height: 80px;
    object-fit: cover;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .product-info {
    flex: 1;
  }
  
  .product-title {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    color: #333;
  }
  
  .product-price-info {
    margin-bottom: 1.5rem;
  }
  
  .price-label {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
  }
  
  .below-moq-price {
    display: block;
    margin-top: 0.5rem;
    color: #666;
  }
  
  .moq-info {
    margin-top: 1rem;
  }
  
  .moq-progress {
    margin-top: 0.5rem;
  }
  
  .progress-bar {
    height: 10px;
    background-color: #eee;
    border-radius: 5px;
    overflow: hidden;
    margin-bottom: 0.25rem;
  }
  
  .progress-fill {
    height: 100%;
    background-color: #8e7d2e;
  }
  
  .progress-text {
    font-size: 0.8rem;
    color: #666;
  }
  
  .moq-per-person {
    margin-bottom: 1.5rem;
    color: #666;
  }
  
  .order-section {
    border-top: 1px solid #eee;
    padding-top: 1.5rem;
  }
  
  .quantity-selector {
    margin-bottom: 1.5rem;
  }
  
  .quantity-input {
    padding: 0.5rem;
    width: 100%;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .order-attributes {
    margin-bottom: 1.5rem;
  }
  
  .variant-selector {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  
  .variant-select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .shipping-method {
    margin-bottom: 1.5rem;
  }
  
  .shipping-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .shipping-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .promo-code {
    margin-bottom: 1.5rem;
  }
  
  .promo-input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .add-to-cart-button {
    width: 100%;
    padding: 0.75rem;
    background-color: #8e7d2e;
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .add-to-cart-button:hover {
    background-color: #7b6b22;
  }
  
  .add-to-cart-button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .product-description {
    margin-bottom: 2rem;
  }
  
  .customer-reviews {
    margin-bottom: 2rem;
  }
  
  .rating-display {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .stars {
    color: #ddd;
  }
  
  .star.filled {
    color: #ffc107;
  }
  
  .add-review-button {
    padding: 0.5rem 1rem;
    background-color: #8e7d2e;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .loading {
    text-align: center;
    padding: 2rem;
    font-size: 1.2rem;
    color: #666;
  }
  
  @media (max-width: 768px) {
    .product-main {
      flex-direction: column;
    }
    
    .variant-selector {
      grid-template-columns: 1fr;
    }
  }
  </style>