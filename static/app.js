/**
 * {
 *   "file_type": "frontend_javascript",
 *   "purpose": "Streamlined frontend for ArUCO generator with golden path UX",
 *   "main_class": "ArUCOGenerator",
 *   "ui_architecture": {
 *     "simple_tab": "One-click generation for common use cases",
 *     "advanced_tab": "Full parameter control and batch operations",
 *     "golden_path": "2x2 grid generation for computer vision localization"
 *   },
 *   "api_endpoints": {
 *     "/api/preview": "Generate SVG preview",
 *     "/api/download": "Download LightBurn file",
 *     "/api/quick-test": "Quick laser test generation",
 *     "/api/dictionaries": "Get available ArUCO dictionaries"
 *   },
 *   "ai_navigation": {
 *     "modify_for": "Adding new UI interactions or API integrations",
 *     "ui_template": "templates/index.html",
 *     "styling": "static/style.css"
 *   }
 * }
 */

// ArUCO Generator - Streamlined Frontend

class ArUCOGenerator {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.loadDictionaries();
        console.log('ArUCO Generator initialized');
    }

    initializeElements() {
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

        // Preview elements
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.errorState = document.getElementById('errorState');
        this.errorMessage = document.getElementById('errorMessage');
        this.previewContainer = document.getElementById('previewContainer');
        this.svgPreview = document.getElementById('svgPreview');
        this.dimensionsInfo = document.getElementById('dimensionsInfo');

        // Store current generation data for downloads
        this.currentGenerationData = null;
        this.dictionaries = {};
    }

    attachEventListeners() {
        // Simple tab event listeners
        if (this.generateSingleBtn) {
            this.generateSingleBtn.addEventListener('click', () => this.generateSingle());
        }
        if (this.generateGridBtn) {
            this.generateGridBtn.addEventListener('click', () => this.generateGrid());
        }
        if (this.generateQuickTestBtn) {
            this.generateQuickTestBtn.addEventListener('click', () => this.generateQuickTest());
        }
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => this.downloadCurrent());
        }

        // Advanced tab event listeners
        if (this.generateAdvancedBtn) {
            this.generateAdvancedBtn.addEventListener('click', () => this.generateAdvanced());
        }
        if (this.downloadAdvancedBtn) {
            this.downloadAdvancedBtn.addEventListener('click', () => this.downloadAdvanced());
        }
        if (this.includeOuterBorderCheck) {
            this.includeOuterBorderCheck.addEventListener('change', () => this.toggleBorderWidth());
        }

        // Initialize border width visibility
        this.toggleBorderWidth();
    }

    async loadDictionaries() {
        try {
            const response = await fetch('/api/dictionaries');
            if (response.ok) {
                this.dictionaries = await response.json();
            }
        } catch (error) {
            console.error('Failed to load dictionaries:', error);
        }
    }

    // Simple tab methods
    async generateSingle() {
        const markerId = parseInt(this.singleMarkerIdInput.value) || 0;
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
        
        await this.generatePreview(data, 'single');
    }

    async generateGrid() {
        const startId = parseInt(this.gridStartIdInput.value) || 0;
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
        
        await this.generatePreview(data, 'grid');
    }

    async generateQuickTest() {
        try {
            this.showLoading();
            const response = await fetch('/api/quick-test', { method: 'POST' });
            
            if (response.ok) {
                const result = await response.json();
                this.showPreview(result, { type: 'quick-test' });
                this.currentGenerationData = { type: 'quick-test' };
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to generate quick test');
            }
        } catch (error) {
            this.showError('Network error occurred');
            console.error('Quick test generation failed:', error);
        }
    }

    // Advanced tab methods
    async generateAdvanced() {
        const data = this.getAdvancedFormData();
        if (this.validateAdvancedForm(data)) {
            await this.generatePreview(data, 'advanced');
        }
    }

    async downloadAdvanced() {
        const data = this.getAdvancedFormData();
        if (this.validateAdvancedForm(data)) {
            await this.downloadLightBurn(data);
        }
    }

    getAdvancedFormData() {
        return {
            dictionary: this.dictionarySelect.value,
            rows: parseInt(this.rowsInput.value),
            cols: parseInt(this.colsInput.value),
            start_id: parseInt(this.startIdInput.value),
            size_mm: parseFloat(this.sizeMmInput.value),
            spacing_mm: parseFloat(this.spacingMmInput.value),
            include_borders: this.includeBordersCheck.checked,
            include_labels: this.includeLabelsCheck.checked,
            include_outer_border: this.includeOuterBorderCheck.checked,
            border_width: parseFloat(this.borderWidthInput.value)
        };
    }

    validateAdvancedForm(data) {
        if (!data.dictionary || data.rows < 1 || data.cols < 1 || data.size_mm <= 0) {
            this.showError('Please fill in all required fields with valid values');
            return false;
        }
        return true;
    }

    toggleBorderWidth() {
        if (this.includeOuterBorderCheck && this.borderWidthContainer) {
            this.borderWidthContainer.style.display = this.includeOuterBorderCheck.checked ? 'block' : 'none';
        }
    }

    // Core generation method
    async generatePreview(data, type) {
        try {
            this.showLoading();
            
            const response = await fetch('/api/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                this.showPreview(result, data);
                this.currentGenerationData = { data, type };
            } else {
                const error = await response.json();
                this.showError(error.error || 'Generation failed');
            }
        } catch (error) {
            this.showError('Network error occurred');
            console.error('Preview generation failed:', error);
        }
    }

    // Download methods
    async downloadCurrent() {
        if (!this.currentGenerationData) {
            this.showError('No data to download');
            return;
        }

        if (this.currentGenerationData.type === 'quick-test') {
            await this.downloadQuickTest();
        } else {
            await this.downloadLightBurn(this.currentGenerationData.data);
        }
    }

    async downloadQuickTest() {
        try {
            const response = await fetch('/api/quick-test/download', { method: 'POST' });
            if (response.ok) {
                const blob = await response.blob();
                this.downloadBlob(blob, 'aruco_quick_test.lbrn2');
            } else {
                const error = await response.json();
                this.showError(error.error || 'Download failed');
            }
        } catch (error) {
            this.showError('Download failed');
            console.error('Quick test download failed:', error);
        }
    }

    async downloadLightBurn(data) {
        try {
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
                this.showError(error.error || 'Download failed');
            }
        } catch (error) {
            this.showError('Download failed');
            console.error('LightBurn download failed:', error);
        }
    }

    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        this.showSuccess('File downloaded successfully');
    }

    // UI State Management
    showLoading() {
        this.hideAllStates();
        if (this.loadingState) this.loadingState.style.display = 'block';
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
            if (this.downloadBtn) this.downloadBtn.disabled = false;
            if (this.downloadAdvancedBtn) this.downloadAdvancedBtn.disabled = false;
        }
    }

    showError(message) {
        this.hideAllStates();
        if (this.errorState && this.errorMessage) {
            this.errorState.style.display = 'block';
            this.errorMessage.textContent = message;
        }
    }

    showSuccess(message) {
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
    }

    hideAllStates() {
        if (this.loadingState) this.loadingState.style.display = 'none';
        if (this.emptyState) this.emptyState.style.display = 'none';
        if (this.errorState) this.errorState.style.display = 'none';
        if (this.previewContainer) this.previewContainer.style.display = 'none';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ArUCOGenerator();
});