import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from models.template_models import MysteryTemplate
from config import get_config
from supabase import create_client, Client

class TemplateService:
    def __init__(self):
        config = get_config()
        self.supabase: Client = create_client(
            config.SUPABASE_URL, 
            config.SUPABASE_KEY
        )
        self.table_name = "mystery_templates"
    
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
    
    def create_template(self, template: MysteryTemplate) -> MysteryTemplate:
        """Create a new mystery template."""
        # Generate ID if not provided
        if not template.id:
            template.id = str(uuid.uuid4())
            
        # Set timestamps
        current_time = datetime.utcnow().isoformat()
        template.created_at = current_time
        template.updated_at = current_time
        
        # Insert into database
        template_dict = template.model_dump()
        response = self.supabase.table(self.table_name).insert(template_dict).execute()
        
        # Return the created template
        return MysteryTemplate(**response.data[0])
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Optional[MysteryTemplate]:
        """Update an existing template."""
        # Update timestamp
        template_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update in database
        response = self.supabase.table(self.table_name).update(template_data).eq("id", template_id).execute()
        
        if not response.data:
            return None
            
        return MysteryTemplate(**response.data[0])
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template by ID."""
        response = self.supabase.table(self.table_name).delete().eq("id", template_id).execute()
        
        # If data is empty, deletion failed
        return len(response.data) > 0
    
    def search_templates(self, query: str, limit: int = 10) -> List[MysteryTemplate]:
        """Search for templates by title or description."""
        # This is a simplified search implementation
        response = self.supabase.table(self.table_name).select("*").like("title", f"%{query}%").limit(limit).execute()
        
        templates = []
        for item in response.data:
            templates.append(MysteryTemplate(**item))
            
        return templates 