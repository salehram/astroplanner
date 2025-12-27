"""
Test Database Migration Module

Tests for database migration functionality including
data export/import, validation, and error handling.
"""
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime

from config.migration import (
    DatabaseMigrator, migrate_database,
    export_database_data, import_database_data
)


class TestDatabaseMigrator:
    """Test DatabaseMigrator class."""
    
    def test_migrator_initialization(self, sqlite_config, postgresql_config):
        """Test migrator initialization."""
        migrator = DatabaseMigrator(sqlite_config, postgresql_config)
        assert migrator.source_config == sqlite_config
        assert migrator.target_config == postgresql_config
        assert migrator.tables_migrated == []
        assert migrator.records_migrated == 0
        assert migrator.errors == []
        assert migrator.warnings == []
    
    def test_export_empty_database(self, sqlite_config):
        """Test exporting from empty database."""
        # Create a temporary SQLite database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Create empty database file
        sqlite_config.connection_string = f'sqlite:///{tmp_path}'
        
        try:
            data = export_database_data(sqlite_config)
            assert isinstance(data, dict)
            assert 'metadata' in data
            assert 'tables' in data
            assert data['metadata']['export_timestamp'] is not None
            assert data['metadata']['source_database_type'] == 'sqlite'
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_migration_validation(self, sqlite_config, postgresql_config):
        """Test migration validation."""
        migrator = DatabaseMigrator(sqlite_config, postgresql_config)
        
        # Test source validation
        source_valid, source_error = migrator.validate_source()
        assert isinstance(source_valid, bool)
        if not source_valid:
            assert isinstance(source_error, str)
        
        # Test target validation (may fail if PostgreSQL not available)
        target_valid, target_error = migrator.validate_target()
        assert isinstance(target_valid, bool)
        if not target_valid:
            assert isinstance(target_error, str)


class TestMigrationFunction:
    """Test the migrate_database function."""
    
    def test_same_database_type_rejection(self, sqlite_config):
        """Test rejection of migration between same database types."""
        with pytest.raises(ValueError, match="same database type"):
            migrate_database(sqlite_config, sqlite_config)
    
    def test_migration_with_invalid_source(self, sqlite_config, postgresql_config):
        """Test migration with invalid source database."""
        # Use non-existent SQLite file
        invalid_config = sqlite_config
        invalid_config.connection_string = 'sqlite:///nonexistent.db'
        
        result = migrate_database(invalid_config, postgresql_config)
        assert result['status'] == 'failed'
        assert len(result['errors']) > 0
    
    def test_migration_parameters(self, sqlite_config, postgresql_config):
        """Test migration with various parameters."""
        # Test with validate_before=False, validate_after=False
        result = migrate_database(
            sqlite_config, 
            postgresql_config,
            validate_before=False,
            validate_after=False,
            backup_target=False
        )
        
        assert 'status' in result
        assert 'tables_migrated' in result
        assert 'records_migrated' in result
        assert 'errors' in result
        assert 'warnings' in result


class TestDataExportImport:
    """Test data export and import functions."""
    
    def test_export_data_structure(self, sqlite_config):
        """Test exported data structure."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        sqlite_config.connection_string = f'sqlite:///{tmp_path}'
        
        try:
            data = export_database_data(sqlite_config)
            
            # Verify structure
            assert 'metadata' in data
            assert 'tables' in data
            
            metadata = data['metadata']
            assert 'export_timestamp' in metadata
            assert 'source_database_type' in metadata
            assert 'total_records' in metadata
            assert 'table_count' in metadata
            
            assert isinstance(data['tables'], dict)
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_import_data_validation(self, postgresql_config):
        """Test import data validation."""
        # Create invalid data structure
        invalid_data = {
            'metadata': {},
            'tables': {}
        }
        
        # This should handle invalid data gracefully
        try:
            result = import_database_data(postgresql_config, invalid_data)
            # Should either succeed with empty data or fail gracefully
            assert isinstance(result, dict)
        except Exception as e:
            # Should provide meaningful error
            assert isinstance(e, (ValueError, TypeError))


class TestMigrationErrorHandling:
    """Test error handling during migration."""
    
    def test_connection_error_handling(self):
        """Test handling of connection errors."""
        from config.database import DatabaseConfig
        
        # Create config with invalid connection
        invalid_config = DatabaseConfig()
        invalid_config.db_type = 'postgresql'
        invalid_config.connection_string = 'postgresql://invalid:invalid@invalid:5432/invalid'
        invalid_config.pool_config = {}
        
        valid_sqlite = DatabaseConfig()
        valid_sqlite.db_type = 'sqlite'
        valid_sqlite.connection_string = 'sqlite:///test.db'
        valid_sqlite.pool_config = {}
        
        result = migrate_database(valid_sqlite, invalid_config)
        assert result['status'] == 'failed'
        assert len(result['errors']) > 0
    
    def test_migration_interruption(self, sqlite_config, postgresql_config):
        """Test handling of migration interruption."""
        # This is a conceptual test - in real scenarios you might test
        # keyboard interrupts or connection timeouts
        migrator = DatabaseMigrator(sqlite_config, postgresql_config)
        
        # Test that migrator handles partial failures gracefully
        assert migrator.errors == []
        assert migrator.warnings == []
        assert migrator.records_migrated == 0


class TestMigrationIntegration:
    """Integration tests for migration (requires both databases)."""
    
    @pytest.mark.skipif(
        not os.getenv('TEST_DATABASE_URL'),
        reason="PostgreSQL test database not configured"
    )
    def test_full_migration_cycle(self, db_config):
        """Test complete migration cycle with real databases."""
        if db_config.db_type == 'sqlite':
            pytest.skip("Need both SQLite and PostgreSQL for migration test")
        
        # This would be a full integration test
        # In a real scenario, you would:
        # 1. Set up test data in source database
        # 2. Perform migration
        # 3. Verify data integrity in target database
        # 4. Test reverse migration if supported
        pass
    
    def test_migration_performance(self, sqlite_config):
        """Test migration performance with larger datasets."""
        # This would test migration performance
        # with various data sizes and complexity
        pass