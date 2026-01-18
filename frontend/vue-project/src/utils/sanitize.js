import DOMPurify from 'dompurify';

/**
 * Sanitizes HTML to prevent XSS attacks
 * @param {string} html - Raw HTML string
 * @param {object} options - DOMPurify configuration
 * @returns {string} - Sanitized HTML
 */
export const sanitizeHtml = (html, options = {}) => {
  if (!html || typeof html !== 'string') {
    return '';
  }

  const defaultConfig = {
    ALLOWED_TAGS: [
      'b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 'img'
    ],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'id'],
    ALLOW_DATA_ATTR: false,
  };

  return DOMPurify.sanitize(html, { ...defaultConfig, ...options });
};

/**
 * Strips all HTML tags, leaving only text
 * @param {string} html - Raw HTML string
 * @returns {string} - Plain text
 */
export const stripHtml = (html) => {
  if (!html || typeof html !== 'string') {
    return '';
  }

  return DOMPurify.sanitize(html, { ALLOWED_TAGS: [] });
};
