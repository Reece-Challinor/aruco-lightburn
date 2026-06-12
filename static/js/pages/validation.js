/**
 * <!--
 * <ai_agent_documentation>
 *   <file_meta>
 *     <name>validation.js</name>
 *     <version>2.4.0</version>
 *     <type>frontend_controller</type>
 *     <purpose>Validation page controller for marker detection and quality reporting</purpose>
 *     <last_updated>2026-02-08</last_updated>
 *     <maintainer>ArUCO Generator Team</maintainer>
 *   </file_meta>
 * </ai_agent_documentation>
 * -->
 *
 * Validation Page JavaScript
 * Handles marker validation, testing, and quality metrics
 */

class ValidationManager {
    constructor() {
        this.uploadZone = document.getElementById('uploadZone');
        this.fileInput = document.getElementById('fileInput');
        this.testResults = document.getElementById('testResults');

        this.init();
    }

    init() {
        this.setupUploadZone();
        this.setupHammingCalculator();
        this.setupTestPatternGenerator();
        this.loadMetrics();
    }

    setupUploadZone() {
        if (!this.uploadZone || !this.fileInput) return;

        // Click to upload
        this.uploadZone.addEventListener('click', () => {
            this.fileInput.click();
        });

        // File selection
        this.fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.processImage(file);
            }
        });

        // Drag and drop
        this.uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadZone.classList.add('drag-over');
        });

        this.uploadZone.addEventListener('dragleave', () => {
            this.uploadZone.classList.remove('drag-over');
        });

        this.uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadZone.classList.remove('drag-over');

            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                this.processImage(file);
            }
        });
    }

    async processImage(file) {
        // Validate file size
        if (file.size > 10 * 1024 * 1024) {
            window.notificationManager.showError('File size must be less than 10MB');
            return;
        }

        try {
            window.notificationManager.showLoading('Processing image...');

            const dictionarySelect = document.getElementById('detectDictionary');
            const expectedInput = document.getElementById('expectedMarkers');
            const dictionary = dictionarySelect ? dictionarySelect.value : '4X4_50';
            let expectedMarkers = null;
            if (expectedInput && expectedInput.value) {
                const parsed = parseInt(expectedInput.value, 10);
                expectedMarkers = Number.isFinite(parsed) ? parsed : null;
            }

            const result = await window.arucoAPI.detectMarkers(file, {
                dictionary: dictionary,
                expected_markers: expectedMarkers
            });

            this.displayDetection(result);
            this.showWarnings(result);

            window.notificationManager.hideLoading();
            window.notificationManager.showSuccess('Image processed successfully');
        } catch (error) {
            window.notificationManager.hideLoading();
            window.notificationManager.showError('Failed to process image: ' + error.message);
        }
    }

    displayDetection(result) {
        const payload = result?.detection || result;
        if (!payload) {
            window.notificationManager.showError('Detection service returned no data');
            return;
        }

        const detectedCount = payload.detected_markers || 0;
        const quality = payload.detection_quality;

        document.getElementById('detectedCount').textContent = detectedCount;
        document.getElementById('detectionQuality').textContent =
            quality !== null && quality !== undefined ? `${quality}%` : '-';

        const details = document.getElementById('detectionDetails');
        details.innerHTML = '';

        if (payload.markers && payload.markers.length) {
            payload.markers.forEach(marker => {
                const confidence = marker.confidence ?? 0;
                const detailCard = document.createElement('div');
                detailCard.className = 'alert alert-secondary';
                detailCard.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <span><strong>Marker ID ${window.escapeHtml(marker.id)}</strong></span>
                        <span class="badge ${confidence >= 90 ? 'bg-success' : 'bg-warning'}">
                            ${confidence}% confidence
                        </span>
                    </div>
                `;
                details.appendChild(detailCard);
            });
        } else {
            const empty = document.createElement('div');
            empty.className = 'alert alert-warning';
            empty.textContent = 'No markers detected in the uploaded image.';
            details.appendChild(empty);
        }

        if (payload.rejected_candidates) {
            const rejected = document.createElement('div');
            rejected.className = 'text-muted small mt-2';
            rejected.textContent = `${payload.rejected_candidates} rejected candidates detected`;
            details.appendChild(rejected);
        }

        this.testResults.style.display = 'block';
        this.updateRequestMeta('detectionRequestMeta', result?.request_id);
    }

    setupHammingCalculator() {
        const btn = document.getElementById('calculateHammingBtn');
        if (btn) {
            btn.addEventListener('click', () => this.calculateHamming());
        }
    }

    async calculateHamming() {
        const dictionary = document.getElementById('hammingDictionary').value;
        const id1 = parseInt(document.getElementById('markerId1').value);
        const id2 = parseInt(document.getElementById('markerId2').value);

        if (id1 === id2) {
            window.notificationManager.showWarning('Please select different marker IDs');
            return;
        }

        try {
            const result = await window.arucoAPI.calculateHammingDistance({
                dictionary: dictionary,
                id1: id1,
                id2: id2
            });

            this.displayHammingResult(result);
            this.showWarnings(result);
        } catch (error) {
            window.notificationManager.showError('Failed to calculate Hamming distance');
        }
    }

    displayHammingResult(result) {
        const resultDiv = document.getElementById('hammingResult');
        const alert = document.getElementById('hammingAlert');
        const value = document.getElementById('hammingValue');
        const safety = document.getElementById('hammingSafety');

        value.textContent = result.hamming_distance;
        safety.textContent = result.safety_level;

        // Update alert class based on safety level
        alert.className = 'alert';
        if (result.safety_level.includes('Safe')) {
            alert.classList.add('alert-success');
        } else if (result.safety_level.includes('Warning')) {
            alert.classList.add('alert-warning');
        } else {
            alert.classList.add('alert-danger');
        }

        resultDiv.style.display = 'block';
        this.updateRequestMeta('hammingRequestMeta', result?.request_id);
    }

    setupTestPatternGenerator() {
        const btn = document.getElementById('generateTestPatternBtn');
        if (btn) {
            btn.addEventListener('click', () => this.generateTestPattern());
        }
    }

    async generateTestPattern() {
        const dictionary = document.getElementById('testDictionary').value;
        const scalesText = document.getElementById('testScales').value;
        const scales = scalesText.split(',').map(s => parseFloat(s.trim()));
        const includeDistortions = document.getElementById('includeDistortions').checked;
        const includeOcclusions = document.getElementById('includeOcclusions').checked;

        try {
            window.notificationManager.showLoading('Generating test pattern...');

            const result = await window.arucoAPI.generateTestPattern({
                dictionary: dictionary,
                scales: scales,
                include_distortions: includeDistortions,
                include_occlusions: includeOcclusions
            });

            this.displayTestPattern(result);
            this.showWarnings(result);

            window.notificationManager.hideLoading();
            window.notificationManager.showSuccess('Test pattern generated');
        } catch (error) {
            window.notificationManager.hideLoading();
            window.notificationManager.showError('Failed to generate test pattern');
        }
    }

    displayTestPattern(result) {
        const preview = document.getElementById('testPatternPreview');

        if (result.image_base64) {
            // Create container with internal button
            preview.innerHTML = `
                <div class="text-center">
                    <img src="data:image/png;base64,${window.escapeHtml(result.image_base64)}"
                         class="img-fluid border rounded"
                         style="max-height: 400px; background: white;">
                    <div class="mt-3">
                        <button class="btn btn-success" id="downloadPatternBtn">
                            <i class="bi bi-download me-2"></i>Download Pattern
                        </button>
                    </div>
                </div>
            `;

            // Store for download
            window.currentTestPattern = result.image_base64;

            // Attach listener to new button
            const downloadBtn = document.getElementById('downloadPatternBtn');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', () => this.downloadTestPattern());
            }
        }
        this.updateRequestMeta('testPatternRequestMeta', result?.request_id);
    }

    async loadMetrics() {
        try {
            const result = await window.arucoAPI.getValidationMetrics();
            this.renderMetrics(result);
            this.showWarnings(result);
        } catch (error) {
            window.notificationManager.showWarning('Unable to load validation metrics');
        }
    }

    renderMetrics(result) {
        const summary = result?.summary;
        const avgDetectionRate = document.getElementById('avgDetectionRate');
        const avgPoseError = document.getElementById('avgPoseError');
        const avgProcessingTime = document.getElementById('avgProcessingTime');
        const recentList = document.getElementById('recentTestsList');

        if (summary) {
            if (avgDetectionRate) {
                const rate = summary.avg_detection_rate;
                avgDetectionRate.textContent = rate !== null && rate !== undefined
                    ? `${(rate * 100).toFixed(1)}%`
                    : '-';
            }
            if (avgPoseError) {
                const pose = summary.avg_pose_error_mm;
                avgPoseError.textContent = pose !== null && pose !== undefined ? `${pose}mm` : '-';
            }
            if (avgProcessingTime) {
                const time = summary.avg_detection_time_ms;
                avgProcessingTime.textContent = time !== null && time !== undefined ? `${time}ms` : '-';
            }
        }

        if (recentList) {
            recentList.innerHTML = '';
            const recent = result?.recent || [];
            if (!recent.length) {
                const emptyItem = document.createElement('div');
                emptyItem.className = 'list-group-item bg-transparent text-muted';
                emptyItem.textContent = 'No recent validation runs.';
                recentList.appendChild(emptyItem);
                return;
            }

            recent.forEach(metric => {
                const rate = metric.detection_rate;
                const ratePct = rate !== null && rate !== undefined ? `${Math.round(rate * 100)}%` : 'n/a';
                const badgeClass = rate !== null && rate >= 0.95 ? 'bg-success' : (rate !== null && rate >= 0.8 ? 'bg-warning' : 'bg-danger');
                const item = document.createElement('div');
                item.className = 'list-group-item bg-transparent';
                item.innerHTML = `
                    <div class="d-flex justify-content-between">
                        <span>Pattern ${window.escapeHtml(metric.pattern_id || 'Unlinked')}</span>
                        <span class="badge ${badgeClass}">${ratePct} detected</span>
                    </div>
                `;
                recentList.appendChild(item);
            });
        }
    }

    downloadTestPattern() {
        if (!window.currentTestPattern) return;

        const link = document.createElement('a');
        link.href = 'data:image/png;base64,' + window.currentTestPattern;
        link.download = 'test_pattern.png';
        link.click();
    }

    showWarnings(result) {
        if (!result || !Array.isArray(result.warnings)) return;
        result.warnings.forEach(warning => {
            window.notificationManager.showWarning(warning.message || 'Warning');
        });
    }

    updateRequestMeta(elementId, requestId) {
        const el = document.getElementById(elementId);
        if (!el) return;
        if (requestId) {
            el.textContent = `Request ID: ${requestId}`;
            el.style.display = 'block';
        } else {
            el.style.display = 'none';
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ValidationManager();
});
