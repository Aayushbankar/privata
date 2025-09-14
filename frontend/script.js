class MOSDACChatBot {
    constructor() {
        this.API_BASE_URL = 'http://localhost:8000/api/v1';
        this.sessionId = this.generateSessionId();
        this.isTyping = false;
        this.initializeEventListeners();
        this.checkSystemStatus();
        this.updateSystemInfo();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeEventListeners() {
        const chatForm = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const exampleButtons = document.querySelectorAll('.example-btn');
        const modalClose = document.getElementById('modalClose');
        const modal = document.getElementById('sourcesModal');

        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUserMessage();
        });

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleUserMessage();
            }
        });

        exampleButtons.forEach(button => {
            button.addEventListener('click', () => {
                const question = button.getAttribute('data-question');
                messageInput.value = question;
                this.handleUserMessage();
            });
        });

        modalClose.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Auto-focus input on load
        messageInput.focus();
    }

    async handleUserMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!message) return;

        // Clear input and disable send button
        messageInput.value = '';
        document.getElementById('sendButton').disabled = true;

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await this.sendToAPI(message);
            this.hideTypingIndicator();
            this.addMessage(response.response, 'bot', response.sources);
        } catch (error) {
            this.hideTypingIndicator();
            this.addErrorMessage('Sorry, I encountered an error while processing your request. Please try again.');
            console.error('API Error:', error);
        }

        // Re-enable send button
        document.getElementById('sendButton').disabled = false;
        messageInput.focus();
    }

    async sendToAPI(message) {
        const response = await fetch(`${this.API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: message,
                session_id: this.sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    addMessage(content, type, sources = []) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const timestamp = new Date().toLocaleTimeString();

        let sourcesHTML = '';
        if (sources && sources.length > 0) {
            sourcesHTML = `
                <div class="sources">
                    ${sources.map((source, index) => `
                        <div class="source-item" onclick="chatBot.showSourcesModal(${index})">
                            <span class="source-relevance">${Math.round(source.relevance * 100)}%</span>
                            <span class="source-title">${this.escapeHtml(source.title || source.url)}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(content)}</p>
                ${sourcesHTML}
            </div>
            <div class="message-timestamp">${timestamp}</div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Store sources for modal
        if (sources && sources.length > 0) {
            messageDiv._sources = sources;
        }
    }

    addErrorMessage(message) {
        const chatMessages = document.getElementById('chatMessages');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        chatMessages.appendChild(errorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'flex';
        this.isTyping = true;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'none';
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
            sourcesList.innerHTML = `
                <div class="source-modal-item">
                    <a href="${source.url}" target="_blank" class="source-modal-url">${source.url}</a>
                    <div class="source-modal-title">${this.escapeHtml(source.title || 'No title available')}</div>
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

    async updateSystemInfo() {
        const systemInfo = document.getElementById('systemInfo');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/status`);
            if (response.ok) {
                const data = await response.json();
                
                systemInfo.innerHTML = `
                    <div class="info-item">
                        <span class="info-label">Scraped Pages:</span>
                        <span class="info-value">${data.scraped_pages || 'N/A'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Vector Database:</span>
                        <span class="info-value">${data.vector_db_status || 'N/A'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">LLM Status:</span>
                        <span class="info-value">${data.llm_status || 'N/A'}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Last Update:</span>
                        <span class="info-value">${data.last_update || 'N/A'}</span>
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
    chatBot = new MOSDACChatBot();
    
    // Make chatBot globally available for onclick events
    window.chatBot = chatBot;
    
    // Add keyboard shortcut for focusing input
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement !== document.getElementById('messageInput')) {
            e.preventDefault();
            document.getElementById('messageInput').focus();
        }
    });
});

// Utility function for external access
window.showSourcesModal = function(sourceIndex) {
    if (window.chatBot) {
        window.chatBot.showSourcesModal(sourceIndex);
    }
};
