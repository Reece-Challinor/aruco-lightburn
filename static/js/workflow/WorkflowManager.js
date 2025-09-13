/**
 * Enhanced Workflow Manager for ArUCO Generator
 * Provides guided workflows, validation, and improved UX
 */
class WorkflowManager {
    constructor() {
        this.currentWorkflow = null;
        this.workflowHistory = [];
        this.validationRules = new Map();
        this.presetTemplates = new Map();
        this.init();
    }

    init() {
        this.setupValidationRules();
        this.setupPresetTemplates();
        this.setupWorkflowGuides();
        this.loadWorkflowHistory();
        this.setupEventListeners();
    }

    setupValidationRules() {
        // Validation rules for different parameters
        this.validationRules.set('markerId', {
            min: 0,
            max: 1000,
            message: 'Marker ID must be between 0 and 1000'
        });
        
        this.validationRules.set('markerSize', {
            min: 10,
            max: 500,
            message: 'Marker size must be between 10mm and 500mm'
        });
        
        this.validationRules.set('gridRows', {
            min: 1,
            max: 20,
            message: 'Grid rows must be between 1 and 20'
        });
        
        this.validationRules.set('gridCols', {
            min: 1,
            max: 20,
            message: 'Grid columns must be between 1 and 20'
        });
        
        this.validationRules.set('spacing', {
            min: 1,
            max: 100,
            message: 'Spacing must be between 1mm and 100mm'
        });
    }

    setupPresetTemplates() {
        // Common preset configurations
        this.presetTemplates.set('robotics_navigation', {
            name: 'Robotics Navigation',
            description: 'Optimized for robot localization',
            dictionary: '4X4_250',
            size: 100,
            rows: 1,
            cols: 1,
            spacing: 20,
            includeBorders: true,
            includeLabels: true
        });
        
        this.presetTemplates.set('drone_landing', {
            name: 'Drone Landing Pad',
            description: 'Large markers for aerial detection',
            dictionary: '6X6_50',
            size: 200,
            rows: 1,
            cols: 1,
            spacing: 50,
            includeBorders: true,
            includeLabels: false
        });
        
        this.presetTemplates.set('camera_calibration', {
            name: 'Camera Calibration',
            description: 'Grid for camera calibration',
            dictionary: '4X4_100',
            size: 50,
            rows: 5,
            cols: 7,
            spacing: 10,
            includeBorders: false,
            includeLabels: false
        });
        
        this.presetTemplates.set('ar_tracking', {
            name: 'AR Tracking',
            description: 'Small markers for AR applications',
            dictionary: '4X4_50',
            size: 30,
            rows: 2,
            cols: 2,
            spacing: 5,
            includeBorders: true,
            includeLabels: true
        });
        
        this.presetTemplates.set('inventory_management', {
            name: 'Inventory Management',
            description: 'Compact markers for product tracking',
            dictionary: '5X5_1000',
            size: 20,
            rows: 10,
            cols: 10,
            spacing: 2,
            includeBorders: false,
            includeLabels: true
        });
    }

    setupWorkflowGuides() {
        // Workflow guides for different use cases
        this.workflows = {
            firstTime: {
                name: 'First Time User',
                steps: [
                    {
                        element: '#quickDictionary',
                        title: 'Choose a Dictionary',
                        content: 'Select a dictionary type. 4×4_250 is recommended for most applications.',
                        position: 'bottom'
                    },
                    {
                        element: '#singleMarkerId',
                        title: 'Set Marker ID',
                        content: 'Each marker needs a unique ID. Start with 0 for your first marker.',
                        position: 'right'
                    },
                    {
                        element: '#singleMarkerSize',
                        title: 'Set Marker Size',
                        content: 'Size in millimeters. 50mm is a good starting size.',
                        position: 'right'
                    },
                    {
                        element: '#generateSingle',
                        title: 'Generate Your Marker',
                        content: 'Click to generate your first ArUCO marker!',
                        position: 'top'
                    }
                ]
            },
            batchGeneration: {
                name: 'Batch Generation',
                steps: [
                    {
                        element: '#batch-tab',
                        title: 'Switch to Batch Mode',
                        content: 'Click here for generating multiple markers at once.',
                        position: 'bottom'
                    },
                    {
                        element: '#batchPresets',
                        title: 'Use a Preset',
                        content: 'Select a preset configuration or create your own.',
                        position: 'bottom'
                    },
                    {
                        element: '#batchGenerate',
                        title: 'Generate Batch',
                        content: 'Generate all markers with progress tracking.',
                        position: 'top'
                    }
                ]
            }
        };
    }

