from typing import Any, Dict, Optional
import logging
from utils.error_handlers import (
    APIError, ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)

logger = logging.getLogger(__name__)

class BaseService:
    """Base class for all services with common error handling."""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def handle_database_error(self, error: Exception, operation: str) -> None:
        """Handle database-related errors."""
        error_msg = str(error)
        if "not found" in error_msg.lower():
            raise ResourceNotFoundError(f"Resource not found during {operation}")
        elif "permission denied" in error_msg.lower():
            raise AuthorizationError(f"Permission denied during {operation}")
        elif "invalid input" in error_msg.lower():
            raise ValidationError(f"Invalid input during {operation}")
        else:
            logger.error(f"Database error during {operation}: {error_msg}")
            raise APIError(f"Database operation failed during {operation}")
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> None:
        """Validate that required fields are present in the data."""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                details={'missing_fields': missing_fields}
            )
    
    def log_operation(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log an operation with optional details."""
        log_msg = f"Operation: {operation}"
        if details:
            log_msg += f" - Details: {details}"
        logger.info(log_msg)
    
    def handle_service_error(self, error: Exception, operation: str) -> None:
        """Handle service-level errors."""
        # If it's already one of our custom errors, just re-raise it
        if isinstance(error, (APIError, ValidationError, ResourceNotFoundError, AuthenticationError, AuthorizationError)):
            raise error
        
        # For other errors, try to map them to appropriate error types
        error_msg = str(error)
        if "not found" in error_msg.lower():
            raise ResourceNotFoundError(f"Resource not found during {operation}")
        elif "permission denied" in error_msg.lower():
            raise AuthorizationError(f"Permission denied during {operation}")
        elif "invalid input" in error_msg.lower():
            raise ValidationError(f"Invalid input during {operation}")
        else:
            logger.error(f"Service error during {operation}: {error_msg}")
            raise APIError(f"Service operation failed during {operation}") 