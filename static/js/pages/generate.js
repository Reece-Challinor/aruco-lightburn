/**
 * <!--
 * <ai_agent_documentation>
 *   <file_meta>
 *     <name>generate.js</name>
 *     <version>2.6.1</version>
 *     <type>frontend_controller</type>
 *     <purpose>Manage marker generation workflows across simple, advanced, and batch tabs</purpose>
 *     <last_updated>2026-02-07</last_updated>
 *     <maintainer>ArUCO Generator Team</maintainer>
 *   </file_meta>
 * </ai_agent_documentation>
 * -->
 *
 * Generate Page JavaScript
 * Handles marker generation with improved navigation and state management
 */

class GenerateManager {
    constructor() {
        this.simpleResult = null;
        this.advancedResult = null;
        this.lastSimpleParams = null;
        this.lastAdvancedParams = null;
        this.dictionaries = {};

        this.init();
    }

    async init() {
        await this.loadDictionaries();
        this.setupEventListeners();
        this.setupAdvancedMode();
        this.restoreTabState();
    }

    async loadDictionaries() {
        try {
            this.dictionaries = await window.arucoAPI.getDictionaries();
        } catch (error) {
            console.error('Failed to load dictionaries:', error);
            const message = error?.message || 'Unable to load dictionaries';
            window.notificationManager.showError(`Failed to load dictionaries. ${message}`);
            this.showError(message);
        }
    }

