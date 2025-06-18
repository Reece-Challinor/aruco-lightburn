/**
 * ArUCO Generator - Enhanced Frontend with Comprehensive Error Handling
 */

class ArUCOGenerator {
    constructor() {
        this.debugMode = true;
        this.setupErrorLogging();
        this.initializeElements();
        this.attachEventListeners();
        this.loadDictionaries();
        this.log('ArUCO Generator initialized successfully');
    }

    setupErrorLogging() {
        // Global error handler
        window.addEventListener('error', (event) => {
            this.logError('Global Error', event.error);
        });

        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            this.logError('Unhandled Promise Rejection', event.reason);
        });
    }

    logError(context, error) {
        const errorData = {
            timestamp: new Date().toISOString(),
            context: context,
            message: error?.message || error,
            stack: error?.stack,
            url: window.location.href
        };
        console.error(`[ArUCO Error] ${context}:`, errorData);
        
        // Send error to server for logging (non-blocking)
        this.sendErrorToServer(errorData).catch(e => 
            console.warn('Failed to send error to server:', e)
        );
    }

    async sendErrorToServer(errorData) {
        try {
            await fetch('/api/log-error', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(errorData)
            });
        } catch (e) {
            // Silently fail - don't create infinite error loops
        }
    }

    log(message, data = null) {
        if (this.debugMode) {
            console.log(`[ArUCO Debug] ${message}`, data || '');
        }
    }

    initializeElements() {
        this.log('Initializing UI elements');
        
        try {
            // Simple tab elements
            this.singleMarkerIdInput = document.getElementById('singleMarkerId');
            this.gridStartIdInput = document.getElementById('gridStartId');
            this.generateSingleBtn = document.getElementById('generateSingle');
            this.generateGridBtn = document.getElementById('generateGrid');
            this.generateQuickTestBtn = document.getElementById('generateQuickTest');
            this.downloadBtn = document.getElementById('downloadBtn');

            // Advanced tab elements
            this.advancedForm = document.getElementById('advancedForm');
            this.dictionarySelect = document.getElementById('dictionary');
            this.rowsInput = document.getElementById('rows');
            this.colsInput = document.getElementById('cols');
            this.startIdInput = document.getElementById('start_id');
            this.sizeMmInput = document.getElementById('size_mm');
            this.spacingMmInput = document.getElementById('spacing_mm');
            this.includeBordersCheck = document.getElementById('include_borders');
            this.includeLabelsCheck = document.getElementById('include_labels');
            this.includeOuterBorderCheck = document.getElementById('include_outer_border');
            this.borderWidthInput = document.getElementById('border_width');
            this.borderWidthContainer = document.getElementById('borderWidthContainer');
            this.generateAdvancedBtn = document.getElementById('generateAdvanced');
            this.downloadAdvancedBtn = document.getElementById('downloadAdvanced');

            // Simple tab preview elements
            this.loadingState = document.getElementById('loadingState');
            this.emptyState = document.getElementById('emptyState');
            this.errorState = document.getElementById('errorState');
            this.errorMessage = document.getElementById('errorMessage');
            this.previewContainer = document.getElementById('previewContainer');
            this.svgPreview = document.getElementById('svgPreview');
            this.dimensionsInfo = document.getElementById('dimensionsInfo');

            // Advanced tab preview elements
            this.advancedPreview = document.getElementById('advancedPreview');

            // Store current generation data
            this.currentGenerationData = null;
            this.currentAdvancedData = null;
            this.dictionaries = {};

            this.validateCriticalElements();
        } catch (error) {
            this.logError('Element Initialization', error);
        }
    }

    validateCriticalElements() {
        const criticalElements = [
            { name: 'generateAdvancedBtn', element: this.generateAdvancedBtn },
            { name: 'advancedForm', element: this.advancedForm },
            { name: 'dictionarySelect', element: this.dictionarySelect },
            { name: 'advancedPreview', element: this.advancedPreview }
        ];
        
        for (const { name, element } of criticalElements) {
            if (!element) {
                this.logError('Missing Element', `Critical element ${name} not found`);
            }
        }
    }

    attachEventListeners() {
        this.log('Attaching event listeners');
        
        try {
            // Simple tab event listeners
            if (this.generateSingleBtn) {
                this.generateSingleBtn.addEventListener('click', () => {
                    this.log('Single marker button clicked');
                    this.generateSingle();
                });
            }
            
            if (this.generateGridBtn) {
                this.generateGridBtn.addEventListener('click', () => {
                    this.log('Grid button clicked');
                    this.generateGrid();
                });
            }
            
            if (this.generateQuickTestBtn) {
                this.generateQuickTestBtn.addEventListener('click', () => {
                    this.log('Quick test button clicked');
                    this.generateQuickTest();
                });
            }
            
            if (this.downloadBtn) {
                this.downloadBtn.addEventListener('click', () => {
                    this.log('Download button clicked');
                    this.downloadCurrent();
                });
            }

            // Advanced tab event listeners
            if (this.generateAdvancedBtn) {
                this.generateAdvancedBtn.addEventListener('click', () => {
                    this.log('Advanced generate button clicked');
                    this.generateAdvanced();
                });
            }
            
            if (this.downloadAdvancedBtn) {
                this.downloadAdvancedBtn.addEventListener('click', () => {
                    this.log('Advanced download button clicked');
                    this.downloadAdvanced();
                });
            }
            
            if (this.includeOuterBorderCheck) {
                this.includeOuterBorderCheck.addEventListener('change', () => {
                    this.log('Outer border checkbox changed');
                    this.toggleBorderWidth();
                });
            }

            // Enhanced advanced mode listeners
            this.attachAdvancedModeListeners();

            // Initialize border width visibility
            this.toggleBorderWidth();
        } catch (error) {
            this.logError('Event Listener Attachment', error);
        }
    }

    attachAdvancedModeListeners() {
        // Dictionary change listener
        if (this.dictionarySelect) {
            this.dictionarySelect.addEventListener('change', () => {
                this.updateMaxMarkerInfo();
                this.updateMarkerCounts();
            });
        }

        // Grid dimension listeners
        if (this.rowsInput) {
            this.rowsInput.addEventListener('input', () => this.updateMarkerCounts());
        }
        if (this.colsInput) {
            this.colsInput.addEventListener('input', () => this.updateMarkerCounts());
        }
        if (this.startIdInput) {
            this.startIdInput.addEventListener('input', () => this.updateMarkerCounts());
        }

        // Size preset buttons
        document.querySelectorAll('.size-preset').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const size = parseFloat(e.target.dataset.size);
                if (this.sizeMmInput) {
                    this.sizeMmInput.value = size;
                    this.log('Size preset applied', size);
                }
                // Update button states
                document.querySelectorAll('.size-preset').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Real-time validation
        if (this.advancedForm) {
            this.advancedForm.addEventListener('input', () => {
                this.validateAdvancedFormRealTime();
            });
        }
    }

    updateMaxMarkerInfo() {
        try {
            const selectedDict = this.dictionarySelect?.value;
            const maxIdElement = document.getElementById('maxIdInfo');
            
            if (selectedDict && this.dictionaries[selectedDict] && maxIdElement) {
                const maxMarkers = this.dictionaries[selectedDict].max_markers;
                maxIdElement.textContent = `/ ${maxMarkers}`;
                
                // Update input max value
                if (this.startIdInput) {
                    this.startIdInput.max = maxMarkers - 1;
                }
                
                this.log('Max marker info updated', { dict: selectedDict, max: maxMarkers });
            }
        } catch (error) {
            this.logError('Max Marker Info Update', error);
        }
    }

    updateMarkerCounts() {
        try {
            const rows = parseInt(this.rowsInput?.value) || 1;
            const cols = parseInt(this.colsInput?.value) || 1;
            const startId = parseInt(this.startIdInput?.value) || 0;
            
            const totalMarkers = rows * cols;
            const endId = startId + totalMarkers - 1;
            
            const totalMarkersElement = document.getElementById('totalMarkers');
            const idRangeElement = document.getElementById('idRange');
            
            if (totalMarkersElement) {
                totalMarkersElement.textContent = `Total markers: ${totalMarkers}`;
            }
            
            if (idRangeElement) {
                if (totalMarkers === 1) {
                    idRangeElement.textContent = `${startId}`;
                } else {
                    idRangeElement.textContent = `${startId}-${endId}`;
                }
            }
            
            // Validate against dictionary limits
            this.validateMarkerRange(startId, totalMarkers);
            
        } catch (error) {
            this.logError('Marker Count Update', error);
        }
    }

    validateMarkerRange(startId, totalMarkers) {
        try {
            const selectedDict = this.dictionarySelect?.value;
            if (!selectedDict || !this.dictionaries[selectedDict]) return;
            
            const maxMarkers = this.dictionaries[selectedDict].max_markers;
            const endId = startId + totalMarkers - 1;
            
            const isValid = startId >= 0 && endId < maxMarkers;
            
            // Update UI validation state
            const startIdInput = this.startIdInput;
            if (startIdInput) {
                if (isValid) {
                    startIdInput.classList.remove('is-invalid');
                    startIdInput.classList.add('is-valid');
                } else {
                    startIdInput.classList.remove('is-valid');
                    startIdInput.classList.add('is-invalid');
                }
            }
            
            return isValid;
        } catch (error) {
            this.logError('Marker Range Validation', error);
            return false;
        }
    }

    validateAdvancedFormRealTime() {
        try {
            const data = this.getAdvancedFormData();
            const errors = this.getValidationErrors(data);
            
            // Update generate button state
            if (this.generateAdvancedBtn) {
                this.generateAdvancedBtn.disabled = errors.length > 0;
            }
            
            return errors.length === 0;
        } catch (error) {
            this.logError('Real-time Validation', error);
            return false;
        }
    }

    getValidationErrors(data) {
        const errors = [];
        
        try {
            if (!data.dictionary) {
                errors.push('Dictionary selection is required');
            }
            
            if (data.rows < 1 || data.rows > 10) {
                errors.push('Rows must be between 1 and 10');
            }
            
            if (data.cols < 1 || data.cols > 10) {
                errors.push('Columns must be between 1 and 10');
            }
            
            if (data.start_id < 0) {
                errors.push('Starting ID must be 0 or greater');
            }
            
            if (data.size_mm <= 0 || data.size_mm > 500) {
                errors.push('Size must be between 0.1 and 500mm');
            }
            
            if (data.spacing_mm < 0 || data.spacing_mm > 100) {
                errors.push('Spacing must be between 0 and 100mm');
            }
            
            // Validate marker range
            if (data.dictionary && this.dictionaries[data.dictionary]) {
                const maxMarkers = this.dictionaries[data.dictionary].max_markers;
                const totalMarkers = data.rows * data.cols;
                const endId = data.start_id + totalMarkers - 1;
                
                if (endId >= maxMarkers) {
                    errors.push(`Marker range exceeds dictionary limit (${maxMarkers} markers)`);
                }
            }
            
        } catch (error) {
            this.logError('Validation Error Processing', error);
            errors.push('Validation error occurred');
        }
        
        return errors;
    }

    async loadDictionaries() {
        this.log('Loading ArUCO dictionaries');
        
        try {
            const response = await fetch('/api/dictionaries');
            if (response.ok) {
                this.dictionaries = await response.json();
                this.log('Dictionaries loaded successfully', this.dictionaries);
                
                // Initialize advanced mode features after dictionaries are loaded
                this.initializeAdvancedMode();
            } else {
                throw new Error(`Failed to load dictionaries: ${response.status}`);
            }
        } catch (error) {
            this.logError('Dictionary Loading', error);
            this.showError('Failed to load ArUCO dictionaries. Please refresh the page.');
        }
    }

    initializeAdvancedMode() {
        try {
            // Initialize max marker info
            this.updateMaxMarkerInfo();
            
            // Initialize marker counts
            this.updateMarkerCounts();
            
            // Set initial validation state
            this.validateAdvancedFormRealTime();
            
            this.log('Advanced mode initialized');
        } catch (error) {
            this.logError('Advanced Mode Initialization', error);
        }
    }

    // Simple tab methods
    async generateSingle() {
        try {
            const markerId = parseInt(this.singleMarkerIdInput?.value) || 0;
            const data = {
                dictionary: '6X6_250',
                rows: 1,
                cols: 1,
                start_id: markerId,
                size_mm: 50.8, // 2 inches
                spacing_mm: 5,
                include_borders: true,
                include_labels: true,
                include_outer_border: true,
                border_width: 2.0
            };
            
            this.log('Generating single marker', data);
            await this.generatePreview(data, 'single');
        } catch (error) {
            this.logError('Single Generation', error);
            this.showError('Failed to generate single marker');
        }
    }

    async generateGrid() {
        try {
            const startId = parseInt(this.gridStartIdInput?.value) || 0;
            const data = {
                dictionary: '6X6_250',
                rows: 2,
                cols: 1,
                start_id: startId,
                size_mm: 50.8, // 2 inches each
                spacing_mm: 10,
                include_borders: true,
                include_labels: true,
                include_outer_border: true,
                border_width: 2.0
            };
            
            this.log('Generating grid', data);
            await this.generatePreview(data, 'grid');
        } catch (error) {
            this.logError('Grid Generation', error);
            this.showError('Failed to generate grid');
        }
    }

    async generateQuickTest() {
        try {
            this.log('Starting quick test generation');
            this.showLoading();
            
            const response = await fetch('/api/quick-test', { method: 'POST' });
            
            if (response.ok) {
                const result = await response.json();
                this.log('Quick test generated successfully', result);
                this.showPreview(result, { type: 'quick-test' });
                this.currentGenerationData = { type: 'quick-test' };
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Quick test generation failed');
            }
        } catch (error) {
            this.logError('Quick Test Generation', error);
            this.showError(error.message || 'Failed to generate quick test');
        }
    }

    // Advanced tab methods
    async generateAdvanced() {
        try {
            this.log('Starting advanced generation');
            
            const data = this.getAdvancedFormData();
            this.log('Advanced form data collected', data);
            
            if (!this.validateAdvancedForm(data)) {
                return; // Validation error already shown
            }
            
            await this.generateAdvancedPreview(data);
        } catch (error) {
            this.logError('Advanced Generation', error);
            this.showAdvancedError('Failed to generate advanced preview');
        }
    }

    async downloadAdvanced() {
        try {
            this.log('Starting advanced download');
            
            const data = this.getAdvancedFormData();
            
            if (!this.validateAdvancedForm(data)) {
                return;
            }
            
            await this.downloadLightBurn(data);
        } catch (error) {
            this.logError('Advanced Download', error);
            this.showAdvancedError('Failed to download file');
        }
    }

    getAdvancedFormData() {
        try {
            const data = {
                dictionary: this.dictionarySelect?.value || '6X6_250',
                rows: parseInt(this.rowsInput?.value) || 1,
                cols: parseInt(this.colsInput?.value) || 1,
                start_id: parseInt(this.startIdInput?.value) || 0,
                size_mm: parseFloat(this.sizeMmInput?.value) || 20,
                spacing_mm: parseFloat(this.spacingMmInput?.value) || 5,
                include_borders: this.includeBordersCheck?.checked || false,
                include_labels: this.includeLabelsCheck?.checked || false,
                include_outer_border: this.includeOuterBorderCheck?.checked || false,
                border_width: parseFloat(this.borderWidthInput?.value) || 2.0
            };
            
            this.log('Form data extracted', data);
            return data;
        } catch (error) {
            this.logError('Form Data Extraction', error);
            throw new Error('Failed to read form data');
        }
    }

    validateAdvancedForm(data) {
        try {
            const errors = [];
            
            if (!data.dictionary) {
                errors.push('Dictionary selection is required');
            }
            
            if (data.rows < 1 || data.rows > 20) {
                errors.push('Rows must be between 1 and 20');
            }
            
            if (data.cols < 1 || data.cols > 20) {
                errors.push('Columns must be between 1 and 20');
            }
            
            if (data.start_id < 0) {
                errors.push('Starting ID must be 0 or greater');
            }
            
            if (data.size_mm <= 0 || data.size_mm > 500) {
                errors.push('Size must be between 0.1 and 500mm');
            }
            
            if (data.spacing_mm < 0 || data.spacing_mm > 100) {
                errors.push('Spacing must be between 0 and 100mm');
            }
            
            if (errors.length > 0) {
                const errorMessage = 'Please fix the following issues:\n• ' + errors.join('\n• ');
                this.showAdvancedError(errorMessage);
                this.log('Form validation failed', errors);
                return false;
            }
            
            this.log('Form validation passed');
            return true;
        } catch (error) {
            this.logError('Form Validation', error);
            this.showAdvancedError('Form validation error occurred');
            return false;
        }
    }

    toggleBorderWidth() {
        try {
            if (this.includeOuterBorderCheck && this.borderWidthContainer) {
                const shouldShow = this.includeOuterBorderCheck.checked;
                this.borderWidthContainer.style.display = shouldShow ? 'block' : 'none';
                this.log('Border width visibility toggled', shouldShow);
            }
        } catch (error) {
            this.logError('Border Width Toggle', error);
        }
    }

    // Core generation methods
    async generatePreview(data, type) {
        try {
            this.log('Generating preview', { data, type });
            this.showLoading();
            
            const response = await fetch('/api/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                this.log('Preview generated successfully', result);
                this.showPreview(result, data);
                this.currentGenerationData = { data, type };
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Preview generation failed');
            }
        } catch (error) {
            this.logError('Preview Generation', error);
            this.showError(error.message || 'Failed to generate preview');
        }
    }

    async generateAdvancedPreview(data) {
        try {
            this.log('Generating advanced preview', data);
            this.showAdvancedLoading();
            
            const response = await fetch('/api/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                this.log('Advanced preview generated successfully', result);
                this.showAdvancedPreview(result, data);
                this.currentAdvancedData = data;
                
                // Enable download button
                if (this.downloadAdvancedBtn) {
                    this.downloadAdvancedBtn.disabled = false;
                }
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Advanced preview generation failed');
            }
        } catch (error) {
            this.logError('Advanced Preview Generation', error);
            this.showAdvancedError(error.message || 'Failed to generate advanced preview');
        }
    }

    // Download methods
    async downloadCurrent() {
        try {
            if (!this.currentGenerationData) {
                throw new Error('No data available for download');
            }

            this.log('Downloading current generation');
            
            if (this.currentGenerationData.type === 'quick-test') {
                await this.downloadQuickTest();
            } else {
                await this.downloadLightBurn(this.currentGenerationData.data);
            }
        } catch (error) {
            this.logError('Current Download', error);
            this.showError(error.message || 'Download failed');
        }
    }

    async downloadQuickTest() {
        try {
            this.log('Downloading quick test file');
            
            const response = await fetch('/api/quick-test/download', { method: 'POST' });
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadBlob(blob, 'aruco_quick_test.lbrn2');
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Quick test download failed');
            }
        } catch (error) {
            this.logError('Quick Test Download', error);
            this.showError(error.message || 'Quick test download failed');
        }
    }

    async downloadLightBurn(data) {
        try {
            this.log('Downloading LightBurn file', data);
            
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const blob = await response.blob();
                const filename = `aruco_${data.dictionary}_${data.rows}x${data.cols}_id${data.start_id}.lbrn2`;
                this.downloadBlob(blob, filename);
            } else {
                const error = await response.json();
                throw new Error(error.error || 'LightBurn download failed');
            }
        } catch (error) {
            this.logError('LightBurn Download', error);
            this.showError(error.message || 'Download failed');
        }
    }

    downloadBlob(blob, filename) {
        try {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            this.showSuccess(`File "${filename}" downloaded successfully`);
            this.log('File downloaded', filename);
        } catch (error) {
            this.logError('Blob Download', error);
            this.showError('File download failed');
        }
    }

    // UI State Management - Simple Tab
    showLoading() {
        this.hideAllStates();
        if (this.loadingState) {
            this.loadingState.style.display = 'block';
        }
    }

    showPreview(result, data) {
        this.hideAllStates();
        if (this.previewContainer && this.svgPreview) {
            this.previewContainer.style.display = 'block';
            this.svgPreview.innerHTML = result.svg;
            
            if (this.dimensionsInfo && result.dimensions) {
                this.dimensionsInfo.textContent = 
                    `Dimensions: ${result.dimensions.width}mm × ${result.dimensions.height}mm`;
            }

            // Enable download button
            if (this.downloadBtn) {
                this.downloadBtn.disabled = false;
            }
        }
    }

    showError(message) {
        this.hideAllStates();
        if (this.errorState && this.errorMessage) {
            this.errorState.style.display = 'block';
            this.errorMessage.textContent = message;
        }
        this.log('Error displayed', message);
    }

    hideAllStates() {
        if (this.loadingState) this.loadingState.style.display = 'none';
        if (this.emptyState) this.emptyState.style.display = 'none';
        if (this.errorState) this.errorState.style.display = 'none';
        if (this.previewContainer) this.previewContainer.style.display = 'none';
    }

    // UI State Management - Advanced Tab
    showAdvancedLoading() {
        this.hideAdvancedStates();
        if (this.advancedPreview) {
            this.advancedPreview.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div>Generating advanced preview...</div>
                </div>
            `;
        }
    }

    showAdvancedPreview(result, data) {
        this.hideAdvancedStates();
        if (this.advancedPreview) {
            this.advancedPreview.innerHTML = `
                <div class="text-center">
                    <div class="mb-3">
                        ${result.svg}
                    </div>
                    <div class="text-muted">
                        <small>
                            <i class="bi bi-rulers me-1"></i>
                            Dimensions: ${result.dimensions.width}mm × ${result.dimensions.height}mm
                        </small>
                    </div>
                    <div class="text-muted mt-2">
                        <small>
                            <i class="bi bi-grid me-1"></i>
                            ${data.rows}×${data.cols} grid | IDs: ${data.start_id}-${data.start_id + (data.rows * data.cols) - 1}
                        </small>
                    </div>
                </div>
            `;
        }
    }

    showAdvancedError(message) {
        this.hideAdvancedStates();
        if (this.advancedPreview) {
            this.advancedPreview.innerHTML = `
                <div class="text-center py-5 text-danger">
                    <i class="bi bi-exclamation-triangle display-2 mb-3"></i>
                    <h5>Error</h5>
                    <p class="text-muted">${message}</p>
                    <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                        <i class="bi bi-arrow-clockwise me-1"></i>Refresh Page
                    </button>
                </div>
            `;
        }
        this.log('Advanced error displayed', message);
    }

    hideAdvancedStates() {
        // Advanced tab states are managed through innerHTML replacement
    }

    showSuccess(message) {
        try {
            // Create temporary success alert
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
            alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
            alertDiv.innerHTML = `
                <i class="bi bi-check-circle me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alertDiv);

            // Auto-remove after 3 seconds
            setTimeout(() => {
                if (alertDiv.parentElement) {
                    alertDiv.remove();
                }
            }, 3000);
        } catch (error) {
            this.logError('Success Message Display', error);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        new ArUCOGenerator();
    } catch (error) {
        console.error('[ArUCO Fatal] Failed to initialize:', error);
        
        // Show critical error to user
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger position-fixed';
        errorDiv.style.cssText = 'top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999;';
        errorDiv.innerHTML = `
            <h5><i class="bi bi-exclamation-triangle me-2"></i>Application Error</h5>
            <p>Failed to initialize ArUCO Generator. Please refresh the page.</p>
            <button class="btn btn-outline-danger" onclick="location.reload()">Refresh</button>
        `;
        document.body.appendChild(errorDiv);
    }
});