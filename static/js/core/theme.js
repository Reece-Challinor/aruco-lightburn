/**
 * Theme Manager
 * Provides theme toggling and syncs with StateManager.
 */
document.addEventListener('DOMContentLoaded', () => {
    // The inline script in <head> has already set data-theme and data-bs-theme
    // to avoid FOUC, but we want to ensure StateManager is in sync if present.
    let currentTheme = 'dark';
    if (window.stateManager) {
        currentTheme = window.stateManager.get('theme', 'dark');
    }

    // Provide a global toggle method
    window.toggleTheme = function() {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', next);
        document.documentElement.setAttribute('data-bs-theme', next);

        if (window.stateManager) {
            window.stateManager.set('theme', next);
        }
    };
});
