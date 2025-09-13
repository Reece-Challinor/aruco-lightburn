/**
 * Enhanced Frontend Logger with structured logging and batching
 * Integrates with backend structured logging system
 */
class Logger {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.buffer = [];
        this.flushInterval = 5000; // 5 seconds
        this.maxBufferSize = 50;
        this.logLevels = {
            DEBUG: 0,
            INFO: 1,
            WARNING: 2,
            ERROR: 3,
            CRITICAL: 4
        };
        this.currentLevel = this.logLevels.INFO;
        
        // Setup auto-flush
        this.setupAutoFlush();
        
        // Setup global error handlers
        this.setupErrorHandlers();
        
        // Track page performance
        this.trackPerformance();
    }
    
    /**
     * Generate unique session ID
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * Setup automatic log flushing
     */
    setupAutoFlush() {
        setInterval(() => {
            if (this.buffer.length > 0) {
                this.flush();
            }
        }, this.flushInterval);
        
        // Flush on page unload
        window.addEventListener('beforeunload', () => {
            this.flush(true); // Force sync flush
        });
    }
    
    /**
     * Setup global error handlers
     */
    setupErrorHandlers() {
        // Handle JavaScript errors
        window.addEventListener('error', (event) => {
            this.error('JavaScript Error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                stack: event.error?.stack
            });
        });
        
        // Handle promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.error('Unhandled Promise Rejection', {
                reason: event.reason,
                promise: event.promise
            });
        });
    }
    
    /**
     * Track page performance metrics
     */
    trackPerformance() {
        if (window.performance && window.performance.timing) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const timing = window.performance.timing;
                    const metrics = {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart,
                        loadComplete: timing.loadEventEnd - timing.loadEventStart,
                        domInteractive: timing.domInteractive - timing.domLoading,
                        pageLoadTime: timing.loadEventEnd - timing.navigationStart,
                        connectTime: timing.connectEnd - timing.connectStart,
                        renderTime: timing.domComplete - timing.domLoading
                    };
                    
                    this.info('Page Performance Metrics', metrics);
                }, 0);
            });
        }
    }
    
    /**
     * Core logging method
     */
    log(level, message, context = {}) {
        // Check if we should log this level
        if (this.logLevels[level] < this.currentLevel) {
            return;
        }
        
        const entry = {
            timestamp: new Date().toISOString(),
            sessionId: this.sessionId,
            level: level,
            message: message,
            context: {
                ...context,
                url: window.location.href,
                userAgent: navigator.userAgent,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            }
        };
        
        // Console output
        this.consoleOutput(level, message, context);
        
        // Add to buffer
        this.buffer.push(entry);
        
        // Immediate flush for errors
        if (level === 'ERROR' || level === 'CRITICAL' || this.buffer.length >= this.maxBufferSize) {
            this.flush();
        }
    }
    
    /**
     * Console output with styling
     */
    consoleOutput(level, message, context) {
        const styles = {
            DEBUG: 'color: #6c757d',
            INFO: 'color: #17a2b8',
            WARNING: 'color: #ffc107; font-weight: bold',
            ERROR: 'color: #dc3545; font-weight: bold',
            CRITICAL: 'color: #721c24; background: #f8d7da; font-weight: bold'
        };
        
        const prefix = `[${level}] [${this.sessionId.substr(-8)}]`;
        console.log(`%c${prefix} ${message}`, styles[level], context);
    }
    
    /**
     * Flush logs to backend
     */
    async flush(sync = false) {
        if (this.buffer.length === 0) return;
        
        const logs = [...this.buffer];
        this.buffer = [];
        
        const payload = {
            logs: logs,
            sessionId: this.sessionId
        };
        
        try {
            if (sync) {
                // Synchronous request for page unload
                const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
                navigator.sendBeacon('/api/v1/logs/batch', blob);
            } else {
                // Async request for normal operation
                const response = await fetch('/api/v1/logs/batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
            }
        } catch (error) {
            console.error('Failed to send logs:', error);
            // Re-add first few logs to buffer for retry (avoid infinite growth)
            if (this.buffer.length < this.maxBufferSize / 2) {
                this.buffer.unshift(...logs.slice(0, 10));
            }
        }
    }
    
    /**
     * Log API call
     */
    logApiCall(method, endpoint, status, duration, requestData = null, responseData = null) {
        const context = {
            method: method,
            endpoint: endpoint,
            status: status,
            duration_ms: duration,
            request: requestData,
            response: responseData
        };
        
        if (status >= 500) {
            this.error(`API Error: ${method} ${endpoint}`, context);
        } else if (status >= 400) {
            this.warning(`API Client Error: ${method} ${endpoint}`, context);
        } else {
            this.info(`API Call: ${method} ${endpoint}`, context);
        }
    }
    
    /**
     * Log user action
     */
    logUserAction(action, details = {}) {
        this.info(`User Action: ${action}`, {
            action: action,
            ...details,
            timestamp: Date.now()
        });
    }
    
    /**
     * Convenience methods
     */
    debug(message, context = {}) {
        this.log('DEBUG', message, context);
    }
    
    info(message, context = {}) {
        this.log('INFO', message, context);
    }
    
    warning(message, context = {}) {
        this.log('WARNING', message, context);
    }
    
    error(message, context = {}) {
        this.log('ERROR', message, context);
    }
    
    critical(message, context = {}) {
        this.log('CRITICAL', message, context);
    }
    
    /**
     * Set logging level
     */
    setLevel(level) {
        if (this.logLevels[level] !== undefined) {
            this.currentLevel = this.logLevels[level];
            this.info(`Logging level set to ${level}`);
        }
    }
    
    /**
     * Clear logs
     */
    clear() {
        this.buffer = [];
        console.clear();
    }
}

// Create global logger instance
window.logger = new Logger();

// Log initialization
window.logger.info('ArUCO Generator Frontend Logger Initialized', {
    version: '2.0.0',
    features: ['structured-logging', 'batching', 'performance-tracking', 'error-handling']
});