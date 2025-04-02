import placeholder from "@/assets/images/office.jpeg"
// Utility to track recent categories and products
const TRACKING_LIMIT = 3; // Limit to 3 items

// Track recent categories
export const trackCategory = (category) => {
  let recentCategories = JSON.parse(localStorage.getItem('recentCategories')) || [];

  // Remove the category if it already exists to avoid duplicates
  recentCategories = recentCategories.filter(cat => cat.id !== category.id);

  // Add the new category to the beginning
  recentCategories.unshift({
    id: category.id,
    name: category.name,
    slug: category.slug,
    image: category.image || placeholder // Use a placeholder if no image
  });

  // Limit to 3 items
  recentCategories = recentCategories.slice(0, TRACKING_LIMIT);

  // Save to localStorage
  localStorage.setItem('recentCategories', JSON.stringify(recentCategories));
};

// Get recent categories
export const getRecentCategories = () => {
  return JSON.parse(localStorage.getItem('recentCategories')) || [];
};

// Track recent products from search or homepage
export const trackProduct = (product, categorySlug) => {
  let recentProducts = JSON.parse(localStorage.getItem('recentProducts')) || [];
  recentProducts = recentProducts.filter(prod => prod.id !== product.id);
  recentProducts.unshift({
    id: product.id,
    name: product.name,
    slug: product.slug, // Store the product slug
    image: product.thumbnail || placeholder,
    categorySlug: categorySlug
  });
  recentProducts = recentProducts.slice(0, TRACKING_LIMIT);
  localStorage.setItem('recentProducts', JSON.stringify(recentProducts));
};

// Get recent products
export const getRecentProducts = () => {
  return JSON.parse(localStorage.getItem('recentProducts')) || [];
};
