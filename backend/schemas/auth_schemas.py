"""
Authentication validation schemas
"""
from marshmallow import Schema, fields, validate
from marshmallow.validate import Email

class UserRegistrationSchema(Schema):
    """Schema for user registration"""
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=64),
        description='Username'
    )
    email = fields.String(
        required=True,
        validate=Email(),
        description='Email address'
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=8),
        description='Password (minimum 8 characters)'
    )

class UserLoginSchema(Schema):
    """Schema for user login"""
    username = fields.String(
        required=True,
        description='Username'
    )
    password = fields.String(
        required=True,
        description='Password'
    )

class UserResponseSchema(Schema):
    """Schema for user response"""
    id = fields.Integer(description='User ID')
    username = fields.String(description='Username')
    email = fields.String(description='Email address')
    is_admin = fields.Boolean(description='Admin status')
    created_at = fields.DateTime(description='Creation timestamp')

class AuthResponseSchema(Schema):
    """Schema for authentication response"""
    message = fields.String(description='Response message')
    user = fields.Nested(UserResponseSchema, description='User information')