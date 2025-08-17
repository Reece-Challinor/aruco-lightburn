"""
Marker validation schemas
"""
from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class MarkerGenerationSchema(Schema):
    """Schema for marker generation request"""
    dictionary = fields.String(
        required=True,
        validate=validate.OneOf([
            '4X4_50', '4X4_100', '4X4_250', '4X4_1000',
            '5X5_50', '5X5_100', '5X5_250', '5X5_1000',
            '6X6_50', '6X6_100', '6X6_250', '6X6_1000',
            '7X7_50', '7X7_100', '7X7_250', '7X7_1000'
        ]),
        description='ArUCO dictionary type'
    )
    start_id = fields.Integer(
        missing=0,
        validate=validate.Range(min=0),
        description='Starting marker ID'
    )
    rows = fields.Integer(
        missing=1,
        validate=validate.Range(min=1, max=100),
        description='Number of rows in grid'
    )
    cols = fields.Integer(
        missing=1,
        validate=validate.Range(min=1, max=100),
        description='Number of columns in grid'
    )
    size_mm = fields.Float(
        missing=20.0,
        validate=validate.Range(min=1.0, max=1000.0),
        description='Marker size in millimeters'
    )
    spacing_mm = fields.Float(
        missing=5.0,
        validate=validate.Range(min=0.0, max=100.0),
        description='Spacing between markers in millimeters'
    )
    include_borders = fields.Boolean(
        missing=True,
        description='Include borders around markers'
    )
    include_labels = fields.Boolean(
        missing=True,
        description='Include ID labels'
    )
    include_outer_border = fields.Boolean(
        missing=False,
        description='Include outer border around entire grid'
    )
    border_width = fields.Float(
        missing=2.0,
        validate=validate.Range(min=0.1, max=10.0),
        description='Border width in millimeters'
    )
    save = fields.Boolean(
        missing=False,
        description='Save markers to database'
    )
    
    @validates_schema
    def validate_marker_count(self, data, **kwargs):
        """Validate total marker count"""
        rows = data.get('rows', 1)
        cols = data.get('cols', 1)
        total = rows * cols
        
        if total > 1000:
            raise ValidationError('Total markers cannot exceed 1000')

class MarkerResponseSchema(Schema):
    """Schema for marker generation response"""
    markers = fields.List(fields.Dict(), description='Generated markers')
    dimensions = fields.Dict(description='Grid dimensions')
    count = fields.Integer(description='Number of markers generated')
    success = fields.Boolean(description='Operation success status')

class MarkerPreviewRequestSchema(MarkerGenerationSchema):
    """Schema for marker preview request (same as generation)"""
    pass

class MarkerPreviewResponseSchema(Schema):
    """Schema for marker preview response"""
    svg = fields.String(description='SVG content')
    success = fields.Boolean(description='Operation success status')

class MarkerBatchSchema(Schema):
    """Schema for batch marker generation"""
    batch_config = fields.List(
        fields.Nested(MarkerGenerationSchema),
        required=True,
        validate=validate.Length(min=1, max=10),
        description='Batch configuration array'
    )

class MarkerExportSchema(MarkerGenerationSchema):
    """Schema for marker export request"""
    format = fields.String(
        validate=validate.OneOf(['svg', 'lightburn', 'pdf', 'dxf']),
        description='Export format'
    )

class DictionaryInfoSchema(Schema):
    """Schema for dictionary information"""
    bits = fields.String(description='Bit size of markers')
    description = fields.String(description='Dictionary description')
    max_markers = fields.Integer(description='Maximum number of markers')