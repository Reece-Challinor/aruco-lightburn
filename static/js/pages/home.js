/**
 * Home Page Manager
 * Handles ArUCO marker generation from the main landing page (index.html)
 *
 * Dependencies (loaded by base.html):
 * - window.arucoAPI (js/core/api.js) - API interface
 * - window.showToast (js/core/notifications.js) - Toast notifications
 * - window.appState (js/core/state.js) - State management
 */

class HomeManager {
    constructor() {
        this.currentGenerationData = null;
        this.dictionaries = {};
        this.init();
    }

    async init() {
        this.initializeElements();
        this.attachEventListeners();
        await this.loadDictionaries();
        this.updateMaxMarkerInfo();
    }

    initializeElements() {
        // Quick generation elements
        this.quickDictionary = document.getElementById('quickDictionary');
        this.singleMarkerIdInput = document.getElementById('singleMarkerId');
        this.singleMarkerSizeInput = document.getElementById('singleMarkerSize');
        this.gridRowsInput = document.getElementById('gridRows');
        this.gridColsInput = document.getElementById('gridCols');
        this.gridStartIdInput = document.getElementById('gridStartId');
        this.generateSingleBtn = document.getElementById('generateSingle');
        this.generateGridBtn = document.getElementById('generateGrid');
        this.exportFormatSelect = document.getElementById('exportFormat');
        this.downloadQuickBtn = document.getElementById('downloadQuick');
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
        this.generateAdvancedBtn = document.getElementById('generateAdvancedBtn');
        this.downloadAdvancedBtn = document.getElementById('downloadAdvanced');

        // Preview elements
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.errorState = document.getElementById('errorState');
        this.errorMessage = document.getElementById('errorMessage');
        this.previewContainer = document.getElementById('previewContainer');
        this.svgPreview = document.getElementById('svgPreview');
        this.dimensionsInfo = document.getElementById('dimensionsInfo');
        this.advancedPreview = document.getElementById('advancedPreview');
    }

