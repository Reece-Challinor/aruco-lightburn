// @ts-check

class ToastManager {
    constructor() {
        this.container = null;
        this.queue = [];
        this.activeToast = null;
    }

    _initContainer() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container-fixed';
            document.body.appendChild(this.container);
        }
    }

    /**
     * Show a toast message
     * @param {string} message - The message
     * @param {string} [iconClass] - Bootstrap icon class e.g. 'bi-check-circle'
     */
    show(message, iconClass = 'bi-info-circle') {
        this._initContainer();
        
        // Add to queue
        this.queue.push({ message, iconClass });
        
        // If queue > 1, drop oldest (keep only 1 in queue waiting)
        if (this.queue.length > 2) {
            this.queue.shift(); // Remove oldest waiting
        }
        
        this._processQueue();
    }

    _processQueue() {
        if (this.activeToast || this.queue.length === 0) return;
        
        const next = this.queue.shift();
        if (!next) return;
        
        const toastEl = document.createElement('div');
        toastEl.className = 'toast-msg';
        toastEl.setAttribute('role', 'status');
        
        toastEl.innerHTML = `
            <i class="bi ${next.iconClass} fs-5 text-muted"></i>
            <div>${next.message}</div>
        `;
        
        this.container.appendChild(toastEl);
        this.activeToast = toastEl;
        
        setTimeout(() => {
            if (this.activeToast === toastEl) {
                toastEl.classList.add('toast-out');
                setTimeout(() => {
                    toastEl.remove();
                    this.activeToast = null;
                    this._processQueue();
                }, 150); // Match animation duration
            }
        }, 4000);
    }
}

// Singleton instance
const manager = new ToastManager();

/**
 * C-17 Toast
 * 
 * @param {string} message 
 * @param {string} [iconClass] 
 */
export function showToast(message, iconClass) {
    manager.show(message, iconClass);
}

// For unit testing only
export function _resetToastManager() {
    if (manager.container) {
        manager.container.remove();
        manager.container = null;
    }
    manager.queue = [];
    manager.activeToast = null;
}
