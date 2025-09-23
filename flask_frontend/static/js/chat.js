/* MOSDAC AI Help Bot - Chat System */
/* Enhanced chat functionality with multi-language support and feedback integration */

class ChatSystem {
    constructor() {
        this.apiClient = new MOSDACAPIClient();
        this.messages = [];
        this.isTyping = false;
        this.currentLanguage = 'en';
        this.messageCounter = 0;
        this.maxMessages = 1000;
        this.autoSaveInterval = 30000; // 30 seconds
        
        // DOM elements
        this.chatWidget = null;
        this.chatToggle = null;
        this.chatMessages = null;
        this.messageInput = null;
        this.sendButton = null;
        this.languageSelect = null;
        this.typingIndicator = null;
        
        // Chat state
        this.isOpen = false;
        this.unreadCount = 0;
        this.lastMessageTime = null;
        this.conversationStarted = false;
        
        // Voice recognition
        this.speechRecognition = null;
        this.isListening = false;
        
        // Message queue for offline support
        this.messageQueue = [];
        this.isOnline = navigator.onLine;
        
        this.setupEventListeners();
        this.initializeVoiceRecognition();
        this.loadChatHistory();
    }

    init() {
        this.initializeElements();
        this.setupChatEventListeners();
        this.setupAPIEventListeners();
        this.startAutoSave();
        this.checkOnlineStatus();
    }

    initializeElements() {
        this.chatWidget = document.getElementById('chatbotWidget');
        this.chatToggle = document.getElementById('chatbotToggle');
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.languageSelect = document.getElementById('languageSelect');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        if (!this.chatWidget || !this.chatToggle) {
            console.error('Chat elements not found');
            return;
        }
        
        // Set initial language
        this.currentLanguage = this.languageSelect?.value || 'en';
        this.apiClient.setLanguage(this.currentLanguage);
    }

