<template>
  <div class="category-products">
    <div v-if="loading" class="loading">Loading categories...</div>
    <div v-else-if="!categories.length" class="no-categories">No categories available.</div>
    
    <!-- Container for 2-column category layout -->
    <div class="categories-grid">
      <div v-for="(category, index) in categories" :key="category.id" class="category-section">
        <div class="category-header">
          <h2 class="category-title">{{ category.name }}</h2>
          <router-link :to="`/category/${category.slug}`" class="see-more-button">See more</router-link>
        </div>
        
        <div class="products-grid">
          <div v-for="product in getLatestProducts(category.products)" :key="product.id" class="product-card">
            <!-- Make the entire card clickable to go to product detail -->
            <router-link :to="`/product/${category.slug}/${product.slug}`" class="product-link">
              <div class="product-image">
                <img :src="product.thumbnail || '/path/to/placeholder.jpg'" :alt="product.name">
              </div>
              
              <div class="product-info">
                <h3 class="product-name">{{ product.name }}</h3>
                <div class="product-moq">MOQ: {{ product.minimum_order_quantity || product.moq || 1 }}</div>
                <div class="product-price">
                  Below MOQ Price: KES {{ product.below_moq_price || product.price }}
                </div>
                <div class="product-status">
                  <span class="status-active">{{ product.moq_status || 'Active' }}</span>
                  <span class="status-percentage">{{ product.moq_progress?.percentage || '100' }}%</span>
                  <span :class="['status-availability', isLowStock(product) ? 'low-stock' : 'in-stock']">
                    {{ isLowStock(product) ? 'Low Stock' : 'In Stock' }}
                  </span>
                </div>
              </div>
              
              <div class="product-price-tag">
                KES {{ product.price }}
              </div>
            </router-link>
          </div>
          
          <p v-if="!getLatestProducts(category.products).length" class="no-products">
            No products available in this category.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script>
import axios from 'axios';

export default {
  name: 'CategoryProducts',
  data() {
    return {
      categories: [],
      loading: true,
    };
  },
  mounted() {
    this.fetchCategories();
  },
  methods: {
    async fetchCategories() {
      try {
        const response = await axios.get('/api/all-categories-with-products/');
        console.log('API Response:', response.data);
        
        // Verify data structure and log for debugging
        if (response.data && response.data.length > 0) {
          console.log('First category:', response.data[0].name, 'slug:', response.data[0].slug);
          if (response.data[0].products && response.data[0].products.length > 0) {
            console.log('First product:', response.data[0].products[0].name, 'slug:', response.data[0].products[0].slug);
          }
        }
        
        this.categories = response.data || [];
      } catch (error) {
        console.error('Error fetching categories:', error);
        this.categories = [];
      } finally {
        this.loading = false;
      }
    },
    getLatestProducts(products) {
      // Handle case where products is undefined or not an array
      if (!Array.isArray(products) || !products.length) {
        return []; // Return empty array if no valid products
      }
      // Sort by created_at and take exactly 4 products (2x2 grid)
      return products
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 4);
    },
    isLowStock(product) {
      // For MOQ products, check if we're far from reaching the minimum order threshold
      if (product.moq_status === 'active' && product.moq > 1) {
        // Get the current progress toward MOQ completion
        const currentCount = product.moq_progress?.current || 0;
        const targetMOQ = product.moq || 1;
        const percentage = Math.min(100, Math.floor((currentCount / targetMOQ) * 100));
        
        // Consider "low stock" if we're below 75% of reaching MOQ
        return percentage < 75;
      }
      
      // For regular products (non-MOQ or completed MOQ)
      return false;
    }
  },
};
</script>
  
  <style scoped>

.product-link {
  display: block;
  text-decoration: none;
  color: inherit;
  height: 100%;
}

.product-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}


 .category-products {
  font-family: 'Roboto', sans-serif;
  padding: 8px;
}

.loading, .no-categories {
  text-align: center;
  padding: 15px;
  color: #666;
}

/* Two-column layout for categories */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.category-section {
  background-color: #f2f2f2;
  border-radius: 8px;
  padding: 10px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.category-title {
  color: #606c38;
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.see-more-button {
  background-color: white;
  border: 1px solid #FF8C00;
  border-radius: 15px;
  padding: 2px 10px;
  text-decoration: none;
  color: #333;
  font-size: 11px;
  transition: all 0.2s ease;
}

.see-more-button:hover {
  background-color: #FFF0E0;
}

.see-more-button:active {
  background-color: #FF8C00;
  color: white;
}

/* 2x2 grid for products within each category */
.products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
}

.product-card {
  position: relative;
  background-color: white;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  padding: 6px;
  display: flex;
  flex-direction: column;
  height: auto;
  max-height: 180px;
}

.product-image {
  height: 60px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.product-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.product-info {
  flex-grow: 1;
}

.product-name {
  margin: 0 0 2px 0;
  font-size: 11px;
  font-weight: 500;
  color: #333;
  /* Limit to two lines with ellipsis */
  display: -webkit-box;
  display: box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  max-height: 28px;
}

.product-moq {
  font-size: 9px;
  color: #666;
  margin-bottom: 1px;
}

.product-price {
  font-size: 8px;
  color: #666;
  margin-bottom: 3px;
}

.product-status {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  font-size: 8px;
}

.status-active {
  color: #666;
}

.status-percentage {
  color: #666;
  margin-left: 2px;
}

.status-availability {
  padding: 1px 4px;
  border-radius: 6px;
  font-size: 8px;
  color: white;
  text-align: center;
}

.in-stock {
  background-color: #606c38;
}

.low-stock {
  background-color: #bb6c1a;
}

.product-price-tag {
  position: absolute;
  top: 6px;
  right: 6px;
  background-color: white;
  color: #e63946;
  font-weight: bold;
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 3px;
}

.no-products {
  grid-column: span 2;
  text-align: center;
  color: #888;
  padding: 8px;
}

/* Responsive design */
@media (max-width: 768px) {
  .categories-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .no-products {
    grid-column: span 1;
  }
  
  .category-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .see-more-button {
    margin-top: 5px;
  }
}
  </style>