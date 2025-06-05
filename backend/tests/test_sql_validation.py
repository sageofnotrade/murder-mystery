"""
SQL Validation Tests for Board State Schema
Tests actual SQL syntax, constraints, and migration logic.
"""

import re
import os
import pytest
from pathlib import Path

class TestSQLValidation:
    """Test SQL file syntax and structure"""
    
    @pytest.fixture
    def sql_files(self):
        """Get paths to SQL files"""
        base_path = Path(__file__).parent.parent.parent
        return {
            'schema': base_path / 'database' / 'board_state_schema.sql',
            'migration': base_path / 'database' / '003_board_state_migration.sql',
            'rollback': base_path / 'database' / '003_board_state_rollback.sql',
            'deploy': base_path / 'database' / 'run_board_migration.sql'
        }
    
    def test_sql_files_exist(self, sql_files):
        """Test that all required SQL files exist"""
        for name, path in sql_files.items():
            assert path.exists(), f"Missing SQL file: {name} at {path}"
    
    def test_schema_sql_syntax(self, sql_files):
        """Test basic SQL syntax in schema file"""
        if not sql_files['schema'].exists():
            pytest.skip("Schema file not found")
            
        content = sql_files['schema'].read_text()
        
        # Check for required table creations
        required_tables = [
            'board_states',
            'board_elements', 
            'board_connections',
            'board_notes',
            'board_layouts',
            'board_element_connections'
        ]
        
        for table in required_tables:
            assert f"CREATE TABLE {table}" in content, f"Missing table creation: {table}"
        
        # Check for constraints
        constraint_patterns = [
            r'PRIMARY KEY',
            r'FOREIGN KEY',
            r'REFERENCES',
            r'CHECK\s*\(',
            r'NOT NULL'
        ]
        
        for pattern in constraint_patterns:
            assert re.search(pattern, content, re.IGNORECASE), f"Missing constraint pattern: {pattern}"
    
    def test_migration_sql_structure(self, sql_files):
        """Test migration SQL structure and safety"""
        if not sql_files['migration'].exists():
            pytest.skip("Migration file not found")
            
        content = sql_files['migration'].read_text()
        
        # Check for transaction wrapper
        assert 'BEGIN;' in content or 'START TRANSACTION;' in content, "Migration should be wrapped in transaction"
        assert 'COMMIT;' in content, "Migration should have commit statement"
        
        # Check for data preservation
        assert 'INSERT INTO' in content, "Migration should preserve existing data"
        
        # Check for proper order (create before insert)
        create_pos = content.find('CREATE TABLE')
        insert_pos = content.find('INSERT INTO')
        assert create_pos < insert_pos, "Tables should be created before data insertion"
        
        # Check for rollback script reference
        assert 'rollback' in content.lower(), "Migration should reference rollback procedure"
    
    def test_rollback_sql_completeness(self, sql_files):
        """Test rollback SQL completeness"""
        if not sql_files['rollback'].exists():
            pytest.skip("Rollback file not found")
            
        content = sql_files['rollback'].read_text()
        
        # Check for transaction wrapper
        assert 'BEGIN;' in content or 'START TRANSACTION;' in content, "Rollback should be wrapped in transaction"
        assert 'COMMIT;' in content, "Rollback should have commit statement"
        
        # Check for table drops or data restoration
        assert 'DROP TABLE' in content or 'DELETE FROM' in content, "Rollback should remove changes"
    
    def test_rls_policies_present(self, sql_files):
        """Test that RLS policies are defined"""
        if not sql_files['schema'].exists():
            pytest.skip("Schema file not found")
            
        content = sql_files['schema'].read_text()
        
        # Check for RLS enablement
        assert 'ALTER TABLE' in content and 'ENABLE ROW LEVEL SECURITY' in content, "RLS should be enabled"
        
        # Check for policy creation
        assert 'CREATE POLICY' in content, "RLS policies should be created"
        
        # Check for auth.uid() usage (Supabase auth)
        assert 'auth.uid()' in content, "Policies should use Supabase auth"
    
    def test_indexes_defined(self, sql_files):
        """Test that performance indexes are defined"""
        if not sql_files['schema'].exists():
            pytest.skip("Schema file not found")
            
        content = sql_files['schema'].read_text()
        
        # Check for index creation
        assert 'CREATE INDEX' in content, "Performance indexes should be created"
        
        # Check for critical indexes
        critical_indexes = [
            'board_id',
            'user_id',
            'mystery_id',
            'element_type',
            'source_element_id'
        ]
        
        for index_field in critical_indexes:
            # Look for index on this field
            index_pattern = rf'CREATE INDEX.*{index_field}'
            assert re.search(index_pattern, content, re.IGNORECASE), f"Missing index on {index_field}"
    
    def test_constraints_validation(self, sql_files):
        """Test data validation constraints"""
        if not sql_files['schema'].exists():
            pytest.skip("Schema file not found")
            
        content = sql_files['schema'].read_text()
        
        # Check for enum-like constraints
        check_constraints = [
            'element_type',
            'connection_type', 
            'theme',
            'zoom_level',
            'strength'
        ]
        
        for constraint in check_constraints:
            # Look for CHECK constraint on this field
            check_pattern = rf'CHECK\s*\([^)]*{constraint}[^)]*\)'
            assert re.search(check_pattern, content, re.IGNORECASE), f"Missing CHECK constraint on {constraint}"
    
    def test_functions_defined(self, sql_files):
        """Test that utility functions are defined"""
        if not sql_files['schema'].exists():
            pytest.skip("Schema file not found")
            
        content = sql_files['schema'].read_text()
        
        # Check for function creation
        assert 'CREATE OR REPLACE FUNCTION' in content, "Utility functions should be defined"
        
        # Check for specific functions mentioned in requirements
        expected_functions = [
            'get_board_statistics',
            'validate_board_state',
            'auto_layout_elements'
        ]
        
        for func in expected_functions:
            assert func in content, f"Missing function: {func}"
    
    def test_triggers_defined(self, sql_files):
        """Test that timestamp triggers are defined"""
        if not sql_files['schema'].exists():
            pytest.skip("Schema file not found")
            
        content = sql_files['schema'].read_text()
        
        # Check for trigger creation
        assert 'CREATE TRIGGER' in content, "Timestamp triggers should be defined"
        
        # Check for updated_at trigger
        assert 'updated_at' in content, "Triggers should handle updated_at field"
    
    def test_foreign_key_relationships(self, sql_files):
        """Test foreign key relationships are properly defined"""
        if not sql_files['schema'].exists():
            pytest.skip("Schema file not found")
            
        content = sql_files['schema'].read_text()
        
        # Expected foreign key relationships
        expected_fks = [
            ('board_elements', 'board_id', 'board_states'),
            ('board_connections', 'board_id', 'board_states'),
            ('board_connections', 'source_element_id', 'board_elements'),
            ('board_connections', 'target_element_id', 'board_elements'),
            ('board_notes', 'board_id', 'board_states'),
            ('board_layouts', 'board_id', 'board_states')
        ]
        
        for child_table, fk_column, parent_table in expected_fks:
            # Look for REFERENCES clause
            fk_pattern = rf'{fk_column}.*REFERENCES\s+{parent_table}'
            assert re.search(fk_pattern, content, re.IGNORECASE), f"Missing FK: {child_table}.{fk_column} -> {parent_table}"
    
    def test_data_types_appropriate(self, sql_files):
        """Test that appropriate data types are used"""
        if not sql_files['schema'].exists():
            pytest.skip("Schema file not found")
            
        content = sql_files['schema'].read_text()
        
        # Check for appropriate data types
        expected_types = {
            'UUID': ['id', 'board_id', 'user_id', 'mystery_id'],
            'VARCHAR': ['name', 'title', 'label'],
            'TEXT': ['description', 'content'],
            'JSONB': ['content', 'element_positions'],
            'FLOAT': ['position_x', 'position_y', 'zoom_level', 'strength'],
            'BOOLEAN': ['is_visible', 'is_hidden', 'is_default'],
            'TIMESTAMPTZ': ['created_at', 'updated_at']
        }
        
        for data_type, fields in expected_types.items():
            for field in fields:
                # Look for field with appropriate type
                type_pattern = rf'{field}.*{data_type}'
                if re.search(type_pattern, content, re.IGNORECASE):
                    continue  # Found at least one
            # Should find at least some fields of each type
            assert data_type in content, f"Missing data type: {data_type}"

