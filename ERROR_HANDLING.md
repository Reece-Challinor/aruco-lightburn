# Error Handling Documentation

## Overview

This document provides a comprehensive guide to error handling patterns, self-referential messages, and debugging strategies used throughout the ArUCO Generator application.

## Error Response Format

### Standard JSON Error Response
```json
{
  "error": "Human-readable error description",
  "details": "Optional technical details",
  "code": "Optional error code for programmatic handling"
}
```

### HTTP Status Code Standards
- **400 Bad Request**: Invalid user input or parameters
- **404 Not Found**: Resource not found or unavailable
- **500 Internal Server Error**: Unexpected server-side errors
- **501 Not Implemented**: Features not yet available

## Error Handling Patterns by Module

### Core API Endpoints (web.py)

#### Input Validation Errors (400)
```python
# Pattern: Specific validation with helpful messages
if start_id < 0:
    return jsonify({'error': 'Start ID must be non-negative'}), 400
if rows <= 0 or cols <= 0:
    return jsonify({'error': 'Rows and columns must be positive integers'}), 400
if size_mm <= 0:
    return jsonify({'error': 'Marker size must be positive (in millimeters)'}), 400
if spacing_mm < 0:
    return jsonify({'error': 'Spacing must be non-negative (in millimeters)'}), 400
```

#### Dictionary Validation with Context
```python
# Pattern: Contextual error with available options
if not dictionary or dictionary not in aruco_gen.dictionaries:
    available = list(aruco_gen.dictionaries.keys())
    return jsonify({
        'error': f'Invalid dictionary "{dictionary}". Available dictionaries: {", ".join(available[:5])}{"..." if len(available) > 5 else ""}'
    }), 400
```

#### Generic Exception Handling
```python
# Pattern: Self-referential error messages
except ValueError as e:
    return jsonify({'error': f'Invalid input parameter: {str(e)}'}), 400
except Exception as e:
    logger.error(f"Preview generation error: {e}")
    return jsonify({'error': 'Failed to generate preview. Please check your parameters and try again.'}), 500
```

### Advanced API Endpoints (advanced_web.py)

#### Simple Exception Handling
```python
# Pattern: Generic error handling for complex operations
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

#### File Upload Validation
```python
# Pattern: Missing resource validation
if 'image' not in request.files:
    return jsonify({'error': 'No image provided'}), 400
```

### Calibration Endpoints (calibration_web.py)

#### Domain-Specific Validation
```python
# Pattern: Business logic validation
if marker_length >= square_length:
    return jsonify({'error': 'Marker size must be smaller than square size'}), 400
```

#### Database Error Handling
```python
# Pattern: Database unavailability handling
except Exception as e:
    if 'database' in str(e).lower():
        return jsonify({'error': 'Pattern not found or database unavailable'}), 404
    return jsonify({'error': str(e)}), 500
```

## Self-Referential Error Messages

### Identified Patterns

#### User-Blaming Messages (Anti-Pattern)
```python
# ❌ These messages place responsibility on user without specific guidance
'Failed to generate preview. Please check your parameters and try again.'
'Failed to export SVG file. Please check your parameters and try again.'
'Failed to generate LightBurn file. Please check your parameters and try again.'
```

#### Improved Messages (Recommended)
```python
# ✅ Specific, actionable error messages
'Marker size must be positive (in millimeters)'
'Start ID must be non-negative'
'Invalid dictionary "INVALID_DICT". Available dictionaries: 4X4_50, 4X4_100, ...'
```

## Error Handling Best Practices

### 1. Specific Over Generic
```python
# ❌ Generic
return jsonify({'error': 'Invalid input'}), 400

# ✅ Specific
return jsonify({'error': 'Marker size must be positive (in millimeters)'}), 400
```

### 2. Context-Aware Error Messages
```python
# ✅ Provide available options
available = list(aruco_gen.dictionaries.keys())
return jsonify({
    'error': f'Invalid dictionary "{dictionary}". Available: {", ".join(available[:3])}'
}), 400
```

### 3. Consistent Logging
```python
# ✅ Log technical details, return user-friendly messages
try:
    # Operation
    pass
except Exception as e:
    logger.error(f"Technical details: {e}", exc_info=True)
    return jsonify({'error': 'User-friendly message with next steps'}), 500
