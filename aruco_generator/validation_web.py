"""
Web routes for marker validation and testing interface.
"""

from flask import render_template, request, jsonify
from app import app

# Route defined in web.py
# @app.route('/validation')
def validation_page_old():
    """Render validation and testing page."""
    return render_template('validation.html')

# Route defined in web.py
# @app.route('/documentation')
def documentation_page_old():
    """Render documentation page."""
    return render_template('documentation.html')

# Route defined in web.py
# @app.route('/generate')
def generate_page_old():
    """Render the main generation page with tabs."""
    from .aruco import ArUCOGenerator
    aruco_gen = ArUCOGenerator()
    dictionaries = aruco_gen.get_dictionary_info()
    return render_template('generate.html', dictionaries=dictionaries)