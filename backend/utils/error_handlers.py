from flask import jsonify
from datetime import datetime
from typing import Any, Dict, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

class ValidationError(APIError):
    """Raised when input validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(APIError):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)

class AuthorizationError(APIError):
    """Raised when user lacks required permissions."""
    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)

class ResourceNotFoundError(APIError):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)

class ConflictError(APIError):
    """Raised when there's a conflict with existing resources."""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)

def handle_api_error(error: APIError):
    """Handle API errors and return standardized JSON response."""
    # Format response to match frontend expectations
    response = {
        'data': None,
        'error': error.message,
        'status_code': error.status_code,
        'timestamp': error.timestamp
    }
    if error.details:
        response['details'] = error.details
    
    # Log the error
    logger.error(f"API Error: {error.message}", extra={
        'status_code': error.status_code,
        'details': error.details
    })
    
    return jsonify(response), error.status_code

def handle_validation_error(error):
    """Handle validation errors."""
    if isinstance(error, ValidationError):
        return handle_api_error(error)
    # For non-ValidationError errors, wrap them in a ValidationError
    return handle_api_error(ValidationError(str(error), details=getattr(error, 'errors', None)))

def handle_general_error(error):
    """Handle unexpected errors."""
    logger.exception("Unexpected error occurred")
    if isinstance(error, APIError):
        return handle_api_error(error)
    return handle_api_error(APIError(
        message="An unexpected error occurred",
        details={'error_type': error.__class__.__name__}
    )) 