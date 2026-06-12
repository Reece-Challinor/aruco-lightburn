/**
 * Notification Manager - Simple toast notifications
 */

/**
 * Escape a value for safe interpolation into HTML.
 * Use for ANY value that originates from an API response or user input
 * before placing it in an innerHTML template.
 */
window.escapeHtml = function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value === null || value === undefined ? '' : String(value);
    return div.innerHTML;
};

class NotificationManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            this.container = document.createElement('div');
            this.container.id = 'notification-container';
            this.container.className = 'notification-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 350px;
            `;
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('notification-container');
        }
    }

    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${window.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        this.container.appendChild(notification);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                notification.remove();
            }, duration);
        }
    }

    showSuccess(message) {
        this.show(message, 'success');
    }

    showError(message) {
        this.show(message, 'danger');
    }

    showWarning(message) {
        this.show(message, 'warning');
    }

    showInfo(message) {
        this.show(message, 'info');
    }

    showLoading(message = 'Loading...') {
        const loadingId = 'loading-notification';

        // Remove any existing loading notification
        const existing = document.getElementById(loadingId);
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.id = loadingId;
        notification.className = 'alert alert-info';
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                ${window.escapeHtml(message)}
            </div>
        `;

        this.container.appendChild(notification);
    }

    hideLoading() {
        const loadingNotification = document.getElementById('loading-notification');
        if (loadingNotification) {
            loadingNotification.remove();
        }
    }
}

// Initialize notification manager
window.notificationManager = new NotificationManager();
