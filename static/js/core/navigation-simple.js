/**
 * Simplified Navigation System for ArUCO Generator
 * Lightweight, maintainable navigation without complexity
 */

class SimpleNavigation {
    constructor() {
        this.currentPath = window.location.pathname;
        this.init();
    }

    init() {
        // Mark active navigation item
        this.markActiveNav();


        // Log navigation
        console.log(`Navigation initialized: ${this.currentPath}`);
    }

    markActiveNav() {
        // Remove all active classes from global nav only
        document.querySelectorAll('.global-nav .nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to current page in global nav
        document.querySelectorAll('.global-nav .nav-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href === this.currentPath) {
                link.classList.add('active');
            }
        });
    }

}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.navigation = new SimpleNavigation();
});
