<template>
  <MainLayout>
    <div class="top-row-home">
      <RecentCampaigns />
      <HomeCarousel />
      <RecentSearches />
    </div>
    <div id="homePage">
      <div v-if="store.loading.allCategoriesWithProducts" class="skeleton-container">
        <div v-for="n in 2" :key="n" class="skeleton-category">
          <div class="skeleton-title"></div>
          <div class="skeleton-products">
            <div v-for="i in 3" :key="i" class="skeleton-product"></div>
          </div>
        </div>
      </div>
      <div v-else-if="store.error.allCategoriesWithProducts" class="error">
        {{ store.error.allCategoriesWithProducts }}
      </div>
      <div v-else class="categories-container">
        <div
          v-for="category in store.allCategoriesWithProducts"
          :key="category.id"
          class="category-card"
        >
          <div class="category-top">
            <h2 class="category-title">{{ category.name }}</h2>
            <router-link
              v-if="category.products && category.products.length > 0"
              :to="`/category/${category.slug}/products`"
              class="see-more-link"
            >
              See More
            </router-link>
          </div>
          <div v-if="category.products && category.products.length > 0" class="products-grid">
            <div
              v-for="product in category.products.slice(0, 3)"
              :key="product.id"
              class="product-card"
            >
              <router-link
                :to="{
                  name: 'product-detail',
                  params: { categorySlug: category.slug, productSlug: product.slug }
                }"
                class="product-link"
              >
                <img
                  :src="product.thumbnail || 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxAQEA8PEBAQDw8PDw8QDQ4PDw8ODw8PFREWFhURFRUYHSggGBolGxUVITEhJSkrLi4uFx8zODMsNygtLisBCgoKDg0OGhAQFy0dHx0tLS0rLS0tLS0tLSstLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLSsrLS0tKy0tLS0tLf/AABEIAL4BCgMBIgACEQEDEQH/xAAaAAABBQEAAAAAAAAAAAAAAAABAAIDBAUG/8QAQRAAAgECAwUEBwQIBQUAAAAAAAECAxEEEiEFMUFRYXGBkbETIjJCocHRBlKC8CMkYqKywuHxFENyktIVM1Njs//EABgBAQADAQAAAAAAAAAAAAAAAAABAgME/8QAIhEBAQEBAAIDAAEFAAAAAAAAAAERAiExAxJBUQQTIjKB/9oADAMBAAIRAxEAPwDqcNM1sNUMGjKxpYeqcXNd3UblGZYSuZ2Hql+lM2lYWK1XCpZo2vSn7cfuv7yMLFYaVOWV6rfGX3lz7TrCpjMKpRcX7O9c4vmhYTpzICfE4eVN2fdJbmiEhoAgiABJh6LnKMI75Pw5sYa32cgs9SXFRSXe9fIItX8PglBwjFaRvKTdryluVy7WdoPr5Clo0+D0G46Wmm5LQn1rPdscN9oI/pLmZJWXJvjxt0Oj2phszMDExvJxW6Lt4HPXZz5U3A2cDQyQS4vV9rI8JhLWlLhuRdL8c55V+TrfACEJs0ZECwRAAA4AAsIIgGiCJeWpArL2n2sjxb/S4ZftVf8A5v6ktNalXGy/WcLHkqsn3xsvJmHPtpWgIIjdmaIIgI6ZZpysQ0kSuJk1q9Qrmnh6vU52NSxewuJLzpn1y6KnMe2UKFcsKoaaxvJlfDqSaaunw5dUY2LwEoar1o/FdpvqQpRGJlxygjcxOChLW2V81oUZ7Ptumu9MhfVEvbHxipVLy9iSyy6cn+eY3/CQW+o+xQf1IqkIL3pduW40zXVZk1pqnutqV6991+wwcDj3TejU4cY33dnJm66salPNF3S1XNc0xquYz6tK7MGnh1Ftvfd38To73MfFxtOS638Vf5lJJrTbIhAOAXQAJx9Sb5Ql420J8PQc30W9h2k1H0dGO+TzyXKEXvfa7LxK2/griCIsAIJewuBus09Fwju8SLcFABcxEqadoxTa462K7k+zsSRS/JEyGZe7q9COpLgu98x8okVWtCCvJpFb3atIMY21eiWrfJGTgZemxM63uwjlh5L+ZkeNxk6z9HBNRfDjLt6GtgcKqUFFb98nzY4m1N8RMIIjZmAAiIFijZ70WVh77tUVo0+pbw02uvmUkWqjiaLiRRutTfq4eNSOhjzpOLcXwHUw561Lh8SadCrcxHT4rwLeCq6kc9J65jdpFmxWwxbTRvHPVepTuV5UDRaGSgMJWbLDlLF0bI2ppGXtTERitXq9yK2Yvzba5ivUcZXW9fmxs7Mxbi017NRJSj2/NGLODnPRPU1MPG2RcnHzKc1p3PDUpSKe0o+unzivFN/0LNGRHtSP/bl/qT77NeTERVCw6lTcmore/h1AX8NalTzvWUvZXTh9S1qpY/FU8LTXGb0pw96UubMjDwk81So71Kms+i4RXRENKMqtWdao72k4w5K29+PkXSvP8p9AII+jTzNLxfJF0J8BhszzP2Vu6sWNxV3kj3sbtPHKlFU4e09EuS5lOjJQjmerfxZj11q3M/U87RV5NJcWzOrbTj7qcuu5D6tB1Xeb04R4LsXzHwwsFwT7dROLVtkZlTF1Z6RT/CrihsypN3m8v70jZSEWnxz9Pv8Awr4bCQpq0Vrxk9ZPvJgiNFN0LAHAAABwALdhWCIITYbFODV9Y8Vxt0L2OwqqRzRtmSvHqt5lmzs+V6UX92cod1lJebGarfHliwQIxtJPmXsdSyzzL2Z/CRC4mVmNp1sbOC1SLqRQwL0RpZeJvPTm69go3JY01xGRl0ZnbdxbhGMI3Tne742XD4lvUV93FbaW0Um407N7nLgvqY0km7v1m+LCIys323nj0aojqa1XavMFwkoXMOTYujnptLfvXby8LkNF31XeuTLVOZmvaxsMs7iuLaT7bmhtFa24JaDJU1TrwnuhOWvJS/P50LO0oa35r5sdelf1z+FdpSjyu/35P+aJZKWOThNVI717UfvR49/9C5TmpJSWqe4ni7FuoNiWrioUKbm9/m+CRUxNdRsm1G925PdGK3s5nam0XWnpdU46Qi+XN9WR31+J551fw9d1ajqS4vTojSw8/SNy92Lyx7eLMTBzstORZ2HXyXhLc+PLr+ehnz78r9em4CwRHQxAVgiAaIIgGiCIAACIJW7CsOFYINNnAQth786ra7kl8jHaOhcHGhTjp7Kfe9SYp0p4uGaLj3rozPpSvo963mhVKFRa3KdRflqYJq3U0acjEwlez1NOlU7C/NZ9Tyv01cpbUw8ZpPKpON7LddPfZ9xMqtkVq1axe1WTyw8RRjvhfT2oveiqtTYxeGc/WhZSX73Qw3K0npbW0lyZlbjaeUtgDgWJBhNp3RbhUusy4b1yf0KdixhPffDJ8cysRYSp9oRz0KnSOaPatSvgcX6ahGV7yj6svl8LEm0amTDVHzhlXa9DL+y60rQ6U33+svkjOr5/jqDak0jBliJxd4SlHsbVzZ23BpswpmWtuZ4R16k56zlKXK7bsRKBK2GCTYWWsFC5pQwlrSW9DNm4fcbkaOhLPqqlJ2tF7n7D/l/PyJhuNov0UmvajaUXyknoNwtdVIRmt0lu5PivE24rHpIAdYBdACCIAAsEQAsAcIC5YVh1gWCAsbccTGdOOusYpSjxulbwMWwgizVurW4FWd3uXiLUFiMWlwxKS5eJJGtJcfAFgWGGnuvLmx1PEyW/VcUyLKDKThrZj6tpL2ZWaZnbdwy0rR42jU79zNeMP1aPSCZQcvSUpw5xfjbQWfinN86yKDuuzQksNoR9VPnqSWInppfZtizCOvo17rvUf7f3e7zuSU6Xo6U8RL3It01zlui33srYCWWm5t8HJsjq/hzP1T+0mIvlpLdH1pdvAbsD1E5P338Fon43M+d6tTrN3fRf2NmEEkktySS7CnM26078c4W28HnjmW85GvRabVjusPO6yv8AuiljdlqV2kV658nHeeHFejbLWFwrubX/AE2z3EsaCXAri17OwFO1jStoUKD1LdedkSzp8YZoyjzTRzOwcRlqVKD4tyh2revDXuZ0eHqetFc2jinUyYtzXCvL/bmafwbJlypk3XX2FYNhG7I2wLDwWAbYA+wLANBYc0KwSvAsPyisTiDLCsPygyjA2wrDsorDAwVh2UWUYG2EOsKwwdBa1FL/ANa/hMHBVbKT5J+Ru5U6K601/Ccvh36k+sWvHQjuo4nipIRskuSXkOUb6czH/wAXU+98i7gas5SV5Req37zKfLGt+Ozy1/tQ7YVpbs1NdyZh1q9sI2v2V4s6LbtDPh6iW+2Zd2py2CXpKM6T4rTtWqHftb4/9f8AqbZGHtDO/anu6R4fnsL9hmDknCPSKTXJpWsS5TTmZGfVtpq01Ro4eSkr+PaULE2FnaS5PRixU/aNKKd1xSfY+KMmrI0NrV7aHPY/FWRjavzKfSxKz2LOIr3aXezAwlb1rlmeK1bb3+RXWn1bmBl+kzPdBOXgji5vM5S5yb8Xc6mjUlKhOUYuN00rrVrmc1g6bk4x4yko+LsCeHbJCsPsCx0sTLCsOyisA2wB9gWAaKw7KCwQ0coLFjIDIWQgsLKT5BZAK7QrE+QWQCDKLKT5AZAILCsT5AZQNLATzUrcVeL+RzNL1Jyi+EmvBmxQqODuu9cytj8PnlnjpJ+1Hn1RXpPHisnE4GEnmi3Fvha6HYfC29790md1o00+o6LMbzK32428JVUoJN3ssrOQrxdCvOC3X07Hqjeotrc7P4d5j7Xq55xk4uMlHLNPmpPVPiuo6vhHxzyidWSlmg7X3rgy9hcbm0lFp81qZPpLFzAzuys7xr18cxsZNLrUUKkY3fHguRPRhpdd4alNM122ObI57H4i7bOextRyZ2OKwEZJ6eGjOcx+y3B3TvH4oxsrbnGdQi1qa2xdnekfpJr1Iv1Y8JNfIrYPBurONOO7fKXKPFnX0qKjFRirRirJdC/x8b5V+TrPBjhdNcGjHrbOcZqcIXkmnF8G+pu5RZTW8Ssp1iEViXKLKWxVFlA0S5RZRiUNhZSXKDKMEWUFiawsowalugspNlBlLKInEFnyJbCsBFlFlJbAsBE10BboTZQZQI7AaJbAygRW6BjBvgSWJFokRUoZYVNetZoo1aFGne8pPomvoXq2abUY73cqz2Sn7U5dyS8zO7fUac2T3WZiNpxjpCH4ptv4IxcVinJtt3b3s6l7BovfnfbO3khr+z2F402+2pU+pnfj6rbn5fj5/lx/pC7syreSR0i2FhV/lL/fU+pJS2Rh4O8aaT/1T+pE+HrVuv6jizMqXC7h9ZWJYwS3IVSKe82+tc328qLZn7Vist9xsOjFcWu1ozqsacqsF6WM3dtU42bulfWz3aFbzVueoj2NgPRQu1689ZdFwiX7EmUVjWTJjO3bqIRJYFgGWA0PsCwDLdBWHgsAywLElgWAjsKxIADYaG5Xz+BIAlQxRDlHAAY4jcrJRNAR2BYe0AJMsxWHisAywnqrDrCykUiLCxaqLsfkXyCjD1k+j8idjmZDq7UUypVb/KLcypWJpFGvWkveM3EY2qt05LvL+JMnEmdrbmRWq4+t/wCWp3TaKtTF1HvqVH21Jv5jqpVqSKa1yGVJN7232u5f+zz/AFin+L+BmVUqFjYuMUK0Jb7ZtPwtEz2jr075pgyszFtlfd+I9bWX3X8DXY5/rWjYDRSjtOL4MkjjIsaYnsKwxVkOzhA2GtBzCuAMoLDgNgNsCw4QS1rCADMiVBYMoswrgIVxrYMyALQLCuBsB1wMbmFdBIjkxlxNgSqYXLqQZhZghJL86tEE4t8vF/QfmGuQSp1sLN/d8X9ChW2VVe5w75S/4m1mA2RkWnVczV2BXfvUl+Kf/Erz+y1d/wCdSX4Zy+h1rYLkfWLf3OnHr7G1H7WIX4advNlrD/ZKMHf0jk1ub/odNcVxkR9qyI7Et73wHrZC+8aeYGYnEbVGOy4riySOBii1cDYw1GqCQfRodmBmCAyCsG41sAjWhZhACwQXBcJatwEecVyVD7iuRuQM4EgBikK4SfcFxjkDOA8Q24mwHXBcZnEpAOFcbcDkA+4BmYNyARXGtjc4SeAapCuAbiuMcgZwHgG3BcB1xNjMwMwDwXG3A2EnXANzCuA4FwAzAOANzBuB/9k='"
                  alt=""
                  class="product-image"
                  loading="lazy"
                />
                <h3 class="product-name">{{ product.name }}</h3>
                <div class="product-price">
                  <span class="price-highlight">KES {{ product.price }}</span>
                  <span v-if="product.below_moq_price" class="below-moq-price">
                    Below MOQ Price: KES {{ product.below_moq_price }}
                  </span>
                  <span v-else class="below-moq-price">Below MOQ Price: NA</span>
                </div>
                <p class="moq-info">MOQ: {{ product.moq }} items</p>

                <!-- Progress bar container -->
                <div class="moq-progress-container">
                  <div
                    class="moq-progress-bar"
                    :style="{ width: Math.min(100, product.moq_progress?.percentage) + '%' }"
                  ></div>
                  <span class="moq-progress-text">
                    {{ product.moq_progress?.percentage }}%
                  </span>
                </div>
              </router-link>
            </div>
          </div>
          <div v-else class="no-products">
            No products available
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script>
import { onMounted } from 'vue';
import { useEcommerceStore } from '@/stores/ecommerce';
import MainLayout from '@/components/navigation/MainLayout.vue';
import RecentCampaigns from '@/components/home/recents/RecentCampaigns.vue';
import RecentSearches from '@/components/home/recents/RecentSearches.vue';
import HomeCarousel from '@/components/home/recents/HomeCarousel.vue';

