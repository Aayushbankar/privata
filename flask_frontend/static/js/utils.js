/* MOSDAC AI Help Bot - Utility Functions */
/* Common utility functions used across the application */

// DOM Utilities
const DOM = {
    /**
     * Get element by ID with error handling
     */
    get: (id) => {
        const element = document.getElementById(id);
        if (!element) {
            console.warn(`Element with ID '${id}' not found`);
        }
        return element;
    },

    /**
     * Get elements by selector
     */
    getAll: (selector) => {
        return document.querySelectorAll(selector);
    },

    /**
     * Create element with attributes and content
     */
    create: (tag, attributes = {}, content = '') => {
        const element = document.createElement(tag);
        
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'innerHTML') {
                element.innerHTML = value;
            } else if (key === 'textContent') {
                element.textContent = value;
            } else if (key.startsWith('data-')) {
                element.setAttribute(key, value);
            } else {
                element[key] = value;
            }
        });
        
        if (content) {
            element.innerHTML = content;
        }
        
        return element;
    },

    /**
     * Add event listener with cleanup tracking
     */
    on: (element, event, handler, options = {}) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            element.addEventListener(event, handler, options);
            
            // Track for cleanup
            if (!element._eventListeners) {
                element._eventListeners = [];
            }
            element._eventListeners.push({ event, handler, options });
        }
    },

    /**
     * Remove all event listeners from element
     */
    cleanup: (element) => {
        if (element && element._eventListeners) {
            element._eventListeners.forEach(({ event, handler, options }) => {
                element.removeEventListener(event, handler, options);
            });
            element._eventListeners = [];
        }
    },

    /**
     * Check if element is visible in viewport
     */
    isVisible: (element) => {
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },

    /**
     * Smooth scroll to element
     */
    scrollTo: (element, options = {}) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
                ...options
            });
        }
    },

    /**
     * Toggle class with optional condition
     */
    toggleClass: (element, className, condition = null) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            if (condition !== null) {
                element.classList.toggle(className, condition);
            } else {
                element.classList.toggle(className);
            }
        }
    }
};

