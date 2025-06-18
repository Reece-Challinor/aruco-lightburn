"""
{
  "file_type": "flask_entry_point",
  "purpose": "Application entry point for deployment and development",
  "dependencies": ["app.py"],
  "deployment": "Used by gunicorn and Replit workflows",
  "ai_navigation": {
    "modify_for": "Deployment configuration changes only",
    "primary_file": "app.py contains actual application logic"
  }
}
"""

from app import app  # noqa: F401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)