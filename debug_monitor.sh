#!/bin/bash

# ArUCO Generator Debug Monitor - Comprehensive Logging for AI Debugging
# This script provides real-time monitoring and logging for troubleshooting

LOGFILE="ai_debug_logs.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Initialize log file
echo "========================================" >> $LOGFILE
echo "ArUCO Generator Debug Session Started: $TIMESTAMP" >> $LOGFILE
echo "========================================" >> $LOGFILE

# Function to log with timestamp
log_debug() {
    local message="$1"
    local context="${2:-SYSTEM}"
    echo "[$TIMESTAMP] [$context] $message" | tee -a $LOGFILE
}

# System information
log_debug "System Information" "INIT"
log_debug "OS: $(uname -a)" "SYSTEM"
log_debug "Python version: $(python3 --version)" "SYSTEM"
log_debug "Node available: $(which node || echo 'Not installed')" "SYSTEM"
log_debug "Current directory: $(pwd)" "SYSTEM"
log_debug "User: $(whoami)" "SYSTEM"

# Process monitoring
log_debug "Process Status" "INIT"
log_debug "Flask processes: $(pgrep -f flask || echo 'None running')" "PROCESS"
log_debug "Gunicorn processes: $(pgrep -f gunicorn || echo 'None running')" "PROCESS"
log_debug "Python processes: $(pgrep -f python || echo 'None running')" "PROCESS"

# Port monitoring
log_debug "Port Status" "INIT"
log_debug "Port 5000 status: $(netstat -ln | grep :5000 || echo 'Not listening')" "NETWORK"
log_debug "All listening ports: $(netstat -ln | grep LISTEN)" "NETWORK"

# File system checks
log_debug "File System Status" "INIT"
log_debug "Static files exist: $(ls -la static/ | head -5)" "FILES"
log_debug "Templates exist: $(ls -la templates/ | head -5)" "FILES"
log_debug "ArUCO module files: $(ls -la aruco_generator/)" "FILES"

# Application health check
log_debug "Application Health Check" "INIT"
if curl -s http://localhost:5000/api/debug/status > /dev/null 2>&1; then
    log_debug "Application responding on port 5000" "HEALTH"
    curl -s http://localhost:5000/api/debug/status >> $LOGFILE
else
    log_debug "Application NOT responding on port 5000" "HEALTH"
fi

# Memory and CPU usage
log_debug "Resource Usage" "INIT"
log_debug "Memory usage: $(free -h | grep Mem)" "RESOURCES"
log_debug "CPU usage: $(top -bn1 | grep "Cpu(s)")" "RESOURCES"
log_debug "Disk usage: $(df -h | grep -E '/$|/home')" "RESOURCES"

# Environment variables (filtered for security)
log_debug "Environment Variables" "INIT"
log_debug "PATH: $PATH" "ENV"
log_debug "PYTHONPATH: ${PYTHONPATH:-Not set}" "ENV"
log_debug "FLASK_ENV: ${FLASK_ENV:-Not set}" "ENV"
log_debug "DATABASE_URL: ${DATABASE_URL:-Not set}" "ENV"

# Recent error logs
log_debug "Recent Application Logs" "INIT"
if [ -f "debug_logs.txt" ]; then
    log_debug "Last 20 lines from debug_logs.txt:" "LOGS"
    tail -20 debug_logs.txt >> $LOGFILE
else
    log_debug "No debug_logs.txt file found" "LOGS"
fi

