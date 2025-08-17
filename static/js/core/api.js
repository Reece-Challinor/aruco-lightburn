/**
 * API Client Module
 * Centralized API communication with error handling and loading states
 */

class APIClient {
    constructor() {
        this.baseURL = '/api';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.defaultHeaders,
                ...options.headers
            }
        };

        try {
            // Show loading state
            this.showLoading(true);
            
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            this.handleError(error);
            throw error;
        } finally {
            this.showLoading(false);
        }
    }

    // GET request
    async get(endpoint, params = {}) {
        const url = new URL(`${window.location.origin}${this.baseURL}${endpoint}`);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        
        return this.request(endpoint + url.search, {
            method: 'GET'
        });
    }

    // POST request
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // File upload
    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type for FormData
        });
    }

    // Download file
    async downloadFile(endpoint, params = {}, filename = 'download') {
        try {
            this.showLoading(true);
            
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify(params)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            this.handleError(error);
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        // Global loading indicator
        const loader = document.getElementById('globalLoader');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }

    handleError(error) {
        console.error('API Error:', error);
        
        // Show error notification
        if (window.notificationManager) {
            window.notificationManager.showError(error.message || 'An error occurred');
        }
    }
}

// ArUCO specific API methods
class ArUCOAPI extends APIClient {
    constructor() {
        super();
    }

    // Dictionary management
    async getDictionaries() {
        return this.get('/dictionaries');
    }

    // Generation methods
    async generatePreview(params) {
        return this.post('/preview', params);
    }

    async generateAdvanced(params) {
        return this.post('/advanced/preview', params);
    }

    async generateBatch(params) {
        return this.post('/batch_generate', params);
    }

    // Calibration methods
    async generateChArUco(params) {
        return this.post('/calibration/charuco', params);
    }

    async generateArUcoBoard(params) {
        return this.post('/calibration/aruco_board', params);
    }

    async generateAprilTag(params) {
        return this.post('/calibration/apriltag', params);
    }

    async generateAprilTagGrid(params) {
        return this.post('/calibration/apriltag_grid', params);
    }

    // Validation methods
    async generateTestPattern(params) {
        return this.post('/validation/test_pattern', params);
    }

    async calculateHammingDistance(params) {
        return this.post('/validation/hamming_distance', params);
    }

    async verifyQuality(imageFile, expectedId, dictionary) {
        return this.uploadFile('/validation/verify_quality', imageFile, {
            expected_id: expectedId,
            dictionary: dictionary
        });
    }

    async generateDetectionReport(params) {
        return this.post('/validation/detection_report', params);
    }

    // Export methods
    async exportOpenCV(params) {
        return this.downloadFile('/export/opencv_yaml', params, 'opencv_calibration.yaml');
    }

    async exportROS(params) {
        return this.downloadFile('/export/ros', params, 'ros_calibration.json');
    }

    async exportDXF(params) {
        return this.downloadFile('/export/dxf', params, 'aruco_pattern.dxf');
    }

    async exportSTL(params) {
        return this.downloadFile('/export/stl', params, 'landing_pad.stl');
    }

    async exportLightBurn(params) {
        return this.downloadFile('/download', params, 'aruco_markers.lbrn2');
    }

    // Presets
    async getPresets() {
        return this.get('/presets');
    }
}

// Initialize API client when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.apiClient = new APIClient();
    window.arucoAPI = new ArUCOAPI();
});