/* MOSDAC AI Help Bot - Navigation System */
/* Enhanced navigation assistance and guidance system */

class NavigationSystem {
    constructor() {
        this.apiClient = new MOSDACAPIClient();
        this.currentGuide = null;
        this.guideHistory = [];
        this.navigationData = null;
        this.isGuideActive = false;
        this.currentStep = 0;
        this.totalSteps = 0;
        
        // DOM elements
        this.navigationModal = null;
        this.guideContainer = null;
        this.stepIndicator = null;
        this.progressBar = null;
        
        // Navigation categories
        this.categories = {
            'data-access': 'Data Access & Download',
            'registration': 'User Registration',
            'search': 'Search & Discovery',
            'tools': 'Tools & Services',
            'support': 'Help & Support',
            'account': 'Account Management'
        };
        
        // Quick navigation items
        this.quickNavItems = [
            {
                id: 'satellite-data',
                title: 'Satellite Data',
                description: 'Access satellite imagery and data products',
                category: 'data-access',
                icon: 'fas fa-satellite',
                url: 'https://www.mosdac.gov.in/data/data.do',
                steps: [
                    'Visit the Data section',
                    'Select your satellite/sensor',
                    'Choose date range',
                    'Select area of interest',
                    'Download data'
                ]
            },
            {
                id: 'weather-data',
                title: 'Weather Data',
                description: 'Get meteorological data and forecasts',
                category: 'data-access',
                icon: 'fas fa-cloud-sun',
                url: 'https://www.mosdac.gov.in/data/weather.do',
                steps: [
                    'Go to Weather section',
                    'Select data type',
                    'Choose location',
                    'Set time period',
                    'Download or view data'
                ]
            },
            {
                id: 'ocean-data',
                title: 'Ocean Data',
                description: 'Access oceanographic data and products',
                category: 'data-access',
                icon: 'fas fa-water',
                url: 'https://www.mosdac.gov.in/data/ocean.do',
                steps: [
                    'Navigate to Ocean section',
                    'Select parameter type',
                    'Choose geographic area',
                    'Set temporal range',
                    'Access data products'
                ]
            },
            {
                id: 'user-registration',
                title: 'New User Registration',
                description: 'Create account for data access',
                category: 'registration',
                icon: 'fas fa-user-plus',
                url: 'https://www.mosdac.gov.in/register.do',
                steps: [
                    'Click on Register/Sign Up',
                    'Fill personal details',
                    'Provide organization info',
                    'Verify email address',
                    'Complete registration'
                ]
            },
            {
                id: 'data-search',
                title: 'Search Data Products',
                description: 'Find specific datasets and products',
                category: 'search',
                icon: 'fas fa-search',
                url: 'https://www.mosdac.gov.in/search.do',
                steps: [
                    'Use the search function',
                    'Enter keywords or filters',
                    'Browse search results',
                    'Select desired product',
                    'Access or download'
                ]
            },
            {
                id: 'visualization-tools',
                title: 'Visualization Tools',
                description: 'Use online tools for data visualization',
                category: 'tools',
                icon: 'fas fa-chart-line',
                url: 'https://www.mosdac.gov.in/tools/visualization.do',
                steps: [
                    'Go to Tools section',
                    'Select visualization tool',
                    'Load your data',
                    'Configure display options',
                    'Generate visualizations'
                ]
            }
        ];
        
        this.init();
    }

    init() {
        this.initializeElements();
        this.setupEventListeners();
        this.loadNavigationData();
        this.renderQuickNavigation();
    }

    initializeElements() {
        this.navigationModal = document.getElementById('navigationModal');
        this.guideContainer = document.getElementById('navigationGuide');
        this.stepIndicator = document.getElementById('stepIndicator');
        this.progressBar = document.getElementById('navigationProgress');
        
        if (!this.navigationModal) {
            console.error('Navigation modal not found');
            return;
        }
    }