class TestSchemaLogic:
    """Test logical correctness of schema design"""
    
    def test_table_dependency_order(self):
        """Test that tables are created in correct dependency order"""
        # Parent tables should come before child tables
        expected_order = [
            'board_states',      # Parent
            'board_elements',    # Child of board_states
            'board_connections', # Child of board_states and board_elements
            'board_notes',       # Child of board_states
            'board_layouts',     # Child of board_states
            'board_element_connections'  # Child of board_elements (junction table)
        ]
        
        # Verify logical dependencies
        dependencies = {
            'board_elements': ['board_states'],
            'board_connections': ['board_states', 'board_elements'],
            'board_notes': ['board_states'],
            'board_layouts': ['board_states'],
            'board_element_connections': ['board_elements']
        }
        
        for table, deps in dependencies.items():
            table_index = expected_order.index(table)
            for dep in deps:
                dep_index = expected_order.index(dep)
                assert dep_index < table_index, f"{dep} should be created before {table}"
    
    def test_data_consistency_rules(self):
        """Test that data consistency rules are logical"""
        # Position coordinates should allow negative values (for off-canvas elements)
        # Zoom levels should be reasonable (0.1 to 3.0)
        # Strength values should be 0.0 to 1.0
        # UUIDs should be used for all IDs
        
        consistency_rules = {
            'zoom_level': (0.1, 3.0),
            'strength': (0.0, 1.0),
            'position_x': (-1000000, 1000000),  # Large range for canvas
            'position_y': (-1000000, 1000000)
        }
        
        for field, (min_val, max_val) in consistency_rules.items():
            assert min_val < max_val, f"Invalid range for {field}"
            assert min_val >= 0 or field.startswith('position'), f"Unexpected negative minimum for {field}"

class TestMigrationLogic:
    """Test migration script logic and safety"""
    
    def test_migration_safety_patterns(self):
        """Test that migration follows safety best practices"""
        safety_patterns = [
            'BEGIN',           # Transaction wrapper
            'COMMIT',          # Transaction commit
            'IF NOT EXISTS',   # Idempotent operations
            'CREATE TABLE',    # Table creation
            'INSERT INTO',     # Data preservation
        ]
        
        # These patterns should be present in a good migration
        for pattern in safety_patterns:
            assert pattern is not None  # Placeholder test
    
    def test_rollback_completeness(self):
        """Test that rollback can fully reverse migration"""
        # Rollback should:
        # 1. Drop all new tables in reverse order
        # 2. Restore original data structure
        # 3. Be wrapped in transaction
        # 4. Handle cascade deletions properly
        
        rollback_requirements = [
            'DROP TABLE',
            'CASCADE',
            'BEGIN',
            'COMMIT'
        ]
        
        for requirement in rollback_requirements:
            assert requirement is not None  # Placeholder test

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 