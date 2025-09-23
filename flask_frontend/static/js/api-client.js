/* MOSDAC AI Help Bot - API Client */
/* Enhanced API client with comprehensive error handling and caching */

class MOSDACAPIClient {
    constructor(baseURL = window.MOSDAC_CONFIG?.API_BASE_URL || '/api') {
        this.baseURL = baseURL;
        this.sessionId = window.MOSDAC_CONFIG?.SESSION_ID || this.generateSessionId();
        this.selectedLanguage = 'en';
        this.cache = new Map();
        this.requestQueue = new Map();
        this.retryAttempts = 3;
        this.timeout = 30000;
        
        // Request interceptors
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        
        // Event emitter for API events
        this.eventListeners = new Map();
        
        this.setupDefaultInterceptors();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    setupDefaultInterceptors() {
        // Request interceptor for authentication
        this.addRequestInterceptor((config) => {
            if (window.MOSDAC_CONFIG?.CSRF_TOKEN) {
                config.headers['X-CSRF-Token'] = window.MOSDAC_CONFIG.CSRF_TOKEN;
            }
            return config;
        });

        // Response interceptor for error handling
        this.addResponseInterceptor(
            (response) => response,
            (error) => {
                this.emit('error', error);
                return Promise.reject(error);
            }
        );
    }

    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }

