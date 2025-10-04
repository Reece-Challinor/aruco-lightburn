"""
Integration tests for API endpoints
"""

import unittest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ArUCO', response.data)
    
    def test_generate_page(self):
        """Test generate page loads"""
        response = self.client.get('/generate')
        self.assertEqual(response.status_code, 200)
    
    def test_calibration_page(self):
        """Test calibration page loads"""
        response = self.client.get('/calibration')
        self.assertEqual(response.status_code, 200)
    
    def test_validation_page(self):
        """Test validation page loads"""
        response = self.client.get('/validation')
        self.assertEqual(response.status_code, 200)
    
    def test_documentation_page(self):
        """Test documentation page loads"""
        response = self.client.get('/documentation')
        self.assertEqual(response.status_code, 200)
    
    def test_get_dictionaries(self):
        """Test dictionary list API"""
        response = self.client.get('/api/dictionaries')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertIn('4X4_50', data)
        
        # Check dictionary structure
        dict_info = data['4X4_50']
        self.assertIn('size', dict_info)
        self.assertIn('max_markers', dict_info)
        self.assertIn('recommended_use', dict_info)
    
    def test_preview_generation(self):
        """Test SVG preview generation"""
        test_data = {
            'dictionary': '4X4_50',
            'start_id': 0,
            'rows': 2,
            'cols': 2,
            'size_mm': 20,
            'spacing_mm': 5,
            'border_bits': 1,
            'include_labels': True,
            'include_outer_border': False
        }
        
        response = self.client.post(
            '/api/preview',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('svg', data)
        self.assertIn('dimensions', data)
        self.assertIn('marker_count', data)
        self.assertEqual(data['marker_count'], 4)
        self.assertTrue(data['success'])
    
    def test_preview_invalid_dictionary(self):
        """Test preview with invalid dictionary"""
        test_data = {
            'dictionary': 'INVALID',
            'start_id': 0,
            'rows': 1,
            'cols': 1,
            'size_mm': 20,
            'spacing_mm': 5,
            'border_bits': 1
        }
        
        response = self.client.post(
            '/api/preview',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_preview_invalid_params(self):
        """Test preview with invalid parameters"""
        test_data = {
            'dictionary': '4X4_50',
            'start_id': -1,  # Invalid negative ID
            'rows': 0,  # Invalid zero rows
            'cols': 1,
            'size_mm': 20,
            'spacing_mm': 5,
            'border_bits': 1
        }
        
        response = self.client.post(
            '/api/preview',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_download_lightburn(self):
        """Test LightBurn file download"""
        test_data = {
            'dictionary': '4X4_50',
            'start_id': 0,
            'rows': 1,
            'cols': 1,
            'size_mm': 20,
            'spacing_mm': 5,
            'border_bits': 1,
            'include_labels': False
        }
        
        response = self.client.post(
            '/api/download',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/octet-stream', response.content_type)
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
    
    def test_quick_test_endpoint(self):
        """Test quick test API endpoint"""
        response = self.client.get('/api/quick-test')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('message', data)
        self.assertIn('available_dictionaries', data)
        self.assertIn('timestamp', data)
    
    def test_debug_status_endpoint(self):
        """Test debug status endpoint"""
        response = self.client.get('/api/debug/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'operational')
        self.assertIn('opencv', data)
        self.assertIn('dictionaries', data)
        self.assertIn('timestamp', data)
    
    def test_log_error_endpoint(self):
        """Test error logging endpoint"""
        error_data = {
            'timestamp': '2024-01-01T00:00:00Z',
            'context': 'Test',
            'message': 'Test error',
            'stack': 'Test stack trace',
            'url': 'http://test.com'
        }
        
        response = self.client.post(
            '/api/log-error',
            data=json.dumps(error_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'logged')
    
    def test_preview_with_outer_border(self):
        """Test preview generation with outer border"""
        test_data = {
            'dictionary': '4X4_50',
            'start_id': 0,
            'rows': 1,
            'cols': 1,
            'size_mm': 20,
            'spacing_mm': 5,
            'border_bits': 1,
            'include_outer_border': True,
            'border_width': 3.0
        }
        
        response = self.client.post(
            '/api/preview',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check dimensions include border
        self.assertGreater(data['total_width'], 20)
        self.assertGreater(data['total_height'], 20)


if __name__ == '__main__':
    unittest.main()