    setupEventListeners() {
        // Add real-time validation to input fields
        document.querySelectorAll('input[type="number"]').forEach(input => {
            input.addEventListener('input', (e) => this.validateInput(e.target));
            input.addEventListener('blur', (e) => this.validateInput(e.target, true));
        });

        // Add preset template selection
        this.addPresetSelector();
        
        // Add workflow guide triggers
        this.addWorkflowTriggers();
        
        // Add keyboard shortcuts for workflows
        this.setupWorkflowShortcuts();
    }

    validateInput(input, showError = false) {
        const value = parseFloat(input.value);
        const ruleKey = this.getValidationRuleKey(input.id);
        
        if (!ruleKey || !this.validationRules.has(ruleKey)) return true;
        
        const rule = this.validationRules.get(ruleKey);
        const isValid = !isNaN(value) && value >= rule.min && value <= rule.max;
        
        // Update visual feedback
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            this.clearValidationMessage(input);
        } else {
            input.classList.remove('is-valid');
            if (showError) {
                input.classList.add('is-invalid');
                this.showValidationMessage(input, rule.message);
            }
        }
        
        return isValid;
    }

    getValidationRuleKey(inputId) {
        const ruleMap = {
            'singleMarkerId': 'markerId',
            'singleMarkerSize': 'markerSize',
            'gridRows': 'gridRows',
            'gridCols': 'gridCols',
            'gridStartId': 'markerId',
            'advancedSize': 'markerSize',
            'advancedSpacing': 'spacing',
            'advancedRows': 'gridRows',
            'advancedCols': 'gridCols'
        };
        return ruleMap[inputId];
    }

    showValidationMessage(input, message) {
        // Remove existing feedback
        this.clearValidationMessage(input);
        
        // Add new feedback
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        input.parentElement.appendChild(feedback);
    }

    clearValidationMessage(input) {
        const feedback = input.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    }

    addPresetSelector() {
        // Add preset selector to the UI
        const quickActions = document.querySelector('.quick-action-item');
        if (!quickActions) return;
        
        const presetSection = document.createElement('div');
        presetSection.className = 'mb-4';
        presetSection.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <label class="form-label fw-bold mb-0">Quick Presets</label>
                <button class="btn btn-sm btn-outline-primary" onclick="workflowManager.showAllPresets()">
                    <i class="bi bi-grid-3x3-gap me-1"></i>View All
                </button>
            </div>
            <div class="preset-grid" id="presetGrid">
                ${this.renderPresetButtons()}
            </div>
        `;
        
        quickActions.parentElement.insertBefore(presetSection, quickActions);
    }

    renderPresetButtons() {
        let html = '';
        let count = 0;
        this.presetTemplates.forEach((preset, key) => {
            if (count < 3) { // Show only first 3 presets
                html += `
                    <button class="btn btn-outline-secondary btn-sm w-100 mb-2" 
                            onclick="workflowManager.applyPreset('${key}')"
                            title="${preset.description}">
                        <i class="bi bi-lightning me-1"></i>${preset.name}
                    </button>
                `;
                count++;
            }
        });
        return html;
    }

    applyPreset(presetKey) {
        const preset = this.presetTemplates.get(presetKey);
        if (!preset) return;
        
        // Apply preset values to form
        const dictionarySelect = document.getElementById('quickDictionary');
        if (dictionarySelect) dictionarySelect.value = preset.dictionary;
        
        const sizeInput = document.getElementById('singleMarkerSize');
        if (sizeInput) sizeInput.value = preset.size;
        
        const rowsInput = document.getElementById('gridRows');
        if (rowsInput) rowsInput.value = preset.rows;
        
        const colsInput = document.getElementById('gridCols');
        if (colsInput) colsInput.value = preset.cols;
        
        // Show notification
        if (window.notificationManager) {
            window.notificationManager.showInfo(`Applied preset: ${preset.name}`);
        }
        
        // Track preset usage
        this.trackWorkflowAction('preset_applied', { preset: presetKey });
    }

    showAllPresets() {
        // Create modal to show all presets
        const modalHtml = `
            <div class="modal fade" id="presetsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Preset Templates</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                ${this.renderAllPresets()}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page if not exists
        if (!document.getElementById('presetsModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('presetsModal'));
        modal.show();
    }

    renderAllPresets() {
        let html = '';
        this.presetTemplates.forEach((preset, key) => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card preset-card h-100">
                        <div class="card-body">
                            <h6 class="card-title">${preset.name}</h6>
                            <p class="card-text small text-muted">${preset.description}</p>
                            <div class="preset-details small">
                                <span class="badge bg-secondary me-1">${preset.dictionary}</span>
                                <span class="badge bg-info me-1">${preset.size}mm</span>
                                <span class="badge bg-primary">${preset.rows}×${preset.cols}</span>
                            </div>
                            <button class="btn btn-primary btn-sm mt-3 w-100" 
                                    onclick="workflowManager.applyPreset('${key}'); bootstrap.Modal.getInstance(document.getElementById('presetsModal')).hide();">
                                Apply This Preset
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        return html;
    }

    addWorkflowTriggers() {
        // Add help button for workflows
        const pageHeader = document.querySelector('.display-6');
        if (pageHeader) {
            const helpButton = document.createElement('button');
            helpButton.className = 'btn btn-outline-info btn-sm ms-3';
            helpButton.innerHTML = '<i class="bi bi-question-circle me-1"></i>Guided Tour';
            helpButton.onclick = () => this.startWorkflow('firstTime');
            pageHeader.appendChild(helpButton);
        }
    }

    setupWorkflowShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+G - Start guided tour
            if (e.ctrlKey && e.key === 'g') {
                e.preventDefault();
                this.startWorkflow('firstTime');
            }
            // Ctrl+P - Show presets
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                this.showAllPresets();
            }
            // Ctrl+H - Show history
            if (e.ctrlKey && e.key === 'h') {
                e.preventDefault();
                this.showWorkflowHistory();
            }
        });
    }

    startWorkflow(workflowKey) {
        const workflow = this.workflows[workflowKey];
        if (!workflow) return;
        
        this.currentWorkflow = {
            key: workflowKey,
            ...workflow,
            currentStep: 0
        };
        
        this.showWorkflowStep(0);
    }

    showWorkflowStep(stepIndex) {
        if (!this.currentWorkflow || stepIndex >= this.currentWorkflow.steps.length) {
            this.completeWorkflow();
            return;
        }
        
        const step = this.currentWorkflow.steps[stepIndex];
        
        // Highlight element
        const element = document.querySelector(step.element);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            element.classList.add('workflow-highlight');
            
            // Show tooltip
            this.showWorkflowTooltip(element, step);
        }
        
        this.currentWorkflow.currentStep = stepIndex;
    }

    showWorkflowTooltip(element, step) {
        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = 'workflow-tooltip';
        tooltip.innerHTML = `
            <div class="workflow-tooltip-header">
                <h6>${step.title}</h6>
                <button class="btn-close btn-close-white" onclick="workflowManager.cancelWorkflow()"></button>
            </div>
            <div class="workflow-tooltip-body">
                <p>${step.content}</p>
            </div>
            <div class="workflow-tooltip-footer">
                <button class="btn btn-sm btn-secondary" onclick="workflowManager.previousStep()">
                    Previous
                </button>
                <span class="step-counter mx-2">
                    Step ${this.currentWorkflow.currentStep + 1} of ${this.currentWorkflow.steps.length}
                </span>
                <button class="btn btn-sm btn-primary" onclick="workflowManager.nextStep()">
                    Next
                </button>
            </div>
        `;
        
        // Position tooltip
        document.body.appendChild(tooltip);
        this.positionTooltip(tooltip, element, step.position);
    }

    positionTooltip(tooltip, element, position) {
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let top, left;
        
        switch (position) {
            case 'top':
                top = rect.top - tooltipRect.height - 10;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + 10;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - 10;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + 10;
                break;
            default:
                top = rect.bottom + 10;
                left = rect.left;
        }
        
        // Ensure tooltip stays within viewport
        top = Math.max(10, Math.min(top, window.innerHeight - tooltipRect.height - 10));
        left = Math.max(10, Math.min(left, window.innerWidth - tooltipRect.width - 10));
        
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
    }

    nextStep() {
        this.cleanupCurrentStep();
        this.showWorkflowStep(this.currentWorkflow.currentStep + 1);
    }

    previousStep() {
        if (this.currentWorkflow.currentStep > 0) {
            this.cleanupCurrentStep();
            this.showWorkflowStep(this.currentWorkflow.currentStep - 1);
        }
    }

    cleanupCurrentStep() {
        // Remove existing tooltips
        document.querySelectorAll('.workflow-tooltip').forEach(t => t.remove());
        
        // Remove highlights
        document.querySelectorAll('.workflow-highlight').forEach(e => {
            e.classList.remove('workflow-highlight');
        });
    }

    cancelWorkflow() {
        this.cleanupCurrentStep();
        this.currentWorkflow = null;
    }

    completeWorkflow() {
        this.cleanupCurrentStep();
        
        if (this.currentWorkflow) {
            // Track workflow completion
            this.trackWorkflowAction('workflow_completed', {
                workflow: this.currentWorkflow.key
            });
            
            // Show completion message
            if (window.notificationManager) {
                window.notificationManager.showSuccess('Tutorial completed! You\'re ready to generate markers.');
            }
        }
        
        this.currentWorkflow = null;
    }

    trackWorkflowAction(action, data) {
        // Add to workflow history
        const entry = {
            timestamp: new Date().toISOString(),
            action: action,
            data: data
        };
        
        this.workflowHistory.push(entry);
        this.saveWorkflowHistory();
        
        // Log to frontend logger if available
        if (window.frontendLogger) {
            window.frontendLogger.info(`Workflow: ${action}`, data);
        }
    }

    saveWorkflowHistory() {
        // Save last 100 entries
        const recentHistory = this.workflowHistory.slice(-100);
        localStorage.setItem('aruco_workflow_history', JSON.stringify(recentHistory));
    }

    loadWorkflowHistory() {
        const saved = localStorage.getItem('aruco_workflow_history');
        if (saved) {
            try {
                this.workflowHistory = JSON.parse(saved);
            } catch (e) {
                this.workflowHistory = [];
            }
        }
    }

    showWorkflowHistory() {
        // Create modal to show workflow history
        const recentActions = this.workflowHistory.slice(-20).reverse();
        
        const modalHtml = `
            <div class="modal fade" id="historyModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Generation History</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="list-group">
                                ${this.renderHistoryItems(recentActions)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page if not exists
        if (!document.getElementById('historyModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('historyModal'));
        modal.show();
    }

    renderHistoryItems(actions) {
        if (actions.length === 0) {
            return '<p class="text-muted text-center">No generation history yet</p>';
        }
        
        return actions.map(action => {
            const date = new Date(action.timestamp);
            const timeStr = date.toLocaleTimeString();
            const dateStr = date.toLocaleDateString();
            
            let icon = 'bi-clock-history';
            let title = action.action;
            
            if (action.action === 'preset_applied') {
                icon = 'bi-lightning';
                title = `Applied preset: ${action.data.preset}`;
            } else if (action.action === 'workflow_completed') {
                icon = 'bi-check-circle';
                title = `Completed tutorial: ${action.data.workflow}`;
            }
            
            return `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">
                            <i class="bi ${icon} me-2"></i>${title}
                        </h6>
                        <small class="text-muted">${timeStr}</small>
                    </div>
                    <small class="text-muted">${dateStr}</small>
                </div>
            `;
        }).join('');
    }

    // Progress tracking for batch generation
    showBatchProgress(current, total) {
        let progressBar = document.getElementById('batchProgressBar');
        if (!progressBar) {
            const container = document.getElementById('batchResults');
            if (container) {
                const progressHtml = `
                    <div class="progress mb-3" style="height: 25px;">
                        <div id="batchProgressBar" class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 0%">
                            <span class="progress-label">0 / 0</span>
                        </div>
                    </div>
                `;
                container.insertAdjacentHTML('afterbegin', progressHtml);
                progressBar = document.getElementById('batchProgressBar');
            }
        }
        
        if (progressBar) {
            const percentage = (current / total) * 100;
            progressBar.style.width = `${percentage}%`;
            progressBar.querySelector('.progress-label').textContent = `${current} / ${total}`;
            
            if (current === total) {
                progressBar.classList.remove('progress-bar-animated');
                progressBar.classList.add('bg-success');
            }
        }
    }

    // Enhanced error handling with recovery suggestions
    handleGenerationError(error) {
        const suggestions = this.getErrorSuggestions(error);
        
        const errorHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <h6 class="alert-heading">
                    <i class="bi bi-exclamation-triangle me-2"></i>Generation Error
                </h6>
                <p>${error.message || 'An unexpected error occurred'}</p>
                ${suggestions ? `
                    <hr>
                    <p class="mb-0"><strong>Suggestions:</strong></p>
                    <ul class="mb-0">
                        ${suggestions.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                ` : ''}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Show error in appropriate location
        const resultContainer = document.querySelector('.preview-container') || 
                              document.getElementById('advancedPreview');
        if (resultContainer) {
            resultContainer.innerHTML = errorHtml;
        }
    }

    getErrorSuggestions(error) {
        const errorStr = error.message ? error.message.toLowerCase() : '';
        const suggestions = [];
        
        if (errorStr.includes('invalid') || errorStr.includes('validation')) {
            suggestions.push('Check that all input values are within valid ranges');
            suggestions.push('Ensure marker ID is between 0 and dictionary maximum');
        }
        
        if (errorStr.includes('dictionary')) {
            suggestions.push('Verify the selected dictionary is supported');
            suggestions.push('Try using a standard dictionary like 4X4_250');
        }
        
        if (errorStr.includes('size')) {
            suggestions.push('Marker size should be between 10mm and 500mm');
            suggestions.push('For printing, consider sizes between 30mm and 100mm');
        }
        
        if (errorStr.includes('network') || errorStr.includes('connection')) {
            suggestions.push('Check your internet connection');
            suggestions.push('Refresh the page and try again');
        }
        
        return suggestions.length > 0 ? suggestions : null;
    }
}

// Initialize workflow manager
window.workflowManager = new WorkflowManager();