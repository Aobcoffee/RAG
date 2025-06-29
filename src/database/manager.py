"""
Database connection and operations module.
Handles connections to various SQL databases and schema introspection.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from loguru import logger

from ..utils.config import Config


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine: Optional[Engine] = None
        self.metadata: Optional[MetaData] = None
        self._schema_cache: Dict[str, Any] = {}
        
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            connection_string = self._build_connection_string()
            self.engine = create_engine(
                connection_string,
                pool_timeout=30,
                pool_recycle=3600,
                echo=self.config.app.debug
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            logger.info("Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def _build_connection_string(self) -> str:
        """Build database connection string based on configuration."""
        db_config = self.config.database
        db_type = os.getenv('DB_TYPE', 'sqlserver').lower()
        
        if db_type == 'sqlserver':
            server = os.getenv('DB_SERVER', db_config.sqlserver.server)
            port = os.getenv('DB_PORT', db_config.sqlserver.port)
            database = os.getenv('DB_NAME', db_config.sqlserver.database)
            username = os.getenv('DB_USERNAME', db_config.sqlserver.username)
            password = os.getenv('DB_PASSWORD', db_config.sqlserver.password)
            driver = db_config.sqlserver.driver
            
            return f"mssql+pyodbc://{username}:{password}@{server}:{port}/{database}?driver={driver}"
            
        elif db_type == 'postgresql':
            host = os.getenv('DB_SERVER', db_config.postgresql.host)
            port = os.getenv('DB_PORT', db_config.postgresql.port)
            database = os.getenv('DB_NAME', db_config.postgresql.database)
            username = os.getenv('DB_USERNAME', db_config.postgresql.username)
            password = os.getenv('DB_PASSWORD', db_config.postgresql.password)
            
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
            
        elif db_type == 'mysql':
            host = os.getenv('DB_SERVER', db_config.mysql.host)
            port = os.getenv('DB_PORT', db_config.mysql.port)
            database = os.getenv('DB_NAME', db_config.mysql.database)
            username = os.getenv('DB_USERNAME', db_config.mysql.username)
            password = os.getenv('DB_PASSWORD', db_config.mysql.password)
            
            return f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
            
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def execute_query(self, query: str) -> Tuple[List[Dict], List[str]]:
        """Execute SQL query and return results."""
        if not self.engine:
            raise RuntimeError("Database not connected")
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Get column names
                columns = list(result.keys())
                
                # Fetch all rows
                rows = [dict(row._mapping) for row in result.fetchall()]
                
                logger.info(f"Query executed successfully, returned {len(rows)} rows")
                return rows, columns
                
        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive database schema information."""
        if not self.engine:
            raise RuntimeError("Database not connected")
            
        if self._schema_cache:
            return self._schema_cache
            
        try:
            inspector = inspect(self.engine)
            schema_info = {
                'tables': {},
                'views': {},
                'relationships': []
            }
            
            # Get table information
            for table_name in inspector.get_table_names():
                table_info = self._get_table_info(inspector, table_name)
                schema_info['tables'][table_name] = table_info
            
            # Get view information
            for view_name in inspector.get_view_names():
                view_info = self._get_view_info(inspector, view_name)
                schema_info['views'][view_name] = view_info
            
            # Get foreign key relationships
            schema_info['relationships'] = self._get_relationships(inspector)
            
            self._schema_cache = schema_info
            logger.info(f"Schema information cached for {len(schema_info['tables'])} tables and {len(schema_info['views'])} views")
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            raise
    
    def _get_table_info(self, inspector, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table."""
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        # Get sample data
        sample_data = self._get_sample_data(table_name)
        
        return {
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'indexes': indexes,
            'sample_data': sample_data,
            'row_count': self._get_row_count(table_name)
        }
    
    def _get_view_info(self, inspector, view_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific view."""
        columns = inspector.get_columns(view_name)
        
        return {
            'columns': columns,
            'sample_data': self._get_sample_data(view_name, limit=5)
        }
    
    def _get_relationships(self, inspector) -> List[Dict[str, Any]]:
        """Get foreign key relationships between tables."""
        relationships = []
        
        for table_name in inspector.get_table_names():
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            for fk in foreign_keys:
                relationships.append({
                    'source_table': table_name,
                    'source_columns': fk['constrained_columns'],
                    'target_table': fk['referred_table'],
                    'target_columns': fk['referred_columns'],
                    'constraint_name': fk['name']
                })
        
        return relationships
    
    def _get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict]:
        """Get sample data from a table."""
        try:
            query = f"SELECT TOP {limit} * FROM {table_name}" if 'sqlserver' in str(self.engine.url) else f"SELECT * FROM {table_name} LIMIT {limit}"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return [dict(row._mapping) for row in result.fetchall()]
                
        except Exception as e:
            logger.warning(f"Could not get sample data for {table_name}: {e}")
            return []
    
    def _get_row_count(self, table_name: str) -> Optional[int]:
        """Get approximate row count for a table."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                return result.fetchone()[0]
                
        except Exception as e:
            logger.warning(f"Could not get row count for {table_name}: {e}")
            return None
    
    def get_table_names(self) -> List[str]:
        """Get list of all table names."""
        if not self.engine:
            raise RuntimeError("Database not connected")
            
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Validate SQL query without executing it."""
        if not self.engine:
            return False, "Database not connected"
            
        try:
            # Add EXPLAIN to validate query structure
            explain_query = f"EXPLAIN {query}"
            
            with self.engine.connect() as conn:
                conn.execute(text(explain_query))
                
            return True, "Query is valid"
            
        except Exception as e:
            return False, str(e)
    
    def disconnect(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self._schema_cache.clear()
            logger.info("Database connection closed")