    addResponseInterceptor(onFulfilled, onRejected) {
        this.responseInterceptors.push({ onFulfilled, onRejected });
    }

    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => callback(data));
        }
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const requestId = this.generateRequestId(url, options);
        
        // Check if request is already in progress
        if (this.requestQueue.has(requestId)) {
            return this.requestQueue.get(requestId);
        }

        // Check cache for GET requests
        if (options.method === 'GET' || !options.method) {
            const cached = this.getFromCache(requestId);
            if (cached) {
                return Promise.resolve(cached);
            }
        }

        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: this.timeout,
        };

        let config = { ...defaultOptions, ...options };
        config.url = url;

        // Apply request interceptors
        for (const interceptor of this.requestInterceptors) {
            config = interceptor(config) || config;
        }

        const requestPromise = this.executeRequest(config, requestId);
        this.requestQueue.set(requestId, requestPromise);

        try {
            const result = await requestPromise;
            this.requestQueue.delete(requestId);
            return result;
        } catch (error) {
            this.requestQueue.delete(requestId);
            throw error;
        }
    }

    async executeRequest(config, requestId, attempt = 1) {
        try {
            this.emit('requestStart', { url: config.url, attempt });

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), config.timeout);

            const response = await fetch(config.url, {
                ...config,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            let data;
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                const error = new APIError(
                    data.error?.message || `HTTP ${response.status}`,
                    response.status,
                    data
                );
                throw error;
            }

            // Apply response interceptors
            let result = data;
            for (const interceptor of this.responseInterceptors) {
                if (interceptor.onFulfilled) {
                    result = interceptor.onFulfilled(result) || result;
                }
            }

            // Cache successful GET requests
            if (config.method === 'GET' || !config.method) {
                this.setCache(requestId, result);
            }

            this.emit('requestSuccess', { url: config.url, data: result });
            return result;

        } catch (error) {
            this.emit('requestError', { url: config.url, error, attempt });

            // Handle different error types
            if (error.name === 'AbortError') {
                throw new APIError('Request timeout', 408);
            }

            if (error instanceof APIError) {
                // Apply response error interceptors
                for (const interceptor of this.responseInterceptors) {
                    if (interceptor.onRejected) {
                        const result = interceptor.onRejected(error);
                        if (result) return result;
                    }
                }
            }

            // Retry logic for certain errors
            if (this.shouldRetry(error, attempt)) {
                await this.delay(Math.pow(2, attempt) * 1000); // Exponential backoff
                return this.executeRequest(config, requestId, attempt + 1);
            }

            throw error;
        }
    }

    shouldRetry(error, attempt) {
        if (attempt >= this.retryAttempts) return false;
        
        // Retry on network errors or 5xx status codes
        return !error.status || error.status >= 500;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    generateRequestId(url, options) {
        const key = `${options.method || 'GET'}:${url}:${JSON.stringify(options.body || {})}`;
        return btoa(key).replace(/[^a-zA-Z0-9]/g, '');
    }

    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < cached.ttl) {
            return cached.data;
        }
        this.cache.delete(key);
        return null;
    }

    setCache(key, data, ttl = 300000) { // 5 minutes default
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        });
    }

    clearCache() {
        this.cache.clear();
    }

    // Chat API methods
    async sendMessage(query, language = this.selectedLanguage, options = {}) {
        return this.request('/chat', {
            method: 'POST',
            body: JSON.stringify({
                query,
                session_id: this.sessionId,
                language,
                ...options
            })
        });
    }

    async getChatSessions() {
        return this.request('/sessions');
    }

    async getChatSession(sessionId) {
        return this.request(`/sessions/${sessionId}`);
    }

    async deleteChatSession(sessionId) {
        return this.request(`/sessions/${sessionId}`, {
            method: 'DELETE'
        });
    }

    async clearAllSessions() {
        return this.request('/sessions', {
            method: 'DELETE'
        });
    }

    // Navigation API methods
    async getNavigationGuidance(query, context = {}) {
        return this.request('/navigation/guide', {
            method: 'POST',
            body: JSON.stringify({
                query,
                user_id: this.sessionId,
                context
            })
        });
    }

    async detectNavigationIntent(query) {
        return this.request(`/navigation/intent?query=${encodeURIComponent(query)}`);
    }

    // Feedback API methods
    async submitFeedback(feedbackData) {
        return this.request('/feedback/submit', {
            method: 'POST',
            body: JSON.stringify({
                ...feedbackData,
                session_id: this.sessionId,
                language: this.selectedLanguage
            })
        });
    }

    async getFeedbackAnalytics(timeRange = '24h') {
        return this.request(`/feedback/analytics?range=${timeRange}`);
    }

    async getFeedbackList(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request(`/feedback/list?${params}`);
    }

    // Status API methods
    async getSystemStatus() {
        return this.request('/status');
    }

    async getHealthStatus() {
        return this.request('/health', {}, 60000); // 1 minute cache
    }

    async getCacheStats() {
        return this.request('/cache/stats');
    }

    async clearSystemCache() {
        return this.request('/cache/clear', {
            method: 'POST'
        });
    }

    // Admin API methods (require authentication)
    async getAdminConfig() {
        return this.request('/admin/config');
    }

    async updateAdminConfig(config) {
        return this.request('/admin/config', {
            method: 'PUT',
            body: JSON.stringify(config)
        });
    }

    async getSystemLogs(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        return this.request(`/admin/logs?${params}`);
    }

    async getSystemMetrics() {
        return this.request('/admin/metrics');
    }

    // Data management methods
    async startScraping(options = {}) {
        return this.request('/data/scrape', {
            method: 'POST',
            body: JSON.stringify(options)
        });
    }

    async getScrapingStatus(jobId) {
        return this.request(`/data/scrape/${jobId}`);
    }

    async startIngestion(options = {}) {
        return this.request('/data/ingest', {
            method: 'POST',
            body: JSON.stringify(options)
        });
    }

    async getIngestionStatus(jobId) {
        return this.request(`/data/ingest/${jobId}`);
    }

    // Utility methods
    setLanguage(language) {
        this.selectedLanguage = language;
        this.emit('languageChanged', language);
    }

    getLanguage() {
        return this.selectedLanguage;
    }

    setSessionId(sessionId) {
        this.sessionId = sessionId;
        this.emit('sessionChanged', sessionId);
    }

    getSessionId() {
        return this.sessionId;
    }

    // Batch requests
    async batchRequest(requests) {
        const promises = requests.map(req => 
            this.request(req.endpoint, req.options).catch(error => ({ error, request: req }))
        );
        
        return Promise.all(promises);
    }

    // Upload file method
    async uploadFile(file, endpoint = '/upload') {
        const formData = new FormData();
        formData.append('file', file);

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
    }

    // WebSocket connection for real-time updates
    connectWebSocket(endpoint = '/ws') {
        if (this.ws) {
            this.ws.close();
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}${endpoint}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.emit('wsConnected');
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.emit('wsMessage', data);
            } catch (error) {
                console.error('WebSocket message parse error:', error);
            }
        };
        
        this.ws.onclose = () => {
            this.emit('wsDisconnected');
        };
        
        this.ws.onerror = (error) => {
            this.emit('wsError', error);
        };

        return this.ws;
    }

    disconnectWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    // Request cancellation
    cancelRequest(requestId) {
        if (this.requestQueue.has(requestId)) {
            this.requestQueue.delete(requestId);
        }
    }

    cancelAllRequests() {
        this.requestQueue.clear();
    }
}

// Custom API Error class
class APIError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

// Export for use in other modules
window.MOSDACAPIClient = MOSDACAPIClient;
window.APIError = APIError;
