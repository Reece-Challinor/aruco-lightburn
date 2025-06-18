// ArUCO Marker Generator - Frontend JavaScript

class ArUCOGenerator {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.loadDictionaries();
    }

    initializeElements() {
        // Form elements
        this.form = document.getElementById('parameterForm');
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

        // Buttons
        this.generateBtn = document.getElementById('generatePreview');
        this.downloadBtn = document.getElementById('downloadLightBurn');

        // Preview elements
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.errorState = document.getElementById('errorState');
        this.errorMessage = document.getElementById('errorMessage');
        this.previewContainer = document.getElementById('previewContainer');
        this.svgPreview = document.getElementById('svgPreview');
        this.previewInfo = document.getElementById('previewInfo');
        this.dimensionsInfo = document.getElementById('dimensionsInfo');

        // Store dictionaries info
        this.dictionaries = {};
    }

    attachEventListeners() {
        // Generate preview button
        this.generateBtn.addEventListener('click', () => this.generatePreview());

        // Download button
        this.downloadBtn.addEventListener('click', () => this.downloadLightBurn());

        // Auto-update on form changes
        const autoUpdateInputs = [
            this.dictionarySelect,
            this.rowsInput,
            this.colsInput,
            this.startIdInput,
            this.includeBordersCheck,
            this.includeLabelsCheck
        ];

        autoUpdateInputs.forEach(input => {
            input.addEventListener('change', () => this.validateForm());
        });

        // Validate on input for number fields
        [this.sizeMmInput, this.spacingMmInput].forEach(input => {
            input.addEventListener('input', () => this.validateForm());
        });

        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.generatePreview();
        });
    }

    async loadDictionaries() {
        try {
            const response = await fetch('/api/dictionaries');
            if (!response.ok) throw new Error('Failed to load dictionaries');
            
            this.dictionaries = await response.json();
            this.validateForm();
        } catch (error) {
            console.error('Error loading dictionaries:', error);
            this.showError('Failed to load ArUCO dictionaries');
        }
    }

    getFormData() {
        return {
            dictionary: this.dictionarySelect.value,
            start_id: parseInt(this.startIdInput.value) || 0,
            rows: parseInt(this.rowsInput.value) || 1,
            cols: parseInt(this.colsInput.value) || 1,
            size_mm: parseFloat(this.sizeMmInput.value) || 20,
            spacing_mm: parseFloat(this.spacingMmInput.value) || 5,
            include_borders: this.includeBordersCheck.checked,
            include_labels: this.includeLabelsCheck.checked
        };
    }

    validateForm() {
        const data = this.getFormData();
        const dictionary = this.dictionaries[data.dictionary];
        
        if (!dictionary) {
            this.generateBtn.disabled = true;
            this.downloadBtn.disabled = true;
            return false;
        }

        // Validate marker count
        const totalMarkers = data.rows * data.cols;
        const maxMarkersExceeded = data.start_id + totalMarkers > dictionary.max_markers;

        // Validate dimensions
        const invalidDimensions = data.size_mm <= 0 || data.spacing_mm < 0 || 
                                  data.rows <= 0 || data.cols <= 0;

        // Update form validation state
        const isValid = !maxMarkersExceeded && !invalidDimensions;
        this.generateBtn.disabled = !isValid;

        // Update validation feedback
        if (maxMarkersExceeded) {
            this.showError(`Too many markers! Dictionary ${data.dictionary} supports maximum ${dictionary.max_markers} markers.`);
        } else if (invalidDimensions) {
            this.showError('Invalid dimensions. Please check your input values.');
        } else {
            this.hideError();
        }

        return isValid;
    }

    async generatePreview() {
        if (!this.validateForm()) return;

        const data = this.getFormData();
        
        try {
            this.showLoading();
            
            const response = await fetch('/api/preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to generate preview');
            }

            this.showPreview(result, data);
            this.downloadBtn.disabled = false;

        } catch (error) {
            console.error('Error generating preview:', error);
            this.showError(error.message || 'Failed to generate preview');
            this.downloadBtn.disabled = true;
        }
    }

    async downloadLightBurn() {
        if (!this.validateForm()) return;

        const data = this.getFormData();
        
        try {
            // Show loading state on download button
            const originalText = this.downloadBtn.innerHTML;
            this.downloadBtn.innerHTML = '<i class="bi bi-spinner-border me-2"></i>Generating...';
            this.downloadBtn.disabled = true;

            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to generate LightBurn file');
            }

            // Get filename from response headers or generate one
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `aruco_${data.dictionary}_${data.rows}x${data.cols}_id${data.start_id}.lbrn2`;
            
            if (contentDisposition) {
                const matches = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (matches && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            // Create blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Show success feedback
            this.showSuccess('LightBurn file downloaded successfully!');

        } catch (error) {
            console.error('Error downloading file:', error);
            this.showError(error.message || 'Failed to download LightBurn file');
        } finally {
            // Restore download button
            this.downloadBtn.innerHTML = '<i class="bi bi-download me-2"></i>Download LightBurn File';
            this.downloadBtn.disabled = false;
        }
    }

    showLoading() {
        this.hideAllStates();
        this.loadingState.style.display = 'block';
    }

    showPreview(result, data) {
        this.hideAllStates();
        
        // Update SVG content
        this.svgPreview.innerHTML = result.svg;
        
        // Update info
        this.previewInfo.textContent = `${result.marker_count} markers generated`;
        this.dimensionsInfo.textContent = 
            `Total dimensions: ${result.total_width.toFixed(1)} × ${result.total_height.toFixed(1)} mm`;
        
        this.previewContainer.style.display = 'block';
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorState.style.display = 'block';
        
        // If preview is showing, don't hide it, just show error above
        if (this.previewContainer.style.display !== 'block') {
            this.hideOtherStates();
        }
    }

    hideError() {
        this.errorState.style.display = 'none';
    }

    showSuccess(message) {
        // Create temporary success alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
        alert.innerHTML = `
            <i class="bi bi-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    hideAllStates() {
        this.loadingState.style.display = 'none';
        this.emptyState.style.display = 'none';
        this.errorState.style.display = 'none';
        this.previewContainer.style.display = 'none';
    }

    hideOtherStates() {
        this.loadingState.style.display = 'none';
        this.emptyState.style.display = 'none';
        this.previewContainer.style.display = 'none';
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ArUCOGenerator();
});