# Continuous monitoring function
monitor_app() {
    log_debug "Starting continuous monitoring..." "MONITOR"
    
    while true; do
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        
        # Check if app is responding
        if curl -s http://localhost:5000/api/debug/status > /dev/null 2>&1; then
            log_debug "App health check: OK" "MONITOR"
        else
            log_debug "App health check: FAILED" "MONITOR"
            
            # Try to restart if needed
            if ! pgrep -f gunicorn > /dev/null; then
                log_debug "No gunicorn process found, attempting restart..." "MONITOR"
                # Log the restart attempt
                log_debug "Restart command would be: gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app" "MONITOR"
            fi
        fi
        
        # Monitor error logs
        if [ -f "debug_logs.txt" ]; then
            NEW_ERRORS=$(tail -5 debug_logs.txt | grep "ERROR\|EXCEPTION\|FAILED")
            if [ ! -z "$NEW_ERRORS" ]; then
                log_debug "New errors detected:" "MONITOR"
                echo "$NEW_ERRORS" >> $LOGFILE
            fi
        fi
        
        sleep 30  # Check every 30 seconds
    done
}

# Test advanced tab functionality
test_advanced_tab() {
    log_debug "Testing Advanced Tab Functionality" "TEST"
    
    # Test preview generation
    log_debug "Testing preview generation..." "TEST"
    PREVIEW_RESPONSE=$(curl -s -X POST http://localhost:5000/api/preview \
        -H "Content-Type: application/json" \
        -d '{
            "dictionary": "6X6_250",
            "rows": 2,
            "cols": 2,
            "start_id": 0,
            "size_mm": 20,
            "spacing_mm": 5,
            "include_borders": true,
            "include_labels": true,
            "include_outer_border": false,
            "border_width": 2.0
        }')
    
    if echo "$PREVIEW_RESPONSE" | grep -q "svg"; then
        log_debug "Preview generation: SUCCESS" "TEST"
    else
        log_debug "Preview generation: FAILED" "TEST"
        log_debug "Response: $PREVIEW_RESPONSE" "TEST"
    fi
    
    # Test download functionality
    log_debug "Testing download functionality..." "TEST"
    DOWNLOAD_RESPONSE=$(curl -s -X POST http://localhost:5000/api/download \
        -H "Content-Type: application/json" \
        -d '{
            "dictionary": "6X6_250",
            "rows": 1,
            "cols": 1,
            "start_id": 0,
            "size_mm": 20,
            "spacing_mm": 5,
            "include_borders": true,
            "include_labels": true,
            "include_outer_border": false,
            "border_width": 2.0
        }' \
        --write-out '%{http_code}')
    
    if [ "$DOWNLOAD_RESPONSE" = "200" ]; then
        log_debug "Download generation: SUCCESS" "TEST"
    else
        log_debug "Download generation: FAILED (HTTP $DOWNLOAD_RESPONSE)" "TEST"
    fi
}

# API endpoint tests
test_api_endpoints() {
    log_debug "Testing API Endpoints" "TEST"
    
    # Test dictionaries endpoint
    DICT_RESPONSE=$(curl -s http://localhost:5000/api/dictionaries)
    if echo "$DICT_RESPONSE" | grep -q "6X6_250"; then
        log_debug "Dictionaries endpoint: SUCCESS" "TEST"
    else
        log_debug "Dictionaries endpoint: FAILED" "TEST"
    fi
    
    # Test quick-test endpoint
    QUICK_RESPONSE=$(curl -s -X POST http://localhost:5000/api/quick-test)
    if echo "$QUICK_RESPONSE" | grep -q "svg"; then
        log_debug "Quick test endpoint: SUCCESS" "TEST"
    else
        log_debug "Quick test endpoint: FAILED" "TEST"
    fi
}

# Main execution
case "${1:-status}" in
    "monitor")
        monitor_app
        ;;
    "test")
        test_advanced_tab
        test_api_endpoints
        ;;
    "status")
        log_debug "Debug monitor script completed basic checks" "COMPLETE"
        echo "Debug information saved to $LOGFILE"
        echo "Run './debug_monitor.sh monitor' for continuous monitoring"
        echo "Run './debug_monitor.sh test' for API testing"
        ;;
    *)
        echo "Usage: $0 [status|monitor|test]"
        echo "  status  - Run basic system checks (default)"
        echo "  monitor - Run continuous monitoring"
        echo "  test    - Test API endpoints and functionality"
        ;;
esac