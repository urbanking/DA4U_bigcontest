"""
Database Setup Script
Run this script to initialize the database with schema and sample data
"""

from database.connection import DatabaseManager
import os
import sys


def main():
    """Initialize database with schema"""
    
    print("="*60)
    print("DATABASE SETUP - Multi-Agent Consulting System")
    print("="*60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n❌ ERROR: .env file not found!")
        print("Please create .env file with database credentials.")
        print("See .env.example for template.\n")
        sys.exit(1)
    
    try:
        # Initialize database manager
        print("\n1. Connecting to database...")
        db = DatabaseManager()
        
        # Test connection
        print("2. Testing connection...")
        if not db.test_connection():
            print("❌ Database connection failed!")
            sys.exit(1)
        
        print("✓ Connection successful")
        
        # Execute schema
        print("\n3. Creating tables from schema.sql...")
        schema_path = os.path.join('database', 'schema.sql')
        
        if not os.path.exists(schema_path):
            print(f"❌ Schema file not found: {schema_path}")
            sys.exit(1)
        
        db.execute_from_file(schema_path)
        print("✓ Tables created successfully")
        
        # Verify tables
        print("\n4. Verifying tables...")
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        tables = db.execute_query(query)
        
        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "="*60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*60)
        print("\nYou can now run: python main.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

