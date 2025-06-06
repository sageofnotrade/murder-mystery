import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import logging
from .base_service import BaseService
from utils.error_handlers import (
    APIError, ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)

from backend.agents.models.template_models import MysteryTemplate
from backend.config import get_config
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class TemplateService(BaseService):
    """Service for managing template-related operations."""
    
    def __init__(self):
        config = get_config()
        self.supabase: Client = create_client(
            config.SUPABASE_URL, 
            config.SUPABASE_KEY
        )
        self.table_name = "mystery_templates"
    
    def get_templates(self, template_type: str = None) -> List[Dict[str, Any]]:
        """Get all templates, optionally filtered by type."""
        try:
            self.log_operation("get_templates", {"template_type": template_type})
            
            query = self.supabase.table('templates').select('*')
            if template_type:
                query = query.eq('type', template_type)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            self.handle_service_error(e, "get_templates")
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template."""
        try:
            self.log_operation("get_template", {"template_id": template_id})
            
            template = self.supabase.table('templates').select('*').eq('id', template_id).execute()
            if not template.data:
                raise ResourceNotFoundError(f"Template {template_id} not found")
            
            return template.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "get_template")
    
    def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new template."""
        try:
            self.log_operation("create_template", {"template_data": template_data})
            
            # Validate required fields
            self.validate_required_fields(
                template_data,
                ["name", "type", "content"]
            )
            
            # Add metadata
            template_data.update({
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            # Create template
            result = self.supabase.table('templates').insert(template_data).execute()
            if not result.data:
                raise APIError("Failed to create template")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "create_template")
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing template."""
        try:
            self.log_operation("update_template", {
                "template_id": template_id,
                "updates": updates
            })
            
            # Verify template exists
            template = self.get_template(template_id)
            if not template:
                raise ResourceNotFoundError(f"Template {template_id} not found")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update template
            result = self.supabase.table('templates').update(updates).eq('id', template_id).execute()
            if not result.data:
                raise APIError("Failed to update template")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "update_template")
    
    def delete_template(self, template_id: str) -> None:
        """Delete a template."""
        try:
            self.log_operation("delete_template", {"template_id": template_id})
            
            # Verify template exists
            template = self.get_template(template_id)
            if not template:
                raise ResourceNotFoundError(f"Template {template_id} not found")
            
            # Delete template
            result = self.supabase.table('templates').delete().eq('id', template_id).execute()
            if not result.data:
                raise APIError("Failed to delete template")
            
        except Exception as e:
            self.handle_service_error(e, "delete_template")
    
    def get_template_by_type(self, template_type: str) -> List[Dict[str, Any]]:
        """Get all templates of a specific type."""
        try:
            self.log_operation("get_template_by_type", {"template_type": template_type})
            
            templates = self.supabase.table('templates').select('*').eq('type', template_type).execute()
            return templates.data
            
        except Exception as e:
            self.handle_service_error(e, "get_template_by_type")
    
    def validate_template_content(self, template_type: str, content: Dict[str, Any]) -> bool:
        """Validate template content based on type."""
        try:
            self.log_operation("validate_template_content", {
                "template_type": template_type,
                "content": content
            })
            
            # Define required fields for each template type
            required_fields = {
                'story': ['title', 'description', 'genre', 'difficulty'],
                'suspect': ['name', 'background', 'motives', 'alibi'],
                'clue': ['title', 'description', 'type', 'location'],
                'location': ['name', 'description', 'type', 'connections']
            }
            
            # Check if template type is valid
            if template_type not in required_fields:
                raise ValidationError(f"Invalid template type: {template_type}")
            
            # Validate required fields
            for field in required_fields[template_type]:
                if field not in content:
                    raise ValidationError(f"Missing required field: {field}")
            
            return True
            
        except Exception as e:
            self.handle_service_error(e, "validate_template_content")

    def get_all_templates(self, limit: int = 100, offset: int = 0) -> List[MysteryTemplate]:
        """Retrieve all mystery templates with pagination."""
        response = self.supabase.table(self.table_name).select("*").limit(limit).offset(offset).execute()
        
        templates = []
        for item in response.data:
            templates.append(MysteryTemplate(**item))
        
        return templates
    
    def get_template_by_id(self, template_id: str) -> Optional[MysteryTemplate]:
        """Retrieve a specific template by ID."""
        response = self.supabase.table(self.table_name).select("*").eq("id", template_id).execute()
        
        if not response.data:
            return None
            
        return MysteryTemplate(**response.data[0])
    
    def search_templates(self, query: str, limit: int = 10) -> List[MysteryTemplate]:
        """Search for templates by title or description."""
        # This is a simplified search implementation
        response = self.supabase.table(self.table_name).select("*").like("title", f"%{query}%").limit(limit).execute()
        
        templates = []
        for item in response.data:
            templates.append(MysteryTemplate(**item))
            
        return templates 