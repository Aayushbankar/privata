/* MOSDAC AI Help Bot - Main Application */
/* Central coordination and initialization of all frontend components */

class MOSDACApp {
    constructor() {
        this.version = '2.0.0';
        this.initialized = false;
        this.components = {};
        this.config = window.MOSDAC_CONFIG || {};
        this.debug = this.config.DEBUG || false;
        
        // Core systems
        this.chatSystem = null;
        this.feedbackSystem = null;
        this.navigationSystem = null;
        this.voiceSystem = null;
        this.analytics = null;
        
        // Application state
        this.isOnline = navigator.onLine;
        this.currentTheme = 'light';
        this.currentLanguage = 'en';
        this.sessionId = null;
        this.userId = null;
        
        // Performance monitoring
        this.performanceMetrics = {
            loadTime: 0,
            initTime: 0,
            firstInteraction: null,
            apiCalls: 0,
            errors: 0
        };
        
        // Error handling
        this.errorQueue = [];
        this.maxErrors = 50;
        
        this.log('MOSDAC App initializing...');
    }

    async init() {
        const startTime = performance.now();
        
        try {
            // Set up error handling first
            this.setupGlobalErrorHandling();
            
            // Initialize core configuration
            await this.initializeConfig();
            
            // Initialize analytics
            this.initializeAnalytics();
            
            // Initialize UI components
            await this.initializeUI();
            
            // Initialize core systems
            await this.initializeSystems();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Initialize service worker for offline support
            await this.initializeServiceWorker();
            
            // Load user preferences
            this.loadUserPreferences();
            
            // Start performance monitoring
            this.startPerformanceMonitoring();
            
            // Mark as initialized
            this.initialized = true;
            this.performanceMetrics.initTime = performance.now() - startTime;
            
            this.log('MOSDAC App initialized successfully', {
                initTime: this.performanceMetrics.initTime,
                version: this.version
            });
            
            // Trigger initialization complete event
            this.emit('app:initialized');
            
            // Show welcome message if first visit
            this.checkFirstVisit();
            
        } catch (error) {
            this.handleError('App initialization failed', error);
            throw error;
        }
    }

    async initializeConfig() {
        // Merge default config with server config
        this.config = {
            API_BASE_URL: '/api',
            WS_URL: null,
            DEBUG: false,
            LANGUAGES: {
                'en': 'English',
                'hi': 'हिन्दी',
                'ta': 'தமிழ்',
                'te': 'తెలుగు',
                'bn': 'বাংলা',
                'mr': 'मराठी',
                'gu': 'ગુજરાતી',
                'kn': 'ಕನ್ನಡ',
                'ml': 'മലയാളം',
                'pa': 'ਪੰਜਾਬੀ'
            },
            FEATURES: {
                VOICE_INPUT: true,
                FILE_UPLOAD: true,
                OFFLINE_SUPPORT: true,
                ANALYTICS: true,
                FEEDBACK: true
            },
            LIMITS: {
                MAX_MESSAGE_LENGTH: 1000,
                MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
                RATE_LIMIT: 60 // requests per minute
            },
            ...this.config
        };
        
        // Store config globally
        window.MOSDAC_CONFIG = this.config;
        
        this.log('Configuration initialized', this.config);
    }

    initializeAnalytics() {
        if (!this.config.FEATURES.ANALYTICS) return;
        
        this.analytics = {
            events: [],
            sessions: new Map(),
            metrics: {
                pageViews: 0,
                interactions: 0,
                errors: 0,
                performance: []
            },
            
            track: (event, data = {}) => {
                const eventData = {
                    event,
                    data,
                    timestamp: Date.now(),
                    sessionId: this.sessionId,
                    userId: this.userId,
                    url: window.location.href,
                    userAgent: navigator.userAgent
                };
                
                this.analytics.events.push(eventData);
                this.log('Analytics event:', eventData);
                
                // Limit stored events
                if (this.analytics.events.length > 1000) {
                    this.analytics.events = this.analytics.events.slice(-1000);
                }
                
                // Send to server periodically
                this.sendAnalytics();
            },
            
            metric: (name, value, tags = {}) => {
                this.analytics.metrics.performance.push({
                    name,
                    value,
                    tags,
                    timestamp: Date.now()
                });
            }
        };
        
        // Make analytics available globally
        window.analytics = this.analytics;
        
        // Track page load
        this.analytics.track('page_load', {
            referrer: document.referrer,
            loadTime: this.performanceMetrics.loadTime
        });
    }

