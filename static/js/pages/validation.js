/**
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
            
            // In a real implementation, this would upload to the server
            // For now, we'll simulate the detection
            await this.simulateDetection(file);
            
            window.notificationManager.hideLoading();
            window.notificationManager.showSuccess('Image processed successfully');
        } catch (error) {
            window.notificationManager.hideLoading();
            window.notificationManager.showError('Failed to process image: ' + error.message);
        }
    }

    async simulateDetection(file) {
        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Show simulated results
        const detectedCount = Math.floor(Math.random() * 10) + 1;
        const quality = Math.floor(Math.random() * 30) + 70;
        
        document.getElementById('detectedCount').textContent = detectedCount;
        document.getElementById('detectionQuality').textContent = quality + '%';
        
        // Generate details
        const details = document.getElementById('detectionDetails');
        details.innerHTML = '';
        
        for (let i = 0; i < detectedCount; i++) {
            const markerId = Math.floor(Math.random() * 250);
            const confidence = Math.floor(Math.random() * 20) + 80;
            
            const detailCard = document.createElement('div');
            detailCard.className = 'alert alert-secondary';
            detailCard.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span><strong>Marker ID ${markerId}</strong></span>
                    <span class="badge ${confidence >= 90 ? 'bg-success' : 'bg-warning'}">
                        ${confidence}% confidence
                    </span>
                </div>
            `;
            details.appendChild(detailCard);
        }
        
        this.testResults.style.display = 'block';
    }

    setupHammingCalculator() {
        // This is called from the HTML onclick
        window.calculateHamming = async () => {
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
            } catch (error) {
                window.notificationManager.showError('Failed to calculate Hamming distance');
            }
        };
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
    }

    setupTestPatternGenerator() {
        window.generateTestPattern = async () => {
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
                
                window.notificationManager.hideLoading();
                window.notificationManager.showSuccess('Test pattern generated');
            } catch (error) {
                window.notificationManager.hideLoading();
                window.notificationManager.showError('Failed to generate test pattern');
            }
        };
    }

    displayTestPattern(result) {
        const preview = document.getElementById('testPatternPreview');
        
        if (result.image_base64) {
            preview.innerHTML = `
                <div class="text-center">
                    <img src="data:image/png;base64,${result.image_base64}" 
                         class="img-fluid border rounded" 
                         style="max-height: 400px; background: white;">
                    <div class="mt-3">
                        <button class="btn btn-success" onclick="downloadTestPattern()">
                            <i class="bi bi-download me-2"></i>Download Pattern
                        </button>
                    </div>
                </div>
            `;
            
            // Store for download
            window.currentTestPattern = result.image_base64;
        }
    }
}

// Download test pattern function
window.downloadTestPattern = () => {
    if (!window.currentTestPattern) return;
    
    const link = document.createElement('a');
    link.href = 'data:image/png;base64,' + window.currentTestPattern;
    link.download = 'test_pattern.png';
    link.click();
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ValidationManager();
});