/**
 * State Manager - Simple state management with localStorage persistence
 */

class StateManager {
    constructor() {
        this.state = {};
        this.storageKey = 'aruco_app_state';
        this.loadState();
    }

    loadState() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                this.state = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Failed to load state:', error);
            this.state = {};
        }
    }

    saveState() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.state));
        } catch (error) {
            console.error('Failed to save state:', error);
        }
    }

    get(key, defaultValue = null) {
        const keys = key.split('.');
        let value = this.state;

        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultValue;
            }
        }

        return value;
    }

    set(key, value) {
        const keys = key.split('.');
        let target = this.state;

        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (!(k in target) || typeof target[k] !== 'object') {
                target[k] = {};
            }
            target = target[k];
        }

        target[keys[keys.length - 1]] = value;
        this.saveState();
    }

    remove(key) {
        const keys = key.split('.');
        if (keys.length === 1) {
            delete this.state[key];
        } else {
            const parent = this.get(keys.slice(0, -1).join('.'));
            if (parent && typeof parent === 'object') {
                delete parent[keys[keys.length - 1]];
            }
        }
        this.saveState();
    }

    clear() {
        this.state = {};
        this.saveState();
    }

    getAll() {
        return { ...this.state };
    }
}

// Initialize state manager
window.stateManager = new StateManager();
