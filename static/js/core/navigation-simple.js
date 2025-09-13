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
        
        // Setup basic keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Log navigation
        console.log(`Navigation initialized: ${this.currentPath}`);
    }
    
    markActiveNav() {
        // Remove all active classes
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to current page
        document.querySelectorAll('.nav-link').forEach(link => {
            const href = link.getAttribute('href');
            if (href === this.currentPath) {
                link.classList.add('active');
            }
        });
    }
    
    setupKeyboardShortcuts() {
        // Simple keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ignore if typing in input
            if (e.target.matches('input, textarea, select')) {
                return;
            }
            
            // Alt + key shortcuts
            if (e.altKey) {
                switch(e.key.toLowerCase()) {
                    case 'h':
                        e.preventDefault();
                        this.navigate('/');
                        break;
                    case 'g':
                        e.preventDefault();
                        this.navigate('/generate');
                        break;
                    case 'c':
                        e.preventDefault();
                        this.navigate('/calibration');
                        break;
                    case 'v':
                        e.preventDefault();
                        this.navigate('/validation');
                        break;
                    case 'd':
                        e.preventDefault();
                        this.navigate('/documentation');
                        break;
                }
            }
            
            // Help shortcut
            if (e.key === '?' && !e.altKey && !e.ctrlKey) {
                e.preventDefault();
                this.showHelp();
            }
        });
    }
    
    navigate(path) {
        if (this.currentPath !== path) {
            window.location.href = path;
        }
    }
    
    showHelp() {
        const helpText = `
Keyboard Shortcuts:
• Alt+H - Home
• Alt+G - Generate
• Alt+C - Calibration
• Alt+V - Validation
• Alt+D - Documentation
• ? - Show this help
        `;
        alert(helpText.trim());
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.navigation = new SimpleNavigation();
});