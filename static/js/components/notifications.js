/**
 * Notifications Component
 * Handles toast notifications, alerts, and user feedback
 */

class NotificationManager {
    constructor() {
        this.toastContainer = null;
        this.init();
    }

    init() {
        // Create or get toast container
        this.toastContainer = document.getElementById('toastContainer');
        if (!this.toastContainer) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toastContainer';
            this.toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(this.toastContainer);
        }
    }

    createToast(message, type = 'info', duration = 5000) {
        const toastId = 'toast_' + Date.now();
        const iconMap = {
            'success': 'bi-check-circle-fill',
            'error': 'bi-x-circle-fill',
            'warning': 'bi-exclamation-triangle-fill',
            'info': 'bi-info-circle-fill'
        };

        const colorMap = {
            'success': 'text-success',
            'error': 'text-danger',
            'warning': 'text-warning',
            'info': 'text-info'
        };

        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="bi ${iconMap[type]} ${colorMap[type]} me-2"></i>
                    <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                    <small>Just now</small>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        this.toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: duration
        });

        // Add animation class
        toastElement.classList.add('fade-in');
        
        // Show toast
        toast.show();

        // Remove from DOM after hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });

        return toast;
    }

    showSuccess(message, duration = 5000) {
        return this.createToast(message, 'success', duration);
    }

    showError(message, duration = 7000) {
        return this.createToast(message, 'error', duration);
    }

    showWarning(message, duration = 6000) {
        return this.createToast(message, 'warning', duration);
    }

    showInfo(message, duration = 5000) {
        return this.createToast(message, 'info', duration);
    }

    // Show a confirmation dialog
    async confirm(title, message, confirmText = 'Confirm', cancelText = 'Cancel') {
        return new Promise((resolve) => {
            const modalId = 'confirmModal_' + Date.now();
            const modalHTML = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>${message}</p>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                                <button type="button" class="btn btn-primary" id="${modalId}_confirm">${confirmText}</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement);
            
            const confirmBtn = document.getElementById(`${modalId}_confirm`);
            confirmBtn.addEventListener('click', () => {
                modal.hide();
                resolve(true);
            });

            modalElement.addEventListener('hidden.bs.modal', () => {
                modalElement.remove();
                resolve(false);
            });

            modal.show();
        });
    }

    // Show a prompt dialog
    async prompt(title, message, defaultValue = '', placeholder = '') {
        return new Promise((resolve) => {
            const modalId = 'promptModal_' + Date.now();
            const modalHTML = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">${title}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>${message}</p>
                                <input type="text" class="form-control" id="${modalId}_input" value="${defaultValue}" placeholder="${placeholder}">
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" id="${modalId}_confirm">OK</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement);
            const input = document.getElementById(`${modalId}_input`);
            
            const confirmBtn = document.getElementById(`${modalId}_confirm`);
            confirmBtn.addEventListener('click', () => {
                modal.hide();
                resolve(input.value);
            });

            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    modal.hide();
                    resolve(input.value);
                }
            });

            modalElement.addEventListener('hidden.bs.modal', () => {
                modalElement.remove();
                resolve(null);
            });

            modalElement.addEventListener('shown.bs.modal', () => {
                input.focus();
                input.select();
            });

            modal.show();
        });
    }

    // Show a loading overlay
    showLoading(message = 'Loading...') {
        const loadingId = 'loadingOverlay';
        
        // Remove existing loading overlay
        const existing = document.getElementById(loadingId);
        if (existing) {
            existing.remove();
        }

        const loadingHTML = `
            <div id="${loadingId}" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" style="background: rgba(0,0,0,0.7); z-index: 9999;">
                <div class="text-center">
                    <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div class="text-white">${message}</div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', loadingHTML);
    }

    hideLoading() {
        const loading = document.getElementById('loadingOverlay');
        if (loading) {
            loading.remove();
        }
    }

    // Show inline feedback
    showInlineFeedback(element, message, type = 'info') {
        const feedbackId = 'feedback_' + Date.now();
        const colorMap = {
            'success': 'text-success',
            'error': 'text-danger',
            'warning': 'text-warning',
            'info': 'text-info'
        };

        const feedbackHTML = `
            <div id="${feedbackId}" class="invalid-feedback d-block ${colorMap[type]} fade-in">
                ${message}
            </div>
        `;

        // Remove existing feedback
        const existing = element.parentElement.querySelector('.invalid-feedback');
        if (existing) {
            existing.remove();
        }

        element.insertAdjacentHTML('afterend', feedbackHTML);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            const feedback = document.getElementById(feedbackId);
            if (feedback) {
                feedback.remove();
            }
        }, 5000);
    }
}

// Initialize notification manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
});