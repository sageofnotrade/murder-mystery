from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

class MockSupabaseClient:
    def __init__(self):
        self.tables = {}
        self.auth = MockAuth()
        
    def table(self, table_name: str) -> 'MockTable':
        if table_name not in self.tables:
            self.tables[table_name] = MockTable(table_name)
        return self.tables[table_name]

class MockTable:
    def __init__(self, name: str):
        self.name = name
        self.data = []
        self._select_columns = None
        self._where_conditions = []
        self._order_by = None
        self._limit = None
        
    def select(self, *columns: str) -> 'MockTable':
        self._select_columns = columns
        return self
        
    def insert(self, data: Dict[str, Any]) -> 'MockTable':
        if isinstance(data, dict):
            data = [data]
        for item in data:
            if 'id' not in item:
                item['id'] = str(uuid.uuid4())
            if 'created_at' not in item:
                item['created_at'] = datetime.now().isoformat()
            if 'updated_at' not in item:
                item['updated_at'] = datetime.now().isoformat()
            self.data.append(item)
        return self
        
    def update(self, data: Dict[str, Any]) -> 'MockTable':
        for item in self.data:
            if all(item.get(k) == v for k, v in self._where_conditions):
                item.update(data)
                item['updated_at'] = datetime.now().isoformat()
        return self
        
    def delete(self) -> 'MockTable':
        self.data = [item for item in self.data 
                    if not all(item.get(k) == v for k, v in self._where_conditions)]
        return self
        
    def eq(self, column: str, value: Any) -> 'MockTable':
        self._where_conditions.append((column, value))
        return self
        
    def order(self, column: str, desc: bool = False) -> 'MockTable':
        self._order_by = (column, desc)
        return self
        
    def limit(self, count: int) -> 'MockTable':
        self._limit = count
        return self
        
    def execute(self) -> Dict[str, Any]:
        # Apply filters
        filtered_data = self.data
        if self._where_conditions:
            filtered_data = [
                item for item in filtered_data
                if all(item.get(k) == v for k, v in self._where_conditions)
            ]
            
        # Apply ordering
        if self._order_by:
            column, desc = self._order_by
            filtered_data.sort(
                key=lambda x: x.get(column, ''),
                reverse=desc
            )
            
        # Apply limit
        if self._limit:
            filtered_data = filtered_data[:self._limit]
            
        # Apply column selection
        if self._select_columns:
            filtered_data = [
                {k: item[k] for k in self._select_columns if k in item}
                for item in filtered_data
            ]
            
        return {'data': filtered_data}

class MockAuth:
    def __init__(self):
        self.current_user = None
        
    def sign_in_with_password(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        # Mock successful sign in
        self.current_user = {
            'id': str(uuid.uuid4()),
            'email': credentials.get('email'),
            'role': 'authenticated'
        }
        return {
            'user': self.current_user,
            'session': {
                'access_token': 'mock-token',
                'refresh_token': 'mock-refresh-token'
            }
        }
        
    def sign_out(self) -> None:
        self.current_user = None 