class LEOChatBot {
    constructor() {
        this.API_BASE_URL = 'http://localhost:8000/api/v1';
        this.sessionId = this.generateSessionId();
        this.isOpen = false;
        this.currentNavigationGuidance = null;
        this.currentStepIndex = 0;
        this.isStepByStepMode = false;
        this.selectedLanguage = 'en';
        this.isTyping = false;
        this.navigationMode = false;
        this.currentNavigationSteps = [];
        this.initializeEventListeners();
        this.initializeChatbot();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeEventListeners() {
        const toggleButton = document.getElementById('chatbotToggle');
        const closeButton = document.getElementById('closeChatbot');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const languageSelect = document.getElementById('languageSelect');

        // Toggle chatbot visibility
        toggleButton.addEventListener('click', () => {
            this.toggleChatbot();
        });

        // Close chatbot
        closeButton.addEventListener('click', () => {
            this.closeChatbot();
        });

        // Handle message sending
        sendButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleUserMessage();
        });

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleUserMessage();
            }
        });

        // Handle language selection
        languageSelect.addEventListener('change', (e) => {
            this.selectedLanguage = e.target.value;
            this.addMessage('bot', `Language changed to ${e.target.selectedOptions[0].text}. I can now respond in your selected language.`);
        });

        // Handle feedback modal events
        this.initializeFeedbackEvents();
    }

    initializeFeedbackEvents() {
        const feedbackModal = document.getElementById('feedbackModal');
        const closeFeedback = document.getElementById('closeFeedback');
        const skipFeedback = document.getElementById('skipFeedback');
        const submitFeedback = document.getElementById('submitFeedback');
        const starRating = document.getElementById('starRating');
        
        this.currentFeedbackData = null;
        this.selectedRating = 0;

        // Close feedback modal
        closeFeedback.addEventListener('click', () => {
            this.closeFeedbackModal();
        });

        skipFeedback.addEventListener('click', () => {
            this.closeFeedbackModal();
        });

        // Handle star rating
        starRating.addEventListener('click', (e) => {
            if (e.target.classList.contains('star')) {
                const rating = parseInt(e.target.dataset.rating);
                this.setStarRating(rating);
            }
        });

        // Handle star hover effects
        starRating.addEventListener('mouseover', (e) => {
            if (e.target.classList.contains('star')) {
                const rating = parseInt(e.target.dataset.rating);
                this.highlightStars(rating);
            }
        });

        starRating.addEventListener('mouseout', () => {
            this.highlightStars(this.selectedRating);
        });

        // Submit feedback
        submitFeedback.addEventListener('click', () => {
            this.submitFeedback();
        });

        // Close modal when clicking outside
        feedbackModal.addEventListener('click', (e) => {
            if (e.target === feedbackModal) {
                this.closeFeedbackModal();
            }
        });
    }

    initializeChatbot() {
        // Initially hide the chatbot widget and show toggle button
        const widget = document.getElementById('chatbotWidget');
        const toggle = document.getElementById('chatbotToggle');
        
        widget.classList.remove('open');
        toggle.classList.remove('hidden');
        this.isOpen = false;
    }

    toggleChatbot() {
        const widget = document.getElementById('chatbotWidget');
        const toggle = document.getElementById('chatbotToggle');

        if (this.isOpen) {
            this.closeChatbot();
        } else {
            this.openChatbot();
        }
    }

    openChatbot() {
        const widget = document.getElementById('chatbotWidget');
        const toggle = document.getElementById('chatbotToggle');
        
        widget.classList.add('open');
        toggle.classList.add('hidden');
        this.isOpen = true;
        
        // Focus on input after animation
        setTimeout(() => {
            document.getElementById('messageInput').focus();
        }, 300);
    }

    closeChatbot() {
        const widget = document.getElementById('chatbotWidget');
        const toggle = document.getElementById('chatbotToggle');
        
        widget.classList.remove('open');
        toggle.classList.remove('hidden');
        this.isOpen = false;
    }

    async handleUserMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        messageInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // First check if this is a navigation request
            const navResponse = await this.checkNavigationIntent(message);
            
            if (navResponse && navResponse.confidence > 0.6) {
                // Handle as navigation request
                await this.handleNavigationRequest(message);
                return;
            }

            // Handle as regular chat request
            const response = await fetch(`${this.API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: message,
                    session_id: this.sessionId,
                    language: this.selectedLanguage
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();

            // The chat API returns ChatResponse directly, not wrapped in success
            if (data.response) {
                const messageId = this.addMessage(data.response, 'bot', data.sources || []);
                // Show feedback option for bot responses
                setTimeout(() => this.showFeedbackOption(messageId, message, data.response), 2000);
            } else {
                this.addErrorMessage('Sorry, I encountered an error processing your request.');
            }

        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.addErrorMessage('Sorry, I\'m having trouble connecting right now. Please try again.');
        }
    }

    async checkNavigationIntent(message) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/navigation/intent?query=${encodeURIComponent(message)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.success ? data.data : null;
            }
        } catch (error) {
            console.error('Navigation intent check failed:', error);
        }
        return null;
    }

    async handleNavigationRequest(message) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/navigation/guide`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: message,
                    user_id: this.sessionId
                })
            });

            this.hideTypingIndicator();

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.displayNavigationGuidance(data.data);
                } else {
                    this.addErrorMessage('Sorry, I couldn\'t generate navigation guidance for that request.');
                }
            } else {
                this.addErrorMessage('Sorry, navigation service is temporarily unavailable.');
            }

        } catch (error) {
            console.error('Navigation request failed:', error);
            this.hideTypingIndicator();
            this.addErrorMessage('Sorry, I encountered an error with navigation guidance.');
        }
    }

    displayNavigationGuidance(guidanceData) {
        const path = guidanceData.navigation_path;
        const steps = path.steps || [];
        
        // Create navigation guidance message
        let guidanceHTML = `
            <div class="navigation-guidance">
                <div class="nav-header">
                    <h4>🧭 Navigation Guide: ${path.goal}</h4>
                    <div class="nav-meta">
                        <span class="time-estimate">⏱️ ${path.estimated_time}s</span>
                        <span class="difficulty ${path.difficulty.toLowerCase()}">${path.difficulty}</span>
                        <span class="success-rate">✅ ${Math.round(path.success_rate * 100)}% success rate</span>
                    </div>
                </div>
                
                <div class="nav-steps">
        `;

        steps.forEach((step, index) => {
            guidanceHTML += `
                <div class="nav-step" data-step="${step.step}">
                    <div class="step-number">${step.step}</div>
                    <div class="step-content">
                        <h5>${step.page_title}</h5>
                        <p class="step-description">${step.description}</p>
                        <p class="step-action"><strong>Action:</strong> ${step.action}</p>
                        <div class="step-elements">
                            <small>Look for: ${step.expected_elements.join(', ')}</small>
                        </div>
                        <div class="step-time">⏱️ ~${step.estimated_time}s</div>
                    </div>
                </div>
            `;
        });

        guidanceHTML += `
                </div>
                
                <div class="nav-tips">
                    <h5>💡 Quick Tips:</h5>
                    <ul>
        `;

        (guidanceData.quick_tips || []).forEach(tip => {
            guidanceHTML += `<li>${tip}</li>`;
        });

        guidanceHTML += `
                    </ul>
                </div>
                
                <div class="nav-actions">
                    <button class="btn-start-navigation" onclick="chatbot.startStepByStep()">
                        🚀 Start Step-by-Step Guide
                    </button>
                    <button class="btn-open-mosdac" onclick="window.open('https://mosdac.gov.in', '_blank')">
                        🌐 Open MOSDAC Portal
                    </button>
                </div>
            </div>
        `;

        // Store navigation data for step-by-step mode
        this.currentNavigationSteps = steps;
        this.navigationMode = false;

        // Add the navigation guidance as a bot message
        this.addNavigationMessage(guidanceHTML);
    }

    addNavigationMessage(htmlContent) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message navigation-message';
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="avatar bot-avatar navigation-avatar">
                🧭
            </div>
            <div class="message-content navigation-content">
                ${htmlContent}
                <span class="timestamp">Time: ${timestamp}</span>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    startStepByStep() {
        if (this.currentNavigationSteps.length === 0) {
            this.addMessage("No navigation steps available. Please ask for navigation help first.", 'bot');
            return;
        }

        this.navigationMode = true;
        this.currentStepIndex = 0;
        
        this.addMessage("🚀 Starting step-by-step navigation guide! I'll walk you through each step.", 'bot');
        this.showCurrentStep();
    }

    showCurrentStep() {
        if (!this.navigationMode || this.currentStepIndex >= this.currentNavigationSteps.length) {
            this.completeNavigation();
            return;
        }

        const step = this.currentNavigationSteps[this.currentStepIndex];
        
        let stepHTML = `
            <div class="current-step">
                <h4>Step ${step.step}: ${step.page_title}</h4>
                <p><strong>What to do:</strong> ${step.action}</p>
                <p><strong>Look for:</strong> ${step.expected_elements.join(', ')}</p>
                <p><strong>Estimated time:</strong> ~${step.estimated_time} seconds</p>
                
                <div class="step-controls">
                    <button class="btn-step-complete" onclick="chatbot.nextStep()">
                        ✅ I've completed this step
                    </button>
                    <button class="btn-step-help" onclick="chatbot.getStepHelp()">
                        ❓ I need help with this step
                    </button>
                    <button class="btn-stop-navigation" onclick="chatbot.stopNavigation()">
                        ⏹️ Stop guidance
                    </button>
                </div>
            </div>
        `;

        this.addNavigationMessage(stepHTML);
    }

    nextStep() {
        this.currentStepIndex++;
        this.addMessage("Great! Moving to the next step...", 'bot');
        this.showCurrentStep();
    }

    getStepHelp() {
        const step = this.currentNavigationSteps[this.currentStepIndex];
        const helpMessage = `
            Let me provide more details for this step:
            
            **Page:** ${step.page_title}
            **Description:** ${step.description}
            **Detailed Action:** ${step.action}
            
            **What you should see:** ${step.expected_elements.join(', ')}
            
            If you're still having trouble, try refreshing the page or checking if you're on the correct MOSDAC page.
        `;
        
        this.addMessage(helpMessage, 'bot');
    }

    stopNavigation() {
        this.navigationMode = false;
        this.currentStepIndex = 0;
        this.addMessage("Navigation guidance stopped. Feel free to ask for help anytime!", 'bot');
    }

    completeNavigation() {
        this.navigationMode = false;
        this.addMessage("🎉 Congratulations! You've completed all navigation steps. You should now be able to accomplish your goal on MOSDAC!", 'bot');
    }

    addMessage(content, type, sources = []) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        messageDiv.className = `message ${type}-message`;
        messageDiv.setAttribute('data-message-id', messageId);

        const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

        // Create avatar based on message type
        let avatarHTML = '';
        if (type === 'bot') {
            avatarHTML = `
                <div class="avatar bot-avatar">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="8" r="4" fill="#1F3C90"/>
                        <path d="M8 16C8 14 10 12 12 12C14 12 16 14 16 16V18H8V16Z" fill="#1F3C90" opacity="0.8"/>
                        <circle cx="10" cy="7" r="1" fill="white"/>
                        <circle cx="14" cy="7" r="1" fill="white"/>
                    </svg>
                </div>
            `;
        } else {
            avatarHTML = `
                <div class="avatar user-avatar">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" fill="#3C3C3C"/>
                        <path d="M8 14.5C8 13.1193 9.11929 12 10.5 12H13.5C14.8807 12 16 13.1193 16 14.5V16H8V14.5Z" fill="white"/>
                        <circle cx="12" cy="8" r="2" fill="white"/>
                    </svg>
                </div>
            `;
        }

        messageDiv.innerHTML = `
            ${avatarHTML}
            <div class="message-content">
                <p>${this.escapeHtml(content)}</p>
                <span class="timestamp">Time: ${timestamp}</span>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Store sources for modal if needed
        if (sources && sources.length > 0) {
            messageDiv._sources = sources;
        }

        return messageId;
    }

    addErrorMessage(message) {
        this.addMessage(message, 'bot');
    }

    showTypingIndicator() {
        // Add a typing message that will be replaced
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-message';
        typingDiv.id = 'typingMessage';
        
        typingDiv.innerHTML = `
            <div class="avatar bot-avatar">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="4" fill="#1F3C90"/>
                    <path d="M8 16C8 14 10 12 12 12C14 12 16 14 16 16V18H8V16Z" fill="#1F3C90" opacity="0.8"/>
                    <circle cx="10" cy="7" r="1" fill="white"/>
                    <circle cx="14" cy="7" r="1" fill="white"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        this.isTyping = true;
    }

    hideTypingIndicator() {
        const typingMessage = document.getElementById('typingMessage');
        if (typingMessage) {
            typingMessage.remove();
        }
        this.isTyping = false;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showSourcesModal(sourceIndex) {
        const modal = document.getElementById('sourcesModal');
        const sourcesList = document.getElementById('sourcesList');
        const messageElements = document.querySelectorAll('.message');
        
        let sources = [];
        
        // Find the message that contains these sources
        for (const messageElement of messageElements) {
            if (messageElement._sources) {
                sources = messageElement._sources;
                break;
            }
        }

        if (sources.length > 0) {
            const source = sources[sourceIndex];
            
            // Convert local file paths to more readable display names
            let displayUrl = source.url;
            let displayTitle = source.title || 'No title available';
            
            // If it's a local file path, extract just the filename or directory name
            if (source.url.startsWith('/') || source.url.includes('mosdac_complete_data')) {
                const parts = source.url.split('/');
                const lastPart = parts[parts.length - 2]; // Get the directory name
                displayUrl = `mosdac.gov.in/${lastPart.replace(/-/g, ' ')}`;
                displayTitle = lastPart.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            }
            
            sourcesList.innerHTML = `
                <div class="source-modal-item">
                    <div class="source-modal-title">${this.escapeHtml(displayTitle)}</div>
                    <div class="source-modal-url">Source: ${this.escapeHtml(displayUrl)}</div>
                    <div class="source-modal-relevance">Relevance: ${Math.round(source.relevance * 100)}%</div>
                    ${source.content ? `<p style="margin-top: 10px; font-size: 0.9rem; color: #6c757d;">${this.escapeHtml(source.content.substring(0, 200))}...</p>` : ''}
                </div>
            `;
            modal.style.display = 'flex';
        }
    }

    async checkSystemStatus() {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusDot = statusIndicator.querySelector('.status-dot');
        const statusText = statusIndicator.querySelector('.status-text');

        try {
            const response = await fetch(`${this.API_BASE_URL}/status`);
            if (response.ok) {
                const data = await response.json();
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'System Online';
            } else {
                throw new Error('Status check failed');
            }
        } catch (error) {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'System Offline';
            console.error('Status check error:', error);
        }
    }

    // Feedback System Methods
    showFeedbackOption(messageId, userQuery, botResponse) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (!messageElement || messageElement.querySelector('.message-feedback')) return;

        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'message-feedback';
        feedbackDiv.innerHTML = `
            <button class="feedback-button" onclick="chatbot.openFeedbackModal('${messageId}', '${this.escapeForAttribute(userQuery)}', '${this.escapeForAttribute(botResponse)}')">
                👍 Rate Response
            </button>
        `;
        
        messageElement.querySelector('.message-content').appendChild(feedbackDiv);
    }

    openFeedbackModal(messageId, userQuery, botResponse) {
        this.currentFeedbackData = {
            messageId,
            userQuery: this.unescapeAttribute(userQuery),
            botResponse: this.unescapeAttribute(botResponse)
        };
        
        this.selectedRating = 0;
        this.highlightStars(0);
        document.getElementById('feedbackComment').value = '';
        document.getElementById('feedbackModal').classList.add('show');
    }

    closeFeedbackModal() {
        document.getElementById('feedbackModal').classList.remove('show');
        this.currentFeedbackData = null;
        this.selectedRating = 0;
    }

    setStarRating(rating) {
        this.selectedRating = rating;
        this.highlightStars(rating);
    }

    highlightStars(rating) {
        const stars = document.querySelectorAll('.star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    async submitFeedback() {
        if (!this.currentFeedbackData || this.selectedRating === 0) {
            alert('Please select a rating before submitting.');
            return;
        }

        const submitButton = document.getElementById('submitFeedback');
        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';

        try {
            const response = await fetch(`${this.API_BASE_URL}/feedback/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message_id: this.currentFeedbackData.messageId,
                    feedback_type: 'response_rating',
                    rating: this.selectedRating,
                    comment: document.getElementById('feedbackComment').value.trim() || null,
                    user_query: this.currentFeedbackData.userQuery,
                    bot_response: this.currentFeedbackData.botResponse,
                    language: this.selectedLanguage
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.markMessageAsRated(this.currentFeedbackData.messageId);
                this.addMessage('bot', 'Thank you for your feedback! It helps me improve my responses.');
                this.closeFeedbackModal();
            } else {
                throw new Error('Failed to submit feedback');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            alert('Failed to submit feedback. Please try again.');
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Submit Feedback';
        }
    }

    markMessageAsRated(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            const feedbackButton = messageElement.querySelector('.feedback-button');
            if (feedbackButton) {
                feedbackButton.classList.add('rated');
                feedbackButton.textContent = '✓ Rated';
                feedbackButton.disabled = true;
            }
        }
    }

    escapeForAttribute(str) {
        return str.replace(/'/g, '&#39;').replace(/"/g, '&quot;');
    }

    unescapeAttribute(str) {
        return str.replace(/&#39;/g, "'").replace(/&quot;/g, '"');
    }

    async updateSystemInfo() {
        const systemInfo = document.getElementById('systemInfo');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/status`);
            if (response.ok) {
                const data = await response.json();
                
                const lastUpdate = data.vector_database?.last_ingested ? 
                    new Date(data.vector_database.last_ingested).toLocaleString() : 'N/A';
                
                systemInfo.innerHTML = `
                    <div class="info-item">
                        <span class="info-label">Scraped Pages:</span>
                        <span class="info-value">${data.scraped_data?.pages_count || 0}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Vector Documents:</span>
                        <span class="info-value">${data.vector_database?.document_count || 0}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">LLM Status:</span>
                        <span class="info-value">${data.llm?.available ? 'Available' : 'Unavailable'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Last Update:</span>
                        <span class="info-value">${lastUpdate}</span>
                    </div>
                `;
            }
        } catch (error) {
            systemInfo.innerHTML = `
                <div class="info-item">
                    <span class="info-label">Scraped Pages:</span>
                    <span class="info-value">Error loading</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Vector Database:</span>
                    <span class="info-value">Error loading</span>
                </div>
                <div class="info-item">
                    <span class="info-label">LLM Status:</span>
                    <span class="info-value">Error loading</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Last Update:</span>
                    <span class="info-value">Error loading</span>
                </div>
            `;
        }
    }
}

// Initialize the chat bot when the page loads
let chatBot;

document.addEventListener('DOMContentLoaded', () => {
    chatBot = new LEOChatBot();
    
    // Make chatBot globally available for onclick events
    window.chatBot = chatBot;
});
