/**
 * Enhanced Navigation Manager for ArUCO Generator
 * Provides advanced navigation features, history tracking, and visual feedback
 */
class EnhancedNavigationManager {
    constructor() {
        this.history = [];
        this.shortcuts = new Map();
        this.activeRoute = null;
        this.maxHistorySize = 50;
        this.transitionDuration = 300;
        
        // Initialize on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        this.setupShortcuts();
        this.trackCurrentRoute();
        this.setupBreadcrumbs();
        this.setupTabPersistence();
        this.markActiveNavItem();
        this.setupNavigationTransitions();
        this.setupMobileMenu();
        
        // Log initialization
        if (window.logger) {
            window.logger.info('NavigationManager initialized', {
                currentPath: window.location.pathname,
                historyLength: this.history.length
            });
        }
    }
    
    /**
     * Setup keyboard shortcuts
     */
    setupShortcuts() {
        // Define shortcuts
        this.shortcuts = new Map([
            ['alt+h', { path: '/', description: 'Go to Home' }],
            ['alt+g', { path: '/generate', description: 'Go to Generate' }],
            ['alt+c', { path: '/calibration', description: 'Go to Calibration' }],
            ['alt+v', { path: '/validation', description: 'Go to Validation' }],
            ['alt+d', { path: '/documentation', description: 'Go to Documentation' }],
            ['alt+q', { action: () => this.focusTab('quick'), description: 'Focus Quick tab' }],
            ['alt+a', { action: () => this.focusTab('advanced'), description: 'Focus Advanced tab' }],
            ['alt+b', { action: () => this.focusTab('batch'), description: 'Focus Batch tab' }],
            ['alt+left', { action: () => this.navigateBack(), description: 'Navigate back' }],
            ['alt+right', { action: () => this.navigateForward(), description: 'Navigate forward' }],
            ['?', { action: () => this.showShortcutsHelp(), description: 'Show keyboard shortcuts' }],
            ['/', { action: () => this.focusSearch(), description: 'Focus search' }],
            ['escape', { action: () => this.closeModals(), description: 'Close modals' }]
        ]);
        
        // Setup keyboard listener
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }
    
    /**
     * Handle keyboard events
     */
    handleKeyboard(event) {
        // Ignore if typing in input/textarea
        if (event.target.matches('input, textarea, select')) {
            if (event.key === 'Escape') {
                event.target.blur();
            }
            return;
        }
        
        // Build shortcut key
        let key = '';
        if (event.altKey) key += 'alt+';
        if (event.ctrlKey) key += 'ctrl+';
        if (event.shiftKey) key += 'shift+';
        key += event.key.toLowerCase();
        
        // Check for matching shortcut
        const shortcut = this.shortcuts.get(key);
        if (shortcut) {
            event.preventDefault();
            
            if (shortcut.path) {
                this.navigateTo(shortcut.path);
            } else if (shortcut.action) {
                shortcut.action();
            }
            
            // Log shortcut usage
            if (window.logger) {
                window.logger.logUserAction('Keyboard shortcut used', {
                    shortcut: key,
                    description: shortcut.description
                });
            }
        }
    }
    
    /**
     * Navigate to a specific path with transition
     */
    navigateTo(path, options = {}) {
        const currentPath = window.location.pathname;
        
        // Skip if same path
        if (currentPath === path && !options.force) {
            return;
        }
        
        // Track navigation
        this.trackNavigation(currentPath);
        
        // Add transition effect
        this.addPageTransition(() => {
            window.location.href = path;
        });
        
        // Log navigation
        if (window.logger) {
            window.logger.logUserAction('Navigation', {
                from: currentPath,
                to: path,
                method: options.method || 'direct'
            });
        }
    }
    
    /**
     * Track navigation history
     */
    trackNavigation(path) {
        const entry = {
            path: path,
            timestamp: Date.now(),
            context: this.captureContext(),
            title: document.title
        };
        
        this.history.push(entry);
        
        // Limit history size
        if (this.history.length > this.maxHistorySize) {
            this.history.shift();
        }
        
        // Save to localStorage
        this.saveHistory();
    }
    
