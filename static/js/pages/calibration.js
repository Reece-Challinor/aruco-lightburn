/**
 * <!--
 * <ai_agent_documentation>
 *   <file_meta>
 *     <name>calibration.js</name>
 *     <version>2.4.0</version>
 *     <type>frontend_controller</type>
 *     <purpose>Manage calibration pattern selection, generation, and exports</purpose>
 *     <last_updated>2026-02-08</last_updated>
 *     <maintainer>ArUCO Generator Team</maintainer>
 *   </file_meta>
 * </ai_agent_documentation>
 * -->
 *
 * calibration.js
 * Logic for the calibration page (Pattern generation, export)
 */

class CalibrationManager {
    constructor() {
        this.currentPattern = null;
        this.currentPatternData = null;
        this.currentPatternId = null;

        this.init();
    }

    init() {
        this.ensureCoreModules();
        this.bindPatternCards();
        this.bindActionButtons();
    }

    ensureCoreModules() {
        if (!window.notificationManager && typeof NotificationManager !== 'undefined') {
            window.notificationManager = new NotificationManager();
        }
        if (!window.arucoAPI && typeof ArUCOAPI !== 'undefined') {
            window.arucoAPI = new ArUCOAPI();
        }
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
    }

    bindPatternCards() {
        document.querySelectorAll('.pattern-card[data-pattern]').forEach(card => {
            card.addEventListener('click', () => {
                this.selectPattern(card.dataset.pattern, card);
            });

            card.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    this.selectPattern(card.dataset.pattern, card);
                }
            });
        });
    }

    bindActionButtons() {
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const importBtn = document.getElementById('importBtn');
        const importFile = document.getElementById('importFile');
        const bundleBtn = document.getElementById('bundleBtn');

        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generatePattern());
        }

        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadPattern());
        }

        if (importBtn && importFile) {
            importBtn.addEventListener('click', () => importFile.click());
            importFile.addEventListener('change', (event) => {
                const file = event.target.files[0];
                if (file) {
                    this.importPattern(file);
                }
                importFile.value = '';
            });
        }

        if (bundleBtn) {
            bundleBtn.addEventListener('click', () => this.exportBundle());
        }

        document.querySelectorAll('[data-export-format]').forEach(button => {
            button.addEventListener('click', () => {
                const format = button.dataset.exportFormat;
                this.exportData(format);
            });
        });
    }

    selectPattern(type, element) {
        this.currentPattern = type;
        this.currentPatternData = null;
        this.currentPatternId = null;
        this.showPatternConfig(type, element);
        this.clearPreview();
    }

    showPatternConfig(type, element) {
        document.querySelectorAll('.pattern-config').forEach(el => {
            el.style.display = 'none';
        });

        const configId = type.replace('_', '') + 'Config';
        const configEl = document.getElementById(configId);
        if (configEl) {
            configEl.style.display = 'block';
        }

        const titles = {
            charuco: 'ChArUco Board Configuration',
            aruco_board: 'ARUCO Board Configuration',
            apriltag: 'AprilTag Configuration',
            apriltag_grid: 'AprilTag Grid Configuration'
        };
        const title = titles[type] || 'Configuration';
        document.getElementById('configTitle').textContent = title;

        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.disabled = false;
        }

        this.updateSelectionState(element);
    }

    updateSelectionState(selectedElement) {
        document.querySelectorAll('.pattern-card[data-pattern]').forEach(card => {
            card.classList.remove('is-selected');
            card.setAttribute('aria-pressed', 'false');
        });

        if (selectedElement) {
            selectedElement.classList.add('is-selected');
            selectedElement.setAttribute('aria-pressed', 'true');
        }
    }

    clearPreview() {
        const emptyPreview = document.getElementById('emptyPreview');
        const previewImage = document.getElementById('previewImage');
        const patternInfo = document.getElementById('patternInfo');

        if (emptyPreview) {
            emptyPreview.style.display = 'block';
        }
        if (previewImage) {
            previewImage.style.display = 'none';
        }
        if (patternInfo) {
            patternInfo.style.display = 'none';
        }

        this.setExportEnabled(false);
    }

    setExportEnabled(enabled) {
        const downloadBtn = document.getElementById('downloadBtn');
        const yamlBtn = document.getElementById('yamlBtn');
        const jsonBtn = document.getElementById('jsonBtn');
        const rosBtn = document.getElementById('rosBtn');
        const bundleBtn = document.getElementById('bundleBtn');

        if (downloadBtn) {
            downloadBtn.disabled = !enabled;
        }

        const enableExports = enabled && Boolean(this.currentPatternId);
        if (yamlBtn) {
            yamlBtn.disabled = !enableExports;
        }
        if (jsonBtn) {
            jsonBtn.disabled = !enableExports;
        }
        if (rosBtn) {
            rosBtn.disabled = !enableExports;
        }
        if (bundleBtn) {
            bundleBtn.disabled = !enableExports;
        }
    }

    buildRequest(type) {
        switch (type) {
            case 'charuco':
                return {
                    apiCall: (params) => window.arucoAPI.generateChArUco(params),
                    payload: {
                        squares_x: parseInt(document.getElementById('charuco_squares_x').value),
                        squares_y: parseInt(document.getElementById('charuco_squares_y').value),
                        square_size_mm: parseFloat(document.getElementById('charuco_square_size').value),
                        marker_size_mm: parseFloat(document.getElementById('charuco_marker_size').value),
                        dictionary: document.getElementById('charuco_dictionary').value,
                        save_to_db: true
                    }
                };
            case 'aruco_board':
                return {
                    apiCall: (params) => window.arucoAPI.generateArUcoBoard(params),
                    payload: {
                        markers_x: parseInt(document.getElementById('board_markers_x').value),
                        markers_y: parseInt(document.getElementById('board_markers_y').value),
                        marker_size_mm: parseFloat(document.getElementById('board_marker_size').value),
                        separation_mm: parseFloat(document.getElementById('board_separation').value),
                        first_marker_id: parseInt(document.getElementById('board_first_id').value),
                        dictionary: document.getElementById('board_dictionary').value,
                        save_to_db: true
                    }
                };
            case 'apriltag':
                return {
                    apiCall: (params) => window.arucoAPI.generateAprilTag(params),
                    payload: {
                        tag_family: document.getElementById('apriltag_family').value,
                        tag_id: parseInt(document.getElementById('apriltag_id').value),
                        tag_size_mm: parseFloat(document.getElementById('apriltag_size').value),
                        save_to_db: true
                    }
                };
            case 'apriltag_grid':
                return {
                    apiCall: (params) => window.arucoAPI.generateAprilTagGrid(params),
                    payload: {
                        grid_x: parseInt(document.getElementById('aprilgrid_x').value),
                        grid_y: parseInt(document.getElementById('aprilgrid_y').value),
                        tag_size_mm: parseFloat(document.getElementById('aprilgrid_size').value),
                        spacing_mm: parseFloat(document.getElementById('aprilgrid_spacing').value),
                        tag_family: document.getElementById('aprilgrid_family').value,
                        save_to_db: true
                    }
                };
            default:
                return null;
        }
    }

    async generatePattern() {
        if (!this.currentPattern) return;

        const requestConfig = this.buildRequest(this.currentPattern);
        if (!requestConfig) return;

        try {
            window.notificationManager.showLoading('Generating calibration pattern...');
            const result = await requestConfig.apiCall(requestConfig.payload);

            if (!result || !result.success) {
                throw new Error(result?.error || 'Unable to generate calibration pattern');
            }

            this.currentPatternData = result;
            this.currentPatternId = result.pattern_id;
            this.renderPreview(result);
            this.setExportEnabled(true);

            if (result.persisted === false && result.persistence_message) {
                window.notificationManager.showWarning(result.persistence_message);
            }

            window.notificationManager.showSuccess('Calibration pattern generated');
        } catch (error) {
            window.notificationManager.showError(error.message || 'Failed to generate pattern');
        } finally {
            window.notificationManager.hideLoading();
        }
    }

    renderPreview(result) {
        const emptyPreview = document.getElementById('emptyPreview');
        const previewImage = document.getElementById('previewImage');
        const patternInfo = document.getElementById('patternInfo');

        if (emptyPreview) {
            emptyPreview.style.display = 'none';
        }

        if (previewImage) {
            previewImage.src = 'data:image/png;base64,' + result.image_base64;
            previewImage.style.display = 'block';
        }

        const info = result.calibration_data;
        if (info && patternInfo) {
            const infoContent = document.getElementById('infoContent');
            let infoHtml = `
                <p><strong>Dimensions:</strong> ${result.dimensions_mm[0].toFixed(1)} x ${result.dimensions_mm[1].toFixed(1)} mm</p>
                <p><strong>Pattern Type:</strong> ${info.pattern_type || this.currentPattern}</p>
            `;

            if (info.total_markers || info.total_tags) {
                infoHtml += `<p><strong>Total Markers:</strong> ${info.total_markers || info.total_tags}</p>`;
            }
            if (info.dictionary) {
                infoHtml += `<p><strong>Dictionary:</strong> ${info.dictionary}</p>`;
            }
            if (info.tag_family) {
                infoHtml += `<p><strong>Tag Family:</strong> ${info.tag_family}</p>`;
            }
            if (info.grid_size) {
                infoHtml += `<p><strong>Grid Size:</strong> ${info.grid_size[0]} x ${info.grid_size[1]}</p>`;
            }

            if (infoContent) {
                infoContent.innerHTML = infoHtml;
            }
            patternInfo.style.display = 'block';
        }
    }

    downloadPattern() {
        if (!this.currentPatternData || !this.currentPatternData.image_base64) return;

        const base64 = this.currentPatternData.image_base64;
        const binary = atob(base64);
        const array = [];
        for (let i = 0; i < binary.length; i++) {
            array.push(binary.charCodeAt(i));
        }
        const blob = new Blob([new Uint8Array(array)], { type: 'image/png' });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentPattern}_pattern.png`;
        a.click();
        URL.revokeObjectURL(url);
    }

    async importPattern(file) {
        if (!file) return;

        try {
            window.notificationManager.showLoading('Importing calibration data...');
            const result = await window.arucoAPI.importCalibrationPattern(file, {
                save_to_db: true
            });

            if (!result || !result.success) {
                throw new Error(result?.error || 'Unable to import calibration data');
            }

            const patternType = result.calibration_data?.pattern_type;
            if (patternType) {
                this.currentPattern = patternType;
                const card = document.querySelector(`.pattern-card[data-pattern="${patternType}"]`);
                this.showPatternConfig(patternType, card);
                this.populateFieldsFromMetadata(result.calibration_data);
            }

            this.currentPatternData = result;
            this.currentPatternId = result.pattern_id;
            this.renderPreview(result);
            this.setExportEnabled(true);

            if (result.persisted === false && result.persistence_message) {
                window.notificationManager.showWarning(result.persistence_message);
            }

            window.notificationManager.showSuccess('Calibration data imported');
        } catch (error) {
            window.notificationManager.showError(error.message || 'Failed to import calibration data');
        } finally {
            window.notificationManager.hideLoading();
        }
    }

    populateFieldsFromMetadata(metadata) {
        if (!metadata) return;

        const setValue = (id, value) => {
            const el = document.getElementById(id);
            if (el && value !== undefined && value !== null) {
                el.value = value;
            }
        };

        if (metadata.pattern_type === 'charuco') {
            const boardSize = metadata.board_size || [];
            setValue('charuco_squares_x', boardSize[0]);
            setValue('charuco_squares_y', boardSize[1]);
            setValue('charuco_square_size', metadata.square_size_mm);
            setValue('charuco_marker_size', metadata.marker_size_mm);
            setValue('charuco_dictionary', metadata.dictionary);
        }

        if (metadata.pattern_type === 'aruco_board') {
            const gridSize = metadata.grid_size || [];
            setValue('board_markers_x', gridSize[0]);
            setValue('board_markers_y', gridSize[1]);
            setValue('board_marker_size', metadata.marker_size_mm);
            setValue('board_separation', metadata.separation_mm);
            setValue('board_first_id', metadata.first_marker_id);
            setValue('board_dictionary', metadata.dictionary);
        }

        if (metadata.pattern_type === 'apriltag') {
            setValue('apriltag_family', metadata.tag_family);
            setValue('apriltag_id', metadata.tag_id);
            setValue('apriltag_size', metadata.tag_size_mm);
        }

        if (metadata.pattern_type === 'apriltag_grid') {
            const gridSize = metadata.grid_size || [];
            setValue('aprilgrid_x', gridSize[0]);
            setValue('aprilgrid_y', gridSize[1]);
            setValue('aprilgrid_size', metadata.tag_size_mm);
            setValue('aprilgrid_spacing', metadata.spacing_mm);
            setValue('aprilgrid_family', metadata.tag_family);
            setValue('aprilgrid_first_id', metadata.first_tag_id);
        }
    }

    exportData(format) {
        if (!this.currentPatternId) {
            window.notificationManager.showWarning('Generate and save a pattern before exporting data');
            return;
        }

        window.location.href = `/api/calibration/export/${this.currentPatternId}?format=${format}`;
    }

    exportBundle() {
        if (!this.currentPatternId) {
            window.notificationManager.showWarning('Generate and save a pattern before exporting');
            return;
        }

        window.location.href = `/api/calibration/export/${this.currentPatternId}/bundle`;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.calibrationManager = new CalibrationManager();
});
