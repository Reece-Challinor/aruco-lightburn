/**
 * State Management Module
 * Handles application state, localStorage, and session management
 */

class StateManager {
    constructor() {
        this.state = {
            currentDictionary: '4X4_250',
            currentTab: 'configuration',
            recentPatterns: [],
            preferences: {
                theme: 'dark',
                autoPreview: true,
                showTooltips: true,
                defaultExportFormat: 'lightburn'
            },
            generation: {
                lastParams: null,
                lastResult: null
            }
        };
        
        this.listeners = new Map();
        this.init();
    }

    init() {
        this.loadState();
        this.setupAutoSave();
    }

    loadState() {
        // Load state from localStorage
        const savedState = localStorage.getItem('arucoAppState');
        if (savedState) {
            try {
                const parsed = JSON.parse(savedState);
                this.state = { ...this.state, ...parsed };
            } catch (error) {
                console.error('Failed to load saved state:', error);
            }
        }

        // Load recent patterns
        const recentPatterns = localStorage.getItem('recentPatterns');
        if (recentPatterns) {
            try {
                this.state.recentPatterns = JSON.parse(recentPatterns);
            } catch (error) {
                console.error('Failed to load recent patterns:', error);
            }
        }
    }

    saveState() {
        // Save state to localStorage
        try {
            localStorage.setItem('arucoAppState', JSON.stringify(this.state));
            localStorage.setItem('recentPatterns', JSON.stringify(this.state.recentPatterns));
        } catch (error) {
            console.error('Failed to save state:', error);
        }
    }

    setupAutoSave() {
        // Auto-save state every 30 seconds
        setInterval(() => {
            this.saveState();
        }, 30000);

        // Save state before page unload
        window.addEventListener('beforeunload', () => {
            this.saveState();
        });
    }

    // State getters
    get(key) {
        return key.split('.').reduce((obj, k) => obj?.[k], this.state);
    }

    // State setters
    set(key, value) {
        const keys = key.split('.');
        const lastKey = keys.pop();
        const target = keys.reduce((obj, k) => {
            if (!obj[k]) obj[k] = {};
            return obj[k];
        }, this.state);
        
        target[lastKey] = value;
        this.notify(key, value);
        this.saveState();
    }

    // Update multiple values
    update(updates) {
        Object.entries(updates).forEach(([key, value]) => {
            this.set(key, value);
        });
    }

    // Add to recent patterns
    addRecentPattern(pattern) {
        const recent = this.state.recentPatterns;
        
        // Remove if already exists
        const index = recent.findIndex(p => p.id === pattern.id);
        if (index > -1) {
            recent.splice(index, 1);
        }
        
        // Add to beginning
        recent.unshift({
            ...pattern,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 10
        if (recent.length > 10) {
            recent.pop();
        }
        
        this.notify('recentPatterns', recent);
        this.saveState();
    }

    // Clear recent patterns
    clearRecentPatterns() {
        this.state.recentPatterns = [];
        this.notify('recentPatterns', []);
        this.saveState();
    }

    // Subscribe to state changes
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);
        
        // Return unsubscribe function
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                callbacks.delete(callback);
            }
        };
    }

    // Notify listeners of state changes
    notify(key, value) {
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => callback(value));
        }
        
        // Also notify wildcard listeners
        const wildcardCallbacks = this.listeners.get('*');
        if (wildcardCallbacks) {
            wildcardCallbacks.forEach(callback => callback(key, value));
        }
    }

    // Reset state to defaults
    reset() {
        this.state = {
            currentDictionary: '4X4_250',
            currentTab: 'configuration',
            recentPatterns: [],
            preferences: {
                theme: 'dark',
                autoPreview: true,
                showTooltips: true,
                defaultExportFormat: 'lightburn'
            },
            generation: {
                lastParams: null,
                lastResult: null
            }
        };
        this.saveState();
        this.notify('*', this.state);
    }

    // Export state for debugging
    exportState() {
        return JSON.stringify(this.state, null, 2);
    }

    // Import state
    importState(stateJson) {
        try {
            const imported = JSON.parse(stateJson);
            this.state = { ...this.state, ...imported };
            this.saveState();
            this.notify('*', this.state);
            return true;
        } catch (error) {
            console.error('Failed to import state:', error);
            return false;
        }
    }
}

// Form state management helper
class FormStateManager {
    constructor(formId) {
        this.formId = formId;
        this.form = document.getElementById(formId);
        this.storageKey = `formState_${formId}`;
        
        if (this.form) {
            this.init();
        }
    }

    init() {
        // Load saved form state
        this.loadFormState();
        
        // Save form state on change
        this.form.addEventListener('change', () => {
            this.saveFormState();
        });
        
        // Add reset button handler
        const resetBtn = this.form.querySelector('[type="reset"]');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                setTimeout(() => this.clearFormState(), 0);
            });
        }
    }

    saveFormState() {
        const formData = new FormData(this.form);
        const state = {};
        
        for (const [key, value] of formData.entries()) {
            state[key] = value;
        }
        
        localStorage.setItem(this.storageKey, JSON.stringify(state));
    }

    loadFormState() {
        const savedState = localStorage.getItem(this.storageKey);
        if (!savedState) return;
        
        try {
            const state = JSON.parse(savedState);
            
            Object.entries(state).forEach(([key, value]) => {
                const field = this.form.elements[key];
                if (field) {
                    if (field.type === 'checkbox' || field.type === 'radio') {
                        field.checked = value === 'on' || value === 'true';
                    } else {
                        field.value = value;
                    }
                }
            });
        } catch (error) {
            console.error('Failed to load form state:', error);
        }
    }

    clearFormState() {
        localStorage.removeItem(this.storageKey);
    }

    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
}

// Initialize state manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.stateManager = new StateManager();
});