export default {
  setup() {
    const store = useEcommerceStore();

    onMounted(() => {
      if (!store.allhomeCategoriesWithProducts.length) {
        console.log('Fetching home categories');
        store.fetchHomeCategories();
      }
      // Debug: Log product data
      console.log('Categories with products:', store.allCategoriesWithProducts);
      store.allhomeCategoriesWithProducts.forEach(category => {
        category.products.forEach(product => {
          console.log('Product MOQ details:', {
            id: product.id,
            name: product.name,
            price: product.price,
            below_moq_price: product.below_moq_price,
            moq: product.moq,
            moq_per_person: product.moq_per_person,
            moq_status: product.moq_status,
            moq_progress: product.moq_progress,
          });
        });
      });
    });

    return { store };
  },
  components: {
    MainLayout,
    RecentCampaigns,
    RecentSearches,
    HomeCarousel,
  },
};
</script>


<style scoped>
.top-row-home {
  display: flex;
  flex-direction: row;
  gap: 1.5rem;
  margin: 1.5rem 3%;
}

/* Container for all categories */
.categories-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 2rem;
  padding: 1.5rem 3%;
  justify-content: center;
}

/* Individual category card */
.category-card {
  flex: 1 1 100%; /* Full width by default */
  max-width: 100%;
  min-width: 300px;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 1.5rem;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

/* Category header styling */
.category-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
}