    /**
     * Navigate back in history
     */
    navigateBack() {
        if (this.history.length > 1) {
            const previous = this.history[this.history.length - 2];
            if (previous) {
                this.restoreContext(previous.context);
                this.navigateTo(previous.path, { method: 'back' });
            }
        } else {
            // Fallback to browser back
            window.history.back();
        }
    }
    
    /**
     * Navigate forward
     */
    navigateForward() {
        window.history.forward();
    }
    
    /**
     * Capture current page context
     */
    captureContext() {
        return {
            scrollPosition: window.scrollY,
            activeTab: this.getActiveTab(),
            formData: this.captureFormData()
        };
    }
    
    /**
     * Restore page context
     */
    restoreContext(context) {
        if (!context) return;
        
        // Restore scroll position after navigation
        if (context.scrollPosition) {
            sessionStorage.setItem('restoreScrollPosition', context.scrollPosition);
        }
        
        // Restore active tab
        if (context.activeTab) {
            sessionStorage.setItem('restoreTab', context.activeTab);
        }
        
        // Restore form data
        if (context.formData) {
            sessionStorage.setItem('restoreFormData', JSON.stringify(context.formData));
        }
    }
    
    /**
     * Get current active tab
     */
    getActiveTab() {
        const activeTab = document.querySelector('.nav-tabs .nav-link.active, .nav-pills .nav-link.active');
        return activeTab ? activeTab.getAttribute('data-bs-target') : null;
    }
    
    /**
     * Capture form data
     */
    captureFormData() {
        const forms = document.querySelectorAll('form');
        const data = {};
        
        forms.forEach((form, index) => {
            const formData = new FormData(form);
            data[`form_${index}`] = Object.fromEntries(formData);
        });
        
        return data;
    }
    
    /**
     * Focus specific tab
     */
    focusTab(tabName) {
        const tabElement = document.querySelector(`[data-bs-target*="${tabName}"]`);
        if (tabElement) {
            const tab = new bootstrap.Tab(tabElement);
            tab.show();
        }
    }
    
    /**
     * Setup breadcrumb navigation
     */
    setupBreadcrumbs() {
        const breadcrumbs = document.querySelector('.breadcrumb');
        if (!breadcrumbs) return;
        
        const path = window.location.pathname;
        const segments = path.split('/').filter(s => s);
        
        // Clear existing breadcrumbs (except Home)
        const items = breadcrumbs.querySelectorAll('.breadcrumb-item:not(:first-child)');
        items.forEach(item => item.remove());
        
        // Build breadcrumb path
        let currentPath = '';
        segments.forEach((segment, index) => {
            currentPath += '/' + segment;
            const isLast = index === segments.length - 1;
            
            const item = document.createElement('li');
            item.className = 'breadcrumb-item';
            if (isLast) {
                item.classList.add('active');
                item.setAttribute('aria-current', 'page');
            }
            
            const title = this.formatSegmentTitle(segment);
            
            if (isLast) {
                item.textContent = title;
            } else {
                const link = document.createElement('a');
                link.href = currentPath;
                link.textContent = title;
                item.appendChild(link);
            }
            
            breadcrumbs.appendChild(item);
        });
    }
    
    /**
     * Format URL segment to readable title
     */
    formatSegmentTitle(segment) {
        const titles = {
            'generate': 'Generate',
            'calibration': 'Calibration',
            'validation': 'Validation',
            'documentation': 'Documentation',
            'api': 'API',
            'v1': 'Version 1'
        };
        
        return titles[segment.toLowerCase()] || segment.charAt(0).toUpperCase() + segment.slice(1);
    }
    
