"""
Web routes for marker validation and testing interface.
"""

from flask import render_template, request, jsonify
from app import app

@app.route('/validation')
def validation_page():
    """Render validation and testing page."""
    return render_template('validation.html')

@app.route('/documentation')
def documentation_page():
    """Render documentation page."""
    return render_template('documentation.html')

@app.route('/generate')
def generate_page():
    """Render the main generation page with tabs."""
    from .aruco import ArUCOGenerator
    aruco_gen = ArUCOGenerator()
    dictionaries = aruco_gen.get_dictionary_info()
    return render_template('generate.html', dictionaries=dictionaries)