    async initializeUI() {
        // Initialize theme
        this.initializeTheme();
        
        // Initialize loading screen
        this.initializeLoadingScreen();
        
        // Initialize toast notifications
        this.initializeToasts();
        
        // Initialize modals
        this.initializeModals();
        
        // Initialize navigation
        this.initializeNavigation();
        
        // Initialize responsive handlers
        this.initializeResponsive();
        
        this.log('UI components initialized');
    }

    async initializeSystems() {
        // Initialize API client first
        if (typeof MOSDACAPIClient !== 'undefined') {
            this.components.apiClient = new MOSDACAPIClient();
        }
        
        // Initialize chat system
        if (typeof ChatSystem !== 'undefined') {
            this.chatSystem = new ChatSystem();
            this.chatSystem.init();
            this.components.chat = this.chatSystem;
        }
        
        // Initialize feedback system
        if (typeof FeedbackSystem !== 'undefined') {
            this.feedbackSystem = new FeedbackSystem();
            this.components.feedback = this.feedbackSystem;
        }
        
        // Initialize navigation system
        if (typeof NavigationSystem !== 'undefined') {
            this.navigationSystem = new NavigationSystem();
            this.components.navigation = this.navigationSystem;
        }
        
        // Initialize voice system
        if (typeof VoiceSystem !== 'undefined' && this.config.FEATURES.VOICE_INPUT) {
            this.voiceSystem = new VoiceSystem();
            this.components.voice = this.voiceSystem;
        }
        
        this.log('Core systems initialized', Object.keys(this.components));
    }