    attachEventListeners() {
        // Single marker generation
        if (this.generateSingleBtn) {
            this.generateSingleBtn.addEventListener('click', () => this.generateSingle());
        }

        // Grid generation
        if (this.generateGridBtn) {
            this.generateGridBtn.addEventListener('click', () => this.generateGrid());
        }

        // Download buttons
        if (this.downloadQuickBtn) {
            this.downloadQuickBtn.addEventListener('click', () => this.downloadCurrent());
        }

        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => {
                const format = this.exportFormatSelect?.value || 'lbrn2';
                this.downloadWithFormat(format);
            });
        }

        // Advanced generation
        if (this.generateAdvancedBtn) {
            this.generateAdvancedBtn.addEventListener('click', () => this.generateAdvanced());
        }

        if (this.downloadAdvancedBtn) {
            this.downloadAdvancedBtn.addEventListener('click', () => this.downloadCurrent());
        }

        // Border width toggle
        if (this.includeOuterBorderCheck) {
            this.includeOuterBorderCheck.addEventListener('change', () => this.toggleBorderWidth());
        }

        // Dictionary change handler
        if (this.dictionarySelect) {
            this.dictionarySelect.addEventListener('change', () => this.updateMaxMarkerInfo());
        }
    }

    async loadDictionaries() {
        try {
            this.dictionaries = await window.arucoAPI.getDictionaries();
        } catch (error) {
            console.error('Failed to load dictionaries:', error);
            window.showToast?.('Failed to load dictionaries', 'error');
        }
    }

    updateMaxMarkerInfo() {
        const selectedDict = this.dictionarySelect?.value;
        const maxIdElement = document.getElementById('maxMarkerId');

        if (selectedDict && this.dictionaries[selectedDict] && maxIdElement) {
            const maxMarkers = this.dictionaries[selectedDict];
            maxIdElement.textContent = `0-${maxMarkers - 1}`;
        }
    }

    toggleBorderWidth() {
        const isChecked = this.includeOuterBorderCheck?.checked || false;
        if (this.borderWidthContainer) {
            this.borderWidthContainer.style.display = isChecked ? 'block' : 'none';
        }
    }

    async generateSingle() {
        try {
            const markerId = parseInt(this.singleMarkerIdInput?.value) || 0;
            const markerSize = parseFloat(this.singleMarkerSizeInput?.value) || 50;
            const dictionary = this.quickDictionary?.value || '6X6_250';

            const data = {
                dictionary: dictionary,
                rows: 1,
                cols: 1,
                start_id: markerId,
                size_mm: markerSize,
                spacing_mm: 5,
                include_borders: true,
                include_labels: true,
                include_outer_border: false,
                border_width: 2.0
            };

            await this.generatePreview(data);
        } catch (error) {
            console.error('Single generation error:', error);
            this.showError('Failed to generate single marker');
        }
    }

    async generateGrid() {
        try {
            const startId = parseInt(this.gridStartIdInput?.value) || 0;
            const rows = parseInt(this.gridRowsInput?.value) || 2;
            const cols = parseInt(this.gridColsInput?.value) || 2;
            const dictionary = this.quickDictionary?.value || '6X6_250';

            const data = {
                dictionary: dictionary,
                rows: rows,
                cols: cols,
                start_id: startId,
                size_mm: 50,
                spacing_mm: 10,
                include_borders: true,
                include_labels: true,
                include_outer_border: true,
                border_width: 2.0
            };

            await this.generatePreview(data);
        } catch (error) {
            console.error('Grid generation error:', error);
            this.showError('Failed to generate grid');
        }
    }

    async generateAdvanced() {
        try {
            const data = {
                dictionary: this.dictionarySelect?.value,
                rows: parseInt(this.rowsInput?.value) || 1,
                cols: parseInt(this.colsInput?.value) || 1,
                start_id: parseInt(this.startIdInput?.value) || 0,
                size_mm: parseFloat(this.sizeMmInput?.value) || 50,
                spacing_mm: parseFloat(this.spacingMmInput?.value) || 10,
                include_borders: this.includeBordersCheck?.checked ?? true,
                include_labels: this.includeLabelsCheck?.checked ?? true,
                include_outer_border: this.includeOuterBorderCheck?.checked ?? false,
                border_width: parseFloat(this.borderWidthInput?.value) || 2.0
            };

            await this.generatePreview(data);
        } catch (error) {
            console.error('Advanced generation error:', error);
            this.showError('Failed to generate advanced markers');
        }
    }

    async generatePreview(data) {
        try {
            this.showLoading();

            const result = await window.arucoAPI.generateMarkers(data);

            if (result && result.svg) {
                this.currentGenerationData = { ...data, result };
                this.showPreview(result.svg, result.dimensions);
                window.showToast?.('Markers generated successfully', 'success');
            } else {
                throw new Error('Invalid response from server');
            }
        } catch (error) {
            console.error('Preview generation error:', error);
            this.showError(error.message || 'Failed to generate preview');
        }
    }

    showLoading() {
        if (this.loadingState) this.loadingState.style.display = 'flex';
        if (this.emptyState) this.emptyState.style.display = 'none';
        if (this.errorState) this.errorState.style.display = 'none';
        if (this.previewContainer) this.previewContainer.style.display = 'none';
    }

    showPreview(svg, dimensions) {
        if (this.loadingState) this.loadingState.style.display = 'none';
        if (this.emptyState) this.emptyState.style.display = 'none';
        if (this.errorState) this.errorState.style.display = 'none';
        if (this.previewContainer) this.previewContainer.style.display = 'block';

        if (this.svgPreview) {
            this.svgPreview.innerHTML = svg;
        }

        if (this.dimensionsInfo && dimensions) {
            this.dimensionsInfo.innerHTML = `
                <strong>Dimensions:</strong> ${dimensions.width}mm × ${dimensions.height}mm
            `;
        }
    }

    showError(message) {
        if (this.loadingState) this.loadingState.style.display = 'none';
        if (this.emptyState) this.emptyState.style.display = 'none';
        if (this.previewContainer) this.previewContainer.style.display = 'none';
        if (this.errorState) this.errorState.style.display = 'flex';

        if (this.errorMessage) {
            this.errorMessage.textContent = message;
        }

        window.showToast?.(message, 'error');
    }

    async downloadCurrent() {
        try {
            if (!this.currentGenerationData) {
                window.showToast?.('Please generate markers first', 'warning');
                return;
            }

            const format = 'lbrn2';
            await this.downloadWithFormat(format);
        } catch (error) {
            console.error('Download error:', error);
            window.showToast?.('Failed to download markers', 'error');
        }
    }

    async downloadWithFormat(format) {
        try {
            if (!this.currentGenerationData) {
                window.showToast?.('Please generate markers first', 'warning');
                return;
            }

            const data = this.currentGenerationData;
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...data, format: format })
            });

            if (!response.ok) {
                throw new Error(`Download failed: ${response.statusText}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            const extension = this.getFileExtension(format);
            a.download = `aruco_markers_${Date.now()}.${extension}`;

            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            window.showToast?.(`Downloaded as ${format.toUpperCase()}`, 'success');
        } catch (error) {
            console.error('Download with format error:', error);
            window.showToast?.('Failed to download in selected format', 'error');
        }
    }

    getFileExtension(format) {
        const extensions = {
            'lbrn2': 'lbrn2',
            'lbrn': 'lbrn',
            'svg': 'svg',
            'pdf': 'pdf',
            'yaml': 'yaml',
            'json': 'json'
        };
        return extensions[format] || 'lbrn2';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.arucoAPI) {
        window.homeManager = new HomeManager();
    } else {
        console.error('ArUCO API not loaded - home.js requires base.html to load core modules');
    }
});