// String Utilities
const Str = {
    /**
     * Truncate string with ellipsis
     */
    truncate: (str, length = 100, suffix = '...') => {
        if (!str || str.length <= length) return str;
        return str.substring(0, length) + suffix;
    },

    /**
     * Capitalize first letter
     */
    capitalize: (str) => {
        if (!str) return str;
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    /**
     * Convert to title case
     */
    titleCase: (str) => {
        if (!str) return str;
        return str.replace(/\w\S*/g, (txt) => 
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        );
    },

    /**
     * Convert to kebab case
     */
    kebabCase: (str) => {
        if (!str) return str;
        return str
            .replace(/([a-z])([A-Z])/g, '$1-$2')
            .replace(/\s+/g, '-')
            .toLowerCase();
    },

    /**
     * Convert to camel case
     */
    camelCase: (str) => {
        if (!str) return str;
        return str
            .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => 
                index === 0 ? word.toLowerCase() : word.toUpperCase()
            )
            .replace(/\s+/g, '');
    },

    /**
     * Remove HTML tags
     */
    stripHtml: (str) => {
        if (!str) return str;
        return str.replace(/<[^>]*>/g, '');
    },

    /**
     * Escape HTML special characters
     */
    escapeHtml: (str) => {
        if (!str) return str;
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    /**
     * Generate random string
     */
    random: (length = 8, charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') => {
        let result = '';
        for (let i = 0; i < length; i++) {
            result += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        return result;
    },

    /**
     * Format file size
     */
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    /**
     * Format number with commas
     */
    formatNumber: (num) => {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
};

// Date/Time Utilities
const DateTime = {
    /**
     * Format date to readable string
     */
    format: (date, options = {}) => {
        if (!date) return '';
        
        const d = new Date(date);
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return d.toLocaleDateString('en-US', { ...defaultOptions, ...options });
    },

    /**
     * Get relative time (e.g., "2 minutes ago")
     */
    relative: (date) => {
        if (!date) return '';
        
        const now = new Date();
        const past = new Date(date);
        const diffMs = now - past;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffSecs < 60) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        
        return DateTime.format(date, { year: 'numeric', month: 'short', day: 'numeric' });
    },

    /**
     * Check if date is today
     */
    isToday: (date) => {
        const today = new Date();
        const d = new Date(date);
        return d.toDateString() === today.toDateString();
    },

    /**
     * Get time ago in milliseconds
     */
    timeAgo: (date) => {
        return Date.now() - new Date(date).getTime();
    },

    /**
     * Add days to date
     */
    addDays: (date, days) => {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    },

    /**
     * Get start of day
     */
    startOfDay: (date = new Date()) => {
        const d = new Date(date);
        d.setHours(0, 0, 0, 0);
        return d;
    },

    /**
     * Get end of day
     */
    endOfDay: (date = new Date()) => {
        const d = new Date(date);
        d.setHours(23, 59, 59, 999);
        return d;
    }
};

// Array Utilities
const Arr = {
    /**
     * Remove duplicates from array
     */
    unique: (arr) => {
        return [...new Set(arr)];
    },

    /**
     * Group array by key
     */
    groupBy: (arr, key) => {
        return arr.reduce((groups, item) => {
            const group = item[key];
            groups[group] = groups[group] || [];
            groups[group].push(item);
            return groups;
        }, {});
    },

    /**
     * Chunk array into smaller arrays
     */
    chunk: (arr, size) => {
        const chunks = [];
        for (let i = 0; i < arr.length; i += size) {
            chunks.push(arr.slice(i, i + size));
        }
        return chunks;
    },

    /**
     * Shuffle array
     */
    shuffle: (arr) => {
        const shuffled = [...arr];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    },

    /**
     * Get random item from array
     */
    random: (arr) => {
        return arr[Math.floor(Math.random() * arr.length)];
    },

    /**
     * Sort array by key
     */
    sortBy: (arr, key, direction = 'asc') => {
        return [...arr].sort((a, b) => {
            const aVal = typeof key === 'function' ? key(a) : a[key];
            const bVal = typeof key === 'function' ? key(b) : b[key];
            
            if (direction === 'desc') {
                return bVal > aVal ? 1 : -1;
            }
            return aVal > bVal ? 1 : -1;
        });
    }
};

// Object Utilities
const Obj = {
    /**
     * Deep clone object
     */
    clone: (obj) => {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => Obj.clone(item));
        
        const cloned = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                cloned[key] = Obj.clone(obj[key]);
            }
        }
        return cloned;
    },

    /**
     * Deep merge objects
     */
    merge: (target, ...sources) => {
        if (!sources.length) return target;
        const source = sources.shift();
        
        if (Obj.isObject(target) && Obj.isObject(source)) {
            for (const key in source) {
                if (Obj.isObject(source[key])) {
                    if (!target[key]) Object.assign(target, { [key]: {} });
                    Obj.merge(target[key], source[key]);
                } else {
                    Object.assign(target, { [key]: source[key] });
                }
            }
        }
        
        return Obj.merge(target, ...sources);
    },

    /**
     * Check if value is object
     */
    isObject: (item) => {
        return item && typeof item === 'object' && !Array.isArray(item);
    },

    /**
     * Get nested property safely
     */
    get: (obj, path, defaultValue = undefined) => {
        const keys = path.split('.');
        let result = obj;
        
        for (const key of keys) {
            if (result === null || result === undefined || !(key in result)) {
                return defaultValue;
            }
            result = result[key];
        }
        
        return result;
    },

    /**
     * Set nested property
     */
    set: (obj, path, value) => {
        const keys = path.split('.');
        const lastKey = keys.pop();
        let current = obj;
        
        for (const key of keys) {
            if (!(key in current) || !Obj.isObject(current[key])) {
                current[key] = {};
            }
            current = current[key];
        }
        
        current[lastKey] = value;
        return obj;
    },

    /**
     * Pick specific keys from object
     */
    pick: (obj, keys) => {
        const result = {};
        keys.forEach(key => {
            if (key in obj) {
                result[key] = obj[key];
            }
        });
        return result;
    },

    /**
     * Omit specific keys from object
     */
    omit: (obj, keys) => {
        const result = { ...obj };
        keys.forEach(key => {
            delete result[key];
        });
        return result;
    }
};