    setupEventListeners() {
        // Online/offline status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.handleOnlineStatusChange(true);
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.handleOnlineStatusChange(false);
        });
        
        // Page visibility
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });
        
        // Before unload
        window.addEventListener('beforeunload', (e) => {
            this.handleBeforeUnload(e);
        });
        
        // Resize
        window.addEventListener('resize', debounce(() => {
            this.handleResize();
        }, 250));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
        
        // Performance observer
        if ('PerformanceObserver' in window) {
            this.setupPerformanceObserver();
        }
        
        // First interaction tracking
        ['click', 'keydown', 'touchstart'].forEach(event => {
            document.addEventListener(event, () => {
                if (!this.performanceMetrics.firstInteraction) {
                    this.performanceMetrics.firstInteraction = performance.now();
                    this.analytics?.track('first_interaction', {
                        time: this.performanceMetrics.firstInteraction
                    });
                }
            }, { once: true });
        });
    }

    initializeTheme() {
        // Load saved theme or detect system preference
        const savedTheme = localStorage.getItem('mosdac_theme');
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        
        this.currentTheme = savedTheme || systemTheme;
        this.applyTheme(this.currentTheme);
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!savedTheme) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        
        // Update theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
        
        this.analytics?.track('theme_changed', { theme });
    }

    setTheme(theme) {
        this.applyTheme(theme);
        localStorage.setItem('mosdac_theme', theme);
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    initializeLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            // Hide loading screen after initialization
            setTimeout(() => {
                loadingScreen.classList.add('fade-out');
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                }, 500);
            }, 1000);
        }
    }

    initializeToasts() {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Global toast function
        window.showToast = (message, type = 'info', duration = 5000) => {
            this.showToast(message, type, duration);
        };
    }

    showToast(message, type = 'info', duration = 5000) {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <div class="toast-content">
                <i class="${icon}"></i>
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('fade-out');
                setTimeout(() => {
                    toast.remove();
                }, 300);
            }
        }, duration);
        
        this.analytics?.track('toast_shown', { message, type });
    }

    getToastIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    initializeModals() {
        // Global modal functions
        window.openModal = (modalId) => {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('show');
                document.body.classList.add('modal-open');
                this.analytics?.track('modal_opened', { modalId });
            }
        };
        
        window.closeModal = (modalId) => {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('show');
                document.body.classList.remove('modal-open');
                this.analytics?.track('modal_closed', { modalId });
            }
        };
        
        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    openModal.classList.remove('show');
                    document.body.classList.remove('modal-open');
                }
            }
        });
        
        // Close modals on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('show');
                document.body.classList.remove('modal-open');
            }
        });
    }

    initializeNavigation() {
        // Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const mobileMenu = document.getElementById('mobileMenu');
        
        if (mobileMenuToggle && mobileMenu) {
            mobileMenuToggle.addEventListener('click', () => {
                mobileMenu.classList.toggle('show');
                mobileMenuToggle.classList.toggle('active');
            });
        }
        
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Language selector
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }
    }

    initializeResponsive() {
        // Handle responsive breakpoints
        this.checkResponsiveBreakpoints();
        
        // Add resize listener
        window.addEventListener('resize', debounce(() => {
            this.checkResponsiveBreakpoints();
        }, 250));
    }

    checkResponsiveBreakpoints() {
        const width = window.innerWidth;
        const breakpoints = {
            mobile: width < 768,
            tablet: width >= 768 && width < 1024,
            desktop: width >= 1024
        };
        
        document.documentElement.setAttribute('data-device', 
            breakpoints.mobile ? 'mobile' : 
            breakpoints.tablet ? 'tablet' : 'desktop'
        );
        
        this.emit('breakpoint:change', breakpoints);
    }

    async initializeServiceWorker() {
        if ('serviceWorker' in navigator && this.config.FEATURES.OFFLINE_SUPPORT) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                this.log('Service Worker registered:', registration);
                
                registration.addEventListener('updatefound', () => {
                    this.handleServiceWorkerUpdate(registration);
                });
                
            } catch (error) {
                this.log('Service Worker registration failed:', error);
            }
        }
    }

    handleServiceWorkerUpdate(registration) {
        const newWorker = registration.installing;
        if (newWorker) {
            newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                    this.showToast('App update available. Refresh to update.', 'info', 10000);
                }
            });
        }
    }

    loadUserPreferences() {
        try {
            const preferences = JSON.parse(localStorage.getItem('mosdac_preferences') || '{}');
            
            // Apply language preference
            if (preferences.language) {
                this.setLanguage(preferences.language);
            }
            
            // Apply other preferences
            this.userPreferences = {
                notifications: true,
                soundEffects: true,
                animations: true,
                autoSave: true,
                ...preferences
            };
            
            this.log('User preferences loaded:', this.userPreferences);
            
        } catch (error) {
            this.log('Failed to load user preferences:', error);
        }
    }

    saveUserPreferences() {
        try {
            localStorage.setItem('mosdac_preferences', JSON.stringify(this.userPreferences));
        } catch (error) {
            this.log('Failed to save user preferences:', error);
        }
    }

    setLanguage(language) {
        if (this.config.LANGUAGES[language]) {
            this.currentLanguage = language;
            
            // Update API client language
            if (this.components.apiClient) {
                this.components.apiClient.setLanguage(language);
            }
            
            // Update UI language
            document.documentElement.setAttribute('lang', language);
            
            // Save preference
            this.userPreferences = { ...this.userPreferences, language };
            this.saveUserPreferences();
            
            this.analytics?.track('language_changed', { language });
            this.emit('language:changed', language);
        }
    }

    startPerformanceMonitoring() {
        // Monitor page load time
        window.addEventListener('load', () => {
            this.performanceMetrics.loadTime = performance.now();
            this.analytics?.metric('page_load_time', this.performanceMetrics.loadTime);
        });
        
        // Monitor memory usage (if available)
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                this.analytics?.metric('memory_usage', {
                    used: memory.usedJSHeapSize,
                    total: memory.totalJSHeapSize,
                    limit: memory.jsHeapSizeLimit
                });
            }, 30000); // Every 30 seconds
        }
        
        // Monitor API performance
        if (this.components.apiClient) {
            this.components.apiClient.on('requestSuccess', (data) => {
                this.analytics?.metric('api_response_time', data.duration, {
                    endpoint: data.url,
                    method: data.method
                });
            });
        }
    }

    setupPerformanceObserver() {
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach((entry) => {
                this.analytics?.metric('performance_entry', entry.duration, {
                    type: entry.entryType,
                    name: entry.name
                });
            });
        });
        
        observer.observe({ entryTypes: ['measure', 'navigation', 'resource'] });
    }

    setupGlobalErrorHandling() {
        // Handle JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError('JavaScript Error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error
            });
        });
        
        // Handle promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError('Unhandled Promise Rejection', {
                reason: event.reason,
                promise: event.promise
            });
        });
    }

    handleError(type, error) {
        const errorData = {
            type,
            error: error instanceof Error ? {
                message: error.message,
                stack: error.stack,
                name: error.name
            } : error,
            timestamp: Date.now(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            sessionId: this.sessionId
        };
        
        this.errorQueue.push(errorData);
        this.performanceMetrics.errors++;
        
        // Limit error queue size
        if (this.errorQueue.length > this.maxErrors) {
            this.errorQueue = this.errorQueue.slice(-this.maxErrors);
        }
        
        // Log error
        this.log('Error occurred:', errorData);
        
        // Track in analytics
        this.analytics?.track('error', errorData);
        
        // Show user-friendly error message for critical errors
        if (type.includes('Critical') || type.includes('Fatal')) {
            this.showToast('An error occurred. Please refresh the page if problems persist.', 'error');
        }
    }

    // Event handling
    handleOnlineStatusChange(isOnline) {
        this.isOnline = isOnline;
        
        if (isOnline) {
            this.showToast('Connection restored', 'success');
            this.emit('app:online');
        } else {
            this.showToast('Connection lost - working offline', 'warning');
            this.emit('app:offline');
        }
        
        this.analytics?.track('connection_status', { online: isOnline });
    }

    handleVisibilityChange() {
        const isVisible = !document.hidden;
        this.analytics?.track('visibility_change', { visible: isVisible });
        this.emit('app:visibility', isVisible);
    }

    handleBeforeUnload(event) {
        // Save any pending data
        this.saveUserPreferences();
        
        // Send analytics
        this.sendAnalytics(true);
        
        this.analytics?.track('page_unload');
    }

    handleResize() {
        this.checkResponsiveBreakpoints();
        this.emit('app:resize', {
            width: window.innerWidth,
            height: window.innerHeight
        });
    }

    handleKeyboardShortcuts(event) {
        const shortcuts = {
            'ctrl+k': () => this.chatSystem?.openChat(),
            'ctrl+/': () => this.showHelpModal(),
            'ctrl+shift+d': () => this.toggleDebugMode(),
            'ctrl+shift+t': () => this.toggleTheme()
        };
        
        const key = `${event.ctrlKey ? 'ctrl+' : ''}${event.shiftKey ? 'shift+' : ''}${event.key.toLowerCase()}`;
        
        if (shortcuts[key]) {
            event.preventDefault();
            shortcuts[key]();
        }
    }

    // Utility methods
    checkFirstVisit() {
        const hasVisited = localStorage.getItem('mosdac_visited');
        if (!hasVisited) {
            localStorage.setItem('mosdac_visited', 'true');
            this.showWelcomeMessage();
            this.analytics?.track('first_visit');
        }
    }

    showWelcomeMessage() {
        setTimeout(() => {
            this.showToast('Welcome to MOSDAC AI Help Bot! Click the chat icon to get started.', 'info', 8000);
        }, 2000);
    }

    showHelpModal() {
        window.openModal('helpModal');
    }

    toggleDebugMode() {
        this.debug = !this.debug;
        this.config.DEBUG = this.debug;
        this.showToast(`Debug mode ${this.debug ? 'enabled' : 'disabled'}`, 'info');
    }

    async sendAnalytics(force = false) {
        if (!this.analytics || (!force && this.analytics.events.length < 10)) return;
        
        try {
            const data = {
                events: this.analytics.events.splice(0, 100), // Send up to 100 events
                metrics: this.analytics.metrics,
                sessionId: this.sessionId,
                timestamp: Date.now()
            };
            
            if (this.components.apiClient) {
                await this.components.apiClient.sendAnalytics(data);
            }
            
        } catch (error) {
            this.log('Failed to send analytics:', error);
        }
    }

    // Event emitter functionality
    emit(event, data) {
        const customEvent = new CustomEvent(event, { detail: data });
        document.dispatchEvent(customEvent);
    }

    on(event, callback) {
        document.addEventListener(event, callback);
    }

    off(event, callback) {
        document.removeEventListener(event, callback);
    }

    // Logging
    log(message, data = null) {
        if (this.debug) {
            console.log(`[MOSDAC] ${message}`, data);
        }
    }

    // Public API
    getComponent(name) {
        return this.components[name];
    }

    getConfig() {
        return { ...this.config };
    }

    getMetrics() {
        return {
            performance: { ...this.performanceMetrics },
            analytics: this.analytics?.metrics,
            errors: this.errorQueue.length
        };
    }

    restart() {
        window.location.reload();
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        window.mosdacApp = new MOSDACApp();
        await window.mosdacApp.init();
    } catch (error) {
        console.error('Failed to initialize MOSDAC App:', error);
        
        // Show fallback error message
        document.body.innerHTML = `
            <div style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: Arial, sans-serif;">
                <div style="text-align: center; padding: 2rem;">
                    <h1 style="color: #e74c3c;">Application Error</h1>
                    <p>Failed to initialize the MOSDAC AI Help Bot.</p>
                    <button onclick="window.location.reload()" style="padding: 0.5rem 1rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Reload Page
                    </button>
                </div>
            </div>
        `;
    }
});

// Export for global use
window.MOSDACApp = MOSDACApp;