    /**
     * Mark active navigation item
     */
    markActiveNavItem() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPath || (currentPath === '/' && href === '/')) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
                
                // Add visual indicator
                if (!link.querySelector('.active-indicator')) {
                    const indicator = document.createElement('span');
                    indicator.className = 'active-indicator';
                    link.appendChild(indicator);
                }
            } else {
                link.classList.remove('active');
                link.removeAttribute('aria-current');
                const indicator = link.querySelector('.active-indicator');
                if (indicator) {
                    indicator.remove();
                }
            }
        });
    }
    
    /**
     * Setup tab persistence
     */
    setupTabPersistence() {
        // Handle URL-based tab navigation
        const urlParams = new URLSearchParams(window.location.search);
        const activeTab = urlParams.get('tab') || sessionStorage.getItem('restoreTab');
        
        if (activeTab) {
            const tabElement = document.querySelector(`[data-bs-target="${activeTab}"]`);
            if (tabElement) {
                const tab = new bootstrap.Tab(tabElement);
                tab.show();
            }
            sessionStorage.removeItem('restoreTab');
        }
        
        // Update URL when tab changes
        document.querySelectorAll('[data-bs-toggle="tab"], [data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetId = e.target.getAttribute('data-bs-target');
                if (targetId) {
                    const url = new URL(window.location);
                    url.searchParams.set('tab', targetId);
                    window.history.replaceState({}, '', url);
                    
                    // Save to localStorage
                    localStorage.setItem('lastActiveTab', targetId);
                    
                    // Log tab change
                    if (window.logger) {
                        window.logger.logUserAction('Tab changed', {
                            tab: targetId,
                            page: window.location.pathname
                        });
                    }
                }
            });
        });
    }
    
    /**
     * Add page transition effect
     */
    addPageTransition(callback) {
        const body = document.body;
        body.classList.add('page-transitioning');
        
        setTimeout(() => {
            callback();
        }, this.transitionDuration / 2);
    }
    
    /**
     * Setup navigation transitions
     */
    setupNavigationTransitions() {
        // Add transition class to body
        document.body.classList.add('navigation-ready');
        
        // Restore scroll position if needed
        const scrollPos = sessionStorage.getItem('restoreScrollPosition');
        if (scrollPos) {
            window.scrollTo(0, parseInt(scrollPos));
            sessionStorage.removeItem('restoreScrollPosition');
        }
    }
    
    /**
     * Track current route
     */
    trackCurrentRoute() {
        this.activeRoute = window.location.pathname;
        this.trackNavigation(this.activeRoute);
    }
    
    /**
     * Show keyboard shortcuts help
     */
    showShortcutsHelp() {
        const modalHtml = `
            <div class="modal fade" id="shortcutsModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="bi bi-keyboard me-2"></i>
                                Keyboard Shortcuts
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="shortcuts-grid">
                                ${Array.from(this.shortcuts.entries()).map(([key, shortcut]) => `
                                    <div class="shortcut-item">
                                        <kbd>${key.replace('+', ' + ').toUpperCase()}</kbd>
                                        <span>${shortcut.description}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if present
        const existing = document.getElementById('shortcutsModal');
        if (existing) {
            existing.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('shortcutsModal'));
        modal.show();
    }
    
    /**
     * Focus search input
     */
    focusSearch() {
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    /**
     * Close all modals
     */
    closeModals() {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modalEl => {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) {
                modal.hide();
            }
        });
    }
    
    /**
     * Setup mobile menu
     */
    setupMobileMenu() {
        const navToggler = document.querySelector('.navbar-toggler');
        const navCollapse = document.querySelector('.navbar-collapse');
        
        if (navToggler && navCollapse) {
            // Enhance mobile menu animation
            navToggler.addEventListener('click', () => {
                navCollapse.classList.toggle('show');
                navToggler.classList.toggle('active');
            });
            
            // Close on outside click
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.navbar')) {
                    navCollapse?.classList.remove('show');
                    navToggler?.classList.remove('active');
                }
            });
            
            // Close on navigation
            navCollapse.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', () => {
                    navCollapse.classList.remove('show');
                    navToggler.classList.remove('active');
                });
            });
        }
    }
    
    /**
     * Save history to localStorage
     */
    saveHistory() {
        try {
            const historyData = JSON.stringify(this.history.slice(-20)); // Save last 20 entries
            localStorage.setItem('navigationHistory', historyData);
        } catch (e) {
            console.error('Failed to save navigation history:', e);
        }
    }
    
    /**
     * Load history from localStorage
     */
    loadHistory() {
        try {
            const historyData = localStorage.getItem('navigationHistory');
            if (historyData) {
                this.history = JSON.parse(historyData);
            }
        } catch (e) {
            console.error('Failed to load navigation history:', e);
        }
    }
}

// Initialize enhanced navigation manager
window.enhancedNavigationManager = new EnhancedNavigationManager();