// Storage Utilities
const Storage = {
    /**
     * Set item in localStorage with error handling
     */
    set: (key, value, prefix = 'mosdac_') => {
        try {
            const serialized = JSON.stringify(value);
            localStorage.setItem(prefix + key, serialized);
            return true;
        } catch (error) {
            console.error('Storage.set error:', error);
            return false;
        }
    },

    /**
     * Get item from localStorage with error handling
     */
    get: (key, defaultValue = null, prefix = 'mosdac_') => {
        try {
            const item = localStorage.getItem(prefix + key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Storage.get error:', error);
            return defaultValue;
        }
    },

    /**
     * Remove item from localStorage
     */
    remove: (key, prefix = 'mosdac_') => {
        try {
            localStorage.removeItem(prefix + key);
            return true;
        } catch (error) {
            console.error('Storage.remove error:', error);
            return false;
        }
    },

    /**
     * Clear all items with prefix
     */
    clear: (prefix = 'mosdac_') => {
        try {
            const keys = Object.keys(localStorage).filter(key => key.startsWith(prefix));
            keys.forEach(key => localStorage.removeItem(key));
            return true;
        } catch (error) {
            console.error('Storage.clear error:', error);
            return false;
        }
    },

    /**
     * Check if storage is available
     */
    isAvailable: () => {
        try {
            const test = '__storage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (error) {
            return false;
        }
    },

    /**
     * Get storage usage info
     */
    getUsage: () => {
        if (!Storage.isAvailable()) return null;
        
        let total = 0;
        for (const key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                total += localStorage[key].length + key.length;
            }
        }
        
        return {
            used: total,
            remaining: 5242880 - total, // 5MB typical limit
            percentage: (total / 5242880) * 100
        };
    }
};

// URL Utilities
const URL = {
    /**
     * Get query parameters as object
     */
    getParams: () => {
        const params = {};
        const searchParams = new URLSearchParams(window.location.search);
        for (const [key, value] of searchParams) {
            params[key] = value;
        }
        return params;
    },

    /**
     * Set query parameter
     */
    setParam: (key, value) => {
        const url = new URL(window.location);
        url.searchParams.set(key, value);
        window.history.replaceState({}, '', url);
    },

    /**
     * Remove query parameter
     */
    removeParam: (key) => {
        const url = new URL(window.location);
        url.searchParams.delete(key);
        window.history.replaceState({}, '', url);
    },

    /**
     * Build URL with parameters
     */
    build: (base, params = {}) => {
        const url = new URL(base);
        Object.entries(params).forEach(([key, value]) => {
            url.searchParams.set(key, value);
        });
        return url.toString();
    },

    /**
     * Check if URL is valid
     */
    isValid: (url) => {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }
};

// Validation Utilities
const Validate = {
    /**
     * Check if email is valid
     */
    email: (email) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },

    /**
     * Check if phone number is valid
     */
    phone: (phone) => {
        const regex = /^[\+]?[1-9][\d]{0,15}$/;
        return regex.test(phone.replace(/\s/g, ''));
    },

    /**
     * Check if URL is valid
     */
    url: (url) => {
        return URL.isValid(url);
    },

    /**
     * Check if string is not empty
     */
    required: (value) => {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    },

    /**
     * Check string length
     */
    length: (value, min = 0, max = Infinity) => {
        const length = value ? value.toString().length : 0;
        return length >= min && length <= max;
    },

    /**
     * Check if number is in range
     */
    range: (value, min = -Infinity, max = Infinity) => {
        const num = parseFloat(value);
        return !isNaN(num) && num >= min && num <= max;
    },

    /**
     * Check if value matches pattern
     */
    pattern: (value, regex) => {
        return regex.test(value);
    }
};