```

### 4. Error Code Classification
```python
# ✅ Structured error response
return jsonify({
    'error': 'Human readable message',
    'code': 'INVALID_DICTIONARY',
    'details': {'available_dictionaries': available_options}
}), 400
```

## Frontend Error Handling

### JavaScript Error Pattern
```javascript
// static/js/core/api.js pattern
try {
    const response = await fetch(url, options);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Unknown error occurred');
    }
    return await response.json();
} catch (error) {
    console.error('API Error:', error);
    showNotification(error.message, 'error');
    throw error;
}
```

### Error Display System
```javascript
// static/js/core/notifications.js
function showNotification(message, type = 'info') {
    // Display user-friendly error messages
    // Types: 'info', 'success', 'warning', 'error'
}
```

## Database Error Handling

### Model Validation Errors
```python
# models.py - SQLAlchemy validation
class CalibrationPattern(db.Model):
    def validate(self):
        if self.marker_size_mm <= 0:
            raise ValueError("Marker size must be positive")
        if self.grid_size.count('x') != 1:
            raise ValueError("Grid size must be in format 'rows x cols'")
```

### Database Connection Errors
```python
# Pattern for database unavailability
try:
    db.session.add(object)
    db.session.commit()
except SQLAlchemyError as e:
    db.session.rollback()
    logger.error(f"Database error: {e}")
    return jsonify({'error': 'Database temporarily unavailable'}), 503
```

## Error Recovery Strategies

### 1. Graceful Degradation
```python
# aruco.py - OpenCV fallback
if not OPENCV_AVAILABLE:
    logger.warning("OpenCV not available, using fallback pattern generation")
    return self._create_fallback_pattern(marker_id, dict_name, size_pixels)
```

### 2. Retry Logic
```python
# For transient failures
import time
import random

def retry_operation(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except TemporaryError as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(0.5 * (2 ** attempt) + random.uniform(0, 0.1))
```

### 3. Circuit Breaker Pattern
```python
# For external service dependencies
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
```

## Testing Error Conditions

### Unit Test Examples
```python
# tests/test_api.py
def test_invalid_dictionary_error():
    response = client.post('/api/preview', json={
        'dictionary': 'INVALID_DICT',
        'rows': 1, 'cols': 1
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'Invalid dictionary' in data['error']
    assert 'Available dictionaries' in data['error']

def test_negative_marker_size_error():
    response = client.post('/api/preview', json={
        'dictionary': '4X4_50',
        'size_mm': -10
    })
    assert response.status_code == 400
    assert 'positive' in response.get_json()['error']
```

## Monitoring and Alerting

### Error Metrics to Track
1. **Error Rate by Endpoint**: Track 4xx/5xx responses per endpoint
2. **Error Types**: Categorize errors by type (validation, database, external)
3. **Response Times**: Monitor for performance degradation
4. **User Journey Failures**: Track where users encounter errors

### Logging Best Practices
```python
import logging
import json

# Structured logging for better searchability
logger.info("API request", extra={
    'endpoint': '/api/preview',
    'user_id': user_id,
    'parameters': {
        'dictionary': dictionary,
        'size_mm': size_mm
    }
})

logger.error("Generation failed", extra={
    'error_type': 'ValidationError',
    'endpoint': '/api/preview',
    'parameters': sanitized_params,
    'error_message': str(e)
})
```

## Error Message Localization

### Internationalization Support
```python
# Future enhancement for multiple languages
def get_error_message(error_code, lang='en', **kwargs):
    messages = {
        'en': {
            'INVALID_DICTIONARY': 'Invalid dictionary "{dictionary}". Available: {available}',
            'NEGATIVE_SIZE': 'Size must be positive (in {units})'
        },
        'es': {
            'INVALID_DICTIONARY': 'Diccionario inválido "{dictionary}". Disponibles: {available}',
            'NEGATIVE_SIZE': 'El tamaño debe ser positivo (en {units})'
        }
    }
    return messages[lang][error_code].format(**kwargs)
```

## Recommendations for Improvement

### 1. Standardize Error Response Format
```python
# Proposed standard error response
class APIError(Exception):
    def __init__(self, message, code=None, details=None, status_code=400):
        self.message = message
        self.code = code
        self.details = details
        self.status_code = status_code

def error_handler(error):
    return jsonify({
        'error': error.message,
        'code': error.code,
        'details': error.details,
        'timestamp': datetime.utcnow().isoformat()
    }), error.status_code
```

### 2. Remove Self-Referential Messages
Replace vague "check your parameters" messages with specific validation errors.

### 3. Add Error Context
Include relevant information like valid ranges, available options, or expected formats.

### 4. Implement Error Codes
Add machine-readable error codes for programmatic error handling by API clients.

---

*This error handling documentation is part of the comprehensive repository cleanup and optimization initiative.*