    setupEventListeners() {
        // Simple tab event listeners
        const generateSingleBtn = document.getElementById('generateSingle');
        const generateGridBtn = document.getElementById('generateGrid');

        if (generateSingleBtn) {
            generateSingleBtn.addEventListener('click', () => this.generateSingle());
        }

        if (generateGridBtn) {
            generateGridBtn.addEventListener('click', () => this.generateGrid());
        }

        // Export options (simple tab)
        document.querySelectorAll('.export-option').forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const format = e.currentTarget.dataset.format;
                this.downloadSimpleWithFormat(format);
            });
        });

        // Export options (advanced tab)
        document.querySelectorAll('.advanced-export-option').forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const format = e.currentTarget.dataset.format;
                this.downloadAdvancedWithFormat(format);
            });
        });

        // Advanced tab
        const generateAdvancedBtn = document.getElementById('generateAdvancedBtn');
        if (generateAdvancedBtn) {
            generateAdvancedBtn.addEventListener('click', () => this.generateAdvanced());
        }

        // Dictionary change handler
        const dictionarySelect = document.getElementById('dictionary');
        if (dictionarySelect) {
            dictionarySelect.addEventListener('change', () => this.updateMaxMarkerInfo());
        }

        // Outer border checkbox
        const outerBorderCheck = document.getElementById('includeOuterBorder');
        if (outerBorderCheck) {
            outerBorderCheck.addEventListener('change', () => this.toggleBorderWidth());
        }

        this.setupBatchListeners();
    }

    setupAdvancedMode() {
        this.updateMaxMarkerInfo();
        this.toggleBorderWidth();
        this.setAdvancedExportEnabled(false);

        // Form state management - disabled for now
        // const advancedForm = document.getElementById('advancedForm');
        // if (advancedForm) {
        //     this.formManager = new FormStateManager('advancedForm');
        // }
    }

    restoreTabState() {
        // Restore last active tab from URL or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        const tab = urlParams.get('tab');

        if (tab) {
            const tabElement = document.querySelector(`[data-bs-target="#${tab}"]`);
            if (tabElement) {
                const bsTab = new bootstrap.Tab(tabElement);
                bsTab.show();
            }
        }
    }

    async generateSingle() {
        const dictionary = document.getElementById('quickDictionary').value;
        const markerId = parseInt(document.getElementById('singleMarkerId').value);
        const size = parseInt(document.getElementById('singleMarkerSize').value);

        const params = {
            dictionary: dictionary,
            rows: 1,
            cols: 1,
            size_mm: size,
            spacing_mm: 0,
            start_id: markerId,
            include_borders: true,
            include_labels: true
        };

        await this.generatePreview(params);
    }

    async generateGrid() {
        const dictionary = document.getElementById('quickDictionary').value;
        const rows = parseInt(document.getElementById('gridRows').value);
        const cols = parseInt(document.getElementById('gridCols').value);
        const startId = parseInt(document.getElementById('gridStartId').value);

        const params = {
            dictionary: dictionary,
            rows: rows,
            cols: cols,
            size_mm: 50,
            spacing_mm: 10,
            start_id: startId,
            include_borders: true,
            include_labels: true
        };

        await this.generatePreview(params);
    }

    async generateAdvanced() {
        const form = document.getElementById('advancedForm');
        const formData = new FormData(form);

        const params = {
            dictionary: formData.get('dictionary'),
            rows: parseInt(formData.get('rows')),
            cols: parseInt(formData.get('cols')),
            size_mm: parseFloat(formData.get('size_mm')),
            spacing_mm: parseFloat(formData.get('spacing_mm')),
            start_id: parseInt(formData.get('marker_id')),
            include_borders: formData.get('include_borders') === 'on',
            include_labels: formData.get('include_labels') === 'on',
            include_outer_border: formData.get('include_outer_border') === 'on',
            border_width: parseFloat(formData.get('border_width') || 2)
        };

        await this.generateAdvancedPreview(params);
    }

    async generatePreview(params) {
        this.showLoading();

        try {
            const result = await window.arucoAPI.generatePreview(params);
            this.simpleResult = result;
            this.lastSimpleParams = params;

            // Store in state manager
            window.stateManager.set('generation.lastParams', params);
            window.stateManager.set('generation.lastResult', result);

            this.showPreview(result);
            window.notificationManager.showSuccess('Markers generated successfully');

            // Enable download button
            document.getElementById('downloadBtn').disabled = false;
        } catch (error) {
            this.showError(error.message);
            window.notificationManager.showError(`Failed to generate markers: ${error.message}`);
        }
    }

    async generateAdvancedPreview(params) {
        const preview = document.getElementById('advancedPreview');
        preview.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';

        try {
            const result = await window.arucoAPI.generateAdvanced(params);
            this.advancedResult = result;
            this.lastAdvancedParams = params;
            window.stateManager.set('generation.advancedParams', params);

            preview.innerHTML = `
                <div class="text-center">
                    <div class="preview-svg">${result.svg}</div>
                    <div class="mt-3">
                        <small class="text-muted">
                            <i class="bi bi-rulers me-1"></i>
                            Dimensions: ${result.dimensions.width}mm × ${result.dimensions.height}mm
                        </small>
                    </div>
                    <div class="mt-3 text-muted small">
                        Use the export menu above to download your advanced layout.
                    </div>
                </div>
            `;

            this.setAdvancedExportEnabled(true);
            window.notificationManager.showSuccess('Advanced markers generated');
        } catch (error) {
            preview.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>${error.message}
                </div>
            `;
            this.setAdvancedExportEnabled(false);
            window.notificationManager.showError(`Advanced generation failed: ${error.message}`);
        }
    }

    showLoading() {
        document.getElementById('loadingState').style.display = 'block';
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('errorState').style.display = 'none';
        document.getElementById('previewContainer').style.display = 'none';
    }

    showPreview(result) {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('errorState').style.display = 'none';
        document.getElementById('previewContainer').style.display = 'block';

        document.getElementById('svgPreview').innerHTML = result.svg;
        document.getElementById('dimensionsInfo').textContent =
            `Dimensions: ${result.dimensions.width}mm × ${result.dimensions.height}mm`;
    }

    showError(message) {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('emptyState').style.display = 'none';
        document.getElementById('errorState').style.display = 'block';
        document.getElementById('previewContainer').style.display = 'none';

        document.getElementById('errorMessage').textContent = message;
    }

    async downloadSimpleWithFormat(format) {
        if (!this.simpleResult) {
            window.notificationManager.showWarning('Please generate markers first');
            return;
        }

        const params = this.lastSimpleParams || window.stateManager.get('generation.lastParams');
        if (!params) return;

        try {
            // Show loading notification
            window.notificationManager.showInfo(`Exporting as ${format.toUpperCase()}...`);

            switch (format) {
                case 'lightburn':
                    await window.arucoAPI.exportLightBurn(params);
                    break;
                case 'pdf':
                    await window.arucoAPI.exportPDF(params);
                    break;
                case 'svg':
                    await window.arucoAPI.exportSVG(params);
                    break;
                case 'yaml':
                    await window.arucoAPI.exportOpenCV(params);
                    break;
                case 'json':
                    await window.arucoAPI.exportROS(params);
                    break;
                case 'dxf':
                    await window.arucoAPI.exportDXF(params);
                    break;
                case 'stl':
                    await window.arucoAPI.exportSTL(params);
                    break;
            }

            window.notificationManager.showSuccess(`Successfully exported as ${format.toUpperCase()}`);
        } catch (error) {
            window.notificationManager.showError(`Export failed: ${error.message}`);
        }
    }

    downloadSVG() {
        // SVG download is handled through the API now
        this.downloadSimpleWithFormat('svg');
    }

    downloadCurrent() {
        // Default to SVG export
        this.downloadAdvancedWithFormat('svg');
    }

    async downloadAdvancedWithFormat(format) {
        if (!this.advancedResult) {
            window.notificationManager.showWarning('Please generate advanced markers first');
            return;
        }

        const params = this.lastAdvancedParams || window.stateManager.get('generation.advancedParams');
        if (!params) return;

        try {
            window.notificationManager.showInfo(`Exporting advanced layout as ${format.toUpperCase()}...`);

            switch (format) {
                case 'lightburn':
                    await window.arucoAPI.exportLightBurn(params);
                    break;
                case 'pdf':
                    await window.arucoAPI.exportPDF(params);
                    break;
                case 'svg':
                    await window.arucoAPI.exportSVG(params);
                    break;
                case 'dxf':
                    await window.arucoAPI.exportDXF(params);
                    break;
                case 'stl':
                    await window.arucoAPI.exportSTL(params);
                    break;
            }

            window.notificationManager.showSuccess(`Advanced export complete: ${format.toUpperCase()}`);
        } catch (error) {
            window.notificationManager.showError(`Advanced export failed: ${error.message}`);
        }
    }

    updateMaxMarkerInfo() {
        const select = document.getElementById('dictionary');
        const maxInfo = document.getElementById('maxMarkerInfo');

        if (select && maxInfo && select.selectedIndex >= 0) {
            const selectedOption = select.options[select.selectedIndex];
            if (!selectedOption) return;
            const maxMarkers = selectedOption.dataset?.max || '1000';
            maxInfo.textContent = maxMarkers;

            // Update marker ID input max
            const markerIdInput = document.getElementById('markerId');
            if (markerIdInput) {
                markerIdInput.max = parseInt(maxMarkers) - 1;
            }
        }
    }

    toggleBorderWidth() {
        const checkbox = document.getElementById('includeOuterBorder');
        const borderGroup = document.getElementById('borderWidthGroup');

        if (checkbox && borderGroup) {
            borderGroup.style.display = checkbox.checked ? 'block' : 'none';
        }
    }

    setAdvancedExportEnabled(enabled) {
        const advancedExportBtn = document.getElementById('advancedExportBtn');
        if (advancedExportBtn) {
            advancedExportBtn.disabled = !enabled;
        }
    }

    setupBatchListeners() {
        const batchBtn = document.getElementById('generateBatchBtn');
        if (batchBtn) {
            batchBtn.addEventListener('click', () => this.generateBatch());
        }

        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const preset = e.currentTarget.dataset.preset;
                this.loadPreset(preset);
            });
        });
    }

    async loadPreset(presetName) {
        try {
            const presets = await window.arucoAPI.getPresets();
            const preset = presets[presetName];

            if (preset) {
                // Apply preset values to batch form
                document.getElementById('batchSets').value = preset.rows || 5;
                document.getElementById('batchMarkersPerSet').value = preset.cols || 10;

                window.notificationManager.showSuccess(`Loaded preset: ${preset.name}`);
            }
        } catch (error) {
            window.notificationManager.showError('Failed to load preset');
        }
    }

    async generateBatch() {
        const sets = parseInt(document.getElementById('batchSets').value);
        const markersPerSet = parseInt(document.getElementById('batchMarkersPerSet').value);
        const startId = parseInt(document.getElementById('batchStartId').value);

        const params = {
            sets: sets,
            markers_per_set: markersPerSet,
            start_id: startId,
            dictionary: '4X4_250',
            size_mm: 50,
            spacing_mm: 10
        };

        try {
            window.notificationManager.showLoading('Generating batch...');
            const result = await window.arucoAPI.generateBatch(params);

            // Display batch results
            const resultsDiv = document.getElementById('batchResults');
            resultsDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6>Batch Generation Complete</h6>
                    <p>Generated ${sets} sets with ${markersPerSet} markers each</p>
                    <p>Total markers: ${sets * markersPerSet}</p>
                    <p>ID range: ${startId} - ${startId + (sets * markersPerSet) - 1}</p>
                    <button class="btn btn-success mt-2">
                        <i class="bi bi-download me-2"></i>Download All
                    </button>
                </div>
            `;

            window.notificationManager.hideLoading();
            window.notificationManager.showSuccess('Batch generated successfully');
        } catch (error) {
            window.notificationManager.hideLoading();
            window.notificationManager.showError('Batch generation failed');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Ensure core modules are loaded
    if (!window.notificationManager && typeof NotificationManager !== 'undefined') {
        window.notificationManager = new NotificationManager();
    }
    if (!window.stateManager && typeof StateManager !== 'undefined') {
        window.stateManager = new StateManager();
    }
    if (!window.arucoAPI && typeof ArUCOAPI !== 'undefined') {
        window.arucoAPI = new ArUCOAPI();
    }

    // Add minimal fallbacks if modules aren't loaded
    if (!window.notificationManager) {
        window.notificationManager = {
            showSuccess: (msg) => console.log('Success:', msg),
            showError: (msg) => console.error('Error:', msg),
            showWarning: (msg) => console.warn('Warning:', msg),
            showInfo: (msg) => console.info('Info:', msg),
            showLoading: (msg) => console.log('Loading:', msg),
            hideLoading: () => { }
        };
    }
    if (!window.stateManager) {
        window.stateManager = {
            get: (key, defaultVal) => defaultVal,
            set: (key, val) => { },
            remove: (key) => { },
            clear: () => { }
        };
    }

    window.generateManager = new GenerateManager();
});
