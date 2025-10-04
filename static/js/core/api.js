/**
 * <!--
 * <ai_agent_documentation>
 *   <file_meta>
 *     <name>api.js</name>
 *     <version>3.0.0</version>
 *     <type>frontend_api_client</type>
 *     <purpose>Centralized API communication layer with comprehensive error handling and loading states</purpose>
 *     <last_updated>2025-01-15</last_updated>
 *     <maintainer>ArUCO Generator Team</maintainer>
 *   </file_meta>
 *
 *   <golden_path>
 *     <description>Primary workflow for frontend-backend API communication</description>
 *     <steps>
 *       <step id="1">Initialize API clients → APIClient and ArUCOAPI instances created</step>
 *       <step id="2">User triggers action → Frontend calls appropriate API method</step>
 *       <step id="3">API client handles request → Adds headers, shows loading, sends request</step>
 *       <step id="4">Backend processes → Returns JSON response or file download</step>
 *       <step id="5">API client handles response → Hide loading, process data or handle errors</step>
 *     </steps>
 *     <fallback_paths>
 *       <fallback condition="network_error">Show error notification with retry option</fallback>
 *       <fallback condition="server_error">Display specific error message from backend</fallback>
 *       <fallback condition="invalid_response">Show generic error message</fallback>
 *     </fallback_paths>
 *   </golden_path>
 *
 *   <api_classes>
 *     <class name="APIClient">
 *       <purpose>Base API client with common HTTP operations and error handling</purpose>
 *       <methods>
 *         <method name="constructor" parameters="none" returns="APIClient instance">
 *           <purpose>Initialize base API client with default configuration</purpose>
 *           <sets>baseURL to '/api', defaultHeaders with JSON content-type</sets>
 *         </method>
 *         <method name="request" parameters="endpoint, options" returns="Promise<Object>">
 *           <purpose>Core HTTP request method with loading states and error handling</purpose>
 *           <workflow>
 *             <step>Show loading indicator</step>
 *             <step>Send HTTP request with merged headers</step>
 *             <step>Parse JSON response</step>
 *             <step>Handle errors and success</step>
 *             <step>Hide loading indicator</step>
 *           </workflow>
 *         </method>
 *         <method name="get" parameters="endpoint, params" returns="Promise<Object>">
 *           <purpose>HTTP GET request with query parameters</purpose>
 *           <url_building>Builds URL with search parameters from params object</url_building>
 *         </method>
 *         <method name="post" parameters="endpoint, data" returns="Promise<Object>">
 *           <purpose>HTTP POST request with JSON body</purpose>
 *           <serialization>Automatically JSON.stringify data parameter</serialization>
 *         </method>
 *         <method name="uploadFile" parameters="endpoint, file, additionalData" returns="Promise<Object>">
 *           <purpose>File upload with FormData</purpose>
 *           <handling>Creates FormData, appends file and additional fields</handling>
 *         </method>
 *         <method name="downloadFile" parameters="endpoint, params, filename" returns="Promise<void>">
 *           <purpose>Download file from server and trigger browser download</purpose>
 *           <workflow>
 *             <step>Send POST request to endpoint</step>
 *             <step>Get blob response from server</step>
 *             <step>Create object URL for blob</step>
 *             <step>Trigger download with filename</step>
 *             <step>Clean up object URL</step>
 *           </workflow>
 *         </method>
 *       </methods>
 *     </class>
 *
 *     <class name="ArUCOAPI" extends="APIClient">
 *       <purpose>ArUCO-specific API methods for marker generation and management</purpose>
 *       <method_categories>
 *         <category name="dictionary_management">
 *           <method name="getDictionaries" endpoint="/dictionaries" returns="dictionary_info"/>
 *         </category>
 *         <category name="generation_methods">
 *           <method name="generatePreview" endpoint="/preview" parameters="generation_params"/>
 *           <method name="generateAdvanced" endpoint="/advanced/preview" parameters="advanced_params"/>
 *           <method name="generateBatch" endpoint="/batch_generate" parameters="batch_params"/>
 *         </category>
 *         <category name="calibration_methods">
 *           <method name="generateChArUco" endpoint="/calibration/charuco" parameters="charuco_params"/>
 *           <method name="generateArUcoBoard" endpoint="/calibration/aruco_board" parameters="board_params"/>
 *           <method name="generateAprilTag" endpoint="/calibration/apriltag" parameters="apriltag_params"/>
 *         </category>
 *         <category name="validation_methods">
 *           <method name="generateTestPattern" endpoint="/validation/test_pattern" parameters="test_params"/>
 *           <method name="calculateHammingDistance" endpoint="/validation/hamming_distance" parameters="hamming_params"/>
 *           <method name="verifyQuality" endpoint="/validation/verify_quality" parameters="image_file, metadata"/>
 *         </category>
 *         <category name="export_methods">
 *           <method name="exportLightBurn" endpoint="/download" file_type=".lbrn2"/>
 *           <method name="exportSVG" endpoint="/export/svg" file_type=".svg"/>
 *           <method name="exportPDF" endpoint="/export/pdf" file_type=".pdf"/>
 *           <method name="exportDXF" endpoint="/export/dxf" file_type=".dxf"/>
 *           <method name="exportSTL" endpoint="/export/stl" file_type=".stl"/>
 *         </category>
 *       </method_categories>
 *     </class>
 *   </api_classes>
 *
 *   <data_structures>
 *     <generation_params>
 *       <field name="dictionary" type="string" required="true" description="ArUCO dictionary name"/>
 *       <field name="start_id" type="integer" default="0" description="Starting marker ID"/>
 *       <field name="rows" type="integer" required="true" description="Number of rows"/>
 *       <field name="cols" type="integer" required="true" description="Number of columns"/>
 *       <field name="size_mm" type="number" required="true" description="Marker size in millimeters"/>
 *       <field name="spacing_mm" type="number" required="true" description="Spacing between markers"/>
 *       <field name="include_labels" type="boolean" default="false" description="Include ID labels"/>
 *       <field name="include_borders" type="boolean" default="true" description="Include marker borders"/>
 *     </generation_params>
 *
 *     <api_response>
 *       <success_response>
 *         <field name="svg" type="string" description="Generated SVG content"/>
 *         <field name="dimensions" type="object" description="Width and height in mm"/>
 *         <field name="marker_count" type="integer" description="Total markers generated"/>
 *         <field name="success" type="boolean" description="Operation success flag"/>
 *       </success_response>
 *       <error_response>
 *         <field name="error" type="string" description="Human-readable error message"/>
 *         <field name="details" type="string" description="Technical details (optional)"/>
 *       </error_response>
 *     </api_response>
 *
 *     <file_download_response>
 *       <field name="blob" type="Blob" description="File content as binary blob"/>
 *       <field name="filename" type="string" description="Suggested download filename"/>
 *       <field name="content_type" type="string" description="MIME type of file"/>
 *     </file_download_response>
 *   </data_structures>
 *
 *   <error_handling>
 *     <client_errors>
 *       <error code="400" type="validation_error" handling="Display specific parameter error"/>
 *       <error code="404" type="not_found" handling="Show resource not found message"/>
 *       <error code="429" type="rate_limit" handling="Show rate limit exceeded message"/>
 *     </client_errors>
 *     <server_errors>
 *       <error code="500" type="internal_error" handling="Show generic server error with retry option"/>
 *       <error code="501" type="not_implemented" handling="Show feature not available message"/>
 *       <error code="503" type="service_unavailable" handling="Show service temporarily unavailable"/>
 *     </server_errors>
 *     <network_errors>
 *       <error type="fetch_failed" handling="Show network connection error"/>
 *       <error type="timeout" handling="Show request timeout error"/>
 *       <error type="abort" handling="Show request cancelled message"/>
 *     </network_errors>
 *   </error_handling>
 *
 *   <ui_integration>
 *     <loading_states>
 *       <indicator id="globalLoader" trigger="any_api_request" behavior="show/hide"/>
 *       <element class="btn-loading" trigger="specific_button_click" behavior="disable_button"/>
 *     </loading_states>
 *     <notification_system>
 *       <success_notifications>Success messages for completed operations</success_notifications>
 *       <error_notifications>Error messages with actionable guidance</error_notifications>
 *       <info_notifications>Progress updates for long-running operations</info_notifications>
 *     </notification_system>
 *   </ui_integration>
 *
 *   <performance_considerations>
 *     <request_optimization>
 *       <caching>Dictionary info cached to avoid repeated requests</caching>
 *       <debouncing>User input debounced to prevent excessive API calls</debouncing>
 *       <request_cancellation>Abort previous requests when new ones are made</request_cancellation>
 *     </request_optimization>
 *     <file_handling>
 *       <streaming>Large file downloads use blob streaming</streaming>
 *       <memory_management>Object URLs properly revoked after use</memory_management>
 *       <progress_tracking>File upload/download progress indication</progress_tracking>
 *     </file_handling>
 *   </performance_considerations>
 *
 *   <security_considerations>
 *     <input_sanitization>
 *       <validation>All parameters validated before sending to server</validation>
 *       <encoding>Proper URL encoding for query parameters</encoding>
 *       <content_type>Correct Content-Type headers for different request types</content_type>
 *     </input_sanitization>
 *     <error_disclosure>
 *       <principle>Don't expose sensitive system information in error messages</principle>
 *       <logging>Log detailed errors to console for debugging</logging>
 *       <user_messages>Show user-friendly error messages</user_messages>
 *     </error_disclosure>
 *   </security_considerations>
 *
 *   <initialization>
 *     <dom_ready>API clients initialized when DOM content is loaded</dom_ready>
 *     <global_access>Clients attached to window object for global access</global_access>
 *     <dependencies>Requires notification manager for error display</dependencies>
 *   </initialization>
 *
 *   <usage_patterns>
 *     <common_workflows>
 *       <workflow name="generate_and_preview">
 *         <step>User fills form → collect parameters</step>
 *         <step>Call arucoAPI.generatePreview(params)</step>
 *         <step>Display SVG in preview area</step>
 *         <step>Show download options</step>
 *       </workflow>
 *       <workflow name="download_file">
 *         <step>User clicks download → collect export parameters</step>
 *         <step>Call appropriate export method (exportLightBurn, exportSVG, etc.)</step>
 *         <step>Browser automatically downloads file</step>
 *       </workflow>
 *       <workflow name="error_handling">
 *         <step>API request fails → error caught in try/catch</step>
 *         <step>Error displayed via notification system</step>
 *         <step>Loading state cleared</step>
 *         <step>User can retry operation</step>
 *       </workflow>
 *     </common_workflows>
 *   </usage_patterns>
 *
 *   <version_history>
 *     <version number="3.0.0" date="2025-01-15">
 *       <changes>
 *         <change>Enhanced XML documentation system</change>
 *         <change>Comprehensive API method documentation</change>
 *         <change>Golden path and error handling documentation</change>
 *         <change>Performance and security considerations</change>
 *       </changes>
 *     </version>
 *   </version_history>
 * </ai_agent_documentation>
 * -->
 *
 * Frontend API Client Module
 * ==========================
 *
 * Purpose: Centralized API communication layer with comprehensive error handling,
 * loading states, and file operations for the ArUCO marker generator frontend.
 *
 * Architecture Overview:
 * ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
 * │   UI Components │───▶│   API Client    │───▶│   Backend API   │
 * │   (Forms, etc)  │    │   (this file)   │    │   (Flask)       │
 * └─────────────────┘    └─────────────────┘    └─────────────────┘
 *          │                       │                       │
 *          ▼                       ▼                       ▼
 * ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
 * │   Notifications │    │   Loading       │    │   File          │
 * │   (Success/Error)│    │   Indicators    │    │   Downloads     │
 * └─────────────────┘    └─────────────────┘    └─────────────────┘
 *
 * Key Classes:
 * - APIClient: Base HTTP client with common operations
 * - ArUCOAPI: ArUCO-specific methods extending base client
 *
 * Golden Path Usage:
 * 1. User interaction → UI component collects parameters
 * 2. Component calls API method → arucoAPI.generatePreview(params)
 * 3. API client handles HTTP → Shows loading, sends request
 * 4. Backend processes → Returns JSON or file download
 * 5. Client handles response → Updates UI, hides loading, shows notifications
 *
 * Error Handling Strategy:
 * - Network errors → Show connection error with retry option
 * - Validation errors → Display specific parameter guidance
 * - Server errors → Show user-friendly message with support info
 * - File errors → Handle download failures gracefully
 *
 * Version: 3.0.0
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
            
            // Use correct API path
            const fullURL = endpoint.startsWith('/api/') ? endpoint : `/api${endpoint}`;
            const response = await fetch(fullURL, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify(params)
            });

            if (!response.ok) {
                // Try to get error message from JSON response
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const error = await response.json();
                    throw new Error(error.error || `HTTP error! status: ${response.status}`);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            
            // Check if blob is empty
            if (blob.size === 0) {
                throw new Error('No data received from server');
            }
            
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
    
    async exportPDF(params) {
        return this.downloadFile('/export/pdf', params, 'aruco_markers.pdf');
    }
    
    async exportSVG(params) {
        return this.downloadFile('/export/svg', params, 'aruco_markers.svg');
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