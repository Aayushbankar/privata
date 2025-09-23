/* MOSDAC AI Help Bot - Feedback System */
/* Enhanced feedback collection with analytics and user experience improvements */

class FeedbackSystem {
    constructor() {
        this.apiClient = new MOSDACAPIClient();
        this.currentRating = 0;
        this.feedbackHistory = [];
        this.sessionFeedbacks = new Map();
        this.feedbackPromptDelay = 2000; // 2 seconds
        this.maxFeedbacksPerSession = 5;
        
        // DOM elements
        this.feedbackModal = null;
        this.ratingStars = [];
        this.commentTextarea = null;
        this.categorySelect = null;
        this.submitButton = null;
        
        // Feedback state
        this.isSubmitting = false;
        this.currentMessageId = null;
        this.currentMessageData = null;
        
        // Analytics
        this.feedbackMetrics = {
            totalSubmitted: 0,
            averageRating: 0,
            categoryDistribution: {},
            ratingDistribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 }
        };
        
        this.init();
    }

    init() {
        this.initializeElements();
        this.setupEventListeners();
        this.loadFeedbackHistory();
        this.initializeMetrics();
    }

    initializeElements() {
        this.feedbackModal = document.getElementById('feedbackModal');
        this.ratingStars = document.querySelectorAll('.rating-star');
        this.commentTextarea = document.getElementById('feedbackComment');
        this.categorySelect = document.getElementById('feedbackCategory');
        this.submitButton = document.getElementById('submitFeedback');
        
        if (!this.feedbackModal) {
            console.error('Feedback modal not found');
            return;
        }
    }

    setupEventListeners() {
        // Modal controls
        document.getElementById('closeFeedbackModal')?.addEventListener('click', () => {
            this.closeFeedbackModal();
        });

        document.getElementById('cancelFeedback')?.addEventListener('click', () => {
            this.closeFeedbackModal();
        });

        // Rating stars
        this.ratingStars.forEach((star, index) => {
            star.addEventListener('click', () => {
                this.setRating(index + 1);
            });

            star.addEventListener('mouseenter', () => {
                this.previewRating(index + 1);
            });

            star.addEventListener('mouseleave', () => {
                this.resetRatingPreview();
            });
        });

        // Submit feedback
        this.submitButton?.addEventListener('click', () => {
            this.submitFeedback();
        });

        // Comment textarea
        this.commentTextarea?.addEventListener('input', () => {
            this.updateSubmitButton();
            this.updateCharacterCount();
        });

        // Category selection
        this.categorySelect?.addEventListener('change', () => {
            this.updateSubmitButton();
        });

        // Quick feedback buttons
        document.querySelectorAll('.quick-feedback-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const rating = parseInt(e.target.dataset.rating);
                const category = e.target.dataset.category;
                this.submitQuickFeedback(rating, category);
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (this.feedbackModal?.classList.contains('show')) {
                // Number keys for rating
                if (e.key >= '1' && e.key <= '5') {
                    this.setRating(parseInt(e.key));
                }
                
                // Enter to submit (if valid)
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    this.submitFeedback();
                }
                
                // Escape to close
                if (e.key === 'Escape') {
                    this.closeFeedbackModal();
                }
            }
        });

        // Click outside to close
        this.feedbackModal?.addEventListener('click', (e) => {
            if (e.target === this.feedbackModal) {
                this.closeFeedbackModal();
            }
        });
    }

    showFeedbackModal(messageData = null) {
        if (!this.feedbackModal) return;
        
        // Check if we've already collected enough feedback this session
        if (this.sessionFeedbacks.size >= this.maxFeedbacksPerSession) {
            return;
        }
        
        this.currentMessageData = messageData;
        this.currentMessageId = messageData?.id || null;
        
        // Reset form
        this.resetForm();
        
        // Show modal
        this.feedbackModal.classList.add('show');
        document.body.classList.add('modal-open');
        
        // Focus first star
        setTimeout(() => {
            this.ratingStars[0]?.focus();
        }, 300);
        
        this.trackEvent('feedback_modal_opened');
    }

    closeFeedbackModal() {
        if (!this.feedbackModal) return;
        
        this.feedbackModal.classList.remove('show');
        document.body.classList.remove('modal-open');
        
        this.resetForm();
        this.currentMessageData = null;
        this.currentMessageId = null;
        
        this.trackEvent('feedback_modal_closed');
    }

    showFeedbackPrompt(messageData) {
        // Check if we should show feedback prompt for this message
        if (!this.shouldShowFeedbackPrompt(messageData)) {
            return;
        }
        
        // Create inline feedback prompt
        const prompt = this.createFeedbackPrompt(messageData);
        
        // Find the message element and append prompt
        const messageElement = document.querySelector(`[data-message-id="${messageData.id}"]`);
        if (messageElement) {
            const content = messageElement.querySelector('.message-content');
            if (content && !content.querySelector('.feedback-prompt')) {
                content.appendChild(prompt);
            }
        }
    }

    createFeedbackPrompt(messageData) {
        const prompt = document.createElement('div');
        prompt.className = 'feedback-prompt';
        
        prompt.innerHTML = `
            <div class="feedback-prompt-content">
                <span class="feedback-prompt-text">Was this helpful?</span>
                <div class="feedback-prompt-actions">
                    <button class="feedback-prompt-btn positive" data-rating="5" data-message-id="${messageData.id}">
                        <i class="fas fa-thumbs-up"></i>
                        <span>Yes</span>
                    </button>
                    <button class="feedback-prompt-btn negative" data-rating="2" data-message-id="${messageData.id}">
                        <i class="fas fa-thumbs-down"></i>
                        <span>No</span>
                    </button>
                    <button class="feedback-prompt-btn detailed" data-message-id="${messageData.id}">
                        <i class="fas fa-comment"></i>
                        <span>Details</span>
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners
        prompt.querySelectorAll('.feedback-prompt-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const rating = e.currentTarget.dataset.rating;
                const messageId = e.currentTarget.dataset.messageId;
                
                if (rating) {
                    this.submitQuickFeedback(parseInt(rating), 'general', messageId);
                } else {
                    this.showFeedbackModal(messageData);
                }
                
                // Remove prompt after interaction
                prompt.remove();
            });
        });
        
        return prompt;
    }

    shouldShowFeedbackPrompt(messageData) {
        // Don't show for system messages or errors
        if (messageData.system || messageData.error) {
            return false;
        }
        
        // Don't show if already provided feedback for this message
        if (this.sessionFeedbacks.has(messageData.id)) {
            return false;
        }
        
        // Don't show if reached session limit
        if (this.sessionFeedbacks.size >= this.maxFeedbacksPerSession) {
            return false;
        }
        
        // Show randomly (30% chance) to avoid overwhelming users
        return Math.random() < 0.3;
    }

    setRating(rating) {
        this.currentRating = rating;
        this.updateRatingDisplay();
        this.updateSubmitButton();
        
        // Provide haptic feedback if available
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
        
        this.trackEvent('rating_selected', { rating });
    }

    previewRating(rating) {
        this.ratingStars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('preview');
            } else {
                star.classList.remove('preview');
            }
        });
    }

    resetRatingPreview() {
        this.ratingStars.forEach(star => {
            star.classList.remove('preview');
        });
    }

    updateRatingDisplay() {
        this.ratingStars.forEach((star, index) => {
            if (index < this.currentRating) {
                star.classList.add('active');
                star.classList.remove('inactive');
            } else {
                star.classList.remove('active');
                star.classList.add('inactive');
            }
        });
        
        // Update rating text
        const ratingText = document.getElementById('ratingText');
        if (ratingText) {
            const texts = {
                1: 'Very Poor',
                2: 'Poor',
                3: 'Average',
                4: 'Good',
                5: 'Excellent'
            };
            ratingText.textContent = texts[this.currentRating] || '';
        }
    }

    updateSubmitButton() {
        if (!this.submitButton) return;
        
        const hasRating = this.currentRating > 0;
        const hasComment = this.commentTextarea?.value.trim().length > 0;
        const hasCategory = this.categorySelect?.value !== '';
        
        // Enable if has rating (comment and category are optional)
        this.submitButton.disabled = !hasRating || this.isSubmitting;
        
        // Update button text based on state
        if (this.isSubmitting) {
            this.submitButton.textContent = 'Submitting...';
        } else if (hasRating && (hasComment || hasCategory)) {
            this.submitButton.textContent = 'Submit Feedback';
        } else if (hasRating) {
            this.submitButton.textContent = 'Submit Rating';
        } else {
            this.submitButton.textContent = 'Select Rating';
        }
    }

    updateCharacterCount() {
        const counter = document.getElementById('commentCharCount');
        if (counter && this.commentTextarea) {
            const current = this.commentTextarea.value.length;
            const max = 500;
            counter.textContent = `${current}/${max}`;
            
            if (current > max * 0.9) {
                counter.classList.add('warning');
            } else {
                counter.classList.remove('warning');
            }
        }
    }

    async submitFeedback() {
        if (!this.currentRating || this.isSubmitting) return;
        
        this.isSubmitting = true;
        this.updateSubmitButton();
        
        try {
            const feedbackData = {
                rating: this.currentRating,
                comment: this.commentTextarea?.value.trim() || '',
                category: this.categorySelect?.value || 'general',
                messageId: this.currentMessageId,
                sessionId: this.apiClient.getSessionId(),
                language: this.apiClient.getLanguage(),
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                url: window.location.href
            };
            
            // Add message context if available
            if (this.currentMessageData) {
                feedbackData.messageContext = {
                    content: this.currentMessageData.content,
                    sources: this.currentMessageData.sources,
                    metadata: this.currentMessageData.metadata
                };
            }
            
            const response = await this.apiClient.submitFeedback(feedbackData);
            
            if (response.success) {
                this.handleFeedbackSuccess(feedbackData);
            } else {
                throw new Error(response.error?.message || 'Failed to submit feedback');
            }
            
        } catch (error) {
            console.error('Feedback submission error:', error);
            this.handleFeedbackError(error);
        } finally {
            this.isSubmitting = false;
            this.updateSubmitButton();
        }
    }

    async submitQuickFeedback(rating, category = 'general', messageId = null) {
        try {
            const feedbackData = {
                rating,
                category,
                messageId: messageId || this.currentMessageId,
                sessionId: this.apiClient.getSessionId(),
                language: this.apiClient.getLanguage(),
                timestamp: new Date().toISOString(),
                quick: true
            };
            
            const response = await this.apiClient.submitFeedback(feedbackData);
            
            if (response.success) {
                this.handleFeedbackSuccess(feedbackData, true);
            } else {
                throw new Error(response.error?.message || 'Failed to submit feedback');
            }
            
        } catch (error) {
            console.error('Quick feedback error:', error);
            this.showToast('Failed to submit feedback', 'error');
        }
    }

    handleFeedbackSuccess(feedbackData, isQuick = false) {
        // Store in session
        if (feedbackData.messageId) {
            this.sessionFeedbacks.set(feedbackData.messageId, feedbackData);
        }
        
        // Update metrics
        this.updateMetrics(feedbackData);
        
        // Store in history
        this.feedbackHistory.push(feedbackData);
        this.saveFeedbackHistory();
        
        // Show success message
        if (isQuick) {
            this.showToast('Thank you for your feedback!', 'success');
        } else {
            this.showFeedbackSuccess();
        }
        
        // Close modal if open
        if (!isQuick) {
            setTimeout(() => {
                this.closeFeedbackModal();
            }, 2000);
        }
        
        this.trackEvent('feedback_submitted', {
            rating: feedbackData.rating,
            category: feedbackData.category,
            hasComment: !!feedbackData.comment,
            quick: isQuick
        });
    }

    handleFeedbackError(error) {
        this.showToast('Failed to submit feedback. Please try again.', 'error');
        
        // Store locally for retry
        const feedbackData = {
            rating: this.currentRating,
            comment: this.commentTextarea?.value.trim() || '',
            category: this.categorySelect?.value || 'general',
            messageId: this.currentMessageId,
            timestamp: new Date().toISOString(),
            retry: true
        };
        
        this.storePendingFeedback(feedbackData);
        
        this.trackEvent('feedback_error', { error: error.message });
    }

    showFeedbackSuccess() {
        const successMessage = document.createElement('div');
        successMessage.className = 'feedback-success';
        successMessage.innerHTML = `
            <div class="feedback-success-content">
                <i class="fas fa-check-circle"></i>
                <h3>Thank you for your feedback!</h3>
                <p>Your input helps us improve the MOSDAC AI Help Bot.</p>
            </div>
        `;
        
        // Replace modal content temporarily
        const modalBody = this.feedbackModal?.querySelector('.modal-body');
        if (modalBody) {
            const originalContent = modalBody.innerHTML;
            modalBody.innerHTML = '';
            modalBody.appendChild(successMessage);
            
            // Restore original content after delay
            setTimeout(() => {
                modalBody.innerHTML = originalContent;
                this.initializeElements();
                this.setupEventListeners();
            }, 2000);
        }
    }

    resetForm() {
        this.currentRating = 0;
        this.updateRatingDisplay();
        
        if (this.commentTextarea) {
            this.commentTextarea.value = '';
        }
        
        if (this.categorySelect) {
            this.categorySelect.value = 'general';
        }
        
        this.updateSubmitButton();
        this.updateCharacterCount();
    }

    // Analytics and metrics
    updateMetrics(feedbackData) {
        this.feedbackMetrics.totalSubmitted++;
        this.feedbackMetrics.ratingDistribution[feedbackData.rating]++;
        
        if (feedbackData.category) {
            this.feedbackMetrics.categoryDistribution[feedbackData.category] = 
                (this.feedbackMetrics.categoryDistribution[feedbackData.category] || 0) + 1;
        }
        
        // Calculate average rating
        const total = Object.values(this.feedbackMetrics.ratingDistribution)
            .reduce((sum, count) => sum + count, 0);
        const weightedSum = Object.entries(this.feedbackMetrics.ratingDistribution)
            .reduce((sum, [rating, count]) => sum + (parseInt(rating) * count), 0);
        
        this.feedbackMetrics.averageRating = total > 0 ? weightedSum / total : 0;
        
        this.saveMetrics();
    }

    getMetrics() {
        return { ...this.feedbackMetrics };
    }

    // Data persistence
    saveFeedbackHistory() {
        try {
            const data = {
                history: this.feedbackHistory.slice(-100), // Keep last 100 feedbacks
                sessionFeedbacks: Array.from(this.sessionFeedbacks.entries()),
                timestamp: Date.now()
            };
            
            localStorage.setItem('mosdac_feedback_history', JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save feedback history:', error);
        }
    }

    loadFeedbackHistory() {
        try {
            const saved = localStorage.getItem('mosdac_feedback_history');
            if (saved) {
                const data = JSON.parse(saved);
                
                // Load recent history (within last 7 days)
                const weekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
                if (data.timestamp > weekAgo) {
                    this.feedbackHistory = data.history || [];
                    this.sessionFeedbacks = new Map(data.sessionFeedbacks || []);
                }
            }
        } catch (error) {
            console.error('Failed to load feedback history:', error);
        }
    }

    saveMetrics() {
        try {
            localStorage.setItem('mosdac_feedback_metrics', JSON.stringify(this.feedbackMetrics));
        } catch (error) {
            console.error('Failed to save feedback metrics:', error);
        }
    }

    initializeMetrics() {
        try {
            const saved = localStorage.getItem('mosdac_feedback_metrics');
            if (saved) {
                this.feedbackMetrics = { ...this.feedbackMetrics, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.error('Failed to load feedback metrics:', error);
        }
    }

    storePendingFeedback(feedbackData) {
        try {
            const pending = JSON.parse(localStorage.getItem('mosdac_pending_feedback') || '[]');
            pending.push(feedbackData);
            localStorage.setItem('mosdac_pending_feedback', JSON.stringify(pending));
        } catch (error) {
            console.error('Failed to store pending feedback:', error);
        }
    }

    async retryPendingFeedback() {
        try {
            const pending = JSON.parse(localStorage.getItem('mosdac_pending_feedback') || '[]');
            const successful = [];
            
            for (const feedbackData of pending) {
                try {
                    const response = await this.apiClient.submitFeedback(feedbackData);
                    if (response.success) {
                        successful.push(feedbackData);
                        this.handleFeedbackSuccess(feedbackData, true);
                    }
                } catch (error) {
                    console.error('Retry feedback error:', error);
                }
            }
            
            // Remove successful submissions
            const remaining = pending.filter(item => !successful.includes(item));
            localStorage.setItem('mosdac_pending_feedback', JSON.stringify(remaining));
            
            if (successful.length > 0) {
                this.showToast(`${successful.length} pending feedback(s) submitted`, 'success');
            }
            
        } catch (error) {
            console.error('Failed to retry pending feedback:', error);
        }
    }

    // Public API
    showRatingModal(messageData) {
        this.showFeedbackModal(messageData);
    }

    submitRating(rating, messageId = null) {
        this.submitQuickFeedback(rating, 'general', messageId);
    }

    getFeedbackStats() {
        return {
            totalFeedbacks: this.feedbackHistory.length,
            sessionFeedbacks: this.sessionFeedbacks.size,
            averageRating: this.feedbackMetrics.averageRating,
            ratingDistribution: this.feedbackMetrics.ratingDistribution
        };
    }

    exportFeedbackData() {
        const exportData = {
            history: this.feedbackHistory,
            metrics: this.feedbackMetrics,
            sessionData: Array.from(this.sessionFeedbacks.entries()),
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mosdac-feedback-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }

    // Utility methods
    trackEvent(event, data = {}) {
        if (window.analytics) {
            window.analytics.track(event, {
                ...data,
                sessionId: this.apiClient.getSessionId(),
                timestamp: Date.now()
            });
        }
    }

    showToast(message, type = 'info') {
        if (window.showToast) {
            window.showToast(message, type);
        }
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (typeof MOSDACAPIClient !== 'undefined') {
        window.feedbackSystem = new FeedbackSystem();
    }
});

// Export for global use
window.FeedbackSystem = FeedbackSystem;
