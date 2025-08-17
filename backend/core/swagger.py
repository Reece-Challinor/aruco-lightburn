"""
OpenAPI/Swagger configuration
"""
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from flask_apispec import FlaskApiSpec
from flask_apispec.extension import APISpec
from apispec import APISpec as APISpecBase
from apispec.ext.marshmallow import MarshmallowPlugin

def configure_swagger(app: Flask):
    """Configure OpenAPI/Swagger documentation"""
    
    # API specification
    app.config.update({
        'APISPEC_SPEC': APISpecBase(
            title='ArUCO Generator API',
            version='v1',
            openapi_version='3.0.2',
            info={
                'description': 'Professional ArUCO marker generation API with calibration tools',
                'contact': {
                    'name': 'API Support',
                    'url': 'https://github.com/aruco-generator'
                },
                'license': {
                    'name': 'MIT',
                    'url': 'https://opensource.org/licenses/MIT'
                }
            },
            servers=[
                {
                    'url': '/api/v1',
                    'description': 'API v1 endpoint'
                }
            ],
            plugins=[MarshmallowPlugin()],
        ),
        'APISPEC_SWAGGER_URL': '/swagger.json',
        'APISPEC_SWAGGER_UI_URL': '/api/docs'
    })
    
    # Initialize Flask-APISpec
    docs = FlaskApiSpec(app)
    
    # Register Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/v1/swagger.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'ArUCO Generator API',
            'docExpansion': 'list',
            'defaultModelsExpandDepth': 2,
            'defaultModelExpandDepth': 2,
            'tryItOutEnabled': True,
            'filter': True,
            'showExtensions': True,
            'showCommonExtensions': True,
            'persistAuthorization': True,
            'displayRequestDuration': True
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return docs

def document_endpoint(docs, blueprint_name, endpoint_name, methods=['GET']):
    """Helper to document endpoints"""
    def decorator(func):
        # Register with Flask-APISpec
        docs.register(func, blueprint=blueprint_name, endpoint=endpoint_name)
        return func
    return decorator