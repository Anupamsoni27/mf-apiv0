"""
Validation schemas for API request data.
Uses marshmallow for schema definition and validation.
"""
from marshmallow import Schema, fields, validate, ValidationError


# ============================================================================
# USER SCHEMAS
# ============================================================================

class CreateUserSchema(Schema):
    """Schema for creating a new user."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=True)
    picture = fields.Url(required=False, allow_none=True)
    phoneNumber = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))


class UpdateUserSchema(Schema):
    """Schema for updating a user."""
    name = fields.Str(required=False, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=False)
    picture = fields.Url(required=False, allow_none=True)
    phoneNumber = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))


# ============================================================================
# FAVORITES SCHEMAS
# ============================================================================

class AddFavoriteSchema(Schema):
    """Schema for adding a favorite."""
    userId = fields.Str(required=True, validate=validate.Length(min=1))
    itemId = fields.Str(required=True, validate=validate.Length(min=1))
    itemType = fields.Str(
        required=True,
        validate=validate.OneOf(['stock', 'fund'])
    )
    itemName = fields.Str(required=False, validate=validate.Length(max=500))


class RemoveFavoriteSchema(Schema):
    """Schema for removing a favorite."""
    userId = fields.Str(required=True, validate=validate.Length(min=1))
    itemId = fields.Str(required=True, validate=validate.Length(min=1))
    itemType = fields.Str(
        required=True,
        validate=validate.OneOf(['stock', 'fund'])
    )


# ============================================================================
# QUERY PARAMETER SCHEMAS
# ============================================================================

class PaginationSchema(Schema):
    """Schema for pagination parameters."""
    skip = fields.Int(required=False, validate=validate.Range(min=0), load_default=0)
    limit = fields.Int(required=False, validate=validate.Range(min=1, max=1000), load_default=50)


class SortingSchema(Schema):
    """Schema for sorting parameters."""
    sort_by = fields.Str(required=False, load_default='name')
    order = fields.Str(
        required=False,
        validate=validate.OneOf(['asc', 'desc']),
        load_default='asc'
    )


class SearchSchema(Schema):
    """Schema for search parameters."""
    search = fields.Str(required=False, validate=validate.Length(max=200), load_default='')


class FundQuerySchema(PaginationSchema, SortingSchema):
    """Combined schema for fund queries."""
    date = fields.Str(required=False, allow_none=True)


class StockQuerySchema(PaginationSchema, SortingSchema, SearchSchema):
    """Combined schema for stock queries."""
    pass


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_request_data(schema_class, data):
    """
    Validate request data against a schema.
    
    Args:
        schema_class: The marshmallow schema class to use
        data: The data to validate
        
    Returns:
        Tuple of (validated_data, errors)
    """
    schema = schema_class()
    try:
        validated = schema.load(data)
        return validated, None
    except ValidationError as err:
        return None, err.messages


def validate_query_params(schema_class, params):
    """
    Validate query parameters against a schema.
    
    Args:
        schema_class: The marshmallow schema class to use
        params: The query parameters to validate
        
    Returns:
        Tuple of (validated_params, errors)
    """
    return validate_request_data(schema_class, params)