/* Category title */
.category-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f28c38;
  text-transform: uppercase;
  margin: 0;
  letter-spacing: 0.5px;
  position: relative;
}

.category-title::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 0;
  width: 40px;
  height: 3px;
  background-color: #f28c38;
  border-radius: 3px;
}

/* See More link styling */
.see-more-link {
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  background-color: #f28c38;
  padding: 6px 12px;
  border-radius: 20px;
  text-transform: uppercase;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(242, 140, 56, 0.3);
}

.see-more-link:hover {
  background-color: #e67d21;
  box-shadow: 0 4px 15px rgba(242, 140, 56, 0.4);
  transform: translateY(-2px);
}

/* Products grid inside each category */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

/* Individual product card */
.product-card {
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  height: 100%;
  min-height: 300px; /* Ensure consistent height */
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

/* Product link */
.product-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  transition: all 0.3s ease;
}

/* Product image styling */
.product-image {
  width: 100%;
  height: 160px;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image {
  transform: scale(1.03);
}

/* Product name styling */
.product-name {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0.5rem 0;
  text-align: left;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1; /* Ensure name takes available space */
}

/* Product price styling */
.product-price {
  display: flex;
  flex-direction: column;
  margin: 0.25rem 0;
}

.price-highlight {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f28c38;
}

.below-moq-price {
  font-size: 0.75rem;
}

/* MOQ info styling */
.moq-info {
  font-size: 0.8rem;
  margin: 0.5rem 0;
  padding: 3px 8px;
  border-radius: 4px;
  display: inline-block;
}

/* MOQ progress container */
.moq-progress-container {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: #e6f4ea;
  border-radius: 20px;
  overflow: hidden;
  margin-top: auto; /* Push to bottom of card */
}

.moq-progress-bar {
  height: 100%;
  background: linear-gradient(45deg, #28a745, #5fd778);
  transition: width 0.5s ease;
}

.moq-progress-text {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 0.65rem;
  font-weight: bold;
  text-shadow: 0 0 2px #fff;
}

/* No products messaging */
.no-products {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2.5rem;
  font-size: 0.9rem;
  border-radius: 8px;
  text-align: center;
  font-style: italic;
  height: 150px;
}

/* Loading and error states */
.loading,
.error {
  text-align: center;
  padding: 3rem;
  font-size: 1.1rem;
  border-radius: 8px;
  margin: 1rem 3%;
}

.skeleton-container {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  padding: 1.5rem 3%;
}

.skeleton-category {
  flex: 1 1 calc(50% - 1rem);
  max-width: calc(50% - 1rem);
  min-width: 300px;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.skeleton-title {
  width: 150px;
  height: 20px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 1.5rem;
}

.skeleton-products {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.skeleton-product {
  height: 300px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 10px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (max-width: 767px) {
  .skeleton-category {
    flex: 1 1 100%;
    max-width: 100%;
  }

  .skeleton-products {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .skeleton-products {
    grid-template-columns: 1fr;
  }
}

/* Responsive adjustments */
@media (min-width: 1200px) {
  .category-card {
    flex: 1 1 calc(50% - 1rem); /* Two categories per row */
    max-width: calc(50% - 1rem);
  }

  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .category-card {
    flex: 1 1 calc(50% - 1rem);
    max-width: calc(50% - 1rem);
  }

  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .product-image {
    height: 150px;
  }
}

@media (min-width: 450px) and (max-width: 600px) {
  .top-row-home {
    flex-direction: column;
    gap: 1.5rem;
  }

  .category-card {
    flex: 1 1 100%;
    max-width: 100%;
  }

  .products-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .product-image {
    height: 140px;
  }
}

@media (max-width: 500px) {
  .top-row-home {
    flex-direction: column;
    gap: 1rem;
    margin: 1rem 3%;
  }

  .categories-container {
    padding: 1rem 3%;
    gap: 1.5rem;
  }

  .category-card {
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .category-top {
    margin-bottom: 1rem;
  }

  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .product-card {
    min-height: 280px;
    padding: 0.75rem;
  }

  .product-image {
    height: 130px;
  }

  .product-name {
    font-size: 0.9rem;
  }

  .product-price {
    font-size: 0.9rem;
  }

  .moq-info {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .categories-container {
    padding: 1rem 2%;
    gap: 1rem;
  }

  .products-grid {
    grid-template-columns: 1fr; /* Single column */
    gap: 0.75rem;
  }

  .product-card {
    min-height: 300px;
    padding: 0.75rem;
  }

  .product-image {
    height: 150px;
  }

  .product-name {
    font-size: 0.85rem;
  }

  .product-price {
    font-size: 0.85rem;
  }

  .moq-info {
    font-size: 0.7rem;
    padding: 2px 6px;
  }

  .moq-progress-container {
    height: 8px;
  }
}

@media (max-width: 360px) {
  .product-card {
    min-height: 280px;
  }

  .product-image {
    height: 140px;
  }

  .product-name {
    font-size: 0.8rem;
  }
}
</style>
