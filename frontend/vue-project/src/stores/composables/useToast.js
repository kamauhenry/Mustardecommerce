import { ref, reactive } from 'vue';

/**
 * Toast notification types
 */
export const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

/**
 * Global toast state
 */
const toastState = reactive({
  toasts: [],
  nextId: 0,
});

/**
 * Composable for centralized toast notifications
 * Provides a consistent way to show notifications across the application
 *
 * @example
 * const { success, error, warning, info } = useToast();
 * success('Product added to cart');
 * error('Failed to load products');
 */
export function useToast() {
  /**
   * Show a toast notification
   * @param {string} message - Notification message
   * @param {string} type - Toast type (success, error, warning, info)
   * @param {Object} options - Configuration options
   * @param {number} options.duration - Duration in milliseconds (default: 3000)
   * @param {boolean} options.dismissible - Whether toast can be dismissed (default: true)
   * @param {Function} options.onDismiss - Callback when toast is dismissed
   * @returns {number} - Toast ID
   */
  const show = (message, type = TOAST_TYPES.INFO, options = {}) => {
    const {
      duration = 3000,
      dismissible = true,
      onDismiss = null,
    } = options;

    const id = toastState.nextId++;
    const toast = {
      id,
      message,
      type,
      dismissible,
      onDismiss,
      timestamp: Date.now(),
    };

    toastState.toasts.push(toast);

    // Auto-dismiss after duration
    if (duration > 0) {
      setTimeout(() => {
        dismiss(id);
      }, duration);
    }

    // Log to console in development
    if (import.meta.env.DEV) {
      const logFn = type === TOAST_TYPES.ERROR ? console.error :
                    type === TOAST_TYPES.WARNING ? console.warn :
                    console.log;
      logFn(`[Toast ${type.toUpperCase()}]:`, message);
    }

    return id;
  };

  /**
   * Dismiss a toast notification
   * @param {number} id - Toast ID
   */
  const dismiss = (id) => {
    const index = toastState.toasts.findIndex(t => t.id === id);
    if (index !== -1) {
      const toast = toastState.toasts[index];
      if (toast.onDismiss) {
        toast.onDismiss();
      }
      toastState.toasts.splice(index, 1);
    }
  };

  /**
   * Dismiss all toast notifications
   */
  const dismissAll = () => {
    toastState.toasts.forEach(toast => {
      if (toast.onDismiss) {
        toast.onDismiss();
      }
    });
    toastState.toasts = [];
  };

  /**
   * Show success toast
   * @param {string} message - Success message
   * @param {Object} options - Configuration options
   */
  const success = (message, options = {}) => {
    return show(message, TOAST_TYPES.SUCCESS, options);
  };

  /**
   * Show error toast
   * @param {string} message - Error message
   * @param {Object} options - Configuration options
   */
  const error = (message, options = {}) => {
    return show(message, TOAST_TYPES.ERROR, {
      duration: 5000, // Errors stay longer
      ...options,
    });
  };

  /**
   * Show warning toast
   * @param {string} message - Warning message
   * @param {Object} options - Configuration options
   */
  const warning = (message, options = {}) => {
    return show(message, TOAST_TYPES.WARNING, options);
  };

  /**
   * Show info toast
   * @param {string} message - Info message
   * @param {Object} options - Configuration options
   */
  const info = (message, options = {}) => {
    return show(message, TOAST_TYPES.INFO, options);
  };

  return {
    // State
    toasts: ref(toastState.toasts),

    // Methods
    show,
    dismiss,
    dismissAll,
    success,
    error,
    warning,
    info,
  };
}

/**
 * Global toast instance for imperative usage
 * Can be imported and used directly without the composable
 */
export const toast = {
  success: (message, options) => {
    const { success } = useToast();
    return success(message, options);
  },
  error: (message, options) => {
    const { error } = useToast();
    return error(message, options);
  },
  warning: (message, options) => {
    const { warning } = useToast();
    return warning(message, options);
  },
  info: (message, options) => {
    const { info } = useToast();
    return info(message, options);
  },
  dismiss: (id) => {
    const { dismiss } = useToast();
    return dismiss(id);
  },
  dismissAll: () => {
    const { dismissAll } = useToast();
    return dismissAll();
  },
};