    setupEventListeners() {
        // Online/offline status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.processMessageQueue();
            this.showToast('Connection restored', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showToast('Connection lost - messages will be queued', 'warning');
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K to open chat
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openChat();
            }
            
            // Escape to close chat
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
        });
    }

    setupChatEventListeners() {
        // Chat toggle
        this.chatToggle?.addEventListener('click', () => {
            this.toggleChat();
        });

        // Close chat
        document.getElementById('closeChatbot')?.addEventListener('click', () => {
            this.closeChat();
        });

        // Minimize chat
        document.getElementById('minimizeChat')?.addEventListener('click', () => {
            this.minimizeChat();
        });

        // Send message
        this.sendButton?.addEventListener('click', () => {
            this.handleSendMessage();
        });

        // Input handling
        this.messageInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        this.messageInput?.addEventListener('input', () => {
            this.handleInputChange();
        });

        // Language selection
        this.languageSelect?.addEventListener('change', (e) => {
            this.handleLanguageChange(e.target.value);
        });

        // Quick actions
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.dataset.query;
                if (query) {
                    this.sendQuickMessage(query);
                }
            });
        });

        // Voice input
        document.getElementById('voiceBtn')?.addEventListener('click', () => {
            this.toggleVoiceInput();
        });

        // File attachment
        document.getElementById('attachBtn')?.addEventListener('click', () => {
            this.handleFileAttachment();
        });
    }

    setupAPIEventListeners() {
        this.apiClient.on('requestStart', (data) => {
            if (data.url.includes('/chat')) {
                this.showTypingIndicator();
            }
        });

        this.apiClient.on('requestSuccess', (data) => {
            if (data.url.includes('/chat')) {
                this.hideTypingIndicator();
            }
        });

        this.apiClient.on('requestError', (data) => {
            this.hideTypingIndicator();
            this.handleAPIError(data.error);
        });

        this.apiClient.on('languageChanged', (language) => {
            this.currentLanguage = language;
            this.updateLanguageUI(language);
        });
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        if (!this.chatWidget) return;
        
        this.chatWidget.classList.add('open');
        this.chatToggle?.classList.add('hidden');
        this.isOpen = true;
        this.unreadCount = 0;
        this.updateUnreadBadge();
        
        // Focus input after animation
        setTimeout(() => {
            this.messageInput?.focus();
        }, 300);
        
        // Mark conversation as started if first time
        if (!this.conversationStarted) {
            this.conversationStarted = true;
            this.trackEvent('chat_opened');
        }
        
        // Scroll to bottom
        this.scrollToBottom();
    }

    closeChat() {
        if (!this.chatWidget) return;
        
        this.chatWidget.classList.remove('open');
        this.chatToggle?.classList.remove('hidden');
        this.isOpen = false;
        
        this.trackEvent('chat_closed');
    }

    minimizeChat() {
        this.closeChat();
    }

    async handleSendMessage() {
        const message = this.messageInput?.value.trim();
        if (!message || this.isTyping) return;

        // Clear input
        this.messageInput.value = '';
        this.updateSendButton();

        // Add user message
        this.addMessage(message, 'user');

        // Send to API
        await this.sendMessageToAPI(message);
    }

    async sendQuickMessage(query) {
        this.addMessage(query, 'user');
        await this.sendMessageToAPI(query);
    }

    async sendMessageToAPI(message) {
        if (!this.isOnline) {
            this.queueMessage(message);
            this.showToast('Message queued - will send when online', 'info');
            return;
        }

        try {
            this.isTyping = true;
            this.updateSendButton();

            const response = await this.apiClient.sendMessage(message, this.currentLanguage);

            if (response.success && response.data) {
                this.addMessage(response.data.response, 'bot', {
                    sources: response.data.sources,
                    metadata: response.data.metadata
                });

                // Show feedback prompt after bot response
                setTimeout(() => {
                    this.showFeedbackPrompt(response.data);
                }, 2000);
            } else {
                throw new Error(response.error?.message || 'Failed to get response');
            }

        } catch (error) {
            console.error('Chat error:', error);
            this.addMessage(
                'I apologize, but I encountered an error. Please try again.',
                'bot',
                { error: true }
            );
            this.showToast('Failed to send message', 'error');
        } finally {
            this.isTyping = false;
            this.updateSendButton();
        }
    }

    addMessage(content, sender, options = {}) {
        const messageId = `msg_${++this.messageCounter}`;
        const timestamp = new Date().toISOString();
        
        const message = {
            id: messageId,
            content,
            sender,
            timestamp,
            ...options
        };

        this.messages.push(message);
        this.renderMessage(message);
        this.scrollToBottom();
        this.lastMessageTime = Date.now();

        // Update unread count if chat is closed
        if (!this.isOpen && sender === 'bot') {
            this.unreadCount++;
            this.updateUnreadBadge();
        }

        // Limit message history
        if (this.messages.length > this.maxMessages) {
            this.messages = this.messages.slice(-this.maxMessages);
            this.cleanupOldMessages();
        }

        this.saveChatHistory();
        return message;
    }

    renderMessage(message) {
        if (!this.chatMessages) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.sender}-message`;
        messageElement.dataset.messageId = message.id;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = message.sender === 'bot' ? 
            '<i class="fas fa-robot"></i>' : 
            '<i class="fas fa-user"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const text = document.createElement('div');
        text.className = 'message-text';
        
        if (message.error) {
            text.classList.add('message-error');
        }

        // Handle markdown-like formatting
        text.innerHTML = this.formatMessageContent(message.content);

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = this.formatTime(message.timestamp);

        content.appendChild(text);

        // Add sources if available
        if (message.sources && message.sources.length > 0) {
            const sources = this.createSourcesElement(message.sources);
            content.appendChild(sources);
        }

        // Add message actions
        if (message.sender === 'bot') {
            const actions = this.createMessageActions(message);
            content.appendChild(actions);
        }

        content.appendChild(time);

        messageElement.appendChild(avatar);
        messageElement.appendChild(content);

        // Add animation
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        
        this.chatMessages.appendChild(messageElement);

        // Animate in
        requestAnimationFrame(() => {
            messageElement.style.transition = 'all 0.3s ease-out';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        });
    }

    formatMessageContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    }

    createSourcesElement(sources) {
        const sourcesContainer = document.createElement('div');
        sourcesContainer.className = 'message-sources';

        const title = document.createElement('h4');
        title.textContent = 'Sources';
        sourcesContainer.appendChild(title);

        const sourcesList = document.createElement('div');
        sourcesList.className = 'sources-list';

        sources.forEach(source => {
            const sourceItem = document.createElement('a');
            sourceItem.className = 'source-item';
            sourceItem.href = source.url;
            sourceItem.target = '_blank';
            sourceItem.rel = 'noopener noreferrer';

            const icon = document.createElement('div');
            icon.className = 'source-icon';
            icon.innerHTML = '<i class="fas fa-external-link-alt"></i>';

            const content = document.createElement('div');
            content.className = 'source-content';

            const title = document.createElement('div');
            title.className = 'source-title';
            title.textContent = source.title || 'External Link';

            const url = document.createElement('div');
            url.className = 'source-url';
            url.textContent = source.url;

            content.appendChild(title);
            content.appendChild(url);

            if (source.relevance) {
                const relevance = document.createElement('div');
                relevance.className = 'source-relevance';
                relevance.textContent = Math.round(source.relevance * 100) + '%';
                sourceItem.appendChild(relevance);
            }

            sourceItem.appendChild(icon);
            sourceItem.appendChild(content);
            sourcesList.appendChild(sourceItem);
        });

        sourcesContainer.appendChild(sourcesList);
        return sourcesContainer;
    }

    createMessageActions(message) {
        const actions = document.createElement('div');
        actions.className = 'message-actions';

        // Copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'message-action-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(message.content);
            this.showToast('Message copied', 'success');
        });

        // Feedback buttons
        const feedbackBtn = document.createElement('button');
        feedbackBtn.className = 'message-action-btn';
        feedbackBtn.innerHTML = '<i class="fas fa-star"></i> Rate';
        feedbackBtn.addEventListener('click', () => {
            this.showFeedbackModal(message);
        });

        actions.appendChild(copyBtn);
        actions.appendChild(feedbackBtn);

        return actions;
    }

    showTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.classList.remove('hidden');
            this.scrollToBottom();
        }
    }

    hideTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.classList.add('hidden');
        }
    }

    handleInputChange() {
        const message = this.messageInput?.value.trim();
        this.updateSendButton();
        this.updateCharacterCount();
        
        // Show suggestions based on input
        if (message.length > 2) {
            this.showSuggestions(message);
        } else {
            this.hideSuggestions();
        }
    }

    updateSendButton() {
        if (!this.sendButton || !this.messageInput) return;
        
        const hasMessage = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasMessage || this.isTyping;
    }

    updateCharacterCount() {
        const counter = document.getElementById('charCount');
        if (counter && this.messageInput) {
            counter.textContent = this.messageInput.value.length;
        }
    }

    handleLanguageChange(language) {
        this.currentLanguage = language;
        this.apiClient.setLanguage(language);
        
        // Add system message about language change
        const languageName = window.MOSDAC_CONFIG?.LANGUAGES[language] || language;
        this.addMessage(
            `Language changed to ${languageName}. I will now respond in your selected language.`,
            'bot',
            { system: true }
        );
        
        this.trackEvent('language_changed', { language });
    }

    updateLanguageUI(language) {
        if (this.languageSelect) {
            this.languageSelect.value = language;
        }
    }

    scrollToBottom() {
        if (this.chatMessages) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }

    updateUnreadBadge() {
        const badge = document.getElementById('unreadBadge');
        if (badge) {
            badge.textContent = this.unreadCount;
            badge.classList.toggle('show', this.unreadCount > 0);
        }
    }

    // Voice recognition methods
    initializeVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.speechRecognition = new SpeechRecognition();
            
            this.speechRecognition.continuous = false;
            this.speechRecognition.interimResults = false;
            this.speechRecognition.lang = this.getVoiceLanguage();
            
            this.speechRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                if (this.messageInput) {
                    this.messageInput.value = transcript;
                    this.updateSendButton();
                }
                this.stopListening();
            };
            
            this.speechRecognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopListening();
                this.showToast('Voice recognition failed', 'error');
            };
            
            this.speechRecognition.onend = () => {
                this.stopListening();
            };
        }
    }

    toggleVoiceInput() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (!this.speechRecognition) {
            this.showToast('Voice recognition not supported', 'error');
            return;
        }
        
        this.isListening = true;
        this.speechRecognition.lang = this.getVoiceLanguage();
        this.speechRecognition.start();
        
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.classList.add('recording');
        }
        
        this.showToast('Listening...', 'info');
    }

    stopListening() {
        if (this.speechRecognition && this.isListening) {
            this.speechRecognition.stop();
        }
        
        this.isListening = false;
        
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.classList.remove('recording');
        }
    }

    getVoiceLanguage() {
        const languageMap = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'bn': 'bn-IN',
            'mr': 'mr-IN',
            'gu': 'gu-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'pa': 'pa-IN'
        };
        
        return languageMap[this.currentLanguage] || 'en-US';
    }

    // Suggestions system
    showSuggestions(query) {
        // Implementation for showing query suggestions
        const suggestions = this.generateSuggestions(query);
        const suggestionsContainer = document.getElementById('suggestions');
        
        if (suggestions.length > 0 && suggestionsContainer) {
            this.renderSuggestions(suggestions);
            suggestionsContainer.classList.remove('hidden');
        }
    }

    hideSuggestions() {
        const suggestionsContainer = document.getElementById('suggestions');
        if (suggestionsContainer) {
            suggestionsContainer.classList.add('hidden');
        }
    }

    generateSuggestions(query) {
        const commonQueries = [
            'How to download satellite data?',
            'What weather data is available?',
            'How to access ocean data?',
            'Show me navigation help',
            'What is MOSDAC?',
            'How to register on MOSDAC?'
        ];
        
        return commonQueries.filter(suggestion => 
            suggestion.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 3);
    }

    renderSuggestions(suggestions) {
        const suggestionsList = document.getElementById('suggestionsList');
        if (!suggestionsList) return;
        
        suggestionsList.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                if (this.messageInput) {
                    this.messageInput.value = suggestion;
                    this.updateSendButton();
                    this.hideSuggestions();
                }
            });
            suggestionsList.appendChild(item);
        });
    }

    // File attachment handling
    handleFileAttachment() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,.pdf,.doc,.docx,.txt';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                this.uploadFile(file);
            }
        };
        input.click();
    }

    async uploadFile(file) {
        try {
            this.showToast('Uploading file...', 'info');
            
            const response = await this.apiClient.uploadFile(file);
            
            if (response.success) {
                this.addMessage(`File uploaded: ${file.name}`, 'user', {
                    file: {
                        name: file.name,
                        size: file.size,
                        type: file.type,
                        url: response.data.url
                    }
                });
                this.showToast('File uploaded successfully', 'success');
            } else {
                throw new Error(response.error?.message || 'Upload failed');
            }
        } catch (error) {
            console.error('File upload error:', error);
            this.showToast('File upload failed', 'error');
        }
    }

    // Offline support
    queueMessage(message) {
        this.messageQueue.push({
            message,
            timestamp: Date.now(),
            language: this.currentLanguage
        });
    }

    async processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isOnline) {
            const queued = this.messageQueue.shift();
            await this.sendMessageToAPI(queued.message);
        }
    }

    checkOnlineStatus() {
        setInterval(() => {
            const wasOnline = this.isOnline;
            this.isOnline = navigator.onLine;
            
            if (!wasOnline && this.isOnline) {
                this.processMessageQueue();
            }
        }, 5000);
    }

    // Chat history management
    saveChatHistory() {
        try {
            const history = {
                messages: this.messages.slice(-50), // Save last 50 messages
                sessionId: this.apiClient.getSessionId(),
                language: this.currentLanguage,
                timestamp: Date.now()
            };
            
            localStorage.setItem('mosdac_chat_history', JSON.stringify(history));
        } catch (error) {
            console.error('Failed to save chat history:', error);
        }
    }

    loadChatHistory() {
        try {
            const saved = localStorage.getItem('mosdac_chat_history');
            if (saved) {
                const history = JSON.parse(saved);
                
                // Load recent messages (within last 24 hours)
                const dayAgo = Date.now() - (24 * 60 * 60 * 1000);
                if (history.timestamp > dayAgo) {
                    this.messages = history.messages || [];
                    this.messageCounter = this.messages.length;
                    
                    // Render loaded messages
                    this.messages.forEach(message => {
                        this.renderMessage(message);
                    });
                }
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    cleanupOldMessages() {
        // Remove old message elements from DOM
        const messageElements = this.chatMessages?.querySelectorAll('.message');
        if (messageElements && messageElements.length > this.maxMessages) {
            const toRemove = messageElements.length - this.maxMessages;
            for (let i = 0; i < toRemove; i++) {
                messageElements[i].remove();
            }
        }
    }

    startAutoSave() {
        setInterval(() => {
            this.saveChatHistory();
        }, this.autoSaveInterval);
    }

    // Feedback integration
    showFeedbackPrompt(messageData) {
        if (window.feedbackSystem) {
            window.feedbackSystem.showFeedbackPrompt(messageData);
        }
    }

    showFeedbackModal(message) {
        if (window.feedbackSystem) {
            window.feedbackSystem.showFeedbackModal(message);
        }
    }

    // Analytics and tracking
    trackEvent(event, data = {}) {
        if (window.analytics) {
            window.analytics.track(event, {
                ...data,
                sessionId: this.apiClient.getSessionId(),
                language: this.currentLanguage,
                timestamp: Date.now()
            });
        }
    }

    // Error handling
    handleAPIError(error) {
        let message = 'An error occurred. Please try again.';
        
        if (error.status === 429) {
            message = 'Too many requests. Please wait a moment before trying again.';
        } else if (error.status >= 500) {
            message = 'Server error. Please try again later.';
        } else if (error.status === 0) {
            message = 'Connection error. Please check your internet connection.';
        }
        
        this.addMessage(message, 'bot', { error: true });
    }

    // Utility methods
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            return `${Math.floor(diff / 60000)}m ago`;
        } else if (date.toDateString() === now.toDateString()) { // Same day
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else {
            return date.toLocaleDateString();
        }
    }

    showToast(message, type = 'info') {
        if (window.showToast) {
            window.showToast(message, type);
        }
    }

    // Public API
    sendMessage(message) {
        if (this.messageInput) {
            this.messageInput.value = message;
            this.handleSendMessage();
        }
    }

    clearChat() {
        this.messages = [];
        this.messageCounter = 0;
        if (this.chatMessages) {
            this.chatMessages.innerHTML = '';
        }
        this.saveChatHistory();
    }

    exportChat() {
        const chatData = {
            messages: this.messages,
            sessionId: this.apiClient.getSessionId(),
            language: this.currentLanguage,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(chatData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mosdac-chat-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
}

// Export for global use
window.ChatSystem = ChatSystem;
