/**
 * Navigation Module
 * Handles global navigation, breadcrumbs, and URL management
 */

class NavigationManager {
    constructor() {
        this.currentPage = window.location.pathname;
        this.init();
    }

    init() {
        this.setupMobileMenu();
        this.setupKeyboardShortcuts();
        this.handleTabNavigation();
        this.setupBreadcrumbs();
        this.markActiveNavItem();
    }

    setupMobileMenu() {
        // Handle mobile menu toggle animations
        const navToggler = document.querySelector('.navbar-toggler');
        const navCollapse = document.querySelector('.navbar-collapse');
        
        if (navToggler) {
            navToggler.addEventListener('click', () => {
                navCollapse?.classList.toggle('show');
            });
        }

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.navbar')) {
                navCollapse?.classList.remove('show');
            }
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt + H - Go to Home
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                window.location.href = '/';
            }
            // Alt + G - Go to Generate
            if (e.altKey && e.key === 'g') {
                e.preventDefault();
                window.location.href = '/generate';
            }
            // Alt + C - Go to Calibration
            if (e.altKey && e.key === 'c') {
                e.preventDefault();
                window.location.href = '/calibration';
            }
            // Alt + V - Go to Validation
            if (e.altKey && e.key === 'v') {
                e.preventDefault();
                window.location.href = '/validation';
            }
            // ? - Show help
            if (e.key === '?' && !e.target.matches('input, textarea')) {
                e.preventDefault();
                this.showKeyboardShortcuts();
            }
        });
    }

    showKeyboardShortcuts() {
        const shortcuts = `
            <div class="modal fade" id="shortcutsModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Keyboard Shortcuts</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <table class="table">
                                <tr><td><kbd>Alt</kbd> + <kbd>H</kbd></td><td>Go to Home</td></tr>
                                <tr><td><kbd>Alt</kbd> + <kbd>G</kbd></td><td>Go to Generate</td></tr>
                                <tr><td><kbd>Alt</kbd> + <kbd>C</kbd></td><td>Go to Calibration</td></tr>
                                <tr><td><kbd>Alt</kbd> + <kbd>V</kbd></td><td>Go to Validation</td></tr>
                                <tr><td><kbd>?</kbd></td><td>Show this help</td></tr>
                                <tr><td><kbd>Esc</kbd></td><td>Close dialogs</td></tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('shortcutsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', shortcuts);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('shortcutsModal'));
        modal.show();
    }

    handleTabNavigation() {
        // Handle URL-based tab navigation
        const urlParams = new URLSearchParams(window.location.search);
        const activeTab = urlParams.get('tab');
        
        if (activeTab) {
            const tabElement = document.querySelector(`[data-bs-target="#${activeTab}"]`);
            if (tabElement) {
                const tab = new bootstrap.Tab(tabElement);
                tab.show();
            }
        }

        // Update URL when tab changes
        document.querySelectorAll('[data-bs-toggle="tab"], [data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetId = e.target.getAttribute('data-bs-target')?.substring(1);
                if (targetId) {
                    const url = new URL(window.location);
                    url.searchParams.set('tab', targetId);
                    window.history.replaceState({}, '', url);
                    
                    // Save to localStorage for persistence
                    localStorage.setItem('lastActiveTab', targetId);
                }
            });
        });

        // Restore last active tab from localStorage
        const lastTab = localStorage.getItem('lastActiveTab');
        if (lastTab && !activeTab) {
            const tabElement = document.querySelector(`[data-bs-target="#${lastTab}"]`);
            if (tabElement && window.location.pathname === '/generate') {
                const tab = new bootstrap.Tab(tabElement);
                tab.show();
            }
        }
    }

    setupBreadcrumbs() {
        // Dynamically update breadcrumbs based on current page
        const breadcrumbContainer = document.querySelector('.breadcrumb');
        if (!breadcrumbContainer) return;

        const path = window.location.pathname.split('/').filter(Boolean);
        let currentPath = '';
        
        path.forEach((segment, index) => {
            currentPath += '/' + segment;
            const isLast = index === path.length - 1;
            const title = segment.charAt(0).toUpperCase() + segment.slice(1);
            
            const li = document.createElement('li');
            li.className = 'breadcrumb-item';
            
            if (isLast) {
                li.classList.add('active');
                li.textContent = title;
            } else {
                const a = document.createElement('a');
                a.href = currentPath;
                a.textContent = title;
                li.appendChild(a);
            }
            
            breadcrumbContainer.appendChild(li);
        });
    }

    markActiveNavItem() {
        // Mark current page as active in navigation
        const currentPath = window.location.pathname;
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPath || (currentPath === '/' && href === '/')) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    navigateTo(path, params = {}) {
        // Programmatic navigation with optional parameters
        const url = new URL(path, window.location.origin);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        window.location.href = url.toString();
    }

    addNavigationListener(callback) {
        // Listen for navigation changes
        window.addEventListener('popstate', callback);
    }
}

// Initialize navigation manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.navigationManager = new NavigationManager();
});