    setupEventListeners() {
        // Navigation modal controls
        document.getElementById('openNavigation')?.addEventListener('click', () => {
            this.openNavigationModal();
        });

        document.getElementById('closeNavigation')?.addEventListener('click', () => {
            this.closeNavigationModal();
        });

        // Guide controls
        document.getElementById('startGuide')?.addEventListener('click', () => {
            this.startSelectedGuide();
        });

        document.getElementById('nextStep')?.addEventListener('click', () => {
            this.nextStep();
        });

        document.getElementById('prevStep')?.addEventListener('click', () => {
            this.previousStep();
        });

        document.getElementById('finishGuide')?.addEventListener('click', () => {
            this.finishGuide();
        });

        document.getElementById('cancelGuide')?.addEventListener('click', () => {
            this.cancelGuide();
        });

        // Quick navigation items
        document.querySelectorAll('.quick-nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const navId = item.dataset.navId;
                this.startQuickNavigation(navId);
            });
        });

        // Category filters
        document.querySelectorAll('.nav-category-filter').forEach(filter => {
            filter.addEventListener('click', () => {
                const category = filter.dataset.category;
                this.filterByCategory(category);
            });
        });

        // Search functionality
        const searchInput = document.getElementById('navSearchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchNavigation(e.target.value);
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (this.isGuideActive) {
                this.handleGuideKeyboard(e);
            }
        });
    }

    async loadNavigationData() {
        try {
            const response = await this.apiClient.getNavigationData();
            if (response.success) {
                this.navigationData = response.data;
                this.updateNavigationUI();
            }
        } catch (error) {
            console.error('Failed to load navigation data:', error);
            // Use fallback data
            this.navigationData = this.getFallbackNavigationData();
        }
    }

    openNavigationModal() {
        if (this.navigationModal) {
            this.navigationModal.classList.add('show');
            document.body.classList.add('modal-open');
            
            // Focus search input
            const searchInput = document.getElementById('navSearchInput');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 300);
            }
            
            this.trackEvent('navigation_modal_opened');
        }
    }

    closeNavigationModal() {
        if (this.navigationModal) {
            this.navigationModal.classList.remove('show');
            document.body.classList.remove('modal-open');
            
            // Cancel active guide if modal is closed
            if (this.isGuideActive) {
                this.cancelGuide();
            }
            
            this.trackEvent('navigation_modal_closed');
        }
    }

    renderQuickNavigation() {
        const container = document.getElementById('quickNavContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Group by category
        const grouped = this.quickNavItems.reduce((acc, item) => {
            if (!acc[item.category]) {
                acc[item.category] = [];
            }
            acc[item.category].push(item);
            return acc;
        }, {});
        
        // Render each category
        Object.entries(grouped).forEach(([category, items]) => {
            const categorySection = document.createElement('div');
            categorySection.className = 'nav-category-section';
            
            const categoryTitle = document.createElement('h3');
            categoryTitle.className = 'nav-category-title';
            categoryTitle.textContent = this.categories[category] || category;
            
            const itemsContainer = document.createElement('div');
            itemsContainer.className = 'nav-items-container';
            
            items.forEach(item => {
                const itemElement = this.createNavItem(item);
                itemsContainer.appendChild(itemElement);
            });
            
            categorySection.appendChild(categoryTitle);
            categorySection.appendChild(itemsContainer);
            container.appendChild(categorySection);
        });
    }

    createNavItem(item) {
        const element = document.createElement('div');
        element.className = 'quick-nav-item';
        element.dataset.navId = item.id;
        element.dataset.category = item.category;
        
        element.innerHTML = `
            <div class="nav-item-icon">
                <i class="${item.icon}"></i>
            </div>
            <div class="nav-item-content">
                <h4 class="nav-item-title">${item.title}</h4>
                <p class="nav-item-description">${item.description}</p>
                <div class="nav-item-steps">
                    ${item.steps.length} steps
                </div>
            </div>
            <div class="nav-item-actions">
                <button class="nav-item-btn start-guide-btn" data-nav-id="${item.id}">
                    <i class="fas fa-play"></i>
                    Start Guide
                </button>
                <button class="nav-item-btn direct-link-btn" data-url="${item.url}">
                    <i class="fas fa-external-link-alt"></i>
                    Go Direct
                </button>
            </div>
        `;
        
        // Add event listeners
        const startBtn = element.querySelector('.start-guide-btn');
        const directBtn = element.querySelector('.direct-link-btn');
        
        startBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.startQuickNavigation(item.id);
        });
        
        directBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            this.openDirectLink(item.url);
        });
        
        return element;
    }

    startQuickNavigation(navId) {
        const navItem = this.quickNavItems.find(item => item.id === navId);
        if (!navItem) return;
        
        this.currentGuide = navItem;
        this.currentStep = 0;
        this.totalSteps = navItem.steps.length;
        this.isGuideActive = true;
        
        this.renderGuide();
        this.updateStepIndicator();
        this.showGuideContainer();
        
        this.trackEvent('navigation_guide_started', { navId, title: navItem.title });
    }

    async startSelectedGuide() {
        const selectedNav = document.querySelector('.quick-nav-item.selected');
        if (selectedNav) {
            const navId = selectedNav.dataset.navId;
            this.startQuickNavigation(navId);
        }
    }

    renderGuide() {
        if (!this.currentGuide || !this.guideContainer) return;
        
        const guide = this.currentGuide;
        const currentStepData = guide.steps[this.currentStep];
        
        this.guideContainer.innerHTML = `
            <div class="guide-header">
                <div class="guide-title">
                    <i class="${guide.icon}"></i>
                    <h3>${guide.title}</h3>
                </div>
                <div class="guide-progress">
                    <span>Step ${this.currentStep + 1} of ${this.totalSteps}</span>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${((this.currentStep + 1) / this.totalSteps) * 100}%"></div>
                    </div>
                </div>
            </div>
            
            <div class="guide-content">
                <div class="current-step">
                    <div class="step-number">${this.currentStep + 1}</div>
                    <div class="step-content">
                        <h4>Current Step</h4>
                        <p>${currentStepData}</p>
                    </div>
                </div>
                
                ${this.renderStepDetails()}
                
                <div class="guide-actions">
                    <button class="guide-btn secondary" id="prevStepBtn" ${this.currentStep === 0 ? 'disabled' : ''}>
                        <i class="fas fa-chevron-left"></i>
                        Previous
                    </button>
                    
                    ${this.currentStep < this.totalSteps - 1 ? `
                        <button class="guide-btn primary" id="nextStepBtn">
                            Next
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    ` : `
                        <button class="guide-btn success" id="finishGuideBtn">
                            <i class="fas fa-check"></i>
                            Finish
                        </button>
                    `}
                    
                    <button class="guide-btn tertiary" id="cancelGuideBtn">
                        <i class="fas fa-times"></i>
                        Cancel
                    </button>
                </div>
            </div>
        `;
        
        // Reattach event listeners
        this.attachGuideEventListeners();
    }

    renderStepDetails() {
        if (!this.currentGuide) return '';
        
        const guide = this.currentGuide;
        let details = '';
        
        // Show helpful tips based on current step
        switch (this.currentStep) {
            case 0:
                details = `
                    <div class="step-details">
                        <div class="step-tip">
                            <i class="fas fa-lightbulb"></i>
                            <strong>Tip:</strong> Make sure you have a MOSDAC account. If not, you can register for free.
                        </div>
                        <div class="step-link">
                            <a href="${guide.url}" target="_blank" class="external-link">
                                <i class="fas fa-external-link-alt"></i>
                                Open ${guide.title} Page
                            </a>
                        </div>
                    </div>
                `;
                break;
            
            case 1:
                details = `
                    <div class="step-details">
                        <div class="step-tip">
                            <i class="fas fa-info-circle"></i>
                            <strong>Note:</strong> Different data types may have different access requirements.
                        </div>
                    </div>
                `;
                break;
            
            default:
                details = `
                    <div class="step-details">
                        <div class="step-help">
                            <i class="fas fa-question-circle"></i>
                            Need help with this step? 
                            <button class="help-btn" onclick="window.mosdacApp.chatSystem.sendMessage('Help with ${guide.title} step ${this.currentStep + 1}')">
                                Ask the AI assistant
                            </button>
                        </div>
                    </div>
                `;
        }
        
        return details;
    }

    attachGuideEventListeners() {
        document.getElementById('prevStepBtn')?.addEventListener('click', () => {
            this.previousStep();
        });
        
        document.getElementById('nextStepBtn')?.addEventListener('click', () => {
            this.nextStep();
        });
        
        document.getElementById('finishGuideBtn')?.addEventListener('click', () => {
            this.finishGuide();
        });
        
        document.getElementById('cancelGuideBtn')?.addEventListener('click', () => {
            this.cancelGuide();
        });
    }

    nextStep() {
        if (this.currentStep < this.totalSteps - 1) {
            this.currentStep++;
            this.renderGuide();
            this.updateStepIndicator();
            
            this.trackEvent('navigation_step_next', {
                navId: this.currentGuide.id,
                step: this.currentStep
            });
        }
    }

    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.renderGuide();
            this.updateStepIndicator();
            
            this.trackEvent('navigation_step_previous', {
                navId: this.currentGuide.id,
                step: this.currentStep
            });
        }
    }

    finishGuide() {
        if (!this.currentGuide) return;
        
        // Add to history
        this.guideHistory.push({
            guide: this.currentGuide,
            completedAt: new Date().toISOString(),
            stepsCompleted: this.totalSteps
        });
        
        // Show completion message
        this.showCompletionMessage();
        
        // Reset state
        this.resetGuideState();
        
        this.trackEvent('navigation_guide_completed', {
            navId: this.currentGuide.id,
            title: this.currentGuide.title,
            stepsCompleted: this.totalSteps
        });
    }

    cancelGuide() {
        if (this.isGuideActive) {
            this.trackEvent('navigation_guide_cancelled', {
                navId: this.currentGuide?.id,
                step: this.currentStep
            });
        }
        
        this.resetGuideState();
        this.hideGuideContainer();
    }

    resetGuideState() {
        this.currentGuide = null;
        this.currentStep = 0;
        this.totalSteps = 0;
        this.isGuideActive = false;
    }

    showGuideContainer() {
        if (this.guideContainer) {
            this.guideContainer.classList.add('active');
        }
    }

    hideGuideContainer() {
        if (this.guideContainer) {
            this.guideContainer.classList.remove('active');
        }
    }

    updateStepIndicator() {
        if (this.stepIndicator) {
            this.stepIndicator.textContent = `Step ${this.currentStep + 1} of ${this.totalSteps}`;
        }
        
        if (this.progressBar) {
            const progress = ((this.currentStep + 1) / this.totalSteps) * 100;
            this.progressBar.style.width = `${progress}%`;
        }
    }

    showCompletionMessage() {
        const message = document.createElement('div');
        message.className = 'guide-completion';
        message.innerHTML = `
            <div class="completion-content">
                <i class="fas fa-check-circle"></i>
                <h3>Guide Completed!</h3>
                <p>You've successfully completed the ${this.currentGuide.title} guide.</p>
                <div class="completion-actions">
                    <button class="guide-btn primary" onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i class="fas fa-thumbs-up"></i>
                        Great!
                    </button>
                    <button class="guide-btn secondary" onclick="window.mosdacApp.feedbackSystem.showFeedbackModal()">
                        <i class="fas fa-star"></i>
                        Rate Guide
                    </button>
                </div>
            </div>
        `;
        
        if (this.guideContainer) {
            this.guideContainer.innerHTML = '';
            this.guideContainer.appendChild(message);
            
            // Auto-hide after delay
            setTimeout(() => {
                this.hideGuideContainer();
            }, 5000);
        }
    }

    openDirectLink(url) {
        window.open(url, '_blank', 'noopener,noreferrer');
        
        this.trackEvent('navigation_direct_link', { url });
        
        // Show helpful message
        if (window.showToast) {
            window.showToast('Opening MOSDAC page in new tab', 'info');
        }
    }

    filterByCategory(category) {
        const items = document.querySelectorAll('.quick-nav-item');
        
        items.forEach(item => {
            if (category === 'all' || item.dataset.category === category) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        // Update active filter
        document.querySelectorAll('.nav-category-filter').forEach(filter => {
            filter.classList.toggle('active', filter.dataset.category === category);
        });
        
        this.trackEvent('navigation_filter', { category });
    }

    searchNavigation(query) {
        const items = document.querySelectorAll('.quick-nav-item');
        const lowerQuery = query.toLowerCase();
        
        items.forEach(item => {
            const title = item.querySelector('.nav-item-title')?.textContent.toLowerCase() || '';
            const description = item.querySelector('.nav-item-description')?.textContent.toLowerCase() || '';
            
            const matches = title.includes(lowerQuery) || description.includes(lowerQuery);
            item.style.display = matches ? 'block' : 'none';
        });
        
        // Show "no results" message if needed
        const visibleItems = Array.from(items).filter(item => item.style.display !== 'none');
        const noResults = document.getElementById('noNavigationResults');
        
        if (noResults) {
            noResults.style.display = visibleItems.length === 0 && query.trim() ? 'block' : 'none';
        }
        
        this.trackEvent('navigation_search', { query, results: visibleItems.length });
    }

    handleGuideKeyboard(event) {
        switch (event.key) {
            case 'ArrowRight':
            case 'Enter':
                if (this.currentStep < this.totalSteps - 1) {
                    event.preventDefault();
                    this.nextStep();
                }
                break;
                
            case 'ArrowLeft':
                if (this.currentStep > 0) {
                    event.preventDefault();
                    this.previousStep();
                }
                break;
                
            case 'Escape':
                event.preventDefault();
                this.cancelGuide();
                break;
        }
    }

    // API integration
    async getNavigationHelp(query) {
        try {
            const response = await this.apiClient.getNavigationHelp(query);
            if (response.success) {
                return response.data;
            }
        } catch (error) {
            console.error('Navigation help error:', error);
        }
        return null;
    }

    async reportNavigationIssue(issue) {
        try {
            const response = await this.apiClient.reportNavigationIssue(issue);
            if (response.success) {
                if (window.showToast) {
                    window.showToast('Thank you for reporting the issue', 'success');
                }
            }
        } catch (error) {
            console.error('Report navigation issue error:', error);
            if (window.showToast) {
                window.showToast('Failed to report issue', 'error');
            }
        }
    }

    // Data management
    getFallbackNavigationData() {
        return {
            categories: this.categories,
            quickNavItems: this.quickNavItems,
            popularGuides: ['satellite-data', 'user-registration', 'weather-data'],
            recentUpdates: []
        };
    }

    updateNavigationUI() {
        if (!this.navigationData) return;
        
        // Update popular guides
        const popularContainer = document.getElementById('popularGuides');
        if (popularContainer && this.navigationData.popularGuides) {
            this.renderPopularGuides(popularContainer);
        }
        
        // Update recent updates
        const updatesContainer = document.getElementById('recentUpdates');
        if (updatesContainer && this.navigationData.recentUpdates) {
            this.renderRecentUpdates(updatesContainer);
        }
    }

    renderPopularGuides(container) {
        container.innerHTML = '';
        
        this.navigationData.popularGuides.forEach(guideId => {
            const guide = this.quickNavItems.find(item => item.id === guideId);
            if (guide) {
                const element = this.createNavItem(guide);
                element.classList.add('popular-guide');
                container.appendChild(element);
            }
        });
    }

    renderRecentUpdates(container) {
        container.innerHTML = '';
        
        this.navigationData.recentUpdates.forEach(update => {
            const element = document.createElement('div');
            element.className = 'update-item';
            element.innerHTML = `
                <div class="update-date">${DateTime.format(update.date)}</div>
                <div class="update-content">
                    <h4>${update.title}</h4>
                    <p>${update.description}</p>
                </div>
            `;
            container.appendChild(element);
        });
    }

    // Public API
    startGuide(guideId) {
        this.startQuickNavigation(guideId);
    }

    getGuideHistory() {
        return [...this.guideHistory];
    }

    exportGuideHistory() {
        const data = {
            history: this.guideHistory,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mosdac-navigation-history-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }

    // Analytics
    trackEvent(event, data = {}) {
        if (window.analytics) {
            window.analytics.track(event, {
                ...data,
                timestamp: Date.now()
            });
        }
    }
}

// Export for global use
window.NavigationSystem = NavigationSystem;
