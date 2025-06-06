from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging
import uuid
from .base_service import BaseService
from utils.error_handlers import (
    APIError, ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)

logger = logging.getLogger(__name__)

class AuthService(BaseService):
    """Service for managing authentication-related operations."""
    
    def register_user(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user."""
        try:
            self.log_operation("register_user", {
                "email": email,
                "user_data": user_data
            })
            
            # Validate required fields
            self.validate_required_fields(
                user_data,
                ["username", "full_name"]
            )
            
            # Create user in auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                raise APIError("Failed to create user account")
            
            # Add metadata
            user_data.update({
                'id': auth_response.user.id,
                'email': email,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            # Create user profile
            result = self.supabase.table('users').insert(user_data).execute()
            if not result.data:
                raise APIError("Failed to create user profile")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "register_user")
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login a user."""
        try:
            self.log_operation("login_user", {"email": email})
            
            # Authenticate user
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                raise AuthenticationError("Invalid email or password")
            
            # Get user profile
            user = self.supabase.table('users').select('*').eq('id', auth_response.user.id).execute()
            if not user.data:
                raise ResourceNotFoundError("User profile not found")
            
            return {
                'user': user.data[0],
                'session': auth_response.session
            }
            
        except Exception as e:
            self.handle_service_error(e, "login_user")
    
    def logout_user(self, user_id: str) -> None:
        """Logout a user."""
        try:
            self.log_operation("logout_user", {"user_id": user_id})
            
            # Sign out user
            self.supabase.auth.sign_out()
            
        except Exception as e:
            self.handle_service_error(e, "logout_user")
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user's profile."""
        try:
            self.log_operation("get_user_profile", {"user_id": user_id})
            
            user = self.supabase.table('users').select('*').eq('id', user_id).execute()
            if not user.data:
                return None
            
            return user.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "get_user_profile")
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user's profile."""
        try:
            self.log_operation("update_user_profile", {
                "user_id": user_id,
                "updates": updates
            })
            
            # Verify user exists
            user = self.get_user_profile(user_id)
            if not user:
                raise ResourceNotFoundError("User not found")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update profile
            result = self.supabase.table('users').update(updates).eq('id', user_id).execute()
            if not result.data:
                raise APIError("Failed to update user profile")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "update_user_profile")
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        """Change a user's password."""
        try:
            self.log_operation("change_password", {"user_id": user_id})
            
            # Update password
            self.supabase.auth.update_user({
                "password": new_password
            })
            
        except Exception as e:
            self.handle_service_error(e, "change_password")
    
    def reset_password(self, email: str) -> None:
        """Send a password reset email."""
        try:
            self.log_operation("reset_password", {"email": email})
            
            # Send reset email
            self.supabase.auth.reset_password_for_email(email)
            
        except Exception as e:
            self.handle_service_error(e, "reset_password")
    
    def verify_email(self, token: str) -> None:
        """Verify a user's email address."""
        try:
            self.log_operation("verify_email", {"token": token})
            
            # Verify email
            self.supabase.auth.verify_otp({
                "token_hash": token,
                "type": "email"
            })
            
        except Exception as e:
            self.handle_service_error(e, "verify_email")
    
    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh a user's session."""
        try:
            self.log_operation("refresh_session", {"refresh_token": refresh_token})
            
            # Refresh session
            session = self.supabase.auth.refresh_session()
            if not session:
                raise AuthenticationError("Failed to refresh session")
            
            return session
            
        except Exception as e:
            self.handle_service_error(e, "refresh_session")