// Performance Utilities
const Perf = {
    /**
     * Debounce function execution
     */
    debounce: (func, wait, immediate = false) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },

    /**
     * Throttle function execution
     */
    throttle: (func, limit) => {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Measure function execution time
     */
    measure: async (func, label = 'Function') => {
        const start = performance.now();
        const result = await func();
        const end = performance.now();
        console.log(`${label} took ${end - start} milliseconds`);
        return result;
    },

    /**
     * Create performance observer
     */
    observe: (callback, options = {}) => {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver(callback);
            observer.observe({
                entryTypes: ['measure', 'navigation', 'resource'],
                ...options
            });
            return observer;
        }
        return null;
    }
};

// Animation Utilities
const Animate = {
    /**
     * Fade in element
     */
    fadeIn: (element, duration = 300) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            element.style.opacity = '0';
            element.style.display = 'block';
            
            const start = performance.now();
            
            function animate(currentTime) {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                element.style.opacity = progress;
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            }
            
            requestAnimationFrame(animate);
        }
    },

    /**
     * Fade out element
     */
    fadeOut: (element, duration = 300) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            const start = performance.now();
            const initialOpacity = parseFloat(getComputedStyle(element).opacity) || 1;
            
            function animate(currentTime) {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                element.style.opacity = initialOpacity * (1 - progress);
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.display = 'none';
                }
            }
            
            requestAnimationFrame(animate);
        }
    },

    /**
     * Slide down element
     */
    slideDown: (element, duration = 300) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            element.style.display = 'block';
            const height = element.scrollHeight;
            element.style.height = '0';
            element.style.overflow = 'hidden';
            
            const start = performance.now();
            
            function animate(currentTime) {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                element.style.height = (height * progress) + 'px';
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.height = '';
                    element.style.overflow = '';
                }
            }
            
            requestAnimationFrame(animate);
        }
    },

    /**
     * Slide up element
     */
    slideUp: (element, duration = 300) => {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        
        if (element) {
            const height = element.scrollHeight;
            element.style.height = height + 'px';
            element.style.overflow = 'hidden';
            
            const start = performance.now();
            
            function animate(currentTime) {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                element.style.height = (height * (1 - progress)) + 'px';
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.display = 'none';
                    element.style.height = '';
                    element.style.overflow = '';
                }
            }
            
            requestAnimationFrame(animate);
        }
    }
};

// Device Detection Utilities
const Device = {
    /**
     * Check if mobile device
     */
    isMobile: () => {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },

    /**
     * Check if tablet device
     */
    isTablet: () => {
        return /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);
    },

    /**
     * Check if desktop device
     */
    isDesktop: () => {
        return !Device.isMobile() && !Device.isTablet();
    },

    /**
     * Get device type
     */
    getType: () => {
        if (Device.isMobile()) return 'mobile';
        if (Device.isTablet()) return 'tablet';
        return 'desktop';
    },

    /**
     * Check if touch device
     */
    isTouch: () => {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },

    /**
     * Get screen size category
     */
    getScreenSize: () => {
        const width = window.innerWidth;
        if (width < 768) return 'small';
        if (width < 1024) return 'medium';
        return 'large';
    }
};

// Export utilities for global use
window.Utils = {
    DOM,
    Str,
    DateTime,
    Arr,
    Obj,
    Storage,
    URL,
    Validate,
    Perf,
    Animate,
    Device
};

// Also export individual utilities
window.DOM = DOM;
window.Str = Str;
window.DateTime = DateTime;
window.Arr = Arr;
window.Obj = Obj;
window.Storage = Storage;
window.URLUtils = URL;
window.Validate = Validate;
window.Perf = Perf;
window.Animate = Animate;
window.Device = Device;
