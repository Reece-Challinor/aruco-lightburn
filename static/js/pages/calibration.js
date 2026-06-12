/**
 * <!--
 * <ai_agent_documentation>
 *   <file_meta>
 *     <name>calibration.js</name>
 *     <version>2.6.0</version>
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
        this.clearFieldErrors();
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
        const requestMeta = document.getElementById('requestMeta');

        if (emptyPreview) {
            emptyPreview.style.display = 'block';
        }
        if (previewImage) {
            previewImage.style.display = 'none';
        }
        if (patternInfo) {
            patternInfo.style.display = 'none';
        }
        if (requestMeta) {
            requestMeta.style.display = 'none';
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
                        first_tag_id: parseInt(document.getElementById('aprilgrid_first_id').value),
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
            this.clearFieldErrors();
            window.notificationManager.showLoading('Generating calibration pattern...');
            const result = await requestConfig.apiCall(requestConfig.payload);

            if (!result || result.success !== true) {
                throw new Error(result?.error?.message || result?.error || 'Unable to generate calibration pattern');
            }

            this.currentPatternData = result;
            this.currentPatternId = result.pattern_id;
            this.renderPreview(result);
            this.setExportEnabled(true);

            if (Array.isArray(result.warnings) && result.warnings.length) {
                result.warnings.forEach(warning => {
                    window.notificationManager.showWarning(warning.message || 'Warning');
                });
            }

            window.notificationManager.showSuccess('Calibration pattern generated');
        } catch (error) {
            this.applyFieldErrors(error.fields);
            window.notificationManager.showError(error.message || 'Failed to generate pattern');
        } finally {
            window.notificationManager.hideLoading();
        }
    }

    renderPreview(result) {
        const emptyPreview = document.getElementById('emptyPreview');
        const previewImage = document.getElementById('previewImage');
        const patternInfo = document.getElementById('patternInfo');
        const requestMeta = document.getElementById('requestMeta');

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
            const esc = window.escapeHtml;
            let infoHtml = `
                <p><strong>Pattern Type:</strong> ${esc(info.pattern_type || this.currentPattern)}</p>
            `;
            if (Array.isArray(result.dimensions_mm) && result.dimensions_mm.length >= 2) {
                infoHtml = `
                    <p><strong>Dimensions:</strong> ${esc(result.dimensions_mm[0].toFixed(1))} x ${esc(result.dimensions_mm[1].toFixed(1))} mm</p>
                ` + infoHtml;
            }

            if (info.total_markers || info.total_tags) {
                infoHtml += `<p><strong>Total Markers:</strong> ${esc(info.total_markers || info.total_tags)}</p>`;
            }
            if (info.dictionary) {
                infoHtml += `<p><strong>Dictionary:</strong> ${esc(info.dictionary)}</p>`;
            }
            if (info.tag_family) {
                infoHtml += `<p><strong>Tag Family:</strong> ${esc(info.tag_family)}</p>`;
            }
            if (info.grid_size) {
                infoHtml += `<p><strong>Grid Size:</strong> ${esc(info.grid_size[0])} x ${esc(info.grid_size[1])}</p>`;
            }

            if (infoContent) {
                infoContent.innerHTML = infoHtml;
            }
            patternInfo.style.display = 'block';
        }

        if (requestMeta) {
            if (result.request_id) {
                requestMeta.textContent = `Request ID: ${result.request_id}`;
                requestMeta.style.display = 'block';
            } else {
                requestMeta.style.display = 'none';
            }
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
            this.clearFieldErrors();
            window.notificationManager.showLoading('Importing calibration data...');
            const result = await window.arucoAPI.importCalibrationPattern(file, {
                save_to_db: true
            });

            if (!result || result.success !== true) {
                throw new Error(result?.error?.message || result?.error || 'Unable to import calibration data');
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

            if (Array.isArray(result.warnings) && result.warnings.length) {
                result.warnings.forEach(warning => {
                    window.notificationManager.showWarning(warning.message || 'Warning');
                });
            }

            window.notificationManager.showSuccess('Calibration data imported');
        } catch (error) {
            this.applyFieldErrors(error.fields);
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

    clearFieldErrors() {
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        document.querySelectorAll('.field-error').forEach(el => el.remove());
    }

    applyFieldErrors(fields) {
        if (!fields || typeof fields !== 'object') return;

        const fieldMapByPattern = {
            charuco: {
                squares_x: 'charuco_squares_x',
                squares_y: 'charuco_squares_y',
                square_size_mm: 'charuco_square_size',
                marker_size_mm: 'charuco_marker_size',
                dictionary: 'charuco_dictionary'
            },
            aruco_board: {
                markers_x: 'board_markers_x',
                markers_y: 'board_markers_y',
                marker_size_mm: 'board_marker_size',
                separation_mm: 'board_separation',
                first_marker_id: 'board_first_id',
                dictionary: 'board_dictionary'
            },
            apriltag: {
                tag_family: 'apriltag_family',
                tag_id: 'apriltag_id',
                tag_size_mm: 'apriltag_size'
            },
            apriltag_grid: {
                grid_size: 'aprilgrid_x',
                grid_x: 'aprilgrid_x',
                grid_y: 'aprilgrid_y',
                first_tag_id: 'aprilgrid_first_id',
                tag_size_mm: 'aprilgrid_size',
                spacing_mm: 'aprilgrid_spacing',
                tag_family: 'aprilgrid_family'
            }
        };

        const fieldMap = fieldMapByPattern[this.currentPattern] || {};
        Object.keys(fields).forEach(field => {
            const targetId = fieldMap[field] || fieldMap[field.replace('_mm', '')];
            if (!targetId) return;
            const input = document.getElementById(targetId);
            if (!input) return;
            input.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback field-error';
            errorDiv.textContent = fields[field];
            input.insertAdjacentElement('afterend', errorDiv);
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.calibrationManager = new CalibrationManager();
});
