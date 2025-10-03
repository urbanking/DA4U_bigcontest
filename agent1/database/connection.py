"""
Database Connection Manager
Handles PostgreSQL connections using SQLAlchemy
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for ORM models
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        """Initialize database connection from environment variables"""
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'commercial_district_db')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', '')
        
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Create SQLAlchemy engine with connection pooling"""
        try:
            connection_string = (
                f"postgresql://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
            
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600,
                echo=False  # Set to True for SQL query logging
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database engine initialized: {self.db_host}:{self.db_port}/{self.db_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def get_session(self):
        """
        Get a new database session
        
        Usage:
            db = DatabaseManager()
            with db.get_session() as session:
                result = session.execute(text("SELECT * FROM stores"))
        """
        return self.SessionLocal()
    
    def execute_query(self, query: str, params: dict = None):
        """
        Execute a SQL query and return results
        
        Args:
            query: SQL query string
            params: Dictionary of query parameters
            
        Returns:
            List of result rows
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                session.commit()
                return result.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_from_file(self, file_path: str):
        """
        Execute SQL commands from a file (e.g., schema.sql)
        
        Args:
            file_path: Path to SQL file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_commands = f.read()
            
            with self.engine.begin() as connection:
                # Split by semicolon and execute each statement
                for statement in sql_commands.split(';'):
                    statement = statement.strip()
                    if statement:
                        connection.execute(text(statement))
            
            logger.info(f"Successfully executed SQL from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to execute SQL file: {e}")
            raise
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close(self):
        """Close database engine"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine closed")


# Global database instance
db_manager = None


def get_db_manager():
    """Get or create global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager


if __name__ == "__main__":
    # Test database connection
    db = DatabaseManager()
    if db.test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")

